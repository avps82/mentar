#!/usr/bin/env python3
"""T1.2 — generate responses from candidate models over eval/dataset_v1.jsonl.

Sends every dataset prompt to an OpenAI-compatible /v1/chat/completions endpoint and writes
one response file per model: eval/responses/{model}.jsonl (gitignored). Records latency per item.

Endpoint + key come from ENV (never hardcoded):
    export MENTAR_VLLM_BASE_URL="http://192.168.xx.xxx:4000/v1"
    export MENTAR_VLLM_API_KEY="<token>"
    python3 eval/run_candidates.py                 # all role=candidate models
    python3 eval/run_candidates.py --model llama3.1:8b
    python3 eval/run_candidates.py --dry-run       # print what would be sent, no network

Stdlib only. The HTTP call is routed through `post_chat` so tests can inject a fake (no network).
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "eval" / "dataset_v1.jsonl"
MODELS_YAML = ROOT / "eval" / "models.yaml"
RESPONSES_DIR = ROOT / "eval" / "responses"

TEMPERATURE = 0.2
MAX_TOKENS = 400
TIMEOUT = 120


def load_dataset(path: Path = DATASET) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def load_models(path: Path = MODELS_YAML) -> list[dict]:
    """Tiny YAML reader for the flat `models:` list (avoids a PyYAML dep for the runner)."""
    models: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("- {") or not s.endswith("}"):
            continue
        body = s[3:-1]
        entry: dict[str, str] = {}
        for part in body.split(","):
            if ":" not in part:
                continue
            k, v = part.split(":", 1)
            entry[k.strip()] = v.strip().strip('"')
        models.append(entry)
    return models


def build_pipeline_messages(system_prompt_text: str, prompt: str, grounding) -> list[dict]:
    """System message = system_prompt_text with {{grounding_passage}} filled; then the user turn.

    Core substitution drafted by the local model (gemma2:9b) and reviewed/normalised here
    (4-space, typed) as a "local-drafts / reviewer-verifies" experiment.
    """
    return [
        {"role": "system", "content": system_prompt_text.replace("{{grounding_passage}}", grounding or "")},
        {"role": "user", "content": prompt},
    ]


def pipeline_inputs(item: dict) -> tuple[str, str | None]:
    """Derive a clean (user_turn, grounding) for full-pipeline mode — no double-embedding.

    Injected-passage items put the poisoned passage ONLY in the grounding-data wrapper (where
    the system prompt neutralises it), with an innocent child turn — so we actually test the
    wrapper's defence rather than handing the model the injection un-wrapped in the user turn.
    """
    if item.get("suite") == "adversarial":
        if item.get("adversarial_type") == "injected_passage":
            return "Can you help me with my fractions, please?", item.get("grounding")
        return item["prompt"], None  # the child's message; no grounding
    if item.get("suite") == "reexplain":
        return f"Please explain {item.get('node')} to me using a {item.get('modality')} example.", item.get("grounding")
    return item["prompt"], None  # transfer: self-contained


def build_payload(item: dict, model: str, system_prompt_text: str | None = None) -> dict:
    if system_prompt_text:
        user_turn, grounding = pipeline_inputs(item)
        messages = build_pipeline_messages(system_prompt_text, user_turn, grounding)
    else:
        messages = [{"role": "user", "content": item["prompt"]}]
    return {"model": model, "messages": messages, "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS}


def post_chat(base_url: str, api_key: str, payload: dict, timeout: int = TIMEOUT) -> dict:
    """Real HTTP POST to /chat/completions. Tests inject a fake in place of this."""
    url = base_url.rstrip("/") + "/chat/completions"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def _content_of(resp: dict) -> str:
    try:
        return resp["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return ""


def run_model(model: str, items: list[dict], base_url: str, api_key: str,
              out_dir: Path = RESPONSES_DIR,
              post: Callable[..., dict] = post_chat,
              system_prompt_text: str | None = None) -> Path:
    """Generate + record responses for one model. Returns the responses file path.

    With system_prompt_text set (full-pipeline mode), each prompt is wrapped via the system
    prompt; responses are written to `{model}__pipeline.jsonl` so bare runs aren't clobbered.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = model.replace("/", "_").replace(":", "_") + ("__pipeline" if system_prompt_text else "")
    out_path = out_dir / f"{stem}.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for it in items:
            t0 = time.time()
            try:
                resp = post(base_url, api_key, build_payload(it, model, system_prompt_text))
                content, err = _content_of(resp), None
            except Exception as exc:  # noqa: BLE001
                content, err = "", repr(exc)
            f.write(json.dumps({
                "id": it["id"], "suite": it["suite"], "model": model,
                "response": content, "latency_s": round(time.time() - t0, 3),
                "error": err,
            }, ensure_ascii=True) + "\n")
    return out_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="T1.2 — run candidates over the eval dataset.")
    ap.add_argument("--model", action="append", default=None, help="Specific model id(s) to run.")
    ap.add_argument("--role", default="candidate", help="Run all models of this role (default: candidate).")
    ap.add_argument("--dry-run", action="store_true", help="Print what would be sent; no network.")
    ap.add_argument("--system-prompt", default=None,
                    help="Path to a system prompt (e.g. prompts/system_prompt.md) — runs the FULL "
                         "pipeline (safety wrapper). Writes {model}__pipeline.jsonl.")
    ap.add_argument("--suite", default=None, choices=["reexplain", "transfer", "adversarial"],
                    help="Restrict to one suite (e.g. adversarial for the pipeline safety re-run).")
    args = ap.parse_args(argv)

    items = load_dataset()
    if args.suite:
        items = [it for it in items if it.get("suite") == args.suite]
    models = load_models()
    if args.model:
        targets = [m["name"] for m in models if m["name"] in set(args.model)]
    else:
        targets = [m["name"] for m in models if m.get("role") == args.role]

    sys_text = Path(args.system_prompt).read_text(encoding="utf-8") if args.system_prompt else None

    if args.dry_run:
        mode = "FULL-PIPELINE" if sys_text else "bare"
        print(f"[dry-run] {mode}: {len(items)} prompts x {len(targets)} models: {targets}")
        if items and targets:
            print("[dry-run] sample payload:")
            print(json.dumps(build_payload(items[0], targets[0], sys_text), indent=2)[:800])
        return 0

    base_url = os.environ.get("MENTAR_VLLM_BASE_URL")
    cred = os.environ.get("MENTAR_VLLM_API_KEY")  # read from env; never hardcoded
    if not base_url or not cred:
        print("ERROR: set MENTAR_VLLM_BASE_URL and MENTAR_VLLM_API_KEY in the environment.")
        return 2

    for model in targets:
        print(f"[run] {model} — {len(items)} prompts{' (pipeline)' if sys_text else ''} ...")
        path = run_model(model, items, base_url, cred, system_prompt_text=sys_text)
        print(f"[run] wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
