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

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.inference import backend as B  # noqa: E402

# ── Fake OpenAI client (records calls, optionally raises) ─────────────────────

class _FakeMessage:
    def __init__(self, content, reasoning=None, finish_reason=None):
        attrs = {"content": content}
        if reasoning is not None:
            attrs["reasoning"] = reasoning
        self.message = type("M", (), attrs)
        self.finish_reason = finish_reason


class _FakeCompletions:
    def __init__(self, parent):
        self._parent = parent

    def create(self, **kwargs):
        self._parent.calls.append(kwargs)
        if self._parent.raise_n > 0:
            self._parent.raise_n -= 1
            raise self._parent.raise_exc()
        return type("R", (), {"choices": [_FakeMessage(
            self._parent.reply,
            getattr(self._parent, "reasoning", None),
            getattr(self._parent, "finish_reason", None))]})


class _FakeClient:
    instances: list = []

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.calls = []
        self.reply = "hello from model"
        self.reasoning = None
        self.finish_reason = None
        self.raise_n = 0
        self.raise_exc = lambda: ConnectionError("boom")
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
    # 400 -> 1200 (2026-08-19): 400 truncated a real science explanation
    # mid-list on the maintainer's machine.
    assert cli.calls[-1]["max_tokens"] == 1200


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


def test_gemini_backend_not_implemented():
    """claude/openai are wired (consent-gated) since the cloud-backend work;
    gemini stays a declared placeholder and must say where to go instead."""
    try:
        B.make_llm_call({"backend": "gemini", "gemini": {"model": "x"}})
        raise AssertionError("expected NotImplementedError")
    except NotImplementedError as exc:
        assert "openai / claude" in str(exc)


def _consented(monkeypatch=None):
    """Pretend the parent acknowledgment exists (unit tests never write it).

    ALWAYS returns the original so the caller can restore it. The earlier
    version returned None under monkeypatch and permanently rebound the global
    otherwise -- the exact leak test_autoselect.py's _patch documents, and it
    escaped this file: it left has_cloud_consent always-True for the rest of
    the session (2026-08-28).
    """
    import mentar.consent as C
    orig = C.has_cloud_consent
    if monkeypatch:
        monkeypatch.setattr(C, "has_cloud_consent", lambda b, path=None: True)
    else:
        C.has_cloud_consent = lambda b, path=None: True
    return orig


def test_cloud_backend_without_consent_is_refused(monkeypatch=None):
    """The SAFETY §4.5 guarantee: a hand-edited yaml cannot switch a child's
    sessions to the cloud — the chokepoint refuses without a recorded parent
    acknowledgment, and the message says where to go."""
    try:
        B.make_llm_call({"backend": "openai",
                         "openai": {"model": "gpt-5.2-mini", "api_key": "sk-x"}})
        raise AssertionError("expected the consent refusal")
    except RuntimeError as exc:
        assert "acknowledgment" in str(exc) and "/setup" in str(exc)


def test_cloud_backends_dispatch_with_consent(monkeypatch=None):
    import mentar.consent as C
    _install_fake(monkeypatch)
    orig = _consented(monkeypatch)
    try:
        for backend, base in (("openai", "https://api.openai.com/v1"),
                              ("claude", "https://api.anthropic.com/v1/")):
            fn = B.make_llm_call({"backend": backend,
                                  backend: {"model": "m1", "api_key": "sk-live"}})
            assert fn([{"role": "user", "content": "hi"}]) == "hello from model"
            cli = _FakeClient.instances[-1]
            assert cli.init_kwargs["base_url"] == base
            assert cli.init_kwargs["api_key"] == "sk-live"
    finally:
        C.has_cloud_consent = orig


def test_cloud_backend_requires_model_and_key_by_name():
    """No forgiving local-style defaults on a BILLED account: a wrong default
    model silently spends the parent's money, and an unset ${VAR} expands to ""
    which would only fail later as a bare 401."""
    try:
        B._resolve_http("openai", {"api_key": "sk-x"})
        raise AssertionError("model default must not exist for cloud")
    except ValueError as exc:
        assert "model" in str(exc)
    try:
        B._resolve_http("claude", {"model": "claude-sonnet-5", "api_key": ""})
        raise AssertionError("empty key must fail at resolve time")
    except ValueError as exc:
        assert "ANTHROPIC_API_KEY" in str(exc)


def test_resolve_http_endpoint_sees_cloud_backends():
    ep = B.resolve_http_endpoint({"backend": "claude",
                                  "claude": {"model": "m", "api_key": "k"}})
    assert ep and ep["base_url"].startswith("https://api.anthropic.com")


