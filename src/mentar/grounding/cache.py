"""Passage cache: memoize resolved passages by anchor URL.

Memoisation strategy:
    - In-memory dict (primary): ~zero cost per turn after warm; lives for the
      process lifetime.  Because ZIM files are static per build, the cache is
      deterministic and never stale within a session.
    - Optional on-disk cache (``cache.dir``): pickled dict keyed by anchor URL.
      Enabled via ``cfg.grounding.cache.enabled = true`` + ``cache.dir`` path.
      On-disk cache is best-effort: any I/O failure is logged and ignored (never
      crashes a turn — degradation contract).

Spec: docs/design/W7_grounding_reader.md (Cost row in module contract).
"""

from __future__ import annotations

import hashlib
import logging
import os
import pickle
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── In-memory store ───────────────────────────────────────────────────────────
_MEM_CACHE: dict[str, str] = {}

_DISK_CACHE_VERSION = 1


def _cache_key(anchor: str) -> str:
    """Stable, filesystem-safe cache key derived from the anchor URL."""
    return hashlib.sha256(anchor.encode()).hexdigest()


def _disk_path(cache_dir: str | Path, anchor: str) -> Path:
    key = _cache_key(anchor)
    return Path(cache_dir) / f"{key}.pkl"


# ── Public API ────────────────────────────────────────────────────────────────


def get(anchor: str, cfg: dict) -> Optional[str]:
    """Return a cached passage for ``anchor``, or ``None`` if not cached.

    Checks in-memory first, then on-disk (if enabled).

    Args:
        anchor: The anchor URL (cache key).
        cfg:    The ``grounding:`` config block.

    Returns:
        Cached passage string, or ``None``.
    """
    # 1. In-memory
    if anchor in _MEM_CACHE:
        logger.debug("cache.get: HIT (memory) anchor=%r", anchor)
        return _MEM_CACHE[anchor]

    # 2. On-disk
    cache_cfg = cfg.get("cache", {})
    if not cache_cfg.get("enabled", False):
        return None

    cache_dir = _resolve_cache_dir(cache_cfg)
    if not cache_dir:
        return None

    disk_file = _disk_path(cache_dir, anchor)
    if disk_file.exists():
        try:
            with disk_file.open("rb") as f:
                data = pickle.load(f)
            if isinstance(data, dict) and data.get("v") == _DISK_CACHE_VERSION:
                passage = data["passage"]
                _MEM_CACHE[anchor] = passage  # warm in-memory cache
                logger.debug("cache.get: HIT (disk) anchor=%r", anchor)
                return passage
        except Exception:
            logger.warning("cache.get: failed to read disk cache %s", disk_file, exc_info=True)

    return None


def put(anchor: str, passage: str, cfg: dict) -> None:
    """Store ``passage`` in the cache for ``anchor``.

    Args:
        anchor:  The anchor URL (cache key).
        passage: The resolved passage string.
        cfg:     The ``grounding:`` config block.
    """
    _MEM_CACHE[anchor] = passage

    cache_cfg = cfg.get("cache", {})
    if not cache_cfg.get("enabled", False):
        return

    cache_dir = _resolve_cache_dir(cache_cfg)
    if not cache_dir:
        return

    try:
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        disk_file = _disk_path(cache_dir, anchor)
        with disk_file.open("wb") as f:
            pickle.dump({"v": _DISK_CACHE_VERSION, "passage": passage}, f)
        logger.debug("cache.put: wrote disk cache %s", disk_file)
    except Exception:
        logger.warning("cache.put: failed to write disk cache", exc_info=True)


def clear_memory() -> None:
    """Clear the in-memory cache (useful in tests)."""
    _MEM_CACHE.clear()


def _resolve_cache_dir(cache_cfg: dict) -> Optional[str]:
    """Expand env-var substitution in cache_dir and return the resolved string."""
    raw_dir: str = cache_cfg.get("dir", "")
    if not raw_dir:
        return None
    # Expand ${VAR:-default} style references
    expanded = os.path.expandvars(raw_dir)
    return expanded if expanded else None
