"""Tests for R10 -- in-repo curriculum on/off toggles (/settings/curricula).

Every authored pack ships in the repo and is toggled locally (no download).
Toggling writes a gitignored pack_state.json; the picker applies the change on
the next restart (discovery is scan-once-at-startup). Each test patches
_PACK_STATE_PATH to a scratch file so the repo's own state is never touched.

    python3 tests/web/test_curriculum_toggle.py
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))


def _client(disabled=None):
    """Fresh (app_mod, client). If `disabled` is given, a state file is written
    and pointed at via MENTAR_PACK_STATE BEFORE the module reloads, so the
    disabled set is applied during discovery (which is scan-once-at-startup)."""
    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "toggle.db")
    scratch_state = pathlib.Path(tempfile.mkdtemp()) / "pack_state.json"
    if disabled is not None:
        scratch_state.write_text(json.dumps({"disabled": list(disabled)}), encoding="utf-8")
    os.environ["MENTAR_PACK_STATE"] = str(scratch_state)

    import importlib

    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)  # discovery now reads scratch_state
    app_mod._llm_call_cached = lambda messages: "stub tutor reply"
    app_mod._SETUP_GATE_BYPASS = True
    return app_mod, app_mod.app.test_client(), scratch_state


def _skip_if_no_flask():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")


def test_curricula_list_reports_all_in_repo_packs_enabled_by_default():
    _skip_if_no_flask()
    _app_mod, c, _state = _client()
    data = c.get("/settings/curricula").get_json()
    keys = {x["key"]: x["enabled"] for x in data["curricula"]}
    # The base packs + AU + India all present, all enabled by default.
    for k in ("fractions", "au_acara_year3_maths", "in_generic_class3_maths", "practice_maths"):
        assert keys.get(k) is True, f"{k} should be listed and enabled by default"


def test_disable_writes_state_file_and_listing_reflects_it():
    _skip_if_no_flask()
    _app_mod, c, state = _client()
    r = c.post("/settings/curricula/in_generic_class3_maths/disable")
    assert r.status_code == 200
    body = r.get_json()
    assert body["ok"] is True and body["enabled"] is False and body["restart_required"] is True

    assert state.exists()
    assert "in_generic_class3_maths" in json.loads(state.read_text())["disabled"]

    data = c.get("/settings/curricula").get_json()
    enabled = {x["key"]: x["enabled"] for x in data["curricula"]}
    assert enabled["in_generic_class3_maths"] is False


def test_enable_removes_from_disabled_set():
    _skip_if_no_flask()
    _app_mod, c, state = _client(disabled=["in_generic_class3_maths"])
    # Starts disabled; enable it back.
    r = c.post("/settings/curricula/in_generic_class3_maths/enable")
    assert r.get_json()["enabled"] is True
    assert "in_generic_class3_maths" not in json.loads(state.read_text())["disabled"]


def test_disabled_pack_excluded_from_subjects_after_restart():
    """The load-bearing behaviour: a disabled pack is genuinely gone from the
    picker after a restart (module reload), enabled ones remain."""
    _skip_if_no_flask()
    app_mod, _c, _state = _client(disabled=["in_generic_class3_maths", "science"])
    assert "in_generic_class3_maths" not in app_mod.SUBJECTS
    assert "science" not in app_mod.SUBJECTS
    assert "fractions" in app_mod.SUBJECTS  # unaffected


def test_toggle_rejects_unknown_key_and_bad_action():
    _skip_if_no_flask()
    _app_mod, c, _state = _client()
    assert c.post("/settings/curricula/not_a_real_key/disable").status_code == 404
    assert c.post("/settings/curricula/fractions/frobnicate").status_code == 404


def test_disabling_a_curriculum_preserves_mastery_history():
    """R10 equivalent of R8's uninstall-preserves-mastery: turning a curriculum
    off must never touch skill_state -- re-enabling brings the child's progress
    back. (Disable only writes a state file; it can't reach the DB. Proven
    explicitly rather than by inference.)"""
    _skip_if_no_flask()
    import sqlite3

    app_mod, c, _state = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")
    c.post("/answer", data={"answer": "4"})  # writes a skill_state row

    dbp = os.environ["MENTAR_DB_PATH"]
    db = sqlite3.connect(dbp)
    n_before = db.execute("SELECT count(*) FROM skill_state").fetchone()[0]
    db.close()
    assert n_before >= 1

    r = c.post("/settings/curricula/fractions/disable")
    assert r.status_code == 200

    db = sqlite3.connect(dbp)
    n_after = db.execute("SELECT count(*) FROM skill_state").fetchone()[0]
    db.close()
    assert n_after == n_before, "disabling a curriculum must never touch skill_state"


def test_all_disabled_shows_friendly_picker_message_and_settings_still_reachable():
    """'Everything toggleable' means a family CAN turn every curriculum off.
    That must be a recoverable state, not a dead end: the picker explains how
    to recover, and Settings (with the toggle list) stays reachable."""
    _skip_if_no_flask()
    # Disable every discovered pack.
    app_mod, c, _state = _client()
    all_keys = [x["key"] for x in c.get("/settings/curricula").get_json()["curricula"]]
    app_mod2, c2, _state2 = _client(disabled=all_keys)

    assert app_mod2.SUBJECTS == {}  # nothing loaded
    picker = c2.get("/").get_data(as_text=True)
    assert "No curricula are turned on" in picker
    # Settings + the toggle list still work, so the family can re-enable.
    settings = c2.get("/settings")
    assert settings.status_code == 200
    listing = c2.get("/settings/curricula").get_json()
    assert len(listing["curricula"]) == len(all_keys)  # all still listed, for re-enabling
    assert all(x["enabled"] is False for x in listing["curricula"])


def test_corrupt_state_file_defaults_to_all_enabled():
    """A malformed pack_state.json must never break startup -- default to
    all-enabled rather than crash or silently hide everything."""
    _skip_if_no_flask()
    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "corrupt.db")
    bad_state = pathlib.Path(tempfile.mkdtemp()) / "pack_state.json"
    bad_state.write_text("{ this is not valid json ", encoding="utf-8")
    os.environ["MENTAR_PACK_STATE"] = str(bad_state)

    import importlib

    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)  # must not raise despite the corrupt file
    assert app_mod._load_disabled_packs() == set()
    # And discovery still produced a full catalog (corrupt file => all enabled).
    assert "fractions" in app_mod.SUBJECTS


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} curriculum-toggle tests passed.")
