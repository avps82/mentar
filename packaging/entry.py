"""Entry point for the packaged single-file build.

Someone who downloads a binary has not read the README and is not going to type
flags. Double-clicking must do the obvious thing: start Mentar, open a browser,
say where it is. So this wrapper defaults to `serve` and then hands straight over
to the normal CLI — every flag (`--lan`, `--port`, `setup`, `learn`) still works
for anyone who does run it from a terminal.

Deliberately thin. The binary must not become a second, subtly-different way to
start Mentar that drifts from `python -m mentar`; it is the same code path with a
friendlier default.
"""

from __future__ import annotations

import multiprocessing
import sys
import threading
import webbrowser


def _open_browser_when_it_is_actually_up(port: int) -> None:
    """Open the browser only once the port answers.

    Opening it immediately shows the child a connection error, and first impressions
    of "it's broken" are hard to undo. Poll briefly instead; give up quietly rather
    than ever blocking startup.
    """
    import socket
    import time

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        with socket.socket() as s:
            s.settimeout(0.3)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                webbrowser.open(f"http://127.0.0.1:{port}")
                return
        time.sleep(0.25)


def _selftest() -> int:
    """Prove the bundle is complete, without starting a server or touching a model.

    A PyInstaller build fails in a nasty way: it starts perfectly, then 404s or
    500s the moment someone opens the page that needed the file nobody bundled.
    That is a bad thing to discover on a child's laptop, so CI runs this on every
    built binary and a user can run it if a download looks broken.

    Checks the assets that are easy to forget and impossible to notice missing
    until use, and actually LOADS a curriculum template and draws a question --
    file existence alone would not catch a truncated or unparseable bundle.
    """
    from mentar.paths import bundle_root, data_dir, is_frozen

    root = bundle_root()
    problems: list[str] = []

    for rel in (
        "prompts",
        "curriculum/templates",
        "curriculum/visual_scaffolds",
        "curriculum/itembank",
        "curriculum/packs.json",
        "config/model_roster.yaml",
    ):
        if not (root / rel).exists():
            problems.append(f"missing bundled asset: {rel}")

    templates = list((root / "curriculum" / "templates").rglob("*.md"))
    if len(templates) < 50:
        problems.append(f"only {len(templates)} curriculum templates bundled; expected 100+")

    try:
        from mentar.db.store import _SCHEMA_PATH

        if not _SCHEMA_PATH.exists():
            problems.append(f"missing database schema: {_SCHEMA_PATH}")
    except Exception as exc:  # noqa: BLE001 - report, never crash the selftest
        problems.append(f"database module failed to import: {exc}")

    # Import the web app: catches missing Jinja templates, missing static, and any
    # hidden import the spec forgot, all of which import-time work would surface.
    try:
        from mentar.web.app import app

        with app.test_client() as c:
            if c.get("/static/style.css").status_code != 200:
                problems.append("static assets not served (style.css missing from bundle)")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"web app failed to start: {exc}")

    # Draw one real question end to end. This is the check that would fail on a
    # bundle whose data files are present but unreadable.
    try:
        from mentar.engine.item_sources import build_registry

        registry = build_registry(root / "curriculum" / "itembank" / "pilot_fractions.jsonl")
        if not registry:
            problems.append("item-source registry is empty")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"could not build the item registry: {exc}")

    print(f"Mentar selftest — frozen={is_frozen()}")
    print(f"  bundled assets : {root}")
    print(f"  writable data  : {data_dir()}")
    print(f"  curriculum     : {len(templates)} templates")
    if problems:
        print("\nFAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nOK — this build is complete.")
    return 0


def main() -> int:
    # PyInstaller + multiprocessing on Windows: without this, a child process
    # re-executes the bundle and forks endlessly. Harmless everywhere else.
    multiprocessing.freeze_support()

    argv = sys.argv[1:]
    if argv and argv[0] == "--selftest":
        return _selftest()

    # No arguments at all == a double-click. Anything else is someone who meant it.
    if not argv:
        argv = ["serve"]

    if argv and argv[0] == "serve" and "--no-browser" not in argv:
        port = 5000
        if "--port" in argv:
            try:
                port = int(argv[argv.index("--port") + 1])
            except (IndexError, ValueError):
                pass  # let the CLI report the bad value; don't pre-empt its error
        threading.Thread(
            target=_open_browser_when_it_is_actually_up, args=(port,), daemon=True
        ).start()
    argv = [a for a in argv if a != "--no-browser"]

    from mentar.cli.__main__ import main as cli_main

    return cli_main(argv)


if __name__ == "__main__":
    sys.exit(main())
