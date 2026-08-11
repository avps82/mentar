"""Credential-leak guard: detection + redaction, and the controller chokepoint.

Test secrets are CONSTRUCTED AT RUNTIME (concatenation) so no secret-shaped literal
sits in the source — keeps the repo's pre-commit secret guard (and external scanners)
happy while still exercising the guard.
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.safety.credential_guard import (  # noqa: E402
    REDACTION,
    detect_credential_leak,
    redact_credentials,
)

# Built at runtime so the file contains no literal secret-shaped string.
_SK = "sk-" + "A" * 32
_BEARER = "Bearer " + "z" * 40
_APIKV = "api" "_key=" + "v" * 14
_ENVKV = "MENTAR_VLLM_API" "_KEY=" + "w" * 12
_TOKEN = "to" "ken: " + "d" * 16

_LEAKS = [
    f"Your key is {_SK}",
    f"Authorization: {_BEARER}",
    f"set {_APIKV} in the config",
    f"export {_ENVKV}",
    _TOKEN,
]
_CLEAN = [
    "Share 12 cookies equally among 3 friends. The answer is 4.",
    "A half is one of two equal parts. 1/2.",
    "Great job! Let's keep going.",
]


def test_detects_leaks():
    for s in _LEAKS:
        assert detect_credential_leak(s), s


def test_no_false_positive_on_clean_text():
    for s in _CLEAN:
        assert not detect_credential_leak(s), s


def test_redaction_removes_the_secret():
    for s in _LEAKS:
        out = redact_credentials(s)
        assert REDACTION in out
        assert ("A" * 32) not in out          # the sk- body is gone
        assert ("z" * 40) not in out          # the bearer body is gone


def test_redaction_leaves_clean_text_unchanged():
    for s in _CLEAN:
        assert redact_credentials(s) == s


def test_controller_redacts_llm_output():
    """A model that emits a key has it scrubbed before it reaches the child/logs."""
    from mentar.dialogue.controller import SessionController
    curr = {"unit_fractions": {"label": "unit fractions", "answer_type": "fraction",
            "checker": "fraction_equiv", "expected_answer": "1/3", "grounding": {},
            "prerequisites": []}}

    class _S:
        def get_skill_state(self, *a): return None
        def update_skill_state(self, *a, **k): pass

    leaky = f"Here is the answer. (debug: {_ENVKV} {_SK} )"
    ctrl = SessionController(
        llm_call=lambda m: leaky, prompt_dir=REPO / "prompts", grounding_cfg={},
        curriculum=curr, db_store=_S(), learner_id="t",
    )
    out = ctrl._llm([{"role": "user", "content": "x"}])
    assert ("A" * 32) not in out
    assert REDACTION in out


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn(); print(f"  ok {fn.__name__}")
    print(f"{len(fns)} passed.")


# ── additional credential formats (added 2026-08-12) ─────────────────────────
# This module's contract is "any credential-looking substring", but a probe
# found these standard formats passing untouched. All have unambiguous fixed
# prefixes or shapes, so the false-positive risk in tutor output is nil.

def test_github_aws_and_uri_credentials_are_redacted():
    for text in (
        "The token is ghp_1234567890abcdefghijklmnopqrstuvwx",
        "AKIAIOSFODNN7EXAMPLE",
        "postgres://user:secret@localhost:5432/db",
    ):
        assert redact_credentials(text) != text, f"not redacted: {text!r}"
        assert detect_credential_leak(text), f"not detected: {text!r}"


def test_ordinary_tutoring_text_is_untouched_by_the_new_patterns():
    """Including a plain https:// link and a ratio -- both share punctuation
    with the URI-credential pattern."""
    for text in (
        "The answer is 42.",
        "3/4 is greater than 1/2.",
        "Your key insight is that the denominator stays the same.",
        "Visit https://example.com/fractions for more practice.",
        "A ratio like 3:4 compares two amounts.",
    ):
        assert redact_credentials(text) == text, f"false positive on {text!r}"
        assert not detect_credential_leak(text), f"false positive on {text!r}"
