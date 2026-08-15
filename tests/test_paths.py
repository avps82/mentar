"""`mentar.paths` — the bundled-vs-writable split (2026-08-15, single-binary work).

The failure this guards against is quiet and expensive: in a PyInstaller build,
`sys._MEIPASS` is a temp directory the OS deletes on exit, so a progress database
written there disappears when the child closes the window — and looks fine until
someone notices a week of lessons never happened.

CI never runs a frozen binary, so the frozen branch is simulated by setting the two
attributes PyInstaller sets (`sys.frozen`, `sys._MEIPASS`). That is the whole
contract `is_frozen()` reads, so simulating it exercises the real code path rather
than a parallel one.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from mentar import paths  # noqa: E402


@pytest.fixture
def frozen(tmp_path, monkeypatch):
    """Make `mentar.paths` believe it is inside a packaged binary."""
    meipass = tmp_path / "_MEI123"
    meipass.mkdir()
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(meipass), raising=False)
    monkeypatch.setattr(pathlib.Path, "home", classmethod(lambda cls: tmp_path / "home"))
    return meipass


def test_source_checkout_keeps_everything_where_it_has_always_been():
    """No behaviour change for a developer, a test, or anyone running from git."""
    assert not paths.is_frozen()
    assert paths.bundle_root() == REPO
    assert paths.data_dir() == REPO, "from source the two roots are deliberately identical"


def test_frozen_reads_assets_from_the_unpacked_bundle(frozen):
    assert paths.is_frozen()
    assert paths.bundle_root() == frozen


def test_frozen_never_writes_family_data_into_the_disposable_bundle(frozen):
    """The bug the module exists to prevent, asserted directly."""
    data = paths.data_dir()
    assert data != frozen
    assert frozen not in data.parents, f"{data} is inside the temp bundle and would be deleted"
    assert data.is_dir(), "data_dir() must create the directory it promises"


@pytest.mark.parametrize(
    "platform, env, expected_tail",
    [
        ("win32", {"LOCALAPPDATA": "C:\\Users\\kid\\AppData\\Local"}, "Mentar"),
        ("darwin", {}, "Mentar"),
        ("linux", {}, "mentar"),
    ],
)
def test_frozen_uses_the_conventional_place_on_each_platform(
    frozen, monkeypatch, platform, env, expected_tail
):
    monkeypatch.setattr(sys, "platform", platform)
    for k in ("LOCALAPPDATA", "XDG_DATA_HOME"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    assert paths.data_dir().name == expected_tail


def test_frozen_linux_honours_xdg_data_home(frozen, monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    xdg = tmp_path / "xdg"
    monkeypatch.setenv("XDG_DATA_HOME", str(xdg))
    assert paths.data_dir() == xdg / "mentar"


def test_env_overrides_still_win_in_a_packaged_build(frozen, monkeypatch, tmp_path):
    """A parent who sets MENTAR_DB_PATH (e.g. onto a NAS) must still be obeyed --
    the packaging change must not quietly capture paths the operator chose."""
    chosen = tmp_path / "somewhere" / "else.db"
    monkeypatch.setenv("MENTAR_DB_PATH", str(chosen))
    import importlib

    import mentar.web.app as app_mod

    importlib.reload(app_mod)
    try:
        assert app_mod.DB_PATH == str(chosen)
    finally:
        monkeypatch.undo()
        importlib.reload(app_mod)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
