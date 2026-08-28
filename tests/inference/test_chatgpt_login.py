"""Embedded Sign-in-with-ChatGPT flow (chatgpt_login) — no network, no browser."""

import base64
import hashlib
import json
import time
import urllib.parse

import pytest

from mentar.inference import chatgpt_login as L
from mentar.inference import codex_auth as CA


def _jwt(claims: dict) -> str:
    h = base64.urlsafe_b64encode(b'{"alg":"none"}').rstrip(b"=").decode()
    p = base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b"=").decode()
    return f"{h}.{p}.sig"


def test_authorize_url_is_a_correct_pkce_request():
    verifier, challenge = L._pkce_pair()
    # S256: the challenge must be the b64url sha256 of the verifier
    expect = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    assert challenge == expect
    url = L.build_authorize_url("state-xyz", challenge)
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    assert q["client_id"] == [CA.CODEX_CLIENT_ID]
    assert q["code_challenge_method"] == ["S256"]
    assert q["redirect_uri"] == ["http://localhost:1455/auth/callback"]
    assert q["state"] == ["state-xyz"]
    assert "offline_access" in q["scope"][0], "no refresh token without offline_access"


def test_written_file_is_read_back_by_codex_auth(tmp_path):
    """The whole design: the login writes the SAME shape codex_auth already
    reads/refreshes, so the entire downstream (provider, refresh, guardrails)
    is shared instead of duplicated."""
    id_token = _jwt({"https://api.openai.com/auth": {"chatgpt_account_id": "acct-99"}})
    access = _jwt({"exp": time.time() + 3600})
    p = L.write_auth_file({"access_token": access, "refresh_token": "rt1",
                           "id_token": id_token}, path=tmp_path / "chatgpt_auth.json")
    creds = CA.read_credentials(p)
    assert creds["access_token"] == access
    assert creds["account_id"] == "acct-99"      # extracted from the id_token
    assert creds["refresh_token"] == "rt1"
    assert creds["expires_at"] > time.time()


def test_account_id_extraction_tolerates_garbage():
    assert L._account_id_from_id_token(None) is None
    assert L._account_id_from_id_token("not-a-jwt") is None
    assert L._account_id_from_id_token(_jwt({})) is None


def test_callback_rejects_a_mismatched_state():
    """A forged/replayed callback must be dropped: state is the CSRF check."""
    L._OneShotCallback.expected_state = "the-real-state"
    L._OneShotCallback.result = {}

    import io

    def _drive(path):
        h = L._OneShotCallback.__new__(L._OneShotCallback)  # skip socket __init__
        h.path = path
        h.wfile = io.BytesIO()
        h.send_response = lambda code: None
        h.send_header = lambda *a: None
        h.end_headers = lambda: None
        h.do_GET()

    _drive("/auth/callback?code=stolen&state=WRONG")
    assert L._OneShotCallback.result == {}, "a wrong state must surrender nothing"
    _drive("/auth/callback?code=good&state=the-real-state")
    assert L._OneShotCallback.result["code"] == "good"


def test_exchange_failure_is_a_plain_actionable_error(monkeypatch):
    import httpx

    class _Resp:
        status_code = 403
        @staticmethod
        def json(): return {}

    monkeypatch.setattr(httpx, "post", lambda *a, **kw: _Resp())
    with pytest.raises(RuntimeError) as exc:
        L.exchange_code("code", "verifier")
    assert "try again" in str(exc.value)


def test_default_auth_path_prefers_mentars_own_file(tmp_path, monkeypatch):
    import mentar.paths as P
    monkeypatch.setattr(P, "config_path", lambda: tmp_path / "config" / "inference.yaml")
    # no own file -> codex fallback
    assert CA.default_auth_path() == CA.CODEX_AUTH_PATH
    own = tmp_path / "config" / "chatgpt_auth.json"
    own.parent.mkdir(parents=True)
    own.write_text("{}")
    assert CA.default_auth_path() == own
