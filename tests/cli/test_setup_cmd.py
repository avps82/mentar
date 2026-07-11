"""R9 follow-up -- `mentar setup --runtime vllm`: the CLI counterpart to the
web /setup page, for a remote OpenAI-compatible API (LiteLLM/vLLM proxy).
No roster/download involved; _verify_backend is mocked (no real network).

Inline smoke runner:
    python3 tests/cli/test_setup_cmd.py
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

import mentar.cli.__main__ as CLI  # noqa: E402


def _args(**overrides) -> SimpleNamespace:
    base = {
        "runtime": "vllm", "model": None, "base_url": None, "api_key": None,
        "ctx": 4096, "roster": None, "config": None, "dry_run": False,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_remote_api_requires_base_url_and_model():
    args = _args(base_url=None, model=None)
    assert CLI._setup(args) == 1


def test_remote_api_dry_run_writes_nothing():
    with tempfile.TemporaryDirectory() as td:
        cfg_path = pathlib.Path(td) / "inference.yaml"
        args = _args(base_url="http://x/v1", model="m", api_key="FAKE-K1",
                     config=str(cfg_path), dry_run=True)
        assert CLI._setup(args) == 0
        assert not cfg_path.exists()
        assert not (cfg_path.parent / ".env").exists()


def test_remote_api_writes_config_and_dotenv_with_key():
    with tempfile.TemporaryDirectory() as td:
        cfg_path = pathlib.Path(td) / "inference.yaml"
        args = _args(base_url="http://192.168.xx.xxx:4000/v1", model="gemma2:9b",
                     api_key="FAKE-K1", config=str(cfg_path))
        with patch.object(CLI, "_verify_backend", return_value=(True, "model replied 'pong'")):
            assert CLI._setup(args) == 0

        written_yaml = cfg_path.read_text(encoding="utf-8")
        assert "backend: vllm" in written_yaml
        assert "FAKE-K1" not in written_yaml
        assert "${MENTAR_VLLM_API_KEY}" in written_yaml

        dotenv = (cfg_path.parent / ".env").read_text(encoding="utf-8")
        assert "FAKE-K1" in dotenv


def test_remote_api_blank_key_writes_no_key_default():
    with tempfile.TemporaryDirectory() as td:
        cfg_path = pathlib.Path(td) / "inference.yaml"
        args = _args(base_url="http://x/v1", model="m", api_key=None, config=str(cfg_path))
        with patch.object(CLI, "_verify_backend", return_value=(True, "model replied 'pong'")):
            assert CLI._setup(args) == 0
        written = cfg_path.read_text(encoding="utf-8")
        assert "no-key" in written
        assert not (cfg_path.parent / ".env").exists()


def test_remote_api_verify_failure_returns_1_but_still_writes_config():
    """Same posture as the web /setup route: the config is written even when
    the backend doesn't respond, so the parent/operator doesn't have to
    re-type everything once connectivity is fixed."""
    with tempfile.TemporaryDirectory() as td:
        cfg_path = pathlib.Path(td) / "inference.yaml"
        args = _args(base_url="http://unreachable/v1", model="m", config=str(cfg_path))
        with patch.object(CLI, "_verify_backend", return_value=(False, "ConnectionError: refused")):
            assert CLI._setup(args) == 1
        assert cfg_path.exists()


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} setup-cmd tests passed.")
