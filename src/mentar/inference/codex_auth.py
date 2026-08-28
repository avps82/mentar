"""Read (and refresh) the ChatGPT sign-in that OpenAI's Codex CLI stores locally.

EXPERIMENTAL / UNOFFICIAL (plan §P3, risk R1): "Sign in with ChatGPT" officially
ships only inside Codex tooling. The parent signs in either via Mentar's own
embedded flow (``mentar chatgpt-login`` / the setup button — see
``chatgpt_login.py``, which stores tokens in this same file shape at
``config/chatgpt_auth.json``) or with OpenAI's own ``codex login``; this module
reads whichever exists (Mentar's own file wins) and owns refresh for both.

Refresh policy (maintainer decision, 2026-08-28): access tokens expire after a
few hours, so on (near-)expiry we POST the refresh_token grant to OpenAI's token
endpoint with the public Codex client id — exactly what the established
piggyback integrations do — and write the rotated tokens BACK to auth.json:

  * atomically (tmp + rename), preserving unknown JSON fields verbatim;
  * under a process-wide single-flight lock. Refresh tokens rotate, so two
    racing refreshes mean the loser holds a dead token — and worse, a clobbered
    write could log the parent out of Codex itself (risk R7).

Failure UX: every error raises CodexAuthError naming the file checked and the
remedy (`codex login`). The child-facing path never sees these — the dialogue
controller degrades LLM failures to a safe fallback; parents see them on the
setup/status pages.
"""

from __future__ import annotations

import base64
import binascii
import json
import logging
import os
import shutil
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)

CODEX_AUTH_PATH = Path.home() / ".codex" / "auth.json"
# The public OAuth client id the Codex CLI itself uses (PKCE public client —
# not a secret; it appears verbatim in Codex's own open-source code).
CODEX_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
TOKEN_ENDPOINT = "https://auth.openai.com/oauth/token"
_REFRESH_MARGIN_S = 300.0          # refresh when <5 min of validity remains
_REFRESH_LOCK = threading.Lock()   # single-flight: rotation makes races lossy


def default_auth_path() -> Path:
    """Mentar's own sign-in (written by `mentar chatgpt-login` / the setup
    button) wins; a pre-existing `codex login` is the no-extra-work fallback.
    Chosen fresh on every call — no caching — so signing in either way takes
    effect on the very next turn."""
    from mentar.paths import config_path
    own = config_path().parent / "chatgpt_auth.json"
    return own if own.exists() else CODEX_AUTH_PATH


class CodexAuthError(RuntimeError):
    """The Codex sign-in is missing/unreadable/expired beyond repair."""


def _remedy(path: Path) -> str:
    hint = "sign in with:  mentar chatgpt-login   (or the button on /setup)"
    if shutil.which("codex") is not None:
        hint += "  — or run: codex login"
    else:
        hint += "  (no separate Codex CLI install needed)"
    return f"{hint}. Mentar reads the ChatGPT sign-in stored at {path}."


def _jwt_exp(token: str) -> float | None:
    """The `exp` claim of a JWT, without verifying the signature — we only need
    the timestamp, and the server verifies the signature for real."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
        exp = claims.get("exp")
        return float(exp) if exp is not None else None
    except (IndexError, ValueError, binascii.Error):
        return None


def read_credentials(path: Path | None = None) -> dict:
    """Fresh read of auth.json → {access_token, refresh_token, account_id,
    expires_at}. No caching: after the parent runs `codex login`, the very
    next call sees the new sign-in. Tolerant to the two known shapes."""
    p = Path(path).expanduser() if path else default_auth_path()
    if not p.exists():
        raise CodexAuthError(f"no ChatGPT sign-in found at {p} — {_remedy(p)}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CodexAuthError(f"could not read {p} ({exc}) — {_remedy(p)}") from exc

    tokens = data.get("tokens") if isinstance(data.get("tokens"), dict) else {}
    access = tokens.get("access_token")
    if not access:
        # `codex login --api-key` writes a plain key at the top level instead.
        access = data.get("OPENAI_API_KEY")
        if isinstance(access, str) and access.strip():
            return {"access_token": access.strip(), "refresh_token": None,
                    "account_id": None, "expires_at": None}
        raise CodexAuthError(f"{p} holds no recognizable token — {_remedy(p)}")
    return {
        "access_token": access,
        "refresh_token": tokens.get("refresh_token"),
        "account_id": tokens.get("account_id"),
        "expires_at": _jwt_exp(access),
    }


def _refresh(p: Path, creds: dict) -> dict:
    """Rotate the tokens via the refresh grant and persist back to auth.json."""
    import httpx  # transitive dep of openai-python

    resp = httpx.post(TOKEN_ENDPOINT, json={
        "grant_type": "refresh_token",
        "client_id": CODEX_CLIENT_ID,
        "refresh_token": creds["refresh_token"],
    }, timeout=30.0)
    if resp.status_code != 200:
        raise CodexAuthError(
            f"the sign-in at {p} could not be refreshed "
            f"(HTTP {resp.status_code} from the token endpoint) — {_remedy(p)}")
    fresh = resp.json()
    new_access = fresh.get("access_token")
    if not new_access:
        raise CodexAuthError(f"token refresh returned no access_token — {_remedy(p)}")

    # Write back: read the CURRENT file (not our parsed view), update only the
    # token fields, keep everything else byte-for-byte — then atomic rename.
    data = json.loads(p.read_text(encoding="utf-8"))
    tokens = data.setdefault("tokens", {})
    tokens["access_token"] = new_access
    if fresh.get("refresh_token"):
        tokens["refresh_token"] = fresh["refresh_token"]
    if fresh.get("id_token"):
        tokens["id_token"] = fresh["id_token"]
    data["last_refresh"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp = p.with_suffix(p.suffix + ".mentar-tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, p)
    logger.info("codex_auth: refreshed the ChatGPT sign-in (rotated tokens written back)")
    return read_credentials(p)


def get_access_token(path: Path | None = None) -> str:
    """A currently-valid access token, refreshing (and persisting) if needed."""
    p = Path(path).expanduser() if path else default_auth_path()
    creds = read_credentials(p)
    exp = creds["expires_at"]
    if exp is not None and exp - time.time() < _REFRESH_MARGIN_S:
        if not creds["refresh_token"]:
            raise CodexAuthError(f"the sign-in at {p} has expired and holds no "
                                 f"refresh token — {_remedy(p)}")
        with _REFRESH_LOCK:
            # Re-read under the lock: the winner of a race already refreshed.
            creds = read_credentials(p)
            exp = creds["expires_at"]
            if exp is not None and exp - time.time() < _REFRESH_MARGIN_S:
                creds = _refresh(p, creds)
    return creds["access_token"]


def make_codex_token_provider(auth_file: str | None = None):
    """The api_key_provider callable the backend's credential seam consumes."""
    p = Path(auth_file).expanduser() if auth_file else None

    def provider() -> str:
        return get_access_token(p)

    return provider


def login_status(path: Path | None = None) -> dict:
    """For setup/status pages only — never used on the call path."""
    p = Path(path).expanduser() if path else default_auth_path()
    found = shutil.which("codex") is not None
    try:
        creds = read_credentials(p)
    except CodexAuthError:
        return {"present": False, "expires_at": None, "stale": False,
                "codex_binary_found": found}
    exp = creds["expires_at"]
    return {
        "present": True,
        "expires_at": exp,
        # informational: the probe is the real test
        "stale": bool(exp is not None and exp < time.time()),
        "codex_binary_found": found,
    }
