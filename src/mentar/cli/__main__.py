"""CLI entry point. Wired in pyproject.toml [project.scripts].

Subcommands:
  setup             — Detect hardware, pick + download the best-fit vetted model, write config.
  run-session       — Drive a full tutoring session (headless) against the configured backend.
  serve             — Start the web app on THIS computer; --lan (advanced) also
                      serves other devices on your home network.
  eval              — Generate (local model) + judge (Sonnet) over the eval dataset.
  validate-template — Validate a curriculum template against the W3.1 schema.
  backup            — Checkpoint + copy the DB file, then verify the copy is intact.
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

from mentar.paths import bundle_root, config_path, db_path, is_frozen, models_dir


def _repo_root() -> Path:
    # Shipped assets (curriculum, prompts). Writable state goes to data_dir().
    return bundle_root()


def _build_controller(args):
    """Construct a SessionController wired to the configured inference backend.

    Reuses the same curriculum loader (engine/curriculum.py) and DB adapter
    (db/adapter.py) as the web app (A17: moved out of web/ so this headless path
    no longer has to import Flask) — CLI and web exercise the exact same turn loop.
    """
    from mentar.db.adapter import _DbStoreAdapter
    from mentar.db.store import LearnerStore
    from mentar.dialogue.controller import SessionController
    from mentar.engine.curriculum import load_curriculum, load_template_subject
    from mentar.engine.itembank import load_item_bank
    from mentar.engine.itemgen import build_item_source
    from mentar.inference import load_inference_config, make_llm_call
    from mentar.tools.validate_template import validate_or_raise

    repo = _repo_root()
    curriculum_path = Path(args.curriculum) if args.curriculum else (
        repo / "curriculum" / "templates" / "_pilot" / "fractions.md"
    )
    prompt_dir = Path(args.prompt_dir) if args.prompt_dir else (repo / "prompts")
    scaffold_dir = repo / "curriculum" / "visual_scaffolds"

    cfg = load_inference_config(args.config)  # None -> default config/inference.yaml
    if cfg is None:
        print(
            "ERROR: no inference config found. Create config/inference.yaml "
            "(copy config/inference.example.yaml) or pass --config.",
            file=sys.stderr,
        )
        return None, None

    # A16: validate before loading — a cyclic/bad-prereq template silently produces
    # an empty fringe and a false "you've mastered everything!" completion.
    try:
        validate_or_raise(curriculum_path)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return None, None

    llm_call = make_llm_call(cfg)
    curriculum = load_curriculum(curriculum_path)
    itembank_path = Path(args.itembank) if args.itembank else (
        repo / "curriculum" / "itembank" / "pilot_fractions.jsonl"
    )
    bank = load_item_bank(itembank_path) if itembank_path.exists() else None
    # item_source: composite (default, generator+bank) | generator | bank
    item_bank = build_item_source(cfg.get("item_source", "composite"), bank=bank)

    learner_uuid = str(uuid.uuid4())
    store = LearnerStore(args.db or str(db_path()))
    db_id = store.create_learner(
        name=f"cli-{learner_uuid[:8]}",
        year_level="pilot",
        country="GB",
        age_mode="parent_mediated",  # SPEC §6.2 pilot default
    )
    # A19: pilot scope is parent_mediated only — a clear error, not a silent
    # unsupervised session, if a learner row is ever anything else.
    store.assert_parent_mediated(db_id)

    ctrl = SessionController(
        llm_call=llm_call,
        prompt_dir=prompt_dir,
        scaffold_dir=scaffold_dir,
        grounding_cfg=cfg.get("grounding", {}),
        curriculum=curriculum,
        db_store=_DbStoreAdapter(store, db_id),
        learner_id=learner_uuid,
        item_bank=item_bank,
        subject=load_template_subject(curriculum_path),
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


def _ensure_llama_cpp() -> bool:
    """Ensure llama-cpp-python (the in-process GGUF runtime) is importable,
    installing it on demand. Returns True if available afterwards.

    The GGUF in-process runtime needs this compiled package; without it the
    config writes fine but every model call fails at runtime.
    """
    try:
        import llama_cpp  # noqa: F401
        return True
    except ImportError:
        pass
    if is_frozen():
        # sys.executable is THIS BINARY, not a Python interpreter, so `-m pip` would
        # just re-enter the CLI and fail with an argparse error. There is no
        # interpreter to install a compiled package into, so the in-process GGUF
        # runtime is genuinely unavailable in a packaged build. Say that, and point
        # at the two runtimes that need no Python at all.
        print("\nThis download of Mentar cannot use the built-in GGUF runtime:", file=sys.stderr)
        print("  it needs llama-cpp-python, a compiled Python package, and this", file=sys.stderr)
        print("  build has no Python to install it into.", file=sys.stderr)
        print("\nUse either of these instead — both are ordinary apps, no Python needed:",
              file=sys.stderr)
        print("  * Ollama    https://ollama.com/download   (easiest)", file=sys.stderr)
        print("  * llama.app https://llama.app", file=sys.stderr)
        print("\nInstall one, then run setup again.", file=sys.stderr)
        return False
    print("\nInstalling llama-cpp-python (in-process GGUF runtime) — may take a few minutes...")
    rc = subprocess.run(
        [sys.executable, "-m", "pip", "install", "llama-cpp-python"]
    ).returncode
    if rc == 0:
        try:
            import llama_cpp  # noqa: F401
            return True
        except ImportError:
            pass
    print("ERROR: could not install llama-cpp-python.", file=sys.stderr)
    print("  Install it manually:  pip install llama-cpp-python", file=sys.stderr)
    print("  Or use Ollama instead (no build):  https://ollama.com/download  then  mentar setup",
          file=sys.stderr)
    return False


def _diagnose_hint() -> str:
    """How to investigate a backend that will not answer.

    A packaged build has no `scripts/` directory and no `python3`, so the advice
    that is right for a source checkout is useless -- and worse, it reads as
    "you did something wrong" to someone who has no way to run it.
    """
    if is_frozen():
        return "  Check the model app (Ollama etc.) is running, then run setup again."
    return "  Diagnose:  python3 scripts/check_backend.py"


def _verify_backend(cfg: dict) -> tuple[bool, str]:
    """Best-effort live check that the configured backend actually answers."""
    from mentar.inference import make_llm_call
    probe = dict(cfg)
    gen = dict(cfg.get("generation", {}))
    gen["max_tokens"] = 16
    probe["generation"] = gen
    try:
        call = make_llm_call(probe)
        out = call([{"role": "user", "content": "Reply with the single word: ping"}])
    except Exception as e:  # noqa: BLE001 — report any backend failure plainly
        return False, f"{type(e).__name__}: {e}"
    if out and out.strip():
        return True, f"model replied {out.strip()[:40]!r}"
    return False, "empty reply (reasoning model? set generation.extra_body.think=false)"


def _setup_remote_api(args, repo: Path) -> int:
    """--runtime vllm: a remote OpenAI-compatible API (LiteLLM/vLLM proxy) --
    no roster/download involved, just write what the caller already knows.
    The CLI counterpart to the web /setup page (R9); same
    write_inference_config()/upsert_dotenv_value() a family would otherwise
    only reach through a browser, useful for a scripted/headless install."""
    from mentar.inference.backend import upsert_dotenv_value, write_inference_config

    if not args.base_url or not args.model:
        print("ERROR: --runtime vllm requires --base-url and --model", file=sys.stderr)
        return 1

    cfg_path = Path(args.config) if args.config else config_path()
    cfg: dict = {
        "backend": "vllm",
        "vllm": {"base_url": args.base_url, "model": args.model,
                 "api_key": "${MENTAR_VLLM_API_KEY}" if args.api_key else "no-key"},
        "generation": {"temperature": 0.3, "max_tokens": 512},
    }

    print("\nmentar setup (remote API)")
    print(f"  backend=vllm base_url={args.base_url} model={args.model}")

    if args.dry_run:
        # Dry-run writes NOTHING to disk -- not the yaml, not the .env either.
        import yaml
        print(f"\n[dry-run] would write {cfg_path}:\n")
        print(yaml.safe_dump(cfg, sort_keys=False))
        return 0

    if args.api_key:
        try:
            upsert_dotenv_value(cfg_path.parent / ".env", "MENTAR_VLLM_API_KEY", args.api_key)
        except ValueError as exc:
            # Nothing written yet -- fail before write_inference_config, so a
            # rejected key never leaves a half-configured install behind.
            print(f"✗ {exc}", file=sys.stderr)
            return 1
    write_inference_config(cfg, cfg_path)
    print(f"\n✓ Wrote {cfg_path}")

    print("\nVerifying the backend responds (the first call may load the model)...")
    ok, msg = _verify_backend(cfg)
    if not ok:
        print(f"✗ Backend did not respond: {msg}", file=sys.stderr)
        print(_diagnose_hint(), file=sys.stderr)
        return 1
    print(f"✓ Backend LIVE — {msg}")
    print("✓ Ready — run:  mentar serve   (web)   or   mentar run-session   (terminal)")
    return 0


def _setup(args) -> int:
    repo = _repo_root()
    if args.runtime == "vllm":
        return _setup_remote_api(args, repo)

    from mentar.inference.autoselect import load_roster, select
    from mentar.inference.backend import write_inference_config

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

    # .get, not [] -- this line runs for EVERY runtime but only the gguf and
    # llama_app branches use it, and four of six roster models are ollama-only
    # with no hf_file at all. `mentar setup --runtime auto` on a Mac with Ollama
    # installed picks one of those and died here with KeyError: 'hf_file'
    # (2026-08-25, maintainer's first run). The `or ""` shows the author expected
    # an EMPTY value; the key can be absent entirely. The gguf/llama_app branches
    # are safe either way: autoselect.py only offers those runtimes models that
    # have a GGUF, so this is never empty when it is actually used.
    model_path = models_dir() / (m.get("hf_file") or "")
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
        # Write the FULL grounding block. A config with only `zim_dir` (no `sources`)
        # resolves every passage to "" silently — so emit the pilot sources too.
        cfg["grounding"] = {
            "zim_dir": zim_dir,
            "sources": {
                "vikidia": {
                    "project": "vikidia",
                    "lang": "en",
                    "selection": "all",
                    "flavour": "nopic",
                },
                "wikipedia_simple": {
                    "project": "wikipedia",
                    "lang": "en",
                    "selection": "simple_all",
                    "flavour": "nopic",
                },
            },
        }

    cfg_path = Path(args.config) if args.config else config_path()

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
        if sel.runtime == "gguf" and not _ensure_llama_cpp():
            return 1
        if not _download_gguf(m["hf_repo"], m["hf_file"], models_dir()):
            return 1

    write_inference_config(cfg, cfg_path)
    print(f"\n✓ Wrote {cfg_path}")
    if sel.runtime == "llama_app":
        # The server is started manually, so we can't verify it here.
        print(f"✓ Start the model server:  llama serve -m {model_path} --port 8081")
        print("  then run:  mentar serve")
        return 0
    # Verify the backend actually responds — never claim 'Ready' on a config that
    # can't serve (the failure this guards: config written, model unreachable).
    print("\nVerifying the backend responds (the first call may load the model)...")
    ok, msg = _verify_backend(cfg)
    if not ok:
        print(f"✗ Backend did not respond: {msg}", file=sys.stderr)
        print(_diagnose_hint(), file=sys.stderr)
        return 1
    print(f"✓ Backend LIVE — {msg}")
    print("✓ Ready — run:  mentar serve   (web)   or   mentar run-session   (terminal)")
    return 0


def _eval(args, repo) -> int:
    """Run the generate→verify pipeline by shelling out to the eval scripts."""
    if is_frozen():
        # A maintainer command, not a family one: it shells out to eval/*.py with a
        # Python interpreter. A packaged build bundles neither (sys.executable is
        # this binary), so fail with the reason rather than an argparse error from
        # re-entering ourselves.
        print("`mentar eval` is a development command and is not available in the",
              file=sys.stderr)
        print("downloadable build — it needs the source checkout and a Python",
              file=sys.stderr)
        print("interpreter. See docs/RUNNING.md.", file=sys.stderr)
        return 2
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


def _backup(args) -> int:
    """Checkpoint the WAL, copy the DB file, then verify the copy is intact.

    D6: "export = file copy" isn't safe on its own with WAL mode -- the copy
    can be mid-write. store.checkpoint() (already exists, nothing user-facing
    called it) flushes+truncates the WAL first so the copy is consistent.
    """
    import sqlite3
    from datetime import UTC, datetime

    from mentar.db.store import LearnerStore

    source_path = Path(args.db or str(db_path()))

    if not source_path.exists():
        print(f"ERROR: no database found at {source_path}", file=sys.stderr)
        return 1

    if args.dest:
        dest_path = Path(args.dest)
    else:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        dest_path = source_path.with_suffix(f"{source_path.suffix}.backup-{timestamp}")

    if dest_path.exists():
        print(f"ERROR: destination already exists: {dest_path} (refusing to overwrite)", file=sys.stderr)
        return 1

    store = LearnerStore(str(source_path))
    try:
        try:
            store.checkpoint()
        except sqlite3.Error as e:
            print(f"ERROR: failed to checkpoint {source_path}: {e}", file=sys.stderr)
            return 1
    finally:
        store.close()

    try:
        shutil.copy2(source_path, dest_path)
    except OSError as e:
        print(f"ERROR: failed to copy {source_path} -> {dest_path}: {e}", file=sys.stderr)
        return 1

    try:
        conn = sqlite3.connect(str(dest_path))
        try:
            result = conn.execute("PRAGMA integrity_check").fetchone()[0]
            if result.lower() != "ok":
                print(f"ERROR: backup integrity check failed: {result}", file=sys.stderr)
                return 1
            n_sessions = conn.execute("SELECT count(*) FROM session").fetchone()[0]
        finally:
            conn.close()
    except sqlite3.Error as e:
        print(f"ERROR: could not verify backup: {e}", file=sys.stderr)
        return 1

    print(f"Backup OK: {source_path} -> {dest_path} ({n_sessions} session row(s), integrity check passed)")
    return 0




def _force_utf8_console() -> None:
    """Make stdout/stderr able to carry the characters this CLI actually prints.

    Windows blocker, found 2026-08-15: Python uses the console's locale encoding
    there (usually cp1252), which has no "✓" and no emoji -- so `mentar setup`
    ended with UnicodeEncodeError on its own success message, on the very first
    command a family runs. Nothing to do with the tutor; the output just could not
    be written.

    errors="replace" rather than strict: an old console that cannot render a glyph
    should show a placeholder, never crash the run. No-op where stdout is already
    UTF-8 (Linux, macOS) or is not a reconfigurable stream (a pipe in a test).
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            if (getattr(stream, "encoding", "") or "").lower().replace("-", "") != "utf8":
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass          # not reconfigurable (redirected/wrapped) -- leave it alone


