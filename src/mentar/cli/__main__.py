"""CLI entry point. Wired in pyproject.toml [project.scripts].

Subcommands:
  serve            — Start a pilot tutoring session (stub).
  eval             — Run the eval harness (stub).
  validate-template — Validate a curriculum template against the W3.1 schema.
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mentar")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("serve", help="Start a pilot tutoring session (stub).")
    sub.add_parser("eval", help="Run the eval harness (stub).")
    vt = sub.add_parser(
        "validate-template",
        help="Validate a curriculum template against the W3.1 schema.",
    )
    vt.add_argument("path", help="Path to curriculum template Markdown file.")

    args = parser.parse_args(argv)

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
