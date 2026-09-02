"""Recompute stored p_mastery by replaying each learner's own response history.

Why this exists (2026-08-16): A20's `learns` gate was corrected so that a WRONG
answer earns no learning credit whether or not Help was pressed. That changes
future updates only -- every `skill_state` row already on disk still carries a
value produced by the old rule, which inflated mastery on hinted-wrong answers
(measured: 0.10 -> 0.2231 for a child who answered wrong every turn). Without a
replay, a child keeps mastery they were never shown to have, and the engine
keeps not teaching the skill.

This is a faithful replay, not an estimate. Everything it needs is already in
the database:

  * `response_log` holds every scored attempt with its `scored` and `hinted`
    flags, in insertion order (`id` AUTOINCREMENT -- used rather than
    `timestamp`, which is only second-granular and ties within a turn).
  * The per-skill BKT params come from the CURRICULUM, exactly as the controller
    derives them each turn (`params_for(node.answer_type, node.bkt_priors)`).
    NOT from skill_state's p_guess/p_slip/p_learns columns. Until 2026-09-02
    those were never written -- `update_skill_state` omitted them from its
    INSERT, so every row carried the schema defaults (0.2/0.1/0.2, the mc4
    class) regardless of the node's real class. Reading them made this replay
    disagree with the live engine on the very first test, which is how the
    column bug was found. The store now writes them (W3.3 §6 B1), but any row
    last updated before that still holds the defaults, so the curriculum stays
    the one source that is right for every row. The consequence is that a
    template whose answer_type changed since a session would replay under the
    new class; the alternative -- replaying under params that were never used
    -- is worse.
  * One item can log several attempts (unaided, then hinted re-checks). Since
    2026-09-02 only the FIRST attempt and a hinted CORRECT are BKT observations;
    a hinted WRONG on an already-observed item is not (W3.3 §3.3). The replay
    applies the same rule via prompt_ref adjacency -- see _replay_one.
  * `probe_event` identifies which responses were PROBES. Probes never feed
    bkt_update (only FSMState.BKT_UPDATE and HELP_RECHECK_BKT_UPDATE call it);
    a non-clean probe instead DEMOTES mastery to PROBE_DEMOTE_MASTERY. Both
    halves are reproduced here, or the replay would drift from what the FSM did.

Read-only unless `apply=True`. The CLI defaults to a dry run: this rewrites a
child's records, so it prints what would change and does nothing until told.

    mentar recompute-mastery            # show what would change
    mentar recompute-mastery --apply    # write it
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from mentar.dialogue.controller import PROBE_DEMOTE_MASTERY
from mentar.engine.bkt import P_L0, BktParams, bkt_update, params_for
from mentar.engine.curriculum import load_curriculum
from mentar.paths import bundle_root

__all__ = ["Change", "recompute_mastery"]


@dataclass(frozen=True)
class Change:
    learner_id: int
    skill_id: str
    stored: float
    replayed: float
    observations: int

    @property
    def delta(self) -> float:
        return self.replayed - self.stored


def _params_by_node() -> dict[str, BktParams]:
    """node_id -> the params the controller would use, from every shipped template.

    Every template is scanned, not just the enabled ones: a learner can hold
    history in a pack a parent has since switched off, and that row still needs
    replaying.
    """
    out: dict[str, BktParams] = {}
    root = bundle_root() / "curriculum" / "templates"
    for path in sorted(root.glob("**/*.md")):
        if path.name in ("index.md", "log.md"):
            continue
        try:
            curriculum = load_curriculum(path)
        except Exception:  # noqa: BLE001 -- a broken template is other tests' problem
            continue
        for node_id, node in curriculum.items():
            try:
                out[node_id] = params_for(
                    node.get("answer_type", "numeric"), node.get("bkt_priors")
                )
            except ValueError:
                continue          # answer_type with no BKT class (free_text): never scored
    return out


def _replay_one(
    conn: sqlite3.Connection, learner_id: int, skill_id: str, params: BktParams
) -> tuple[float, int]:
    """The learner's mastery in this skill, replayed from the first attempt."""
    # Which response rows were probe attempts, and which one CLOSED each probe.
    probe_response_ids: set[int] = set()
    demote_after: dict[int, str] = {}
    for first_id, retry_id, klass in conn.execute(
        "SELECT response_log_id, retry_response_log_id, class FROM probe_event "
        "WHERE learner_id = ? AND skill_id = ?",
        (learner_id, skill_id),
    ):
        probe_response_ids.add(first_id)
        if retry_id is not None:
            probe_response_ids.add(retry_id)
        # The classification happens after the LAST response of the probe.
        demote_after[retry_id if retry_id is not None else first_id] = klass

    p, seen = P_L0, 0
    prev_ref: tuple[str, str] | None = None
    for rid, scored, hinted, prompt_ref, session_id in conn.execute(
        "SELECT id, scored, hinted, prompt_ref, session_id FROM response_log "
        "WHERE learner_id = ? AND skill_id = ? ORDER BY id",
        (learner_id, skill_id),
    ):
        if rid not in probe_response_ids:
            # W3.3 §3.3: a hinted WRONG on the item that produced the previous
            # observation is logged but not observed (controller: item_observed
            # gate in _do_help_recheck_score). prompt_ref is "item:<id>", unique
            # per draw and identical across an item's attempts, so adjacency
            # identifies the item -- WITHIN a session: the item bank's no-repeat
            # is per session, so the same bank item can close one session and
            # open the next, and the controller's flag resets at every PRESENT.
            # Limitation: the LLM-transfer fallback logs "pattern:<name>",
            # identical across consecutive items of one node, where this rule
            # would also skip a hinted wrong that opened the NEXT item; no
            # shipped node takes that path (every node is item-backed).
            correlated_wrong = (
                bool(hinted) and not scored and prev_ref == (session_id, prompt_ref)
            )
            if not correlated_wrong:
                p = bkt_update(p, correct=bool(scored), hinted=bool(hinted), params=params)
                seen += 1
            prev_ref = (session_id, prompt_ref)
        klass = demote_after.get(rid)
        if klass is not None and klass != "clean_pass":
            # _do_probe_classify: the probe revealed mastery was OVERESTIMATED.
            p = min(p, PROBE_DEMOTE_MASTERY)
    return p, seen


