"""Tests for R9 -- the first-run setup gate (/setup) and live config reload.

Deliberately does NOT set _SETUP_GATE_BYPASS -- these tests exist specifically
to prove the gate itself works, unlike every other web test which bypasses it.

    python3 tests/web/test_setup_gate.py
"""

from __future__ import annotations

import os
import pathlib
import sys
import tempfile
from unittest.mock import MagicMock, patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))


def _client():
    """Fresh (app_mod, test_client) pair, gate NOT bypassed -- each test
    patches app_mod._INFERENCE_CONFIG_PATH to its own scratch location so
    nothing ever touches the real repo's config/inference.yaml."""
    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test_setup_gate.db")
    os.environ.pop("MENTAR_PACK_STATE", None)  # isolation: don't inherit a toggle test's state file
    import importlib

    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)
    app_mod._llm_call_cached = lambda messages: "stub tutor reply"
    return app_mod, app_mod.app.test_client()


def _reachable_openai_mock():
    mock_client = MagicMock()
    mock_client.models.list.return_value = []
    return mock_client


def test_gate_redirects_to_setup_when_config_missing():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    scratch = pathlib.Path(tempfile.mkdtemp()) / "inference.yaml"  # never created
    with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", scratch):
        r = c.get("/", follow_redirects=False)
        assert r.status_code == 302
        assert r.headers["Location"].endswith("/setup")


def test_gate_redirects_to_setup_when_backend_unreachable():
    """Config file EXISTS but the backend fails the reachability probe --
    must still gate (the maintainer's explicit call: missing OR not working)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    scratch_dir = pathlib.Path(tempfile.mkdtemp())
    scratch_cfg = scratch_dir / "inference.yaml"
    scratch_cfg.write_text("backend: vllm\nvllm:\n  base_url: http://x/v1\n  model: m\n", encoding="utf-8")

    with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", scratch_cfg):
        app_mod._LLM_STATUS_ENDPOINT = {"base_url": "http://x/v1", "api_key": "no-key", "model": "m"}
        app_mod._SETUP_GATE_CACHE["ok"] = None
        app_mod._SETUP_GATE_CACHE["checked_at"] = 0.0
        with patch("openai.OpenAI", side_effect=ConnectionError("refused")):
            r = c.get("/", follow_redirects=False)
            assert r.status_code == 302
            assert r.headers["Location"].endswith("/setup")


def test_gate_allows_through_when_backend_reachable():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    scratch_dir = pathlib.Path(tempfile.mkdtemp())
    scratch_cfg = scratch_dir / "inference.yaml"
    scratch_cfg.write_text("backend: vllm\nvllm:\n  base_url: http://x/v1\n  model: m\n", encoding="utf-8")

    with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", scratch_cfg):
        app_mod._LLM_STATUS_ENDPOINT = {"base_url": "http://x/v1", "api_key": "no-key", "model": "m"}
        app_mod._SETUP_GATE_CACHE["ok"] = None
        app_mod._SETUP_GATE_CACHE["checked_at"] = 0.0
        with patch("openai.OpenAI", return_value=_reachable_openai_mock()):
            r = c.get("/", follow_redirects=False)
            assert r.status_code == 200


def test_gate_allows_in_process_backend_without_probing():
    """An in-process llamacpp backend has no HTTP endpoint -- its mere
    presence (config file exists, _LLM_STATUS_ENDPOINT is None) counts as
    configured, never probed, never gated."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    scratch_dir = pathlib.Path(tempfile.mkdtemp())
    scratch_cfg = scratch_dir / "inference.yaml"
    scratch_cfg.write_text("backend: llamacpp\nllamacpp:\n  mode: in_process\n", encoding="utf-8")

    with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", scratch_cfg):
        app_mod._LLM_STATUS_ENDPOINT = None
        app_mod._SETUP_GATE_CACHE["ok"] = None
        app_mod._SETUP_GATE_CACHE["checked_at"] = 0.0
        r = c.get("/", follow_redirects=False)
        assert r.status_code == 200


def test_setup_page_itself_is_never_gated():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    scratch = pathlib.Path(tempfile.mkdtemp()) / "inference.yaml"  # missing -> gate would trigger
    with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", scratch):
        r = c.get("/setup")
        assert r.status_code == 200
        assert "Let's connect Mentar" in r.get_data(as_text=True)


