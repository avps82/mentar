"""codex_auth — reading (and refreshing) the Codex CLI's stored ChatGPT sign-in.

All network is faked; all files are tmp_path fixtures. The module must NEVER
mutate auth.json except through the explicit refresh write-back, and that
write-back must preserve fields it does not understand.
"""

import base64
import json
import time

import pytest

from mentar.inference import codex_auth as CA


def _jwt(exp: float) -> str:
    """A structurally-valid JWT with only an exp claim; signature is garbage —
    the module must not care (the server verifies for real)."""
    header = base64.urlsafe_b64encode(b'{"alg":"none"}').rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(
        json.dumps({"exp": exp}).encode()).rstrip(b"=").decode()
    return f"{header}.{payload}.sig"


def _auth_file(tmp_path, exp=None, refresh="rt-1", extra=None):
    exp = time.time() + 3600 if exp is None else exp
    data = {"tokens": {"access_token": _jwt(exp), "refresh_token": refresh,
                       "account_id": "acct-42"},
            "last_refresh": "2026-08-28T00:00:00Z"}
    if extra:
        data.update(extra)
    p = tmp_path / "auth.json"
    p.write_text(json.dumps(data))
    return p


def test_reads_the_codex_shape(tmp_path):
    p = _auth_file(tmp_path)
    creds = CA.read_credentials(p)
    assert creds["account_id"] == "acct-42"
    assert creds["refresh_token"] == "rt-1"
    assert creds["expires_at"] > time.time()


def test_reads_the_api_key_shape(tmp_path):
    p = tmp_path / "auth.json"
    p.write_text(json.dumps({"OPENAI_API_KEY": "sk-plain"}))
    creds = CA.read_credentials(p)
    assert creds["access_token"] == "sk-plain"
    assert creds["expires_at"] is None      # a plain key never triggers refresh


@pytest.mark.parametrize("case", ["missing", "malformed", "empty"])
def test_unusable_files_name_the_file_and_the_remedy(tmp_path, case):
    p = tmp_path / "auth.json"
    if case == "malformed":
        p.write_text("{{{ not json")
    elif case == "empty":
        p.write_text(json.dumps({"tokens": {"access_token": ""}}))
    with pytest.raises(CA.CodexAuthError) as exc:
        CA.read_credentials(p)
    assert str(p) in str(exc.value)
    assert "codex" in str(exc.value).lower()


def test_valid_token_is_returned_without_any_refresh(tmp_path, monkeypatch):
    p = _auth_file(tmp_path, exp=time.time() + 3600)
    before = p.read_text()
    monkeypatch.setattr(CA, "_refresh",
                        lambda *a: (_ for _ in ()).throw(AssertionError("refreshed a valid token")))
    tok = CA.get_access_token(p)
    assert tok.startswith("eyJ")
    assert p.read_text() == before, "reading must never mutate auth.json"


def test_near_expiry_refreshes_and_writes_back_preserving_unknown_fields(tmp_path, monkeypatch):
    """The rotation contract: rotated tokens land in auth.json atomically, and
    fields this module does not understand survive byte-for-byte — clobbering
    them could log the parent out of Codex itself (risk R7)."""
    p = _auth_file(tmp_path, exp=time.time() + 10,   # inside the 5-min margin
                   extra={"codex_private_setting": {"keep": "me"}})

    class _Resp:
        status_code = 200
        @staticmethod
        def json():
            return {"access_token": _jwt(time.time() + 7200),
                    "refresh_token": "rt2B"}

    import httpx
    monkeypatch.setattr(httpx, "post", lambda *a, **kw: _Resp())
    tok = CA.get_access_token(p)
    data = json.loads(p.read_text())
    assert data["tokens"]["access_token"] == tok
    assert data["tokens"]["refresh_token"] == "rt2B"
    assert data["tokens"]["account_id"] == "acct-42"
    assert data["codex_private_setting"] == {"keep": "me"}, "unknown fields must survive"
    assert not list(tmp_path.glob("*.mentar-tmp")), "no tmp file left behind"


