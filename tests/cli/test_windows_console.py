"""The CLI must not crash on a Windows console that cannot encode its own output.

Found 2026-08-15 while making Windows a supported platform: Python uses the
console's locale encoding there (cp1252 on a default install), which has no "✓"
and no emoji. `mentar setup` therefore ended in UnicodeEncodeError while printing
its own success line -- the first command a family runs, failing for a reason that
has nothing to do with the tutor.

    python3 tests/cli/test_windows_console.py
"""

from __future__ import annotations

import io
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.cli.__main__ import _force_utf8_console  # noqa: E402

# Every non-ASCII character this CLI prints on a success path.
_CLI_GLYPHS = "✓ Ready — run:  mentar serve  ·  💡  ⚙️  🇦🇺"


def _cp1252_stdout() -> io.TextIOWrapper:
    """A stand-in for a default Windows console: cp1252, strict, reconfigurable."""
    return io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")


def test_cp1252_console_cannot_take_our_output_unaided():
    """The premise, proven rather than assumed -- otherwise the fix guards nothing."""
    stream = _cp1252_stdout()
    try:
        stream.write(_CLI_GLYPHS)
        stream.flush()
    except UnicodeEncodeError:
        return
    raise AssertionError("cp1252 accepted the glyphs, so this test proves nothing")


def test_force_utf8_console_makes_the_output_writable():
    real_out, real_err = sys.stdout, sys.stderr
    stream = _cp1252_stdout()
    sys.stdout = sys.stderr = stream
    try:
        _force_utf8_console()
        # After the fix the same write must succeed on the same stream.
        sys.stdout.write(_CLI_GLYPHS)
        sys.stdout.flush()
        assert (sys.stdout.encoding or "").lower().replace("-", "") == "utf8"
    finally:
        sys.stdout, sys.stderr = real_out, real_err


def test_force_utf8_console_is_safe_where_it_cannot_reconfigure():
    """A redirected/wrapped stream (a pipe in CI, a StringIO in a test) has no
    reconfigure() -- that must be a no-op, never an exception."""
    real_out = sys.stdout
    sys.stdout = io.StringIO()
    try:
        _force_utf8_console()          # must not raise
        sys.stdout.write(_CLI_GLYPHS)  # StringIO takes anything
    finally:
        sys.stdout = real_out


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} Windows-console tests passed.")
