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
                "backend": "vllm", "base_url": "http://192.168.xx.xxx:4000/v1",
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
