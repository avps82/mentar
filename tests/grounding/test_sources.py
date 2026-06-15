"""Tests for mentar.grounding.sources — location handling + SMB materialization.

Contract checks (W7.4 — NAS/Samba support):
    - is_smb_location: smb:// , UNC \\\\host , //host → True; local/mounted → False.
    - smb_url_to_unc:  smb:// and // forms normalise to a \\\\host\\share UNC.
    - join_location:   SMB-aware join; local join uses the filesystem.
    - materialize_zim (local): existing path returned as-is; missing → None (no raise).
    - materialize_zim (smb):   copies the share file to zim_cache_dir via a (mocked)
                               smbclient and returns the cached local path.
    - materialize_zim (smb, smbprotocol absent): returns None + warns, never raises.

These run WITHOUT a live SMB server — the SMB client is mocked via sys.modules.

Spec: docs/design/W7_grounding_reader.md (ZIM acquisition / SMB read row).

──────────────────────────────────────────────────────────────────────────────
Inline smoke runner:
    python3 tests/grounding/test_sources.py
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import io
import pathlib
import sys
import types

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

import pytest

from mentar.grounding.sources import (
    is_smb_location,
    join_location,
    materialize_zim,
    smb_url_to_unc,
)

_FAKE_ZIM = b"FAKE-ZIM-BYTES-" * 64


# ── Classification / joining ────────────────────────────────────────────────

def test_is_smb_location():
    assert is_smb_location("smb://nas/share/x.zim")
    assert is_smb_location("//nas/share/x.zim")
    assert is_smb_location(r"\\nas\share\x.zim")
    assert not is_smb_location("/data/zims/x.zim")
    assert not is_smb_location("/mnt/nas/zims/x.zim")
    assert not is_smb_location("relative/x.zim")


def test_smb_url_to_unc():
    assert smb_url_to_unc("smb://nas/share/x.zim") == r"\\nas\share\x.zim"
    assert smb_url_to_unc("//nas/share/x.zim") == r"\\nas\share\x.zim"
    assert smb_url_to_unc(r"\\nas\share\x.zim") == r"\\nas\share\x.zim"


def test_join_location_smb_and_local(tmp_path):
    assert join_location("smb://nas/share/zims", "v.zim") == "smb://nas/share/zims/v.zim"
    assert join_location(r"\\nas\share\zims", "v.zim") == r"\\nas\share\zims\v.zim"
    # local join uses the filesystem
    assert join_location(str(tmp_path), "v.zim") == str(tmp_path / "v.zim")


# ── Local materialization ───────────────────────────────────────────────────

def test_materialize_local_existing(tmp_path):
    f = tmp_path / "v.zim"
    f.write_bytes(b"hello")
    assert materialize_zim(str(f), {}) == f


def test_materialize_local_missing_returns_none(tmp_path):
    assert materialize_zim(str(tmp_path / "nope.zim"), {}) is None


# ── SMB materialization (mocked smbclient) ──────────────────────────────────

@pytest.fixture
def fake_smbclient(monkeypatch):
    """Inject a fake `smbclient` module that serves _FAKE_ZIM bytes."""
    mod = types.ModuleType("smbclient")
    mod.open_file = lambda unc, mode="rb": io.BytesIO(_FAKE_ZIM)
    mod.stat = lambda unc: types.SimpleNamespace(st_size=len(_FAKE_ZIM))
    mod.ClientConfig = lambda **kw: None
    monkeypatch.setitem(sys.modules, "smbclient", mod)
    return mod


def test_materialize_smb_copies_to_cache(tmp_path, fake_smbclient):
    cfg = {"zim_cache_dir": str(tmp_path / "cache"), "smb": {"enabled": False}}
    local = materialize_zim("smb://nas/share/vikidia.zim", cfg)
    assert local is not None
    assert local.exists()
    assert local.read_bytes() == _FAKE_ZIM
    assert local.name == "vikidia.zim"
    assert local.parent == (tmp_path / "cache")


def test_materialize_smb_reuses_cached_copy(tmp_path, fake_smbclient):
    cfg = {"zim_cache_dir": str(tmp_path / "cache"), "smb": {"enabled": False}}
    first = materialize_zim("smb://nas/share/vikidia.zim", cfg)
    second = materialize_zim("smb://nas/share/vikidia.zim", cfg)
    assert first == second
    assert second.read_bytes() == _FAKE_ZIM


def test_materialize_smb_no_smbprotocol_returns_none(tmp_path, monkeypatch):
    """smb:// requested but smbprotocol not installed → None, no raise."""
    monkeypatch.setitem(sys.modules, "smbclient", None)  # makes `import smbclient` raise ImportError
    cfg = {"zim_cache_dir": str(tmp_path / "cache")}
    assert materialize_zim("smb://nas/share/vikidia.zim", cfg) is None


# ── Inline smoke runner ─────────────────────────────────────────────────────

def _smoke():
    import tempfile

    assert is_smb_location("smb://nas/share/x.zim")
    assert not is_smb_location("/data/x.zim")
    assert smb_url_to_unc("smb://nas/share/x.zim") == r"\\nas\share\x.zim"
    assert join_location("smb://nas/share/z", "v.zim") == "smb://nas/share/z/v.zim"
    print("[smoke] classification/join OK")

    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d) / "v.zim"
        f.write_bytes(b"hello")
        assert materialize_zim(str(f), {}) == f
        assert materialize_zim(str(pathlib.Path(d) / "nope.zim"), {}) is None
    print("[smoke] local materialize OK")

    # SMB with a fake client
    mod = types.ModuleType("smbclient")
    mod.open_file = lambda unc, mode="rb": io.BytesIO(_FAKE_ZIM)
    mod.stat = lambda unc: types.SimpleNamespace(st_size=len(_FAKE_ZIM))
    mod.ClientConfig = lambda **kw: None
    sys.modules["smbclient"] = mod
    try:
        with tempfile.TemporaryDirectory() as d:
            local = materialize_zim("smb://nas/share/v.zim", {"zim_cache_dir": d})
            assert local is not None and local.read_bytes() == _FAKE_ZIM
        print("[smoke] smb materialize (mock) OK")
    finally:
        del sys.modules["smbclient"]

    # Missing smbprotocol
    sys.modules["smbclient"] = None
    try:
        with tempfile.TemporaryDirectory() as d:
            assert materialize_zim("smb://nas/share/v.zim", {"zim_cache_dir": d}) is None
        print("[smoke] smb missing-dep → None OK")
    finally:
        del sys.modules["smbclient"]

    print("[smoke] test_sources.py PASS")


if __name__ == "__main__":
    _smoke()
