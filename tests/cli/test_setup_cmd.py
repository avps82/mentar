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


# ── Local runtimes ───────────────────────────────────────────────────────────
# Everything above this line tests the REMOTE api path. Nothing tested the local
# runtimes at all -- which is how `mentar setup --runtime auto` came to crash on
# a Mac with Ollama installed, i.e. the default first run for most people:
#
#   model_path = models_dir() / (m["hf_file"] or "")
#   KeyError: 'hf_file'
#
# That line runs for EVERY runtime but only gguf/llama_app use it, and four of
# six roster models are ollama-only with no hf_file key at all.

def _local_args(**kw):
    """Separate from _args above -- that one defaults to the remote vllm runtime,
    and a same-named second helper here silently shadowed it and broke all five
    remote tests."""
    base = dict(runtime="ollama", model=None, base_url=None, api_key=None,
                ctx=4096, roster=str(REPO_ROOT / "config" / "model_roster.yaml"),
                config=None, dry_run=True)
    base.update(kw)
    return SimpleNamespace(**base)


def test_ollama_only_model_does_not_crash_on_a_missing_gguf_filename(tmp_path, capsys):
    """The regression. gemma4-12b is ollama-only; setup must not reach for a
    GGUF filename it does not have."""
    rc = CLI._setup(_local_args(model="gemma4-12b", config=str(tmp_path / "inf.yaml")))
    out = capsys.readouterr().out
    assert rc == 0, out
    assert "backend: ollama" in out
    assert "ollama pull" in out


def test_every_ollama_only_roster_model_can_be_set_up(tmp_path, capsys):
    """Not just the one that happened to be picked. A roster entry with no
    hf_file is normal, not exotic -- most of them are."""
    import yaml

    roster = yaml.safe_load((REPO_ROOT / "config" / "model_roster.yaml").read_text())
    models = roster["models"] if isinstance(roster, dict) else roster
    ollama_only = [m for m in models if m.get("ollama_tag") and not m.get("hf_file")]
    assert ollama_only, "roster shape changed — this test is no longer meaningful"
    for m in ollama_only:
        rc = CLI._setup(_local_args(model=m["id"], config=str(tmp_path / f"{m['id']}.yaml")))
        assert rc == 0, f"{m['id']}: {capsys.readouterr().out}"
        capsys.readouterr()


def test_ollama_installed_but_not_running_is_started_for_you(tmp_path, capsys, monkeypatch):
    """autoselect picks the ollama runtime on `shutil.which("ollama")` alone -- the
    BINARY being on PATH. On macOS the brew install gives you exactly that while
    the daemon only starts with the app, so "installed but not serving" is an
    ordinary first-run state.

    It used to print "ERROR: ollama pull failed." AFTER "may take a while", then
    (briefly) a message telling you to open a second terminal. Maintainer,
    2026-08-25: "I had to run ollama serve in another terminal.. not one cmd to
    start them". So setup starts it, and only explains itself if that fails.
    """
    started, listed = [], {"n": 0}

    def fake_run(cmd, *a, **kw):
        if cmd[:2] == ["ollama", "list"]:
            listed["n"] += 1
            # down on the first look, up once `serve` has been spawned
            return SimpleNamespace(returncode=0 if started else 1, stdout="", stderr="")
        if cmd[:2] == ["ollama", "pull"]:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        raise AssertionError(f"unexpected command {cmd!r}")

    def fake_popen(cmd, *a, **kw):
        assert cmd == ["ollama", "serve"], cmd
        assert kw.get("start_new_session"), "daemon must outlive setup"
        started.append(cmd)
        return SimpleNamespace(pid=1234)

    monkeypatch.setattr(CLI.shutil, "which", lambda name: "/usr/local/bin/ollama")
    monkeypatch.setattr(CLI.subprocess, "run", fake_run)
    monkeypatch.setattr(CLI.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(CLI.time, "sleep", lambda s: None)
    monkeypatch.setattr(CLI, "_verify_backend", lambda cfg: (True, "model replied 'ping'"))

    rc = CLI._setup(_local_args(model="gemma4-12b", dry_run=False,
                                config=str(tmp_path / "inf.yaml")))
    out = capsys.readouterr().out
    assert started, "setup did not start the ollama server"
    assert rc == 0, out
    assert "starting it" in out


def _written_max_tokens(**kw) -> int:
    """The max_tokens `mentar setup` would actually write, read back from its output."""
    import contextlib
    import io
    import re

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = CLI._setup(_local_args(**kw))
    assert rc == 0, buf.getvalue()
    found = re.search(r"max_tokens: (\d+)", buf.getvalue())
    assert found, f"no max_tokens in setup output:\n{buf.getvalue()}"
    return int(found.group(1))


def test_setup_never_writes_a_smaller_budget_than_the_backend_default():
    """setup used to hardcode 512 -- under HALF of DEFAULT_MAX_TOKENS (1200) -- so
    running it silently DOWNGRADED generation and real turns logged
    "output TRUNCATED at max_tokens=512" (live macOS run, 2026-08-25).

    The bug is not the number, it is setup keeping a competing default at all.
    """
    import yaml

    from mentar.inference.backend import DEFAULT_MAX_TOKENS

    roster = yaml.safe_load((REPO_ROOT / "config" / "model_roster.yaml").read_text())
    models = roster["models"] if isinstance(roster, dict) else roster
    checked = [m for m in models if m.get("ollama_tag")]
    assert checked, "roster shape changed — this test is no longer meaningful"
    for m in checked:
        got = _written_max_tokens(model=m["id"])
        assert got >= DEFAULT_MAX_TOKENS, (
            f"{m['id']}: setup writes max_tokens={got}, below the backend's own "
            f"default of {DEFAULT_MAX_TOKENS} — setup must never downgrade generation"
        )


def test_a_reasoning_model_gets_more_room_than_a_plain_one():
    """A reasoning model spends budget on hidden chain-of-thought BEFORE the visible
    answer. think=False is meant to suppress that, but Ollama's OpenAI-compatible
    /v1 can ignore the field, so the cap must survive the suppression being ignored.
    """
    import yaml

    from mentar.inference.backend import DEFAULT_MAX_TOKENS

    roster = yaml.safe_load((REPO_ROOT / "config" / "model_roster.yaml").read_text())
    models = roster["models"] if isinstance(roster, dict) else roster
    reasoning = [m for m in models if m.get("reasoning") and m.get("ollama_tag")]
    plain = [m for m in models if not m.get("reasoning") and m.get("ollama_tag")]
    assert reasoning and plain, "roster no longer has both kinds — test is meaningless"
    assert _written_max_tokens(model=reasoning[0]["id"]) > DEFAULT_MAX_TOKENS
    assert _written_max_tokens(model=plain[0]["id"]) == DEFAULT_MAX_TOKENS
