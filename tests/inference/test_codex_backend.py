"""The ChatGPT-subscription call path (codex_backend).

The protocol is UNPUBLISHED and has drifted (openclaw#38706), so these tests
pin the shapes we have actually observed and prove the parser is forgiving in
the ways that matter: an unknown event must never blank out a child's answer.
"""

import json

import pytest

from mentar.inference import codex_backend as CB


def _sse(*events):
    return [f"data: {json.dumps(e)}" for e in events]


def test_deltas_are_accumulated_in_order():
    text = CB.extract_text(_sse(
        {"type": "response.output_text.delta", "delta": "Three "},
        {"type": "response.output_text.delta", "delta": "quarters"},
        {"type": "response.output_text.delta", "delta": " is bigger."},
    ))
    assert text == "Three quarters is bigger."


def test_a_terminal_response_wins_over_deltas():
    """The completed payload is authoritative — if both arrive they agree, and
    trusting the terminal one avoids double-counting a replayed delta."""
    text = CB.extract_text(_sse(
        {"type": "response.output_text.delta", "delta": "partial"},
        {"type": "response.completed", "response": {
            "output": [{"content": [{"type": "output_text", "text": "the full answer"}]}]}},
    ))
    assert text == "the full answer"


def test_output_text_shorthand_on_the_response():
    text = CB.extract_text(_sse(
        {"type": "response.completed", "response": {"output_text": "short form"}}))
    assert text == "short form"


def test_unknown_events_keepalives_and_done_are_ignored_not_fatal():
    """A new event type must not blank a child's answer — the whole reason the
    parser is forgiving rather than strict."""
    text = CB.extract_text([
        ": keepalive",
        "",
        'data: {"type":"response.some_future_event","payload":{"x":1}}',
        "data: not-json-at-all",
        'data: {"type":"response.output_text.delta","delta":"still here"}',
        "data: [DONE]",
    ])
    assert text == "still here"


def test_empty_stream_yields_empty_string_not_an_exception():
    """Upstream (_make_safe_llm) already degrades an empty reply gracefully;
    raising here would turn a quiet stream into a crash."""
    assert CB.extract_text([]) == ""


def test_system_turn_becomes_instructions_not_a_message():
    """Some chat templates on this path reject an inline system role — the
    same failure class the maintainer hit on 2026-08-26."""
    body = CB._build_body(
        [{"role": "system", "content": "You are a tutor."},
         {"role": "user", "content": "What is 3/4 + 1/8?"}],
        model="gpt-5.2", max_tokens=1200, temperature=0.3)
    assert body["instructions"] == "You are a tutor."
    assert [m["role"] for m in body["input"]] == ["user"]
    assert body["input"][0]["content"][0]["text"] == "What is 3/4 + 1/8?"
    assert body["store"] is False, "never ask them to retain a child's turn"
    assert body["model"] == "gpt-5.2"


def test_missing_model_is_refused_at_build_time():
    with pytest.raises(ValueError) as exc:
        CB.make_codex_call({}, {"max_tokens": 100, "temperature": 0.3,
                                "timeout": 10, "retries": 0})
    assert "model" in str(exc.value)


def _gen():
    return {"max_tokens": 100, "temperature": 0.3, "timeout": 10, "retries": 2}


def _fake_stream(monkeypatch, status, lines=(), text=""):
    import httpx

    class _Resp:
        status_code = status
        def __init__(self): self.text = text
        def read(self): return None
        def iter_lines(self): return iter(lines)
        def __enter__(self): return self
        def __exit__(self, *a): return False

    calls = []
    def _stream(*a, **kw):
        calls.append(kw)
        return _Resp()
    monkeypatch.setattr(httpx, "stream", _stream)
    return calls


def _stub_auth(monkeypatch, token="tok"):
    from mentar.inference import codex_auth as CA
    monkeypatch.setattr(CA, "make_codex_token_provider", lambda f: (lambda: token))
    monkeypatch.setattr(CA, "read_credentials", lambda f=None: {"account_id": "acct-1"})


def test_401_says_sign_in_again_and_is_not_retried(monkeypatch):
    _stub_auth(monkeypatch)
    calls = _fake_stream(monkeypatch, 401)
    fn = CB.make_codex_call({"model": "m"}, _gen())
    with pytest.raises(CB.CodexBackendError) as exc:
        fn([{"role": "user", "content": "hi"}])
    assert "sign in again" in str(exc.value)
    assert len(calls) == 1, "a rejected sign-in resent identically is pointless"


def test_429_names_the_plan_limit_and_is_not_retried(monkeypatch):
    _stub_auth(monkeypatch)
    calls = _fake_stream(monkeypatch, 429)
    fn = CB.make_codex_call({"model": "m"}, _gen())
    with pytest.raises(CB.CodexBackendError) as exc:
        fn([{"role": "user", "content": "hi"}])
    assert "usage limit" in str(exc.value) and "plan" in str(exc.value)
    assert len(calls) == 1


def test_a_missing_signin_is_reported_not_retried(monkeypatch):
    from mentar.inference import codex_auth as CA

    def _boom():
        raise CA.CodexAuthError("no ChatGPT sign-in found at /x — sign in with: mentar chatgpt-login")
    monkeypatch.setattr(CA, "make_codex_token_provider", lambda f: _boom)
    monkeypatch.setattr(CA, "read_credentials", lambda f=None: {})
    calls = _fake_stream(monkeypatch, 200)
    fn = CB.make_codex_call({"model": "m"}, _gen())
    with pytest.raises(CB.CodexBackendError) as exc:
        fn([{"role": "user", "content": "hi"}])
    assert "chatgpt-login" in str(exc.value)
    assert len(calls) == 0, "never hit the network without a credential"


def test_a_successful_call_sends_the_account_header_and_returns_text(monkeypatch):
    _stub_auth(monkeypatch, token="tok-abc")
    calls = _fake_stream(monkeypatch, 200, lines=_sse(
        {"type": "response.output_text.delta", "delta": "ping"}))
    fn = CB.make_codex_call({"model": "gpt-5.2"}, _gen())
    assert fn([{"role": "user", "content": "hi"}]) == "ping"
    headers = calls[0]["headers"]
    assert headers["Authorization"] == "Bearer tok-abc"
    assert headers["chatgpt-account-id"] == "acct-1"
