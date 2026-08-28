"""The ChatGPT-subscription call path (backend ``openai_chatgpt``).

EXPERIMENTAL / UNOFFICIAL (plan §P3, risks R1/R2). This cannot ride
``_make_openai_call``: a ChatGPT-plan token does not authenticate against the
platform's ``/v1/chat/completions``. It authenticates against the Codex
backend, which speaks a Responses-API-shaped protocol that OpenAI does not
publish and which has drifted before (openclaw#38706).

So the shape assumptions live HERE and nowhere else, deliberately quarantined:

  * request building  -> ``_build_body`` (messages -> Responses ``input``)
  * response parsing  -> ``extract_text`` (SSE event stream -> plain text)

``extract_text`` is intentionally forgiving: it accepts several event/field
spellings, because the exact one is unpublished. If OpenAI changes them, one
function and its fixtures move, not the backend.

⚠ NOT YET VERIFIED AGAINST THE LIVE ENDPOINT (2026-08-29). The request body and
event shapes below are taken from published descriptions of how the existing
piggyback integrations call this endpoint, NOT from a capture of our own — the
maintainer has no ChatGPT subscription to test with. Everything around this
module (sign-in, refresh, consent, error UX) IS covered by tests; this module's
wire format is the one thing that could be wrong on first contact.

To verify: run ``scripts/capture_codex_probe.py`` on a machine with a ChatGPT
sign-in and correct ``_build_body``/``extract_text`` against the capture. Until
someone does, the setup page labels this option unverified.
"""

from __future__ import annotations

import json
import logging
import time

logger = logging.getLogger(__name__)

CODEX_RESPONSES_URL = "https://chatgpt.com/backend-api/codex/responses"
_RETRY_BACKOFF_S = 1.5


class CodexBackendError(RuntimeError):
    """The codex backend refused or returned nothing usable."""


def _build_body(messages: list[dict], model: str, max_tokens: int,
                temperature: float) -> dict:
    """Chat messages -> the Responses-style body the codex backend expects.

    A system turn becomes ``instructions`` (the Responses API's own slot for
    it) rather than a message, because some chat templates on this path reject
    an inline system role -- the same failure the maintainer hit on 2026-08-26
    with a local model.
    """
    instructions = "\n\n".join(
        m["content"] for m in messages if m.get("role") == "system")
    body_input = [
        {"type": "message", "role": m["role"],
         "content": [{"type": "input_text", "text": m["content"]}]}
        for m in messages if m.get("role") != "system"
    ]
    body = {
        "model": model,
        "input": body_input,
        "stream": True,          # the codex backend is stream-first
        "store": False,          # never ask them to retain a child's turn
        "max_output_tokens": max_tokens,
        "temperature": temperature,
    }
    if instructions:
        body["instructions"] = instructions
    return body


def extract_text(sse_lines) -> str:
    """Pull the assistant's text out of the SSE event stream.

    Forgiving BY DESIGN -- the event names and field paths are unpublished.
    Preference order:
      1. a terminal ``response.completed`` payload's output text (authoritative)
      2. accumulated ``output_text.delta`` chunks (what streaming emits)
    Anything unrecognized is ignored rather than raising: a stray keepalive or
    a new event type must not blank out a child's answer.
    """
    deltas: list[str] = []
    completed: str | None = None
    for raw in sse_lines:
        line = raw.decode() if isinstance(raw, bytes) else raw
        line = line.strip()
        if not line or line.startswith(":") or line in ("data: [DONE]", "[DONE]"):
            continue
        if line.startswith("data:"):
            line = line[5:].strip()
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        etype = event.get("type", "")
        if etype.endswith("output_text.delta"):
            piece = event.get("delta")
            if isinstance(piece, str):
                deltas.append(piece)
        elif etype.endswith("output_text.done") and isinstance(event.get("text"), str):
            completed = completed or event["text"]
        elif etype.endswith("response.completed"):
            completed = _text_from_response(event.get("response") or {}) or completed
        elif etype.endswith("failed") or etype.endswith("error"):
            # An explicit failure event used to fall through and return "" --
            # the child got a blank turn and the log said nothing about why
            # (measured 2026-08-28). Same silent-empty class as the reasoning
            # model bug: name it, so the parent's status page can show it.
            err = (event.get("response") or {}).get("error") or event.get("error") or {}
            msg = err.get("message") if isinstance(err, dict) else str(err)
            raise CodexBackendError(
                f"the ChatGPT backend reported an error: {msg or etype}")
    return completed if completed is not None else "".join(deltas)


def _text_from_response(response: dict) -> str | None:
    """Walk a terminal response object for its assistant text."""
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    chunks: list[str] = []
    for item in response.get("output") or []:
        if not isinstance(item, dict):
            continue
        for part in item.get("content") or []:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                chunks.append(part["text"])
    return "".join(chunks) if chunks else None


def make_codex_call(block: dict, gen: dict):
    """Build the LLMCall for backend ``openai_chatgpt``."""
    import httpx

    from mentar.inference.codex_auth import (
        CodexAuthError,
        make_codex_token_provider,
        read_credentials,
    )

    model = block.get("model")
    if not model:
        raise ValueError(
            "backend 'openai_chatgpt' needs an explicit model: in its config block")
    auth_file = block.get("auth_file")
    provider = make_codex_token_provider(auth_file)
    retries = gen["retries"]

    def call(messages: list[dict]) -> str:
        body = _build_body(messages, model, gen["max_tokens"], gen["temperature"])
        last_exc: Exception | None = None
        for attempt in range(retries + 1):
            try:
                token = provider()          # refreshes transparently if near expiry
                creds = read_credentials(auth_file)
            except CodexAuthError as exc:
                # Deterministic: no retry can conjure a sign-in.
                raise CodexBackendError(str(exc)) from exc
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "chatgpt-account-id": creds.get("account_id") or "",
                "OpenAI-Beta": "responses=experimental",
                "originator": "codex_cli_rs",
            }
            try:
                with httpx.stream("POST", CODEX_RESPONSES_URL, headers=headers,
                                  json=body, timeout=gen["timeout"]) as resp:
                    if resp.status_code == 401:
                        resp.read()
                        raise CodexBackendError(
                            "your ChatGPT sign-in was rejected — sign in again "
                            "(mentar chatgpt-login, or the button on /setup)")
                    if resp.status_code == 429:
                        resp.read()
                        raise CodexBackendError(
                            "your ChatGPT plan hit its usage limit — this is a cap on "
                            "the account's plan, not a Mentar fault. Wait, or use an "
                            "API-key backend for dependable capacity.")
                    if resp.status_code != 200:
                        resp.read()
                        raise RuntimeError(
                            f"codex backend returned HTTP {resp.status_code}: "
                            f"{resp.text[:200]}")
                    return extract_text(resp.iter_lines())
            except CodexBackendError:
                raise                       # deterministic — never retried
            except Exception as exc:        # network/5xx — retry a couple times
                last_exc = exc
                if attempt < retries:
                    time.sleep(_RETRY_BACKOFF_S * (attempt + 1))
                    logger.warning("codex call retry %d/%d: %s",
                                   attempt + 1, retries, exc)
        raise CodexBackendError(
            f"the ChatGPT backend did not answer after {retries + 1} attempt(s): "
            f"{last_exc}")

    return call
