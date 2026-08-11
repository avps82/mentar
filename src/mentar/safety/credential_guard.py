"""Credential-leak guard — scrub secrets from model output before it is shown to a
child or written to the transcript / logs.

Defence-in-depth: Mentar's API key lives in `config/.env` / the environment and is
never placed in a prompt, so the model shouldn't be able to emit it. But a prompt
injection or a hallucination could surface a key-shaped string — so we redact any
credential-looking substring from LLM output at a single chokepoint
(`SessionController._make_safe_llm`).

Pure + stdlib-only: no I/O, no network.
"""

from __future__ import annotations

import re

REDACTION = "[REDACTED]"

# Credential-shaped patterns. Order doesn't matter; all are applied.
_SENSITIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"MENTAR_[A-Z0-9_]*KEY", re.IGNORECASE),         # our env-var names
    re.compile(r"(api[_-]?key|token|secret|password)\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),                     # OpenAI-style keys
    re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),  # bearer tokens
    # Added 2026-08-12: this module's contract is "any credential-looking
    # substring", and a probe found these standard formats passing untouched.
    # All three have unambiguous fixed prefixes/shapes, so the false-positive
    # risk inside a maths tutor's output is effectively nil.
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}\b"),              # GitHub tokens
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                        # AWS access key id
    re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s:@/]+:[^\s:@/]+@"),  # user:pass@ in a URI
]


def detect_credential_leak(text: str) -> bool:
    """True if *text* contains anything credential-shaped."""
    if not text:
        return False
    return any(p.search(text) for p in _SENSITIVE_PATTERNS)


def redact_credentials(text: str) -> str:
    """Replace any credential-shaped substring with ``[REDACTED]``.

    Used on LLM output before it reaches the child or the logs. Returns *text*
    unchanged when nothing matches (the overwhelmingly common case).
    """
    if not text:
        return text
    for pattern in _SENSITIVE_PATTERNS:
        text = pattern.sub(REDACTION, text)
    return text
