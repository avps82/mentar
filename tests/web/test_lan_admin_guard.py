"""`--lan` serves lessons to the network and keeps grown-up pages on the computer.

The maintainer's LAN mode exists so a child can use Mentar on a tablet, which
cannot host the model. That is inside "runs entirely locally" -- nothing leaves
the family's hardware. But the LAN is not the same trust boundary as the
keyboard: without this guard, anything else on the Wi-Fi could open the parent
view (a child's transcripts and mastery), settings (turn curricula off, change
the model) or setup (repoint the backend), with no password.

A boundary rather than a password: nothing to guess, share or forget.
`--expose-admin` opts out for anyone who decides the home network IS their
boundary.

    python3 tests/web/test_lan_admin_guard.py
"""

from __future__ import annotations

import os
import pathlib
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

_CHILD_PAGES = ("/", "/choose", "/learn", "/progress")
_GROWN_UP_PAGES = ("/parent", "/settings", "/setup")


def _app():
    import importlib

    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "lan.db")
    os.environ.pop("MENTAR_PACK_STATE", None)
    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)
    app_mod._llm_call_cached = lambda messages: "stub"
    app_mod._SETUP_GATE_BYPASS = True
    return app_mod


def _skip_without_flask():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")


def test_without_lan_mode_everything_is_reachable_as_before():
    """The default (this computer only) must be untouched: the guard is inert."""
    _skip_without_flask()
    app_mod = _app()
    client = app_mod.app.test_client()
    for path in _CHILD_PAGES + _GROWN_UP_PAGES:
        assert client.get(path).status_code != 403, path


def test_lan_mode_blocks_grown_up_pages_from_another_device():
    _skip_without_flask()
    app_mod = _app()
    app_mod.set_lan_mode(True)
    client = app_mod.app.test_client()

    for path in _GROWN_UP_PAGES:
        r = client.get(path, environ_overrides={"REMOTE_ADDR": "192.168.1.55"})
        assert r.status_code == 403, f"{path} was reachable from the network"
        assert b"stays on the computer running Mentar" in r.data, path

    # ...and the child's own pages still work from that same device.
    for path in _CHILD_PAGES:
        r = client.get(path, environ_overrides={"REMOTE_ADDR": "192.168.1.55"})
        assert r.status_code != 403, f"{path} must stay available to the child"


def test_lan_mode_still_allows_the_computer_itself():
    """The parent opens those pages on the machine running Mentar -- that is the
    whole design, so loopback must be unaffected."""
    _skip_without_flask()
    app_mod = _app()
    app_mod.set_lan_mode(True)
    client = app_mod.app.test_client()
    for addr in ("127.0.0.1", "::1"):
        for path in _GROWN_UP_PAGES:
            r = client.get(path, environ_overrides={"REMOTE_ADDR": addr})
            assert r.status_code != 403, (path, addr)


def test_expose_admin_lifts_the_restriction_deliberately():
    _skip_without_flask()
    app_mod = _app()
    app_mod.set_lan_mode(True, expose_admin=True)
    client = app_mod.app.test_client()
    for path in _GROWN_UP_PAGES:
        r = client.get(path, environ_overrides={"REMOTE_ADDR": "192.168.1.55"})
        assert r.status_code != 403, path


def test_the_guard_covers_sub_paths_not_just_the_landing_pages():
    """/settings/curricula/<key>/disable would otherwise let a device on the Wi-Fi
    turn a child's curriculum off without ever loading /settings."""
    _skip_without_flask()
    app_mod = _app()
    app_mod.set_lan_mode(True)
    client = app_mod.app.test_client()
    remote = {"REMOTE_ADDR": "192.168.1.55"}
    assert client.get("/settings/curricula", environ_overrides=remote).status_code == 403
    assert client.post("/settings/curricula/fractions/disable",
                       environ_overrides=remote).status_code == 403
    assert client.post("/parent/ack", environ_overrides=remote).status_code == 403


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} LAN-guard tests passed.")