def test_provider_seam_rebuilds_client_only_when_the_token_changes(monkeypatch=None):
    """Both mutants must die: 'rebuild every call' (wasteful, and would hide a
    stale-credential bug class) and 'never rebuild' (a rotated token would keep
    authenticating with the dead one forever)."""
    _install_fake(monkeypatch)
    tokens = iter(["tok-A", "tok-A", "tok-A", "tok-B"])
    endpoint = {"base_url": "http://x/v1", "api_key": "unused",
                "api_key_provider": lambda: next(tokens), "model": "m"}
    fn = B._make_openai_call(endpoint, B._gen_params({}))  # eager build: draws tok-A
    after_factory = len(_FakeClient.instances)
    fn([{"role": "user", "content": "1"}])   # tok-A -> reuse
    fn([{"role": "user", "content": "2"}])   # tok-A -> reuse
    assert len(_FakeClient.instances) == after_factory, "same token must reuse the client"
    fn([{"role": "user", "content": "3"}])   # tok-B -> rebuild
    assert len(_FakeClient.instances) == after_factory + 1, "new token must rebuild"
    assert _FakeClient.instances[-1].init_kwargs["api_key"] == "tok-B"


def test_a_rejected_credential_is_not_retried_and_names_the_remedy(monkeypatch=None):
    import httpx
    import openai
    _install_fake(monkeypatch, raise_n=99)
    fn = B.make_llm_call({"backend": "vllm",
                          "vllm": {"base_url": "http://x/v1", "model": "m"}})
    cli = _FakeClient.instances[-1]
    resp = httpx.Response(401, request=httpx.Request("POST", "http://x/v1"))
    cli.raise_exc = lambda: openai.AuthenticationError(
        "bad key", response=resp, body=None)
    try:
        fn([{"role": "user", "content": "hi"}])
        raise AssertionError("expected the 401 to surface")
    except RuntimeError as exc:
        assert "rejected" in str(exc) and "setup" in str(exc)
    assert len(cli.calls) == 1, "a 401 retried sends the identical dead credential"


def test_a_rate_limit_names_the_plan_not_the_network(monkeypatch=None):
    """'Unreachable' sends a parent debugging their WIFI when the truth is
    their subscription's usage cap."""
    import httpx
    import openai
    _install_fake(monkeypatch, raise_n=99)
    fn = B.make_llm_call({"backend": "vllm",
                          "vllm": {"base_url": "http://x/v1", "model": "m"}})
    cli = _FakeClient.instances[-1]
    resp = httpx.Response(429, request=httpx.Request("POST", "http://x/v1"))
    cli.raise_exc = lambda: openai.RateLimitError(
        "slow down", response=resp, body=None)
    try:
        fn([{"role": "user", "content": "hi"}])
        raise AssertionError("expected the 429 to surface")
    except RuntimeError as exc:
        assert "rate-limited" in str(exc) and "plan" in str(exc)
        assert "unreachable" not in str(exc)
    assert len(cli.calls) == 3, "429 keeps its retries — only the final message changes"


def test_resolve_http_endpoint_follows_the_configured_backend():
    """R7.2 fix: resolve_http_endpoint(cfg) must return the SAME endpoint
    make_llm_call(cfg) would hit -- the settings page's reachability check
    tests this, so the original bug (checking env-default localhost:11434
    while the yaml pointed at a remote proxy) can't reappear."""
    vllm_cfg = {"backend": "vllm",
                "vllm": {"base_url": "http://192.168.1.10:4000/v1",
                         "api_key": "tok", "model": "gemma2:9b"}}
    ep = B.resolve_http_endpoint(vllm_cfg)
    assert ep == {"base_url": "http://192.168.1.10:4000/v1",
                  "api_key": "tok", "model": "gemma2:9b"}

    # Ollama: bare base gets /v1 appended, same as make_llm_call's own resolution.
    ollama_cfg = {"backend": "ollama", "ollama": {"base_url": "http://localhost:11434",
                                                  "model": "m"}}
    assert B.resolve_http_endpoint(ollama_cfg)["base_url"] == "http://localhost:11434/v1"

    # Missing block -> backend defaults (llamacpp server), not a crash.
    assert B.resolve_http_endpoint({"backend": "llamacpp"})["base_url"] == "http://localhost:8080/v1"