def test_setup_save_writes_local_config_and_reloads_without_restart():
    """The key claim: an EXISTING controller (built before setup) picks up
    the new backend on its NEXT call, with no process restart -- because
    _llm_call is a stable indirection, not a snapshot."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    scratch_dir = pathlib.Path(tempfile.mkdtemp())
    scratch_cfg = scratch_dir / "inference.yaml"  # does not exist yet
    with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", scratch_cfg):
        with patch("openai.OpenAI", return_value=_reachable_openai_mock()):
            r = c.post("/setup", data={
                "backend": "ollama", "base_url": "http://localhost:11434/v1", "model": "gemma2:9b",
            }, follow_redirects=False)
        assert r.status_code == 302
        assert r.headers["Location"].endswith("/")
        assert scratch_cfg.exists()
        written = scratch_cfg.read_text(encoding="utf-8")
        assert "backend: ollama" in written
        assert "gemma2:9b" in written

        # Reload actually happened -- no restart, just re-reading the file.
        assert app_mod._INFERENCE_CFG["backend"] == "ollama"
        assert app_mod._llm_call_cached is None  # reset, will rebuild from NEW config on next call


def test_llm_call_reflects_new_backend_immediately_no_restart():
    """The actual end-to-end claim: _llm_call (the SAME function object every
    already-constructed SessionController holds a reference to, wrapped in
    controller._make_safe_llm) picks up a config change on its very next
    invocation -- proven by swapping what make_llm_call returns between two
    calls to the SAME _llm_call function, no module reload in between."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()  # noqa: F841
    scratch_dir = pathlib.Path(tempfile.mkdtemp())
    scratch_cfg = scratch_dir / "inference.yaml"

    def _fake_make_llm_call(cfg):
        model = cfg.get(cfg.get("backend"), {}).get("model", "?")
        return lambda messages: f"response-from-{model}"

    with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", scratch_cfg), \
         patch.object(app_mod, "make_llm_call", side_effect=_fake_make_llm_call):
        with patch("openai.OpenAI", return_value=_reachable_openai_mock()):
            c.post("/setup", data={
                "backend": "ollama", "base_url": "http://localhost:11434/v1", "model": "model-one",
            })
        first = app_mod._llm_call([{"role": "user", "content": "hi"}])
        assert first == "response-from-model-one"

        with patch("openai.OpenAI", return_value=_reachable_openai_mock()):
            c.post("/setup", data={
                "backend": "ollama", "base_url": "http://localhost:11434/v1", "model": "model-two",
            })
        # SAME _llm_call function object, SAME test, no reload/restart --
        # yet it now answers with the new model.
        second = app_mod._llm_call([{"role": "user", "content": "hi"}])
        assert second == "response-from-model-two"


def test_setup_save_never_inlines_api_key_writes_to_dotenv_instead():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    scratch_dir = pathlib.Path(tempfile.mkdtemp())
    scratch_cfg = scratch_dir / "inference.yaml"
    with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", scratch_cfg):
        with patch("openai.OpenAI", return_value=_reachable_openai_mock()):
            c.post("/setup", data={
                "backend": "vllm", "base_url": "http://192.168.1.10:4000/v1",
                "model": "gemma2:9b", "api_key": "FAKE-KEY-1",
            })

        written_yaml = scratch_cfg.read_text(encoding="utf-8")
        assert "FAKE-KEY-1" not in written_yaml
        assert "${MENTAR_VLLM_API_KEY}" in written_yaml

        dotenv = (scratch_dir / ".env").read_text(encoding="utf-8")
        assert "FAKE-KEY-1" in dotenv
        assert "MENTAR_VLLM_API_KEY" in dotenv


def test_setup_save_blank_api_key_uses_no_key_default():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    scratch_dir = pathlib.Path(tempfile.mkdtemp())
    scratch_cfg = scratch_dir / "inference.yaml"
    with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", scratch_cfg):
        with patch("openai.OpenAI", return_value=_reachable_openai_mock()):
            c.post("/setup", data={
                "backend": "vllm", "base_url": "http://x/v1", "model": "m", "api_key": "",
            })
        written = scratch_cfg.read_text(encoding="utf-8")
        assert "no-key" in written
        assert not (scratch_dir / ".env").exists()


