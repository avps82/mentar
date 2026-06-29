"""Tests for mentar.inference.backend — config loading + make_llm_call dispatch.

Contract checks:
    - ${VAR} expansion (nested dicts/lists) from the environment.
    - load_inference_config: missing default -> None; explicit missing -> FileNotFoundError.
    - make_llm_call dispatch: vllm / llamacpp(server) / ollama all build an OpenAI-compatible
      caller; ollama base_url gets /v1 appended.
    - The built caller passes model/temperature/max_tokens through and returns the text.
    - Unreachable endpoint -> RuntimeError after retries (no infinite hang).
    - Unknown backend -> ValueError; cloud backends -> NotImplementedError.

No network: the openai client is monkeypatched with a fake.

──────────────────────────────────────────────────────────────────────────────
Inline smoke runner (python3-runnable without pytest):
    python3 tests/inference/test_backend.py
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import os
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.inference import backend as B  # noqa: E402

# ── Fake OpenAI client (records calls, optionally raises) ─────────────────────

class _FakeMessage:
    def __init__(self, content):
        self.message = type("M", (), {"content": content})


class _FakeCompletions:
    def __init__(self, parent):
        self._parent = parent

    def create(self, **kwargs):
        self._parent.calls.append(kwargs)
        if self._parent.raise_n > 0:
            self._parent.raise_n -= 1
            raise ConnectionError("boom")
        return type("R", (), {"choices": [_FakeMessage(self._parent.reply)]})


class _FakeClient:
    instances: list = []

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.calls = []
        self.reply = "hello from model"
        self.raise_n = 0
        self.chat = type("C", (), {"completions": _FakeCompletions(self)})
        _FakeClient.instances.append(self)


def _install_fake(monkeypatch=None, *, raise_n=0):
    import openai
    _FakeClient.instances = []

    def factory(**kwargs):
        c = _FakeClient(**kwargs)
        c.raise_n = raise_n
        return c

    if monkeypatch is not None:
        monkeypatch.setattr(openai, "OpenAI", factory)
    else:
        openai.OpenAI = factory  # smoke-runner path
    # speed up retry sleeps
    if monkeypatch is not None:
        monkeypatch.setattr(B, "_RETRY_BACKOFF_S", 0.0)
    else:
        B._RETRY_BACKOFF_S = 0.0


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_expand_env():
    os.environ["MENTAR_T_TOK"] = "sekret"
    out = B._expand_env({"k": "${MENTAR_T_TOK}", "l": ["${MENTAR_T_TOK}", 7], "n": 1})
    assert out == {"k": "sekret", "l": ["sekret", 7], "n": 1}
    # unset var -> empty string, never crashes
    assert B._expand_env("${MENTAR_DOES_NOT_EXIST_XYZ}") == ""


def test_load_config_missing(tmp_path=None):
    # explicit missing path raises
    raised = False
    try:
        B.load_inference_config("/no/such/inference.yaml")
    except FileNotFoundError:
        raised = True
    assert raised


def test_dotenv_resolves_config_var(tmp_path):
    """A gitignored .env next to the config supplies ${VAR} (no shell export)."""
    os.environ.pop("MENTAR_T_DOTENV_KEY", None)
    cfg_dir = tmp_path
    (cfg_dir / ".env").write_text(
        '# secrets\nexport MENTAR_T_DOTENV_KEY="sk-from-dotenv"\n', encoding="utf-8"
    )
    (cfg_dir / "inference.yaml").write_text(
        'backend: vllm\nvllm:\n  base_url: "http://x/v1"\n  model: "m"\n'
        '  api_key: "${MENTAR_T_DOTENV_KEY}"\n',
        encoding="utf-8",
    )
    try:
        cfg = B.load_inference_config(cfg_dir / "inference.yaml")
        assert cfg["vllm"]["api_key"] == "sk-from-dotenv"
    finally:
        os.environ.pop("MENTAR_T_DOTENV_KEY", None)


def test_dotenv_does_not_override_real_env(tmp_path):
    """A real environment value wins over .env (.env is only a fallback)."""
    os.environ["MENTAR_T_DOTENV_KEY2"] = "from-env"
    (tmp_path / ".env").write_text("MENTAR_T_DOTENV_KEY2=from-dotenv\n", encoding="utf-8")
    (tmp_path / "inference.yaml").write_text(
        'backend: vllm\nvllm:\n  api_key: "${MENTAR_T_DOTENV_KEY2}"\n', encoding="utf-8"
    )
    try:
        cfg = B.load_inference_config(tmp_path / "inference.yaml")
        assert cfg["vllm"]["api_key"] == "from-env"
    finally:
        os.environ.pop("MENTAR_T_DOTENV_KEY2", None)


def test_dispatch_vllm(monkeypatch=None):
    _install_fake(monkeypatch)
    fn = B.make_llm_call({"backend": "vllm",
                          "vllm": {"base_url": "http://h:4000/v1", "model": "gemma2:9b"}})
    out = fn([{"role": "user", "content": "hi"}])
    assert out == "hello from model"
    cli = _FakeClient.instances[-1]
    assert cli.init_kwargs["base_url"] == "http://h:4000/v1"
    assert cli.calls[-1]["model"] == "gemma2:9b"
    assert cli.calls[-1]["temperature"] == 0.3
    assert cli.calls[-1]["max_tokens"] == 400


def test_dispatch_ollama_appends_v1(monkeypatch=None):
    _install_fake(monkeypatch)
    fn = B.make_llm_call({"backend": "ollama",
                          "ollama": {"base_url": "http://localhost:11434", "model": "x"}})
    fn([{"role": "user", "content": "hi"}])
    cli = _FakeClient.instances[-1]
    assert cli.init_kwargs["base_url"] == "http://localhost:11434/v1"


def test_dispatch_llamacpp_server(monkeypatch=None):
    _install_fake(monkeypatch)
    fn = B.make_llm_call({"backend": "llamacpp",
                          "llamacpp": {"mode": "server", "base_url": "http://localhost:8080/v1"}})
    assert fn([{"role": "user", "content": "hi"}]) == "hello from model"


def test_generation_overrides(monkeypatch=None):
    _install_fake(monkeypatch)
    fn = B.make_llm_call({
        "backend": "vllm",
        "vllm": {"base_url": "http://h/v1", "model": "m"},
        "generation": {"temperature": 0.0, "max_tokens": 64},
    })
    fn([{"role": "user", "content": "hi"}])
    call = _FakeClient.instances[-1].calls[-1]
    assert call["temperature"] == 0.0 and call["max_tokens"] == 64


def test_unreachable_raises_runtimeerror(monkeypatch=None):
    # raise on every attempt -> RuntimeError after retries (default retries=2 -> 3 attempts)
    _install_fake(monkeypatch, raise_n=99)
    fn = B.make_llm_call({"backend": "vllm", "vllm": {"base_url": "http://x/v1", "model": "m"}})
    raised = False
    try:
        fn([{"role": "user", "content": "hi"}])
    except RuntimeError as e:
        raised = True
        assert "unreachable" in str(e)
    assert raised
    assert len(_FakeClient.instances[-1].calls) == 3  # retries + 1


def test_retry_then_succeed(monkeypatch=None):
    _install_fake(monkeypatch, raise_n=1)  # fail once, then succeed
    fn = B.make_llm_call({"backend": "vllm", "vllm": {"base_url": "http://x/v1", "model": "m"}})
    assert fn([{"role": "user", "content": "hi"}]) == "hello from model"
    assert len(_FakeClient.instances[-1].calls) == 2


def test_unknown_backend():
    raised = False
    try:
        B.make_llm_call({"backend": "bogus"})
    except ValueError:
        raised = True
    assert raised


def test_cloud_backend_not_implemented():
    raised = False
    try:
        B.make_llm_call({"backend": "claude", "claude": {"model": "x"}})
    except NotImplementedError:
        raised = True
    assert raised


# ── Inline smoke runner ───────────────────────────────────────────────────────

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        fn()  # monkeypatch=None path
        print(f"  ✓ {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} backend tests passed.")
