"""Pilot resolution path: node grounding block → passage string.

Pilot scope (anchor-resolution only):
    node_grounding dict (source, anchor, passage_hint)
        → scope guard (source_map.resolve_zim)
        → cache lookup
        → ZimReader.get_by_url(anchor)
        → ZimReader.get_section(html_bytes, passage_hint)
        → cache put
        → plain-text passage (or "" on any failure)

No LLM title-prediction, no BM25, no embeddings — those are deferred to W7.5.

Degradation contract (SAFETY §1.5 / SPEC §15):
    Every failure mode returns "" and logs a warning.  This function NEVER raises
    (the outer __init__.resolve_grounding has a belt-and-braces try/except too).

Spec: docs/design/W7_grounding_reader.md; SPEC §15 (layer-1 RAG).
"""

from __future__ import annotations

import logging

from mentar.grounding import cache as grounding_cache
from mentar.grounding.reader import ZimReader
from mentar.grounding.source_map import resolve_zim
from mentar.grounding.sources import materialize_zim

logger = logging.getLogger(__name__)

# Module-level ZimReader instances keyed by resolved ZIM path string.
# Avoids re-opening the same archive per turn (opening an archive is cheap but
# not free; re-using the instance is the right posture for a hot path).
_READER_POOL: dict[str, ZimReader] = {}


def _get_reader(zim_path) -> ZimReader | None:
    """Return a cached ZimReader for ``zim_path``, opening it on first use.

    Returns ``None`` (with a warning) if the ZIM file is absent or unreadable.
    """
    key = str(zim_path)
    if key in _READER_POOL:
        return _READER_POOL[key]
    try:
        reader = ZimReader(zim_path)
        _READER_POOL[key] = reader
        return reader
    except FileNotFoundError:
        logger.warning("resolve: ZIM not found at %s — returning empty passage", zim_path)
        return None
    except Exception:
        logger.warning("resolve: failed to open ZIM %s", zim_path, exc_info=True)
        return None


def clear_reader_pool() -> None:
    """Clear the ZimReader pool (useful in tests to force re-open)."""
    _READER_POOL.clear()


def resolve_grounding_inner(node_grounding: dict, cfg: dict) -> str:
    """Core resolution: node grounding block → plain-text passage or "".

    Called by ``mentar.grounding.resolve_grounding``; may raise on truly
    unexpected errors (the public API wraps this in a try/except).

    Args:
        node_grounding: Dict with ``source``, ``anchor``, ``passage_hint``.
        cfg:            The ``grounding:`` section of the runtime config.

    Returns:
        Plain-text passage string, or "" on any recoverable failure.
    """
    source: str = node_grounding.get("source", "")
    anchor: str = node_grounding.get("anchor", "")
    passage_hint: str = node_grounding.get("passage_hint", "")

    if not source or not anchor:
        logger.warning(
            "resolve: missing source or anchor in node_grounding=%r — returning empty",
            node_grounding,
        )
        return ""

    # ── 1. Scope guard + ZIM location resolution ──────────────────────────────
    zim_location = resolve_zim(source, anchor, cfg)
    if zim_location is None:
        # Logged inside resolve_zim (scope error or unconfigured source)
        return ""

    # ── 2. Cache lookup ───────────────────────────────────────────────────────
    # Before materialization, so a cache hit never triggers an SMB copy.
    cached = grounding_cache.get(anchor, cfg)
    if cached is not None:
        logger.debug("resolve: cache hit for anchor=%r", anchor)
        return cached

    # ── 3. Materialize the ZIM to a local path (copies from SMB if needed) ─────
    zim_path = materialize_zim(zim_location, cfg)
    if zim_path is None:
        # Logged inside materialize_zim (missing file / SMB failure / no smbprotocol)
        return ""

    # ── 4. Open ZIM reader ────────────────────────────────────────────────────
    reader = _get_reader(zim_path)
    if reader is None:
        return ""

    # ── 5. Fetch article HTML ─────────────────────────────────────────────────
    html_bytes = reader.get_by_url(anchor)
    if html_bytes is None:
        # Logged inside get_by_url
        return ""

    # ── 6. Extract passage ────────────────────────────────────────────────────
    passage = reader.get_section(html_bytes, passage_hint)
    if not passage or not passage.strip():
        logger.warning("resolve: empty passage for anchor=%r passage_hint=%r", anchor, passage_hint)
        return ""

    # ── 7. Cache and return ───────────────────────────────────────────────────
    grounding_cache.put(anchor, passage, cfg)
    return passage
