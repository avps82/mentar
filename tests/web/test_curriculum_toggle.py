"""Tests for R10 -- in-repo curriculum on/off toggles (/settings/curricula).

Every authored pack ships in the repo and is toggled locally (no download).
Toggling writes a gitignored pack_state.json (an ALLOW-list of enabled keys since
2026-08-14; a legacy deny-list file is still honoured); the picker applies the change
on the next restart (discovery is scan-once-at-startup). Default = General packs only. Each test patches
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


def _client(enabled=None, disabled=None):
    """Fresh (app_mod, client), with an optional pre-existing state file written
    and pointed at via MENTAR_PACK_STATE BEFORE the module reloads, so it is applied
    during discovery (which is scan-once-at-startup).

    `enabled` writes the CURRENT allow-list shape; `disabled` writes the LEGACY
    deny-list shape (pre-2026-08-14 installs, still honoured). Neither = no file at
    all, i.e. the General-only default."""
    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "toggle.db")
    scratch_state = pathlib.Path(tempfile.mkdtemp()) / "pack_state.json"
    if enabled is not None:
        scratch_state.write_text(json.dumps({"enabled": list(enabled)}), encoding="utf-8")
    elif disabled is not None:
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


def test_fresh_install_enables_only_the_general_packs():
    """2026-08-14 (maintainer): "default setting is all toggles are disabled for all
    subjects and grades for each country. Only toggle enabled is the general ones" --
    so nobody has to switch off 66 packs for countries they don't live in. Every pack
    is still LISTED (that's how you turn one on)."""
    _skip_if_no_flask()
    app_mod, c, state = _client()
    listing = c.get("/settings/curricula").get_json()["curricula"]
    assert len(listing) > 60, "every pack must still be listed, on or off"
    for x in listing:
        assert x["enabled"] is (x["country"] is None), f"{x['key']} ({x['country']})"
    # ...and the picker really only loaded those, so a child can start at once.
    assert "fractions" in app_mod.SUBJECTS
    assert "au_acara_year3_maths" not in app_mod.SUBJECTS
    assert not state.exists(), "the default must not need a state file"


def test_a_country_pack_added_by_a_later_release_defaults_to_off():
    """Why the store is an allow-list, not a deny-list: with a deny-list, a pack that
    ships in a later release is absent from the file and would appear uninvited in a
    family's picker."""
    _skip_if_no_flask()
    app_mod, c, _state = _client(enabled=["fractions"])
    listing = c.get("/settings/curricula").get_json()["curricula"]
    on = [x["key"] for x in listing if x["enabled"]]
    assert on == ["fractions"], on
    assert set(app_mod.SUBJECTS) == {"fractions"}


def test_disable_writes_state_file_and_listing_reflects_it():
    _skip_if_no_flask()
    _app_mod, c, state = _client()
    r = c.post("/settings/curricula/in_generic_class3_maths/disable")
    assert r.status_code == 200
    body = r.get_json()
    # restart_required is False since 2026-08-15: a toggle re-scans the curriculum
    # live. The maintainer warned when this shipped that "restart to enable" would
    # bite, and on a packaged build -- which a parent cannot restart from a
    # terminal -- it did.
    assert body["ok"] is True and body["enabled"] is False and body["restart_required"] is False

    assert state.exists()
    assert "in_generic_class3_maths" not in json.loads(state.read_text())["enabled"]

    data = c.get("/settings/curricula").get_json()
    enabled = {x["key"]: x["enabled"] for x in data["curricula"]}
    assert enabled["in_generic_class3_maths"] is False


def test_enable_adds_to_the_enabled_set():
    _skip_if_no_flask()
    _app_mod, c, state = _client()
    # Off by default (it's a country pack); turn it on.
    r = c.post("/settings/curricula/in_generic_class3_maths/enable")
    assert r.get_json()["enabled"] is True
    assert "in_generic_class3_maths" in json.loads(state.read_text())["enabled"]


def test_a_legacy_disabled_list_is_honoured_and_migrated_on_the_next_toggle():
    """An install from before the default flipped stored the DISABLED set. Those
    choices must survive the upgrade -- everything not in that list stays on -- and
    the next toggle rewrites the file in the current allow-list shape."""
    _skip_if_no_flask()
    app_mod, c, state = _client(disabled=["in_generic_class3_maths"])
    assert "in_generic_class3_maths" not in app_mod.SUBJECTS
    assert "au_acara_year3_maths" in app_mod.SUBJECTS, "legacy install keeps its packs on"

    c.post("/settings/curricula/science/disable")
    written = json.loads(state.read_text())
    assert "disabled" not in written, "must be rewritten in the current shape"
    assert "au_acara_year3_maths" in written["enabled"]
    assert "science" not in written["enabled"]
    assert "in_generic_class3_maths" not in written["enabled"]


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
    app_mod, c, _state = _client()
    all_keys = [x["key"] for x in c.get("/settings/curricula").get_json()["curricula"]]
    app_mod2, c2, _state2 = _client(enabled=[])   # nothing turned on at all

    assert app_mod2.SUBJECTS == {}  # nothing loaded
    picker = c2.get("/").get_data(as_text=True)
    assert "No curricula are turned on" in picker
    # Settings + the toggle list still work, so the family can re-enable.
    settings = c2.get("/settings")
    assert settings.status_code == 200
    listing = c2.get("/settings/curricula").get_json()
    assert len(listing["curricula"]) == len(all_keys)  # all still listed, for re-enabling
    assert all(x["enabled"] is False for x in listing["curricula"])


def test_country_master_switch_toggles_every_pack_of_that_country_only():
    """2026-08-14: the Settings curriculum card is country TABS, each opening with a
    master switch. That switch is one server call (a country holds up to 25 packs),
    and it must move only its own country's packs."""
    _skip_if_no_flask()
    _app_mod, c0, _s0 = _client()
    all_keys = [x["key"] for x in c0.get("/settings/curricula").get_json()["curricula"]]
    _app_mod, c, state = _client(enabled=all_keys)   # start from everything on

    def by_country():
        out = {}
        for x in c.get("/settings/curricula").get_json()["curricula"]:
            out.setdefault(x["country"] or "General", []).append(x["enabled"])
        return out

    before = by_country()
    assert all(all(v) for v in before.values()), "this test starts from all-on"

    r = c.post("/settings/curricula/country/IN/disable")
    assert r.status_code == 200
    body = r.get_json()
    assert body["ok"] is True and body["enabled"] is False
    assert body["changed"] == len(before["IN"]), "every IN pack should have flipped off"
    assert body["count"] == 0, "`count` is how many remain ON, which is none"

    after = by_country()
    assert not any(after["IN"]), "every IN pack must be off"
    for country in after:
        if country != "IN":
            assert all(after[country]), f"{country} must be untouched"

    # One state-file write, and re-enabling is symmetric.
    assert set(json.loads(state.read_text())["enabled"]) == {
        x["key"] for x in c.get("/settings/curricula").get_json()["curricula"]
        if x["country"] != "IN"
    }
    # 2026-08-15: enabling a country deliberately enables NOTHING under it. The old
    # assertion here (every IN pack on) encoded the behaviour the maintainer asked to
    # remove: "the parent will turn on what they want" -- bulk-enable made the switch
    # a chore generator. What must hold is that the country is now ON and available.
    r = c.post("/settings/curricula/country/IN/enable")
    assert r.status_code == 200 and r.get_json()["enabled"] is True
    assert "IN" in c.get("/settings/curricula").get_json()["active_countries"]
    listing = c.get("/settings/curricula").get_json()["curricula"]
    assert all(not x["enabled"] for x in listing if x["country"] == "IN"), \
        "enabling a country must not switch its packs on"


def test_country_master_switch_covers_the_country_less_packs_as_general():
    """The pilot/practice packs have no country; the tabs group them as "General",
    so that name has to address them (they'd be unreachable from the UI otherwise)."""
    _skip_if_no_flask()
    _app_mod, c, _state = _client()
    r = c.post("/settings/curricula/country/General/disable")
    # `count` is now how many remain ON (0 after a disable); `changed` is how many
    # actually flipped -- the number this test cares about.
    assert r.status_code == 200 and r.get_json()["changed"] > 0
    listing = c.get("/settings/curricula").get_json()["curricula"]
    assert all(not x["enabled"] for x in listing if not x["country"])
    # The country packs are off by default -- what matters is that this call left
    # them exactly as they were and didn't reach outside its own group.
    assert all(not x["enabled"] for x in listing if x["country"])


def test_levels_are_listed_band_by_band_not_interleaved():
    """2026-08-15 browser sweep: Singapore's Settings tab rendered 21 grade
    headings for 31 rows. _grade_sort_key sorted on the NUMBER alone, so a country
    with two bands interleaved -- Secondary 1, Primary 2, Secondary 2, Primary 3 --
    and the JS emits a heading every time the grade changes, i.e. on every flip.

    Each band must be contiguous and ascending within itself."""
    _skip_if_no_flask()
    _app_mod, c, _state = _client()
    listing = c.get("/settings/curricula").get_json()["curricula"]

    for country in ("SG", "US", "IN", "AU"):
        levels = list(dict.fromkeys(
            x["year_level"] for x in listing if x["country"] == country))
        bands = ["".join(ch for ch in lvl if not ch.isdigit()).strip() for lvl in levels]
        for band in set(bands):
            idx = [i for i, b in enumerate(bands) if b == band]
            assert idx == list(range(idx[0], idx[-1] + 1)), (
                f"{country}: {band!r} levels are interleaved with another band: {levels}"
            )
            nums = [int("".join(ch for ch in levels[i] if ch.isdigit()) or 0) for i in idx]
            assert nums == sorted(nums), f"{country} {band}: out of order {levels}"


def test_country_master_switch_rejects_unknown_country_and_bad_action():
    _skip_if_no_flask()
    _app_mod, c, _state = _client()
    assert c.post("/settings/curricula/country/ZZ/disable").status_code == 404
    assert c.post("/settings/curricula/country/AU/frobnicate").status_code == 404


def test_corrupt_state_file_falls_back_to_the_general_only_default():
    """A malformed pack_state.json must never break startup. It is treated as "no
    choice made yet", i.e. the same General-only default as a fresh install -- the
    family's picks are lost until they re-toggle, but a child can still learn."""
    _skip_if_no_flask()
    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "corrupt.db")
    bad_state = pathlib.Path(tempfile.mkdtemp()) / "pack_state.json"
    bad_state.write_text("{ this is not valid json ", encoding="utf-8")
    os.environ["MENTAR_PACK_STATE"] = str(bad_state)

    import importlib

    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)  # must not raise despite the corrupt file
    assert app_mod._load_pack_state() is None
    assert "fractions" in app_mod.SUBJECTS            # General pack: still there
    assert "au_acara_year3_maths" not in app_mod.SUBJECTS


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} curriculum-toggle tests passed.")
