"""`mentar serve` has two deliberately unequal modes.

Maintainer decision 2026-08-15: "we will ensure it can run in a desktop/laptop as
default... server host is going to be advanced setup and this needs to be clear."

So the default binds loopback and says so, and --lan states what it exposes at
startup rather than in a doc nobody opens. Neither mode is exercised by actually
binding a port here -- the server call is captured.

    python3 tests/cli/test_serve_modes.py
"""

from __future__ import annotations

import io
import pathlib
import sys
import types
from contextlib import redirect_stdout

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))


class _Args:
    def __init__(self, lan=False, port=5000, expose_admin=False):
        self.lan = lan
        self.port = port
        self.expose_admin = expose_admin


def _run(args, with_waitress=True):
    """Call _serve with the actual server calls captured, and return (output, calls)."""
    import mentar.cli.__main__ as cli

    calls = []
    fake_app = types.SimpleNamespace(run=lambda **kw: calls.append(("flask", kw)))
    fake_web = types.ModuleType("mentar.web.app")
    fake_web.app = fake_app
    # --lan tells the app which pages may leave this computer; capture that too,
    # so the test proves the CLI actually arms the guard rather than only printing
    # a reassuring line about it.
    fake_web.set_lan_mode = lambda enabled, expose_admin=False: calls.append(
        ("set_lan_mode", {"enabled": enabled, "expose_admin": expose_admin}))
    saved_web = sys.modules.get("mentar.web.app")
    saved_waitress = sys.modules.get("waitress")
    sys.modules["mentar.web.app"] = fake_web
    if with_waitress:
        fake = types.ModuleType("waitress")
        fake.serve = lambda app, **kw: calls.append(("waitress", kw))
        sys.modules["waitress"] = fake
    else:
        sys.modules.pop("waitress", None)
        sys.modules["waitress"] = None      # import raises ImportError
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            code = cli._serve(args)
    finally:
        for name, saved in (("mentar.web.app", saved_web), ("waitress", saved_waitress)):
            if saved is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = saved
    return code, buf.getvalue(), calls


def test_default_serves_only_this_computer():
    code, out, calls = _run(_Args())
    assert code == 0
    assert calls == [("flask", {"host": "127.0.0.1", "port": 5000, "debug": False})], calls
    assert "127.0.0.1:5000" in out
    assert "Only THIS computer" in out
    # and it points at the advanced path without doing it
    assert "--lan" in out


def test_lan_mode_states_what_it_exposes_before_serving():
    code, out, calls = _run(_Args(lan=True))
    assert code == 0
    armed = [c for c in calls if c[0] == "set_lan_mode"]
    assert armed == [("set_lan_mode", {"enabled": True, "expose_admin": False})], calls
    served = [c for c in calls if c[0] == "waitress"]
    assert served and served[0][1]["host"] == "0.0.0.0", calls
    # What a parent has to know, in the output rather than in a doc: it is still
    # local, and the grown-up pages did NOT go to the network (2026-08-15 — the
    # guard means the honest message changed from "beware" to "these stay here").
    assert "entirely local" in out.lower(), out
    assert "PARENT VIEW" in out and "stay on" in out, out
    assert "--expose-admin" in out, "the opt-out must be discoverable"


def test_expose_admin_says_plainly_what_it_gives_away():
    """Opting out of the boundary has to be blunter than opting in, not quieter."""
    code, out, calls = _run(_Args(lan=True, expose_admin=True))
    assert code == 0
    assert ("set_lan_mode", {"enabled": True, "expose_admin": True}) in calls, calls
    low = out.lower()
    assert "no password" in low, out
    assert "transcripts" in low, out
    assert "parent view" in low, out


def test_lan_mode_fails_clearly_without_a_real_server():
    """Flask's own server must never be the thing exposed to a network, so a
    missing waitress is an error with an install line -- not a silent fallback."""
    code, out, calls = _run(_Args(lan=True), with_waitress=False)
    assert code == 1
    assert not calls, "nothing may be served without a production server"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} serve-mode tests passed.")
