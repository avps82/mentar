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


def build_payload(item: dict, model: str) -> dict:
    return {
        "model": model,
        "messages": [{"role": "user", "content": item["prompt"]}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }


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
              post: Callable[..., dict] = post_chat) -> Path:
    """Generate + record responses for one model. Returns the responses file path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{model.replace('/', '_').replace(':', '_')}.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for it in items:
            t0 = time.time()
            try:
                resp = post(base_url, api_key, build_payload(it, model))
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
    args = ap.parse_args(argv)

    items = load_dataset()
    models = load_models()
    if args.model:
        targets = [m["name"] for m in models if m["name"] in set(args.model)]
    else:
        targets = [m["name"] for m in models if m.get("role") == args.role]

    if args.dry_run:
        print(f"[dry-run] {len(items)} prompts x {len(targets)} models: {targets}")
        if items and targets:
            print("[dry-run] sample payload:")
            print(json.dumps(build_payload(items[0], targets[0]), indent=2)[:600])
        return 0

    base_url = os.environ.get("MENTAR_VLLM_BASE_URL")
    cred = os.environ.get("MENTAR_VLLM_API_KEY")  # read from env; never hardcoded
    if not base_url or not cred:
        print("ERROR: set MENTAR_VLLM_BASE_URL and MENTAR_VLLM_API_KEY in the environment.")
        return 2

    for model in targets:
        print(f"[run] {model} — {len(items)} prompts ...")
        path = run_model(model, items, base_url, cred)
        print(f"[run] wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
