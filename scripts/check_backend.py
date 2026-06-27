#!/usr/bin/env python3
"""Diagnose the local LLM backend Mentar will use.

Runs the EXACT path the tutor uses (load_inference_config -> make_llm_call) and
does one tiny test generation, so a PASS here means the web app / run-session
will talk to the model too. Prints clear remediation for the common failures.

Usage:
    python3 scripts/check_backend.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from a source checkout without an editable install.
_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.exists():
    sys.path.insert(0, str(_SRC))

from mentar.inference import load_inference_config, make_llm_call  # noqa: E402

PROBE_TIMEOUT_S = 20  # keep the diagnostic snappy (the app default is 120s)


def main() -> int:
    print("Mentar backend check\n" + "=" * 20)

    cfg = load_inference_config()
    if cfg is None:
        print("✗ No config/inference.yaml found.")
        print("  Fix: run  `mentar setup`  (or copy config/inference.example.yaml).")
        return 2

    backend = cfg.get("backend", "?")
    block = cfg.get(backend, {}) if isinstance(cfg.get(backend), dict) else {}
    safe_block = {k: v for k, v in block.items() if k != "api_key"}
    model = block.get("model") or block.get("model_path") or "(unset)"
    print(f"  config : {load_inference_config.__module__} -> config/inference.yaml")
    print(f"  backend: {backend}")
    print(f"  target : {safe_block}")
    print(f"  model  : {model}")
    if "api_key" in block:
        print("  api_key: (set)")
    print()

    # Override the timeout just for this probe so a dead backend fails fast.
    probe_cfg = dict(cfg)
    gen = dict(cfg.get("generation", {}))
    gen["timeout"] = PROBE_TIMEOUT_S
    gen["max_tokens"] = 16
    probe_cfg["generation"] = gen

    print(f"Sending a 1-word test prompt (timeout {PROBE_TIMEOUT_S}s)…")
    try:
        call = make_llm_call(probe_cfg)
        reply = call([{"role": "user", "content": "Reply with the single word: ping"}])
    except Exception as e:  # noqa: BLE001 — diagnostic: report any failure plainly
        print(f"\n✗ Backend UNREACHABLE / errored:\n    {type(e).__name__}: {e}\n")
        _remediation(backend, block)
        return 1

    if reply and reply.strip():
        print(f"\n✓ Backend is LIVE. Model replied: {reply.strip()!r}")
        print("  The tutor will use this model for Help explanations and questions.")
        return 0

    print("\n✗ Backend reachable but returned EMPTY text.")
    print("  Likely a 'reasoning' model spending the budget on hidden thinking.")
    print("  Fix: in config/inference.yaml add under `generation`:")
    print("         extra_body:\n           think: false")
    print("  (gemma2:9b is NOT a reasoning model — if you're on gemma*:12b, switch")
    print("   to gemma2:9b or set think:false.)")
    return 1


def _remediation(backend: str, block: dict) -> None:
    if backend == "ollama":
        url = block.get("base_url", "http://localhost:11434")
        model = block.get("model", "gemma2:9b")
        print("  Checklist (Ollama):")
        print("    1. Is the Ollama app running?   ollama list")
        print(f"    2. Is the model pulled?        ollama pull {model}")
        print(f"    3. Is the server up at {url} ?  curl -s {url}/api/tags")
    elif backend in ("vllm", "llamacpp"):
        url = block.get("base_url", "?")
        print("  Checklist (OpenAI-compatible server):")
        print(f"    1. Is the server running at {url} ?")
        print("    2. For llama.app:  llama serve -m <model> --port 8081")
        print("    3. Does base_url end in /v1 ?")
    else:
        print(f"  Backend '{backend}' — check base_url / server is running.")


if __name__ == "__main__":
    raise SystemExit(main())