def test_setup_save_shows_error_and_does_not_redirect_when_unreachable():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    scratch_dir = pathlib.Path(tempfile.mkdtemp())
    scratch_cfg = scratch_dir / "inference.yaml"
    with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", scratch_cfg):
        with patch("openai.OpenAI", side_effect=ConnectionError("refused")):
            r = c.post("/setup", data={
                "backend": "vllm", "base_url": "http://unreachable/v1", "model": "m",
            })
        assert r.status_code == 200  # stays on the setup page, no redirect
        assert "couldn" in r.get_data(as_text=True).lower()
        # Config IS written even though unreachable -- the parent can fix
        # connectivity later without re-typing everything.
        assert scratch_cfg.exists()


def test_setup_save_rejects_missing_fields():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    scratch_dir = pathlib.Path(tempfile.mkdtemp())
    scratch_cfg = scratch_dir / "inference.yaml"
    with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", scratch_cfg):
        r = c.post("/setup", data={"backend": "vllm", "base_url": "", "model": ""})
        assert r.status_code == 200
        assert "fill in all fields" in r.get_data(as_text=True).lower()
        assert not scratch_cfg.exists()


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} setup-gate tests passed.")


# ── Cloud backends (P2): consent-gated /setup Option C ────────────────────────

def _cloud_form(**over):
    base = {"backend": "openai", "model": "gpt-5.2-mini", "api_key": "sk-test",
            "cloud_ack": "on", "cloud_confirm": "AGREE"}
    base.update(over)
    return base


def test_cloud_save_without_consent_writes_nothing(monkeypatch):
    """Missing checkbox OR missing/wrong typed word: the form errors and NOT ONE
    file is written — no yaml, no .env, no consent record. consent_path is
    patched INTO the tmpdir so an early-record bug cannot hide by writing to
    the repo's real config dir instead."""
    import mentar.consent as C
    app_mod, client = _client()
    with tempfile.TemporaryDirectory() as td:
        cfg = pathlib.Path(td) / "inference.yaml"
        monkeypatch.setattr(C, "consent_path",
                            lambda: pathlib.Path(td) / "cloud_consent.yaml")
        with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", cfg), \
             patch.object(app_mod, "_probe_llm_backend", return_value=(True, 5, None)):
            for broken in (_cloud_form(cloud_ack=""), _cloud_form(cloud_confirm="yes"),
                           _cloud_form(cloud_confirm="")):
                r = client.post("/setup", data=broken)
                assert r.status_code == 200
                assert b"AGREE" in r.data          # the error names the fix
                assert not cfg.exists()
                assert not (pathlib.Path(td) / ".env").exists()
        assert not (pathlib.Path(td) / "cloud_consent.yaml").exists()


def test_cloud_save_with_consent_records_and_reloads(monkeypatch):
    import mentar.consent as C
    app_mod, client = _client()
    with tempfile.TemporaryDirectory() as td:
        cfg = pathlib.Path(td) / "inference.yaml"
        consent = pathlib.Path(td) / "cloud_consent.yaml"
        monkeypatch.setattr(C, "consent_path", lambda: consent)
        with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", cfg), \
             patch.object(app_mod, "_probe_llm_backend", return_value=(True, 5, None)):
            r = client.post("/setup", data=_cloud_form())
            assert r.status_code == 302, r.data[:300]
            # yaml holds the ${VAR} reference, never the literal key
            text = cfg.read_text()
            assert "${OPENAI_API_KEY}" in text and "sk-test" not in text
            env = (pathlib.Path(td) / ".env").read_text()
            assert 'OPENAI_API_KEY="sk-test"' in env
            assert C.has_cloud_consent("openai", path=consent)


def test_cloud_config_without_consent_record_fails_the_gate(monkeypatch):
    """A hand-placed cloud yaml (or a wiped consent file) must send every route
    back to /setup — make_llm_call would refuse it, so the gate saying 'ready'
    would bounce the child into a broken session."""
    import mentar.consent as C
    app_mod, client = _client()
    with tempfile.TemporaryDirectory() as td:
        cfg = pathlib.Path(td) / "inference.yaml"
        cfg.write_text(
            'backend: claude\nclaude:\n  model: "m"\n  api_key: "k"\n', encoding="utf-8")
        monkeypatch.setattr(C, "consent_path", lambda: pathlib.Path(td) / "absent.yaml")
        with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", cfg):
            app_mod._reload_inference_config()
            r = client.get("/", follow_redirects=False)
            assert r.status_code == 302 and "/setup" in r.headers["Location"]


