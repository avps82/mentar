"""CLI entry point. Wired in pyproject.toml [project.scripts].

Subcommands:
  run-session       — Drive a full tutoring session (headless) against the configured backend.
  serve             — Start the pilot web app (mentar.web.app).
  eval              — Run the eval harness (stub).
  validate-template — Validate a curriculum template against the W3.1 schema.
"""

from __future__ import annotations

import argparse
import sys
import time
import uuid
from pathlib import Path


def _repo_root() -> Path:
    # src/mentar/cli/__main__.py -> cli -> mentar -> src -> repo root
    return Path(__file__).resolve().parents[3]


def _build_controller(args):
    """Construct a SessionController wired to the configured inference backend.

    Reuses the web app's curriculum loader and DB adapter so CLI and web exercise
    the exact same turn loop.
    """
    from mentar.dialogue.controller import SessionController
    from mentar.db.store import LearnerStore
    from mentar.engine.itembank import load_item_bank
    from mentar.engine.itemgen import build_item_source
    from mentar.inference import load_inference_config, make_llm_call
    from mentar.web.app import _DbStoreAdapter, _load_curriculum

    repo = _repo_root()
    curriculum_path = Path(args.curriculum) if args.curriculum else (
        repo / "curriculum" / "templates" / "_pilot" / "fractions.md"
    )
    prompt_dir = Path(args.prompt_dir) if args.prompt_dir else (repo / "prompts")

    cfg = load_inference_config(args.config)  # None -> default config/inference.yaml
    if cfg is None:
        print(
            "ERROR: no inference config found. Create config/inference.yaml "
            "(copy config/inference.example.yaml) or pass --config.",
            file=sys.stderr,
        )
        return None, None

    llm_call = make_llm_call(cfg)
    curriculum = _load_curriculum(curriculum_path)
    itembank_path = Path(args.itembank) if args.itembank else (
        repo / "curriculum" / "itembank" / "pilot_fractions.jsonl"
    )
    bank = load_item_bank(itembank_path) if itembank_path.exists() else None
    # item_source: composite (default, generator+bank) | generator | bank
    item_bank = build_item_source(cfg.get("item_source", "composite"), bank=bank)

    learner_uuid = str(uuid.uuid4())
    store = LearnerStore(args.db or str(repo / "mentar_pilot.db"))
    db_id = store.create_learner(
        name=f"cli-{learner_uuid[:8]}",
        year_level="pilot",
        country="GB",
        age_mode="parent_mediated",  # SPEC §6.2 pilot default
    )

    ctrl = SessionController(
        llm_call=llm_call,
        prompt_dir=prompt_dir,
        grounding_cfg=cfg.get("grounding", {}),
        curriculum=curriculum,
        db_store=_DbStoreAdapter(store, db_id),
        learner_id=learner_uuid,
        item_bank=item_bank,
    )
    return ctrl, cfg


def _run_session(args) -> int:
    ctrl, cfg = _build_controller(args)
    if ctrl is None:
        return 1

    print(f"mentar run-session — backend={cfg.get('backend')}  (type 'stop' to quit)\n")

    # Kick off: first step takes None.
    t0 = time.monotonic()
    result = ctrl.step(None)
    _emit(result.text)

    while not result.done:
        if result.escalated:
            print("\n[escalation freeze — handoff to parent. Session paused.]")
            break
        try:
            user_in = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        t1 = time.monotonic()
        result = ctrl.step(user_in)
        dt = time.monotonic() - t1
        _emit(result.text, latency=dt)

    print(f"\n[session ended after {time.monotonic() - t0:.1f}s — state={ctrl.state}]")
    return 0


def _emit(text: str, latency: float | None = None) -> None:
    if not text:
        return
    tag = f"mentar> " if latency is None else f"mentar> ({latency:.1f}s) "
    print(f"\n{tag}{text}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mentar")
    sub = parser.add_subparsers(dest="cmd", required=True)

    rs = sub.add_parser("run-session", help="Drive a full tutoring session (headless).")
    rs.add_argument("--config", help="Path to inference config (default: config/inference.yaml).")
    rs.add_argument("--curriculum", help="Curriculum template (default: pilot fractions.md).")
    rs.add_argument("--itembank", help="Item bank jsonl (default: curriculum/itembank/pilot_fractions.jsonl).")
    rs.add_argument("--prompt-dir", dest="prompt_dir", help="Prompts dir (default: prompts/).")
    rs.add_argument("--db", help="SQLite path (default: mentar_pilot.db).")

    sub.add_parser("serve", help="Start the pilot web app.")
    sub.add_parser("eval", help="Run the eval harness (stub).")
    vt = sub.add_parser(
        "validate-template",
        help="Validate a curriculum template against the W3.1 schema.",
    )
    vt.add_argument("path", help="Path to curriculum template Markdown file.")

    args = parser.parse_args(argv)

    if args.cmd == "run-session":
        return _run_session(args)

    if args.cmd == "serve":
        from mentar.web.app import app
        app.run(host="127.0.0.1", port=5000, debug=False)
        return 0

    if args.cmd == "validate-template":
        from mentar.tools.validate_template import validate

        result = validate(args.path)

        for w in result.warnings:
            print(f"WARNING: {w}", file=sys.stderr)

        for e in result.errors:
            print(f"ERROR: {e}", file=sys.stderr)

        if result.ok:
            n = len(result.concept_ids)
            print(
                f"OK: {args.path} — {n} concept(s); "
                f"roots={result.roots}; leaves={result.leaves}",
                file=sys.stdout,
            )
            if result.warnings:
                print(f"  {len(result.warnings)} warning(s) — see stderr.", file=sys.stdout)
        else:
            print(
                f"FAIL: {args.path} — {len(result.errors)} error(s).",
                file=sys.stdout,
            )

        return 0 if result.ok else 1

    # stubs
    print(f"mentar: '{args.cmd}' not implemented yet (stub).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
