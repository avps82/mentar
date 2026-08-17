"""grounding/source_map.py — config handling that must not throw.

resolve_grounding() catches everything and returns an empty passage, so a
grounding fault can never break a lesson. That safety net also HIDES faults: the
only symptom is a traceback in the log, and the traceback names whatever raised
last rather than the cause.

    python3 -m pytest tests/grounding/test_source_map.py
"""

from __future__ import annotations

import logging
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.grounding import resolve_grounding  # noqa: E402


def test_a_null_grounding_config_does_not_raise(caplog):
    """`grounding:` written with no value in config/inference.yaml parses to YAML
    null, so cfg.get("grounding", {}) returns None -- the {} default never fires,
    because the KEY exists. get_zim_path then did cfg.get(...) on None.

    resolve_grounding caught the AttributeError and returned an empty passage, so
    lessons kept working; the cost was a full traceback logged for every grounded
    node, pointing at the wrong thing (found 2026-08-17 while sweeping grounding
    resolution). Both shapes must now resolve quietly.
    """
    node = {"source": "khanacademy", "anchor": "deadbeef", "passage_hint": "x"}
    # Asserting the RETURN VALUE alone is vacuous here, and the first version of
    # this test was: resolve_grounding swallows everything and returns "" whether
    # or not the guard exists, so removing the fix still passed. The observable
    # difference is the logged traceback, so that is what is asserted.
    with caplog.at_level(logging.WARNING, logger="mentar.grounding"):
        assert resolve_grounding(node, None) == ""
        assert resolve_grounding(node, {}) == ""
    blew_up = [r for r in caplog.records if r.exc_info or r.levelno >= logging.ERROR]
    assert not blew_up, (
        "a null grounding config still raises inside resolve_grounding: "
        f"{[r.getMessage() for r in blew_up]}"
    )


def test_an_unknown_source_resolves_quietly():
    """A node naming a source the config does not define is a content problem,
    not a crash: the lesson proceeds ungrounded."""
    assert resolve_grounding(
        {"source": "not_a_real_source", "anchor": "abc"}, {"zim_dir": "/nowhere"}
    ) == ""