def _lan_ip() -> str | None:
    """This machine's address on the local network, or None if it cannot be found.

    Opens a UDP socket toward a public address and reads back which local
    interface the OS would route through. No packet is ever sent, so this works
    with no internet connection -- which matters, because the whole product runs
    offline.
    """
    import socket

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.0.2.1", 9))     # RFC 5737 documentation address
            return sock.getsockname()[0]
    except OSError:
        return None


def _serve_or_explain(run, port: int, host: str) -> int:
    """Run a blocking server, turning a bind failure into a sentence.

    The likely cause by far is Mentar already running -- someone double-clicked
    twice, or closed the window without stopping it. waitress raises a bare OSError
    and prints a traceback, which tells a parent nothing and looks like a crash.
    """
    try:
        run()
    except OSError as exc:
        if getattr(exc, "errno", None) in (48, 98, 10048) or "address already in use" in str(exc).lower():
            print(f"\nMentar is already using port {port} on {host}.", file=sys.stderr)
            print("  It is probably already running -- try your browser first:", file=sys.stderr)
            print(f"      http://127.0.0.1:{port}", file=sys.stderr)
            print(f"  Or start this one on a different port:  mentar serve --port {port + 1}",
                  file=sys.stderr)
            return 1
        raise
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


def _serve(args) -> int:
    """Start the web app.

    Two modes, deliberately unequal (maintainer decision 2026-08-15: "we will
    ensure it can run on a desktop/laptop as default... server host is going to be
    advanced setup and this needs to be clear"):

    * DEFAULT -- bound to 127.0.0.1. Only this computer can reach it. This is the
      supported path for a family: one machine, one browser, nothing exposed.
    * --lan -- ADVANCED. Binds every interface so another device on the same home
      network (an iPad, say, which cannot host the model itself) can open it. Still
      entirely local -- nothing leaves your hardware, no cloud, no accounts -- but
      it is reachable by anything else on that network, INCLUDING the parent view,
      and there is no password. That is stated at startup rather than buried in a
      doc, because a parent has to be able to make that choice knowingly.
    """
    from mentar.web.app import app

    port = getattr(args, "port", 5000)
    if not getattr(args, "lan", False):
        print(f"Mentar — http://127.0.0.1:{port}")
        print("  Only THIS computer can reach it (the default, and the supported setup).")
        print("  To use a tablet on your home network:  mentar serve --lan   (advanced)")
        print("  Stop it with Ctrl-C.")
        # Flush before handing control to a server that blocks forever. stdout is
        # BLOCK-buffered whenever it is not a terminal (a log file, a service
        # manager, a launcher capturing output), so without this the banner -- and
        # the URL a parent needs -- stays in the buffer until the process exits.
        # Found in CI capturing the packaged binary's real output: the log was empty.
        sys.stdout.flush()
        # Waitress for the default path too, when it is available -- which is always
        # for `mentar[web]` and always in the packaged binary. Two reasons, and the
        # second is why this changed:
        #   1. One server, not two. The localhost and --lan paths now behave the same.
        #   2. Flask's dev server prints "WARNING: This is a development server. Do
        #      not use it in a production deployment." in bold red, immediately under
        #      our own calm banner. A parent cannot act on that and should not have to
        #      read it; werkzeug hardcodes it with no way to suppress it. Found by
        #      running the packaged binary as a parent would, not by reading the code.
        # Flask's server stays as the fallback so a bare `pip install flask` still runs.
        try:
            from waitress import serve as waitress_serve
        except ImportError:
            run = lambda: app.run(host="127.0.0.1", port=port, debug=False)  # noqa: E731
        else:
            run = lambda: waitress_serve(app, host="127.0.0.1", port=port, threads=8)  # noqa: E731
        return _serve_or_explain(run, port, "this computer")

    try:
        from waitress import serve as waitress_serve
    except ImportError:
        print("--lan needs a real web server, which is not installed.", file=sys.stderr)
        if is_frozen():
            print("  This build should already include it -- please report this.", file=sys.stderr)
        else:
            print('  pip install "mentar[web]"    (adds waitress)', file=sys.stderr)
        print("  Without it, `mentar serve` still works on this computer.", file=sys.stderr)
        return 1

    from mentar.web.app import set_lan_mode

    expose_admin = getattr(args, "expose_admin", False)
    set_lan_mode(True, expose_admin=expose_admin)

    ip = _lan_ip()
    print("Mentar — ADVANCED: serving to your home network")
    print(f"  On this computer:  http://127.0.0.1:{port}")
    if ip:
        print(f"  On a tablet etc.:  http://{ip}:{port}")
    else:
        print("  Could not detect this machine's network address -- find it in your")
        print(f"  system's network settings and use http://<that address>:{port}")
    print()
    print("  Still entirely local: no cloud, no accounts, nothing leaves your network.")
    if expose_admin:
        print("  --expose-admin: the PARENT VIEW, SETTINGS and SETUP are on the network too.")
        print("  Anything else on this Wi-Fi can read your child's progress and transcripts,")
        print("  and change the app's settings. There is no password. Only do this on a")
        print("  home network you trust completely.")
    else:
        print("  Lessons are on the network; the PARENT VIEW, SETTINGS and SETUP stay on")
        print("  THIS computer, so nothing else on the Wi-Fi can read your child's progress")
        print("  or change the app. Open those here. (`--expose-admin` lifts that.)")
    print("  Use this on a home network you trust, not on public or shared Wi-Fi.")
    if sys.platform == "win32":
        print()
        print("  Windows will ask whether to allow Python through the firewall.")
        print("  Allow it for PRIVATE networks only -- never for public ones.")
    print()
    print("  Stop it with Ctrl-C.")
    sys.stdout.flush()  # see the note in the default branch -- same reason, and here
                        # the text a parent must read to make an informed choice.
    return _serve_or_explain(
        lambda: waitress_serve(app, host="0.0.0.0", port=port, threads=8),  # noqa: S104 -- the point of --lan
        port, "your network",
    )


