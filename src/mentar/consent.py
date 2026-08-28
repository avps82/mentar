"""Parent consent record for opt-in cloud LLM backends (SAFETY.md §4.5).

Why this exists: a cloud backend sends the child's lesson dialogue off the
device under the PARENT's account — the parent, not Mentar, becomes the data
operator for that flow.  SAFETY §4.5 requires an explicit acknowledgment in the
setup flow before that can happen.  This module is the durable record of that
acknowledgment, and ``make_llm_call`` refuses to build a cloud backend without
it — so a hand-edited inference.yaml cannot switch a child's sessions to the
cloud silently.

The record lives NEXT TO the inference config (``config/cloud_consent.yaml``,
gitignored) so it follows the data dir in packaged builds and is wiped by the
same "start over" actions that wipe the backend config.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml

from mentar.paths import config_path

# Bump when the parent-facing consent statement changes materially: an old
# recorded version means the parent agreed to DIFFERENT wording, and setup
# should re-ask rather than silently carry the old acknowledgment forward.
STATEMENT_VERSION = 1

_PROVIDER_NAMES = {
    "openai": "OpenAI",
    "claude": "Anthropic",
    "openai_chatgpt": "OpenAI (ChatGPT subscription)",
}


def consent_path() -> Path:
    return config_path().parent / "cloud_consent.yaml"


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        # A corrupt record is treated as NO consent — the failure mode is the
        # parent being asked again, never a silent cloud turn.
        return {}
    return data if isinstance(data, dict) else {}


def record_cloud_consent(backend: str, path: Path | None = None) -> None:
    """Record the parent's acknowledgment for *backend*, preserving others."""
    p = path or consent_path()
    data = _load(p)
    data[backend] = {
        "acknowledged_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "provider": _PROVIDER_NAMES.get(backend, backend),
        "statement_version": STATEMENT_VERSION,
    }
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def has_cloud_consent(backend: str, path: Path | None = None) -> bool:
    """True only for a record made against the CURRENT statement wording.

    Every malformed shape reads as NO consent rather than raising. A
    hand-written or truncated file used to crash here with AttributeError
    (``{backend: true}`` has no .get), and this is called from make_llm_call
    AND from the web setup gate — so a stray line in a config file 500'd every
    page instead of routing the parent to /setup. Measured 2026-08-29.
    """
    entry = _load(path or consent_path()).get(backend)
    if not isinstance(entry, dict):
        return False
    return entry.get("statement_version") == STATEMENT_VERSION
