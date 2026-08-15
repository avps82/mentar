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



# ── Writers into an EMPTY data directory ─────────────────────────────────────
# 2026-08-15, reported from a real Windows machine running the packaged binary:
# completing /setup crashed with
#   FileNotFoundError: ...\AppData\Local\Mentar\config\.env
# data_dir() creates its ROOT, but nothing created the subdirectories under it.
# From a source checkout `config/` and `curriculum/` already exist in the repo, so
# every test passed and the bug could only appear in a frozen build. These tests
# recreate that condition -- an empty data directory -- rather than trusting that
# the two known writers are the only ones.

def test_dotenv_write_creates_its_directory(tmp_path):
    from mentar.inference.backend import upsert_dotenv_value

    target = tmp_path / "empty-data-dir" / "config" / ".env"
    upsert_dotenv_value(target, "MENTAR_VLLM_API_KEY", "sk-test")
    assert 'MENTAR_VLLM_API_KEY="sk-test"' in target.read_text(encoding="utf-8")


def test_inference_config_write_creates_its_directory(tmp_path):
    from mentar.inference.backend import write_inference_config

    target = tmp_path / "empty-data-dir" / "config" / "inference.yaml"
    write_inference_config({"backend": "ollama"}, target)
    assert target.exists()


def test_pack_toggle_creates_its_directory(tmp_path, monkeypatch):
    """The second instance of the same bug -- never hit, because it needs a
    curriculum toggle rather than the setup wizard."""
    import importlib

    target = tmp_path / "empty-data-dir" / "curriculum" / "pack_state.json"
    monkeypatch.setenv("MENTAR_PACK_STATE", str(target))
    import mentar.web.app as app_mod

    importlib.reload(app_mod)
    try:
        app_mod._save_enabled_packs({"AU_ACARA"})
        assert "AU_ACARA" in target.read_text(encoding="utf-8")
    finally:
        monkeypatch.undo()
        importlib.reload(app_mod)


def test_no_writable_path_resolves_inside_the_disposable_bundle(frozen, monkeypatch):
    """The class-closing check, rather than one test per known writer.

    Every path Mentar WRITES to must land outside sys._MEIPASS. A new writer that
    reaches for bundle_root() out of habit fails here instead of on a family's
    computer, where the symptom is silent data loss on exit.
    """
    import importlib

    from mentar import paths as paths_mod

    writable = {
        "config_path": paths_mod.config_path(),
        "dotenv_path": paths_mod.dotenv_path(),
        "db_path": paths_mod.db_path(),
        "models_dir": paths_mod.models_dir(),
    }

    import mentar.inference.backend as backend_mod
    importlib.reload(backend_mod)
    writable["backend inference.yaml"] = backend_mod._default_config_path()

    import mentar.web.app as app_mod
    importlib.reload(app_mod)
    writable["web DB_PATH"] = pathlib.Path(app_mod.DB_PATH)
    writable["web inference.yaml"] = app_mod._INFERENCE_CONFIG_PATH
    writable["web pack_state.json"] = app_mod._PACK_STATE_PATH

    try:
        inside = {
            name: str(path)
            for name, path in writable.items()
            if str(path).startswith(str(frozen))
        }
        assert not inside, (
            "these would be deleted when the app exits: " + repr(inside)
        )
    finally:
        importlib.reload(app_mod)
        importlib.reload(backend_mod)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