def test_setup_page_discloses_what_leaves_the_device():
    """The SAFETY §4.5 wording is load-bearing: what leaves, to whom, under
    whose account, that the local promise is suspended, and how to turn it off."""
    app_mod, client = _client()
    with tempfile.TemporaryDirectory() as td:
        cfg = pathlib.Path(td) / "inference.yaml"
        cfg.write_text("backend: ollama\nollama: {model: m}\n", encoding="utf-8")
        with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", cfg):
            html = client.get("/setup").data.decode()
    for phrase in ("sent\n    over the internet", "under <em>your</em> account",
                   "data operator", "does not fully apply", "turn it off"):
        assert phrase.replace("\n    ", " ") in html.replace("\n    ", " "), phrase


def test_trust_strip_tells_the_truth_about_cloud(monkeypatch):
    import mentar.consent as C
    app_mod, client = _client()
    with tempfile.TemporaryDirectory() as td:
        cfg = pathlib.Path(td) / "inference.yaml"
        consent = pathlib.Path(td) / "cloud_consent.yaml"
        # local config: the absolute wording stays
        cfg.write_text("backend: ollama\nollama: {model: m}\n", encoding="utf-8")
        with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", cfg):
            app_mod._reload_inference_config()
            html = client.get("/setup").data.decode()
            assert "no cloud · no accounts" in html
            # cloud config + consent: the strip must CHANGE
            monkeypatch.setattr(C, "consent_path", lambda: consent)
            C.record_cloud_consent("claude", path=consent)
            cfg.write_text(
                'backend: claude\nclaude:\n  model: "m"\n  api_key: "k"\n', encoding="utf-8")
            app_mod._reload_inference_config()
            html = client.get("/setup").data.decode()
            assert "no cloud · no accounts" not in html
            assert "Anthropic" in html and "parent-approved" in html


def test_trust_strip_names_the_chatgpt_backend_too(monkeypatch):
    """openai_chatgpt is in _CLOUD_BACKENDS; omitting it from the provider table
    left every page still claiming 'no cloud - no accounts' while a child's
    turns went to OpenAI (measured 2026-08-28)."""
    app_mod, _client_ = _client()
    for backend, expect in (("openai", "OpenAI"), ("claude", "Anthropic"),
                            ("openai_chatgpt", "OpenAI"), ("ollama", None)):
        app_mod._INFERENCE_CFG = {"backend": backend}
        got = app_mod._inject_cloud_state()["cloud_provider"]
        if expect is None:
            assert got is None, f"{backend} must not claim a cloud provider"
        else:
            assert got and expect in got, f"{backend} -> {got!r}"


def test_chatgpt_backend_is_not_ready_without_a_signin(monkeypatch):
    """No OpenAI-compatible endpoint exists for this backend, so the 'None means
    in-process, trust it' branch green-lit it with NO sign-in: the child started
    a session and every turn failed (measured 2026-08-28)."""
    import mentar.consent as C
    app_mod, client = _client()
    with tempfile.TemporaryDirectory() as td:
        cfg = pathlib.Path(td) / "inference.yaml"
        cfg.write_text("backend: openai_chatgpt\nopenai_chatgpt:\n  model: m\n")
        consent = pathlib.Path(td) / "cloud_consent.yaml"
        monkeypatch.setattr(C, "consent_path", lambda: consent)
        C.record_cloud_consent("openai_chatgpt", path=consent)
        with patch.object(app_mod, "_INFERENCE_CONFIG_PATH", cfg):
            app_mod._reload_inference_config()
            # consent recorded, but no sign-in on this machine
            with patch.object(app_mod, "_chatgpt_login_status",
                              return_value={"present": False}):
                app_mod._SETUP_GATE_CACHE["ok"] = None
                assert app_mod._setup_is_complete() is False
                r = client.get("/", follow_redirects=False)
                assert r.status_code == 302 and "/setup" in r.headers["Location"]
            # with a sign-in present it becomes ready
            with patch.object(app_mod, "_chatgpt_login_status",
                              return_value={"present": True}):
                app_mod._SETUP_GATE_CACHE["ok"] = None
                assert app_mod._setup_is_complete() is True