def test_resolve_http_endpoint_returns_none_when_no_http_endpoint_exists():
    """In-process llamacpp and unknown/cloud backends have no HTTP endpoint to
    probe -- None, so the status route reports 'nothing to check' honestly."""
    in_proc = {"backend": "llamacpp", "llamacpp": {"mode": "in_process", "model_path": "x.gguf"}}
    assert B.resolve_http_endpoint(in_proc) is None
    # a cloud block that cannot RESOLVE (no key) is honestly "nothing to probe";
    # gemini stays unwired entirely
    assert B.resolve_http_endpoint({"backend": "claude", "claude": {"model": "x"}}) is None
    assert B.resolve_http_endpoint({"backend": "gemini", "gemini": {"model": "x"}}) is None
    assert B.resolve_http_endpoint({"backend": "vllm", "vllm": "not-a-mapping"}) is None


def test_upsert_dotenv_value_creates_file_and_writes_one_line(tmp_path):
    """R9: shared by both web /setup and the CLI's remote-API setup path --
    one place that touches a credential file, not two independently-
    maintained copies."""
    env_path = tmp_path / ".env"
    assert not env_path.exists()
    B.upsert_dotenv_value(env_path, "MENTAR_VLLM_API_KEY", "first-value")
    assert env_path.exists()
    content = env_path.read_text(encoding="utf-8")
    assert 'MENTAR_VLLM_API_KEY="first-value"' in content