def main(argv: list[str] | None = None) -> int:
    _force_utf8_console()
    parser = argparse.ArgumentParser(prog="mentar")
    sub = parser.add_subparsers(dest="cmd", required=True)

    su = sub.add_parser("setup", help="Detect hardware, pick + download the best-fit model, write config.")
    su.add_argument("--runtime", choices=["auto", "ollama", "llama_app", "gguf", "vllm"], default="auto",
                    help="Runtime: auto = Ollama, else llama.app (`llama serve`), else in-process GGUF. "
                         "vllm = a remote OpenAI-compatible API (LiteLLM/vLLM proxy) -- needs --base-url "
                         "and --model, no download/roster involved.")
    su.add_argument("--model", help="Override auto-selection with a roster id or ollama tag "
                    "(or the exact remote model name, for --runtime vllm).")
    su.add_argument("--base-url", help="Remote API base URL, e.g. http://192.168.xx.xxx:4000/v1 "
                    "(--runtime vllm only).")
    su.add_argument("--api-key", help="Remote API key, if the server needs one (--runtime vllm only) -- "
                    "written to a gitignored .env next to the config, never inlined in the yaml.")
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

    sv = sub.add_parser(
        "serve",
        help="Start the web app on THIS computer (default). Add --lan for other devices.",
    )
    sv.add_argument("--lan", action="store_true",
                    help="ADVANCED: also serve to other devices on your home network "
                         "(e.g. a tablet). Read what it prints before using it.")
    sv.add_argument("--port", type=int, default=5000, help="Port (default: 5000).")
    sv.add_argument("--expose-admin", action="store_true",
                    help="With --lan: also serve the parent view, settings and setup to the "
                         "network. Off by default -- those stay on this computer.")
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

    bk = sub.add_parser("backup", help="Checkpoint + copy the DB file, then verify the copy.")
    bk.add_argument("--db", help="SQLite path (default: mentar_pilot.db).")
    bk.add_argument("--dest", help="Backup destination (default: <db>.backup-<UTC timestamp>).")

    rm = sub.add_parser(
        "recompute-mastery",
        help="Replay each learner's answer history to rebuild stored mastery (dry run by default).",
    )
    rm.add_argument("--db", help="SQLite path (default: mentar_pilot.db).")
    rm.add_argument("--apply", action="store_true",
                    help="Write the recomputed values. Without this, only prints what would change.")

    args = parser.parse_args(argv)

    if args.cmd == "setup":
        return _setup(args)

    if args.cmd == "eval":
        return _eval(args, _repo_root())

    if args.cmd == "run-session":
        return _run_session(args)

    if args.cmd == "serve":
        return _serve(args)

    if args.cmd == "validate-template":
        from mentar.tools.validate_template import report, validate

        return report(validate(args.path), args.path)

    if args.cmd == "backup":
        return _backup(args)

    if args.cmd == "recompute-mastery":
        from mentar.paths import db_path
        from mentar.tools.recompute_mastery import recompute_mastery, report

        target = args.db or str(db_path())
        try:
            changes = recompute_mastery(target, apply=args.apply)
        except FileNotFoundError:
            print(f"recompute-mastery: no database at {target} — nothing to do.")
            return 0
        return report(changes, applied=args.apply)

    # stubs
    print(f"mentar: '{args.cmd}' not implemented yet (stub).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
