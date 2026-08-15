"""Where Mentar's files live — the one place that knows, so a packaged build and a
source checkout can disagree about it safely.

Two distinct questions, and conflating them is the bug this module exists to prevent:

  bundle_root()  read-only things we SHIP  — prompts, curriculum templates, scaffolds,
                 the item bank, the model roster.
  data_dir()     writable things a FAMILY accumulates — the progress database, which
                 curriculum packs they enabled, their chosen backend.

Running from a source checkout the two are the same directory (the repo root), which
is exactly how Mentar has always behaved — so nothing moves for a developer, a test,
or anyone running from git.

Inside a PyInstaller binary they MUST differ. A frozen app unpacks itself into a
temporary directory that the OS deletes on exit; writing the child's progress database
there would silently discard every lesson the moment they close the window. Worse, it
would look like it worked. So when frozen, writable state goes to the platform's
user-data location and survives.

`MENTAR_DB_PATH` / `MENTAR_PACK_STATE` / the rest still override either way.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

__all__ = ["bundle_root", "config_path", "data_dir", "db_path", "is_frozen", "models_dir"]


def is_frozen() -> bool:
    """True when running from a PyInstaller-built binary."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def bundle_root() -> Path:
    """Root for read-only shipped assets (`prompts/`, `curriculum/`, `config/`)."""
    if is_frozen():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    # src/mentar/paths.py -> mentar -> src -> repo root
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    """Root for writable state. Same as bundle_root() from a source checkout.

    ponytail: 10 lines of stdlib instead of a platformdirs dependency. If this ever
    needs cache/config/state split per XDG properly, take the dep then.
    """
    if not is_frozen():
        return bundle_root()

    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        root = base / "Mentar"
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support" / "Mentar"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
        root = base / "mentar"

    root.mkdir(parents=True, exist_ok=True)
    return root


# ── The three writable locations, named once ─────────────────────────────────
# 2026-08-15: `mentar setup` (CLI) computed `repo/config/inference.yaml` while the
# web app and backend.py used data_dir(). From a source checkout both resolve to
# the same file, so nothing ever disagreed; in a packaged build setup would write
# the config into the throwaway bundle and `serve` would then find no config at
# all. Two places computing one path IS the bug -- so there is now one place.


def config_path() -> Path:
    """`inference.yaml` — written by setup and the backend switch, read by both."""
    return data_dir() / "config" / "inference.yaml"


def dotenv_path() -> Path:
    """`config/.env` — the credential file for a remote API backend."""
    return data_dir() / "config" / ".env"


def db_path() -> Path:
    """The learner database. A child's whole history lives here, so this one must
    never resolve inside the bundle -- see the module docstring."""
    return data_dir() / "mentar_pilot.db"


def models_dir() -> Path:
    """Downloaded GGUF models: 4-20 GB, so emphatically not the temp bundle."""
    return data_dir() / "models"