def test_upsert_dotenv_value_replaces_only_the_matching_key(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text('OTHER_VAR="untouched"\nMENTAR_VLLM_API_KEY="old-value"\n', encoding="utf-8")
    B.upsert_dotenv_value(env_path, "MENTAR_VLLM_API_KEY", "new-value")
    content = env_path.read_text(encoding="utf-8")
    assert 'OTHER_VAR="untouched"' in content
    assert 'MENTAR_VLLM_API_KEY="old-value"' not in content
    assert 'MENTAR_VLLM_API_KEY="new-value"' in content
    # Exactly one line for the key -- no duplicate appended alongside the old one.
    assert content.count("MENTAR_VLLM_API_KEY=") == 1


def test_fold_system_messages_prepends_to_first_user_turn():
    """The regression (2026-08-26, fresh install): gemma-2's in-process chat
    template raises on the system role, so every tutoring turn degraded to ""
    while ollama-served gemma silently accepted the same messages."""
    msgs = [
        {"role": "system", "content": "You are a tutor."},
        {"role": "user", "content": "What is 6x8?"},
        {"role": "assistant", "content": "48."},
    ]
    folded = B.fold_system_messages(msgs)
    assert [m["role"] for m in folded] == ["user", "assistant"]
    assert folded[0]["content"] == "You are a tutor.\n\nWhat is 6x8?"
    # The input is not mutated -- callers may retry with the original.
    assert msgs[0]["role"] == "system" and msgs[1]["content"] == "What is 6x8?"


def test_fold_system_messages_with_no_user_turn_becomes_a_user_turn():
    folded = B.fold_system_messages([{"role": "system", "content": "Only rules."}])
    assert folded == [{"role": "user", "content": "Only rules."}]


def test_chat_with_system_fold_retries_once_and_then_folds_upfront():
    calls = []

    def create(messages, **kw):
        calls.append([m["role"] for m in messages])
        if any(m["role"] == "system" for m in messages):
            raise ValueError("System role not supported")
        return {"ok": True, "first": messages[0]["content"]}

    state = {"fold": False}
    msgs = [{"role": "system", "content": "S."}, {"role": "user", "content": "U?"}]
    out = B._chat_with_system_fold(create, msgs, state)
    assert out["ok"] and out["first"] == "S.\n\nU?"
    assert calls == [["system", "user"], ["user"]]  # raw attempt, folded retry
    # Second call folds upfront -- one attempt, no exception round-trip.
    B._chat_with_system_fold(create, msgs, state)
    assert calls[-1] == ["user"] and len(calls) == 3


def test_chat_with_system_fold_leaves_other_valueerrors_alone():
    def create(messages, **kw):
        raise ValueError("something unrelated")

    try:
        B._chat_with_system_fold(create, [{"role": "user", "content": "x"}], {"fold": False})
        raise AssertionError("expected the unrelated ValueError to propagate")
    except ValueError as exc:
        assert "unrelated" in str(exc)


# ── Inline smoke runner ───────────────────────────────────────────────────────

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        fn()  # monkeypatch=None path
        print(f"  ✓ {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} backend tests passed.")


def test_upsert_dotenv_rejects_a_value_with_a_line_break(tmp_path):
    """A newline used to write a TWO-line entry whose continuation line was then
    stranded in .env forever: the replace step only drops lines starting with
    "KEY=". The key read back TRUNCATED (backend auth failed, looking like a
    broken gateway) and a fragment of the old SECRET survived key rotation.

    Found 2026-08-18 by round-tripping value shapes through the real writer.
    """
    env_path = tmp_path / ".env"
    B.upsert_dotenv_value(env_path, "OTHER", "keep-me")

    with pytest.raises(ValueError, match="line break"):
        B.upsert_dotenv_value(env_path, "MENTAR_VLLM_API_KEY", "sk-good\nsk-stranded")

    text = env_path.read_text(encoding="utf-8")
    assert "sk-stranded" not in text, "a rejected secret must not be written at all"
    assert "sk-good" not in text
    assert 'OTHER="keep-me"' in text, "the failed write must not disturb other keys"


def test_upsert_dotenv_strips_surrounding_whitespace(tmp_path):
    """A key pasted from a file or a web page usually carries a trailing newline.
    That one is safe to absorb -- only an EMBEDDED break is ambiguous."""
    env_path = tmp_path / ".env"
    B.upsert_dotenv_value(env_path, "MENTAR_VLLM_API_KEY", "  sk-padded\n")
    assert 'MENTAR_VLLM_API_KEY="sk-padded"' in env_path.read_text(encoding="utf-8")


def test_reasoning_only_reply_is_named_not_returned_as_silence(monkeypatch=None):
    """Ollama /v1 + a reasoning model: content is EMPTY and the whole budget went
    into a non-standard `reasoning` field. Measured 2026-08-25 on gemma4:12b --
    think=false and think=true were equivalent, both empty, so the setting meant
    to prevent this does nothing on that server.

    Returning "" made it look like a model with nothing to say, and the only log
    line blamed max_tokens, which was not the cause.
    """
    _install_fake(monkeypatch)
    fn = B.make_llm_call({"backend": "ollama",
                          "ollama": {"base_url": "http://localhost:11434", "model": "gemma4:12b"}})
    cli = _FakeClient.instances[-1]
    cli.reply = ""
    cli.reasoning = "The objective is to add two fractions: 3/4 and 1/8. " * 20

    # finish_reason="length": the reasoning was CUT OFF before the answer began,
    # so more budget can genuinely fix it and the message must say so.
    cli.finish_reason = "length"
    try:
        fn([{"role": "user", "content": "What is 3/4 + 1/8?"}])
        raise AssertionError("expected ReasoningOnlyReply, got a silent empty answer")
    except B.ReasoningOnlyReply as exc:
        msg = str(exc)
    assert "gemma4:12b" in msg, msg
    assert "max_tokens" in msg, msg
    assert "objective is to add" not in msg, "reasoning text must not be echoed"

    # finish_reason="stop": it finished and still said nothing. Telling someone to
    # raise max_tokens here would send them round a loop that cannot terminate.
    cli.finish_reason = "stop"
    try:
        fn([{"role": "user", "content": "What is 3/4 + 1/8?"}])
        raise AssertionError("expected ReasoningOnlyReply")
    except B.ReasoningOnlyReply as exc:
        msg = str(exc)
    assert "NOT help" in msg, msg
    assert "gemma2-9b" in msg, msg
    assert "objective is to add" not in msg, "reasoning text must not be echoed"


def test_a_reasoning_only_reply_is_not_retried(monkeypatch=None):
    """It is deterministic, and on the hardware where it happens each retry is a
    ~55s wait for the identical failure."""
    _install_fake(monkeypatch)
    fn = B.make_llm_call({"backend": "ollama",
                          "ollama": {"base_url": "http://localhost:11434", "model": "gemma4:12b"}})
    cli = _FakeClient.instances[-1]
    cli.reply = ""
    cli.reasoning = "thinking..."
    try:
        fn([{"role": "user", "content": "hi"}])
    except B.ReasoningOnlyReply:
        pass
    assert len(cli.calls) == 1, f"retried a deterministic failure {len(cli.calls)} times"


def test_an_ordinary_empty_reply_still_returns_empty(monkeypatch=None):
    """Only the reasoning case is reclassified. A server that genuinely returns
    nothing keeps its old behaviour -- this must not become a blanket raise."""
    _install_fake(monkeypatch)
    fn = B.make_llm_call({"backend": "ollama",
                          "ollama": {"base_url": "http://localhost:11434", "model": "x"}})
    cli = _FakeClient.instances[-1]
    cli.reply = ""
    cli.reasoning = None
    assert fn([{"role": "user", "content": "hi"}]) == ""


def test_timeout_covers_the_budget_on_measured_local_hardware():
    """A flat 120s was a remote-API assumption. Measured 2026-08-25 on a base M1:
    7.25 tok/s for a 12B (hardware ceiling, 100% GPU), so the 1200-token budget
    needs ~166s -- every full-length reply timed out, then retried twice.

    The timeout must cover the budget the SAME config allows, or we ship a
    generation limit that cannot be reached.
    """
    MEASURED_TPS = 7.25
    for max_tokens in (1200, 2048):
        got = B._gen_params({"generation": {"max_tokens": max_tokens}})["timeout"]
        needed = max_tokens / MEASURED_TPS
        assert got > needed, (
            f"max_tokens={max_tokens} needs ~{needed:.0f}s at {MEASURED_TPS} tok/s "
            f"but the timeout is {got:.0f}s — the budget can never be spent"
        )


def test_timeout_never_drops_below_the_old_default_and_is_overridable():
    """A small budget must not shorten the timeout (prompt eval alone can be slow),
    and an explicit generation.timeout still wins -- this is a floor, not a policy."""
    assert B._gen_params({"generation": {"max_tokens": 16}})["timeout"] == B._DEFAULT_TIMEOUT_S
    assert B._gen_params({"generation": {"max_tokens": 2048, "timeout": 45}})["timeout"] == 45.0


def _timeout_exc():
    import httpx
    import openai
    return openai.APITimeoutError(request=httpx.Request("POST", "http://x/v1"))


def test_a_timeout_is_not_retried(monkeypatch=None):
    """Retrying a timeout is not free -- it makes ONE turn take
    timeout x (retries+1): up to 22 min at max_tokens=2048. A child's stop waits
    timeout+5s (web/app.py:_stop_wait_seconds), so the retries silently outrun the
    stop and drop it -- the exact bug that derivation was added to fix.

    On a local backend a timeout is not bad luck either; the model is simply
    slower than the budget, so the retry buys the same outcome twice more.
    """
    _install_fake(monkeypatch, raise_n=99)
    fn = B.make_llm_call({"backend": "ollama",
                          "ollama": {"base_url": "http://localhost:11434", "model": "gemma4:12b"}})
    cli = _FakeClient.instances[-1]
    cli.raise_exc = _timeout_exc
    try:
        fn([{"role": "user", "content": "hi"}])
        raise AssertionError("expected the timeout to surface")
    except RuntimeError as exc:
        msg = str(exc)
    assert len(cli.calls) == 1, f"a timeout was retried {len(cli.calls)} times"
    assert "did not answer" in msg, msg
    assert "gemma2-9b" in msg or "max_tokens" in msg, msg


def test_a_connection_error_is_still_retried(monkeypatch=None):
    """Only timeouts stop being retried. A genuinely transient network fault keeps
    its retries -- this must not become a blanket no-retry."""
    _install_fake(monkeypatch, raise_n=2)
    fn = B.make_llm_call({"backend": "ollama",
                          "ollama": {"base_url": "http://localhost:11434", "model": "x"}})
    assert fn([{"role": "user", "content": "hi"}]) == "hello from model"
    assert len(_FakeClient.instances[-1].calls) == 3, "transient faults must still retry"


def test_revoking_consent_stops_an_ALREADY_BUILT_cloud_call(monkeypatch=None):
    """The gate must work in BOTH directions. Consent was checked only when the
    callable was built, so a parent who revoked mid-session kept sending their
    child's turns to the provider — a live SessionController holds that callable
    for the whole session (measured 2026-08-29)."""
    import mentar.consent as C
    _install_fake(monkeypatch)
    state = {"ok": True}
    orig = C.has_cloud_consent
    C.has_cloud_consent = lambda b, path=None: state["ok"]
    try:
        fn = B.make_llm_call({"backend": "openai",
                              "openai": {"model": "m", "api_key": "sk-x"}})
        assert fn([{"role": "user", "content": "hi"}]) == "hello from model"
        state["ok"] = False                     # the parent revokes
        try:
            fn([{"role": "user", "content": "hi again"}])
            raise AssertionError("a revoked backend kept talking to the cloud")
        except RuntimeError as exc:
            assert "acknowledgment" in str(exc)
    finally:
        C.has_cloud_consent = orig
