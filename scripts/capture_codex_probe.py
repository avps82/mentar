#!/usr/bin/env python3
"""Capture the REAL request/response shapes of the Codex backend (plan §P3, R2).

Run this ON A MACHINE WITH A CODEX LOGIN (`codex login` done):

    python3 scripts/capture_codex_probe.py

It sends one minimal request to the codex responses endpoint using the local
ChatGPT sign-in, and writes a REDACTED capture (no tokens, no account id) to
`codex_probe_capture.json` in the current directory. That capture becomes the
fixture the `_make_codex_call` adapter is written and tested against — the body
shape is unpublished and drifts, so we build against evidence, not blog posts.

Costs: one tiny request against the ChatGPT plan's quota. Sends only the words
"Reply with the single word: ping" — no child data, no personal data.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import httpx  # noqa: E402

from mentar.inference.codex_auth import get_access_token, read_credentials  # noqa: E402

ENDPOINT = "https://chatgpt.com/backend-api/codex/responses"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "gpt-5.2"


def main() -> int:
    creds = read_credentials()
    token = get_access_token()
    headers = {
        "Authorization": "Bearer <redacted-in-capture>",
        "Content-Type": "application/json",
        # the account header the codex backend expects
        "chatgpt-account-id": creds["account_id"] or "",
        "OpenAI-Beta": "responses=experimental",
        "originator": "codex_cli_rs",
    }
    body = {
        "model": MODEL,
        "instructions": "You are a helpful assistant.",
        "input": [{"type": "message", "role": "user",
                   "content": [{"type": "input_text",
                                "text": "Reply with the single word: ping"}]}],
        "stream": True,   # the codex backend is stream-first; capture the events
        "store": False,
    }
    real_headers = dict(headers)
    real_headers["Authorization"] = f"Bearer {token}"

    print(f"POST {ENDPOINT}  model={MODEL}")
    events: list[str] = []
    with httpx.stream("POST", ENDPOINT, headers=real_headers, json=body,
                      timeout=120.0) as resp:
        status = resp.status_code
        print(f"HTTP {status}")
        if status != 200:
            resp.read()
            capture = {"endpoint": ENDPOINT, "request_headers": headers,
                       "request_body": body, "status": status,
                       "response_text": resp.text[:5000]}
            Path("codex_probe_capture.json").write_text(json.dumps(capture, indent=2))
            print("Non-200 — capture written anyway (codex_probe_capture.json). "
                  "Try another model name as argv[1], e.g. gpt-5.2-codex.")
            return 1
        for line in resp.iter_lines():
            if line:
                events.append(line)
                if len(events) <= 8 or "output_text" in line:
                    print(" ", line[:160])

    capture = {"endpoint": ENDPOINT, "request_headers": headers,
               "request_body": body, "status": status, "sse_events": events}
    Path("codex_probe_capture.json").write_text(json.dumps(capture, indent=2))
    print(f"\n✓ Captured {len(events)} SSE events -> codex_probe_capture.json")
    print("  Check it for anything personal, then hand it over for the adapter fixture.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
