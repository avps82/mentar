"""Proactive-probe outcome classification — the false-confidence decision table.

Spec: docs/SPEC.md §14 (measurement), §14.4 (this table); PHASE0 W3.4;
docs/SESSION_FSM.md P3 (PROBE_CLASSIFY). Tests: docs/TESTS.md T5.x.

Disambiguates a probe outcome into one of four classes written to
`probe_event.class` (schema CHECK enforces the same four):

    clean_pass         first probe correct — genuine mastery signal
    slip_suspect       a single failure that recovered on retry (or low-mastery miss)
    false_confidence   the dangerous case — believes-but-doesn't, ruled out as slip
    forgetting_suspect previously-mastered skill gone stale (decayed-mastery window)

W3.4 operational definition: classify as `false_confidence` ONLY when
(mastery >= threshold) AND (no Help pressed on the concept) AND (first probe
failed) AND (an immediate second transfer variant ALSO failed — rules out slip).
A single failure is `slip_suspect`; a stale-mastery window is `forgetting_suspect`.

Pure, stdlib-only, side-effect-free: the caller persists the result to
`probe_event` and the retry is driven by the FSM (one retry only — W3.4/FSM §3.2).
"""

from __future__ import annotations

from enum import Enum

# One threshold, one home (engine.fringe); this was a "kept in sync" duplicate.
from mentar.engine.fringe import DEFAULT_MASTERY_THRESHOLD  # re-exported for callers


class ProbeClass(str, Enum):
    CLEAN_PASS = "clean_pass"
    SLIP_SUSPECT = "slip_suspect"
    FALSE_CONFIDENCE = "false_confidence"
    FORGETTING_SUSPECT = "forgetting_suspect"


def classify_probe(
    first_correct: bool,
    retry_correct: bool | None,
    mastery: float,
    help_pressed: bool,
    mastery_is_stale: bool,
    threshold: float = DEFAULT_MASTERY_THRESHOLD,
) -> ProbeClass:
    """Apply the W3.4 false-confidence decision table.

    Args:
        first_correct:   did the learner pass the first probe variant?
        retry_correct:   result of the second transfer variant; None if no retry
                         was run (only valid when first_correct is True).
        mastery:         current BKT p_mastery for the probed skill.
        help_pressed:    was Help pressed on this concept (this session)?
        mastery_is_stale: forgetting window — mastery was attained but the
                         skill_state is older than the staleness window
                         (caller derives from skill_state.updated_at; see §14.4).
        threshold:       mastery threshold (default 0.85).

    Returns a ProbeClass. Ordering is deliberate: forgetting is checked before
    false_confidence so a decayed skill is not mislabelled as never-understood.
    """
    if first_correct:
        return ProbeClass.CLEAN_PASS

    # First probe failed → the FSM has already run one retry variant.
    if retry_correct:
        # Recovered on the second variant → a single failure, treated as a slip.
        return ProbeClass.SLIP_SUSPECT

    # Both the probe and its retry failed — slip is ruled out.
    if mastery_is_stale:
        return ProbeClass.FORGETTING_SUSPECT
    if mastery >= threshold and not help_pressed:
        return ProbeClass.FALSE_CONFIDENCE

    # Both failed but mastery was never high (or Help was pressed): an expected
    # miss, not a pathology of confidence. Logged as slip_suspect in v0 — the
    # least-alarming class — pending post-pilot review of this bucket.
    return ProbeClass.SLIP_SUSPECT
