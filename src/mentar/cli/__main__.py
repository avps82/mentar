"""CLI entry point. Wired in pyproject.toml [project.scripts].

Subcommands:
  setup             — Detect hardware, pick + download the best-fit vetted model, write config.
  run-session       — Drive a full tutoring session (headless) against the configured backend.
  serve             — Start the pilot web app (mentar.web.app).
  eval              — Generate (local model) + judge (Sonnet) over the eval dataset.
  validate-template — Validate a curriculum template against the W3.1 schema.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
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
    from mentar.db.store import LearnerStore
    from mentar.dialogue.controller import SessionController
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
    tag = "mentar> " if latency is None else f"mentar> ({latency:.1f}s) "
    print(f"\n{tag}{text}\n")


def _download_gguf(hf_repo: str, hf_file: str, dest_dir: Path) -> bool:
    import urllib.request
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / hf_file
    if dest.exists():
        print(f"  {hf_file} already present.")
        return True
    url = f"https://huggingface.co/{hf_repo}/resolve/main/{hf_file}?download=true"
    print(f"  downloading {hf_file} from {hf_repo} ...")
    part = dest.with_suffix(dest.suffix + ".part")
    try:
        with urllib.request.urlopen(url, timeout=300) as r, open(part, "wb") as f:
            shutil.copyfileobj(r, f)
        part.replace(dest)
        return True
    except Exception as exc:
        print(f"ERROR: download failed: {exc}", file=sys.stderr)
        return False


def _setup(args) -> int:
    from mentar.inference.autoselect import load_roster, select
    from mentar.inference.backend import write_inference_config

    repo = _repo_root()
    roster = load_roster(args.roster)
    n_ctx = args.ctx

    if args.model:
        chosen = next((m for m in roster
                       if m["id"] == args.model or m.get("ollama_tag") == args.model), None)
        if not chosen:
            print(f"ERROR: --model {args.model!r} not in roster: {[m['id'] for m in roster]}",
                  file=sys.stderr)
            return 1
        roster = [chosen]

    sel = select(roster, prefer=args.runtime, n_ctx=n_ctx)
    m = sel.model

    print("\nmentar setup")
    print(f"  {sel.reason}")
    for w in sel.warnings:
        print(f"  ! {w}")

    gen: dict = {"temperature": 0.3, "max_tokens": 512}
    if m.get("reasoning"):
        gen["extra_body"] = {"think": False}

    model_path = repo / "models" / (m["hf_file"] or "")
    if sel.runtime == "ollama":
        cfg = {"backend": "ollama",
               "ollama": {"base_url": "http://localhost:11434", "model": m["ollama_tag"]},
               "generation": gen}
        model_desc = f"ollama pull {m['ollama_tag']}"
    elif sel.runtime == "llama_app":
        # llama.app's `llama serve` exposes an OpenAI-compatible endpoint — reuse the vllm path.
        cfg = {"backend": "vllm",
               "vllm": {"base_url": "http://127.0.0.1:8081/v1", "model": m["hf_file"],
                        "api_key": "no-key"},
               "generation": gen}
        model_desc = f"download {m['hf_repo']}/{m['hf_file']} (served via `llama serve`)"
    else:  # gguf in-process
        cfg = {"backend": "llamacpp",
               "llamacpp": {"mode": "in_process", "model_path": str(model_path),
                            "n_ctx": n_ctx, "n_gpu_layers": 0},
               "generation": gen}
        model_desc = f"download {m['hf_repo']}/{m['hf_file']}"

    zim_dir = os.environ.get("MENTAR_ZIM_DIR")
    if zim_dir:
        cfg["grounding"] = {"zim_dir": zim_dir}

    cfg_path = Path(args.config) if args.config else (repo / "config" / "inference.yaml")

    if args.dry_run:
        import yaml
        print(f"\n[dry-run] would acquire: {model_desc}")
        print(f"[dry-run] would write {cfg_path}:\n")
        print(yaml.safe_dump(cfg, sort_keys=False))
        return 0

    if sel.runtime == "ollama":
        if shutil.which("ollama") is None:
            print("ERROR: Ollama not installed — get it at https://ollama.com/download, "
                  "or re-run: mentar setup --runtime gguf", file=sys.stderr)
            return 1
        print(f"\nPulling {m['ollama_tag']} (may take a while)...")
        if subprocess.run(["ollama", "pull", m["ollama_tag"]]).returncode != 0:
            print("ERROR: ollama pull failed.", file=sys.stderr)
            return 1
    else:
        if not _download_gguf(m["hf_repo"], m["hf_file"], repo / "models"):
            return 1

    write_inference_config(cfg, cfg_path)
    print(f"\n✓ Wrote {cfg_path}")
    if sel.runtime == "llama_app":
        print(f"✓ Start the model server:  llama serve -m {model_path} --port 8081")
        print("  then run:  mentar run-session")
    else:
        print("✓ Ready — run:  mentar run-session")
    return 0


def _eval(args, repo) -> int:
    """Run the generate→verify pipeline by shelling out to the eval scripts."""
    cmd = [sys.executable, str(repo / "eval" / "run_candidates.py"), "--model", args.model]
    if args.suite:
        cmd += ["--suite", args.suite]
    if args.dry_run:
        cmd += ["--dry-run"]
    print(f"[eval] generating with {args.model} ...")
    rc = subprocess.run(cmd).returncode
    if rc != 0:
        print("ERROR: candidate generation failed.", file=sys.stderr)
        return rc
    if args.dry_run:
        return 0
    cmd2 = [sys.executable, str(repo / "eval" / "judge_responses.py"), "--model", args.model]
    print("[eval] judging with Sonnet ...")
    return subprocess.run(cmd2).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mentar")
    sub = parser.add_subparsers(dest="cmd", required=True)

    su = sub.add_parser("setup", help="Detect hardware, pick + download the best-fit model, write config.")
    su.add_argument("--runtime", choices=["auto", "ollama", "llama_app", "gguf"], default="auto",
                    help="Runtime: auto = Ollama, else llama.app (`llama serve`), else in-process GGUF.")
    su.add_argument("--model", help="Override auto-selection with a roster id or ollama tag.")
    su.add_argument("--ctx", type=int, default=4096, help="Context size for fit sizing (default: 4096).")
    su.add_argument("--roster", help="Roster yaml (default: config/model_roster.yaml).")
    su.add_argument("--config", help="Output config path (default: config/inference.yaml).")
    su.add_argument("--dry-run", action="store_true", help="Show the selection + config without downloading/writing.")

    rs = sub.add_parser("run-session", help="Drive a full tutoring session (headless).")
    rs.add_argument("--config", help="Path to inference config (default: config/inference.yaml).")
    rs.add_argument("--curriculum", help="Curriculum template (default: pilot fractions.md).")
    rs.add_argument("--itembank", help="Item bank jsonl (default: curriculum/itembank/pilot_fractions.jsonl).")
    rs.add_argument("--prompt-dir", dest="prompt_dir", help="Prompts dir (default: prompts/).")
    rs.add_argument("--db", help="SQLite path (default: mentar_pilot.db).")

    sub.add_parser("serve", help="Start the pilot web app.")
    ev = sub.add_parser("eval", help="Generate (local model) + judge (Sonnet) over the eval dataset.")
    ev.add_argument("--model", required=True, help="Candidate model id (e.g. gemma4:12b).")
    ev.add_argument("--suite", default=None,
                    choices=["reexplain", "transfer", "adversarial", "sycophancy", "abstention"],
                    help="Restrict to one suite.")
    ev.add_argument("--dry-run", action="store_true", help="Show what would run; no network, skip judging.")
    vt = sub.add_parser(
        "validate-template",
        help="Validate a curriculum template against the W3.1 schema.",
    )
    vt.add_argument("path", help="Path to curriculum template Markdown file.")

    args = parser.parse_args(argv)

    if args.cmd == "setup":
        return _setup(args)

    if args.cmd == "eval":
        return _eval(args, _repo_root())

    if args.cmd == "run-session":
        return _run_session(args)

    if args.cmd == "serve":
        from mentar.web.app import app
        app.run(host="127.0.0.1", port=5000, debug=False)
        return 0

    if args.cmd == "validate-template":
        from mentar.tools.validate_template import report, validate

        return report(validate(args.path), args.path)

    # stubs
    print(f"mentar: '{args.cmd}' not implemented yet (stub).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
