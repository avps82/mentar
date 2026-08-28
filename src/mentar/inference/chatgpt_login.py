"""Embedded "Sign in with ChatGPT" (PKCE) — no Codex CLI install required.

EXPERIMENTAL / UNOFFICIAL (plan §P3, risk R1): this drives the same OAuth flow
OpenAI's Codex CLI performs, using its public client id, and stores the result
in MENTAR's OWN config dir (``config/chatgpt_auth.json``, gitignored) in the
same file shape Codex uses — so everything downstream (reading, refresh,
rotation guardrails: ``codex_auth``) is shared, and a family that *does* have a
``codex login`` can be read as a fallback without installing anything twice.

Flow (the standard native-app PKCE dance):
  1. generate verifier/challenge + state, build the authorize URL;
  2. listen once on ``localhost:1455`` (the redirect URI registered for this
     client id — the port is NOT ours to choose) and open the browser;
  3. the callback hands us ``code``; we exchange it at the token endpoint;
  4. write tokens atomically in the codex file shape; done — the parent never
     sees a terminal.

The maintainer-facing security notes: the state parameter is checked (a
mismatched callback is dropped), the listener binds loopback only and accepts
exactly one request, and nothing here ever logs a token.
"""

from __future__ import annotations

import base64
import hashlib
import http.server
import json
import logging
import os
import secrets
import time
import urllib.parse
import webbrowser
from pathlib import Path

from mentar.inference.codex_auth import CODEX_CLIENT_ID, TOKEN_ENDPOINT
from mentar.paths import config_path

logger = logging.getLogger(__name__)

AUTHORIZE_ENDPOINT = "https://auth.openai.com/oauth/authorize"
# Registered redirect for the public Codex client id — fixed, not configurable.
_CALLBACK_PORT = 1455
_CALLBACK_PATH = "/auth/callback"
_SCOPE = "openid profile email offline_access"


def mentar_auth_path() -> Path:
    """Where the embedded sign-in stores its tokens (codex file shape)."""
    return config_path().parent / "chatgpt_auth.json"


def _pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(48)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


def build_authorize_url(state: str, challenge: str) -> str:
    return AUTHORIZE_ENDPOINT + "?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": CODEX_CLIENT_ID,
        "redirect_uri": f"http://localhost:{_CALLBACK_PORT}{_CALLBACK_PATH}",
        "scope": _SCOPE,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "id_token_add_organizations": "true",
    })


def _account_id_from_id_token(id_token: str | None) -> str | None:
    """The ChatGPT account id rides in the id_token's auth claims."""
    if not id_token:
        return None
    try:
        payload = id_token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
        auth_claims = claims.get("https://api.openai.com/auth") or {}
        return auth_claims.get("chatgpt_account_id")
    except (IndexError, ValueError):
        return None


def exchange_code(code: str, verifier: str) -> dict:
    import httpx

    resp = httpx.post(TOKEN_ENDPOINT, data={
        "grant_type": "authorization_code",
        "client_id": CODEX_CLIENT_ID,
        "code": code,
        "code_verifier": verifier,
        "redirect_uri": f"http://localhost:{_CALLBACK_PORT}{_CALLBACK_PATH}",
    }, timeout=30.0)
    if resp.status_code != 200:
        raise RuntimeError(
            f"token exchange failed (HTTP {resp.status_code}) — the sign-in "
            "was not completed; try again")
    return resp.json()


def write_auth_file(tokens: dict, path: Path | None = None) -> Path:
    """Persist in the codex file shape, atomically, so codex_auth reads it."""
    p = path or mentar_auth_path()
    data = {
        "tokens": {
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "id_token": tokens.get("id_token"),
            "account_id": _account_id_from_id_token(tokens.get("id_token")),
        },
        "last_refresh": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "written_by": "mentar chatgpt-login",
    }
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".mentar-tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, p)
    return p


class _OneShotCallback(http.server.BaseHTTPRequestHandler):
    """Loopback-only, single-request callback receiver."""

    result: dict = {}
    expected_state: str = ""

    def do_GET(self):  # noqa: N802 — http.server API
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != _CALLBACK_PATH:
            self.send_response(404)
            self.end_headers()
            return
        params = urllib.parse.parse_qs(parsed.query)
        state = (params.get("state") or [""])[0]
        if state != type(self).expected_state:
            # A mismatched state is someone else's (or a replayed) callback —
            # drop it without surrendering anything.
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"State mismatch - please retry the sign-in from Mentar.")
            return
        type(self).result = {
            "code": (params.get("code") or [None])[0],
            "error": (params.get("error") or [None])[0],
        }
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            b"<h2>Signed in.</h2><p>You can close this tab and return to Mentar.</p>")

    def log_message(self, *args):  # silence default stderr access log
        pass


def run_login_flow(open_browser: bool = True, timeout_s: float = 300.0,
                   path: Path | None = None) -> Path:
    """The whole dance. Returns the written auth-file path, or raises."""
    verifier, challenge = _pkce_pair()
    state = secrets.token_urlsafe(24)
    url = build_authorize_url(state, challenge)

    _OneShotCallback.expected_state = state
    _OneShotCallback.result = {}
    server = http.server.HTTPServer(("127.0.0.1", _CALLBACK_PORT), _OneShotCallback)
    server.timeout = 1.0

    print("Opening the ChatGPT sign-in page in your browser…")
    print(f"(if nothing opens, paste this URL yourself)\n  {url}\n")
    if open_browser:
        webbrowser.open(url)

    deadline = time.monotonic() + timeout_s
    try:
        while time.monotonic() < deadline and not _OneShotCallback.result:
            server.handle_request()          # 1s timeout per iteration
    finally:
        server.server_close()

    result = _OneShotCallback.result
    if not result:
        raise RuntimeError("sign-in timed out — no callback arrived; try again")
    if result.get("error") or not result.get("code"):
        raise RuntimeError(f"sign-in was refused: {result.get('error') or 'no code'}")

    tokens = exchange_code(result["code"], verifier)
    p = write_auth_file(tokens, path)
    print(f"✓ Signed in — tokens stored at {p}")
    return p


__all__ = ["build_authorize_url", "exchange_code", "mentar_auth_path",
           "run_login_flow", "write_auth_file"]