def recompute_mastery(db_path: str | Path, *, apply: bool = False) -> list[Change]:
    """Replay every stored skill. Returns only the rows whose value CHANGES.

    A row with no response history is left alone rather than reset to the prior:
    it was seeded some other way (a resumed session's in-memory default), and
    inventing a replay for it would be a guess, not a recomputation.
    """
    if not Path(db_path).exists():
        raise FileNotFoundError(f"no database at {db_path}")
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        # A database that has never held a session (a fresh install, or the
        # stub file a checkout ships) has no tables at all. That is "nothing to
        # do", not an error -- a maintainer running this on day one should not
        # get a traceback.
        have = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )}
        if not {"skill_state", "response_log"} <= have:
            return []
        changes: list[Change] = []
        rows = conn.execute(
            "SELECT learner_id, skill_id, p_mastery "
            "FROM skill_state ORDER BY learner_id, skill_id"
        ).fetchall()
        by_node = _params_by_node()
        for row in rows:
            params = by_node.get(row["skill_id"])
            if params is None:
                # No template defines this node any more (renamed or removed).
                # Guessing its class would be inventing history, so leave it.
                continue
            replayed, seen = _replay_one(conn, row["learner_id"], row["skill_id"], params)
            if seen == 0:
                continue
            if abs(replayed - row["p_mastery"]) < 1e-9:
                continue
            changes.append(Change(
                learner_id=row["learner_id"], skill_id=row["skill_id"],
                stored=row["p_mastery"], replayed=replayed, observations=seen,
            ))
        if apply and changes:
            conn.executemany(
                "UPDATE skill_state SET p_mastery = ? WHERE learner_id = ? AND skill_id = ?",
                [(c.replayed, c.learner_id, c.skill_id) for c in changes],
            )
            conn.commit()
        return changes
    finally:
        conn.close()


def report(changes: list[Change], *, applied: bool) -> int:
    if not changes:
        print("recompute-mastery: every stored mastery already matches its replay.")
        return 0
    verb = "Updated" if applied else "Would update"
    print(f"{verb} {len(changes)} skill row(s):\n")
    print(f"  {'learner':>7}  {'skill':<34} {'stored':>7} {'replayed':>9} {'delta':>8}  obs")
    for c in sorted(changes, key=lambda x: abs(x.delta), reverse=True):
        print(f"  {c.learner_id:>7}  {c.skill_id:<34} {c.stored:>7.4f} "
              f"{c.replayed:>9.4f} {c.delta:>+8.4f}  {c.observations}")
    if not applied:
        print("\nNothing written. Re-run with --apply to write these values.")
    return 0