def test_failed_refresh_names_the_remedy_and_leaves_the_file_alone(tmp_path, monkeypatch):
    p = _auth_file(tmp_path, exp=time.time() - 10)
    before = p.read_text()

    class _Resp:
        status_code = 401
        @staticmethod
        def json():
            return {}

    import httpx
    monkeypatch.setattr(httpx, "post", lambda *a, **kw: _Resp())
    with pytest.raises(CA.CodexAuthError) as exc:
        CA.get_access_token(p)
    assert "chatgpt-login" in str(exc.value)   # the always-available remedy
    assert p.read_text() == before


def test_expired_with_no_refresh_token_is_a_clean_error(tmp_path):
    p = _auth_file(tmp_path, exp=time.time() - 10, refresh=None)
    with pytest.raises(CA.CodexAuthError) as exc:
        CA.get_access_token(p)
    assert "expired" in str(exc.value)


def test_login_status_shapes(tmp_path):
    assert CA.login_status(tmp_path / "nope.json")["present"] is False
    live = CA.login_status(_auth_file(tmp_path, exp=time.time() + 3600))
    assert live["present"] is True and live["stale"] is False
    stale = CA.login_status(_auth_file(tmp_path, exp=time.time() - 3600, refresh=None))
    assert stale["stale"] is True


# ── Bug-hunt regressions (2026-08-28) ────────────────────────────────────────

def test_a_refresh_never_writes_into_codexs_own_file(tmp_path, monkeypatch):
    """Our single-flight lock is process-local; the Codex CLI refreshes in its
    OWN process. Since refresh tokens are single-use and rotate, writing into
    ~/.codex/auth.json could destroy a token codex just rotated and log BOTH
    tools out. Codex's file is read-only input: refreshed tokens go to Mentar's.
    """
    import httpx

    from mentar.inference import chatgpt_login as L

    codex_file = tmp_path / "codex_auth.json"
    codex_file.write_text(json.dumps({"tokens": {
        "access_token": _jwt(time.time() - 10), "refresh_token": "rt1",
        "account_id": "acct-7"}}))
    before = codex_file.read_text()
    own = tmp_path / "chatgpt_auth.json"
    monkeypatch.setattr(CA, "CODEX_AUTH_PATH", codex_file)
    monkeypatch.setattr(L, "mentar_auth_path", lambda: own)

    class _Resp:
        status_code = 200
        @staticmethod
        def json():
            return {"access_token": _jwt(time.time() + 7200), "refresh_token": "rt2"}

    monkeypatch.setattr(httpx, "post", lambda *a, **kw: _Resp())
    CA.get_access_token(codex_file)
    assert codex_file.read_text() == before, "codex's own file must never be written"
    assert own.exists(), "the refreshed tokens must land in Mentar's own file"
    assert json.loads(own.read_text())["tokens"]["refresh_token"] == "rt2"
    assert json.loads(own.read_text())["tokens"]["account_id"] == "acct-7"


def test_credential_files_are_not_world_readable(tmp_path, monkeypatch):
    """A live token at the default 0644 is readable by every other account on a
    shared family computer (measured 2026-08-28)."""
    import stat

    from mentar.inference import chatgpt_login as L

    p = L.write_auth_file({"access_token": "tok", "refresh_token": "r",
                           "id_token": None}, path=tmp_path / "chatgpt_auth.json")
    mode = stat.S_IMODE(p.stat().st_mode)
    assert mode == 0o600, f"token file is {oct(mode)}, want 0600"


def test_dotenv_is_not_world_readable(tmp_path):
    import stat

    from mentar.inference.backend import upsert_dotenv_value
    e = tmp_path / ".env"
    upsert_dotenv_value(e, "OPENAI_API_KEY", "sk-secret")
    assert stat.S_IMODE(e.stat().st_mode) == 0o600, "an API key must not be world-readable"
