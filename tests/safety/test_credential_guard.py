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
    # Built at runtime, per this module's header rule. These two were literals
    # until 2026-08-16, which broke that rule and blocked the pre-commit hook
    # from adopting the matching gh*_/AKIA patterns -- this file was the only
    # false positive across all 572 tracked files.
    for text in (
        "The token is " + "gh" + "p_1234567890abcdefghijklmnopqrstuvwx",
        "AKIA" + "IOSFODNN7EXAMPLE",
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


# ── 2026-08-16 probe: standard formats still passing untouched ───────────────
# Same shape as the 2026-08-12 batch (GitHub / AWS / user:pass URI). This
# module's contract is "any credential-looking substring"; a probe of ten common
# formats found six reaching the child and the transcript unredacted.
# Secrets are BUILT AT RUNTIME so no secret-shaped literal enters the repo.

def _fake(prefix: str, body_char: str, n: int) -> str:
    return prefix + body_char * n


def test_newly_covered_credential_formats_are_detected_and_redacted():
    cases = {
        "huggingface": _fake("hf" + "_", "a", 34),
        "google":      _fake("AIza", "B", 35),
        "slack":       "xoxb" + "-" + "1" * 12 + "-" + "2" * 12,
        "jwt":         "ey" + "J" + "a" * 18 + "." + "b" * 30 + "." + "c" * 20,
        "pem":         "-----BEGIN RSA PRIVATE " + "KEY-----",
        # Mentar's own gateway key shape: a bare 64-char hex string, no prefix.
        "mentar_hex":  "f" * 64,
    }
    for name, secret in cases.items():
        assert detect_credential_leak(secret), f"{name} not detected"
        out = redact_credentials(secret)
        assert secret not in out, f"{name} value survived redaction"
        assert REDACTION in out


def test_khan_academy_grounding_anchors_are_not_redacted():
    """The 64-hex rule is pinned to EXACTLY 64 on purpose: curriculum templates
    carry 32-hex Khan Academy anchors (fractions.md `anchor:`) which are real
    lesson content a model may echo. A looser {32,} would redact them."""
    anchor = "7c5a60e1c0b05ecc9ac404061f654f4d"      # 32 hex, from the pilot template
    assert len(anchor) == 32
    assert not detect_credential_leak(anchor)
    assert redact_credentials(f"anchor: {anchor}  # KA video") == f"anchor: {anchor}  # KA video"


def test_ordinary_lesson_output_is_untouched():
    for text in ("The answer is 3/4", "Half of 8 is 4", "Oxidation is loss of electrons",
                 "The mole is 6.022 x 10^23", "Year 4 (Australia)"):
        assert not detect_credential_leak(text)
        assert redact_credentials(text) == text
