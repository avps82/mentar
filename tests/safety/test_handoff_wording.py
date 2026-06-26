"""W2.2 — the frozen handoff messages pass the wording harness; bad samples fail.

NOTE: passing here is necessary, not sufficient — professional safeguarding review
of the wording remains an open maintainer gate (see handoff_check module docstring).

Inline smoke runner: python3 tests/safety/test_handoff_wording.py
"""
from __future__ import annotations

from mentar.safety.escalation import HANDOFF_MESSAGE_PRIMARY, HANDOFF_MESSAGE_SUPPORT
from mentar.safety.handoff_check import validate_frozen_messages, validate_handoff_message


def test_frozen_messages_pass():
    for name, violations in validate_frozen_messages().items():
        assert violations == [], f"{name} violates: {violations}"


def test_empty_message_fails():
    assert validate_handoff_message("") == ["empty message"]
    assert validate_handoff_message("   ") == ["empty message"]


def test_emergency_signposting_fails():
    v = validate_handoff_message("Call 999 now — this is an emergency. Tell your grown-up.")
    assert any("emergency-signposting" in f for f in v), v


def test_missing_adult_routing_fails():
    v = validate_handoff_message("Let's just keep going with the lesson.")
    assert any("present adult" in f for f in v), v


def test_ai_self_promise_fails():
    # Routes to an adult (so that passes) but the tutor also promises to fix it itself.
    v = validate_handoff_message("Don't worry, I can help you fix this. Talk to your grown-up.")
    assert any("first-person AI promise" in f for f in v), v


def test_template_placeholder_fails():
    v = validate_handoff_message("Please talk to your {{guardian}} about this.")
    assert any("placeholder" in f for f in v), v


def test_real_messages_route_to_adult():
    assert "grown-up" in HANDOFF_MESSAGE_PRIMARY
    assert "grown-up" in HANDOFF_MESSAGE_SUPPORT


if __name__ == "__main__":
    for fn in [
        test_frozen_messages_pass, test_empty_message_fails, test_emergency_signposting_fails,
        test_missing_adult_routing_fails, test_ai_self_promise_fails,
        test_template_placeholder_fails, test_real_messages_route_to_adult,
    ]:
        fn()
        print(f"  ✓ {fn.__name__}")
