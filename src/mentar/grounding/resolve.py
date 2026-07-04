"""Pilot resolution path: node grounding block → passage string.

Pilot scope (anchor-resolution only):
    node_grounding dict (source, anchor, passage_hint)
        → scope guard (source_map.resolve_zim)
        → cache lookup
        → fetch + extract (generic HTML-article path by default; a source in
          _SOURCE_EXTRACTORS below gets its own custom fetch/extract instead —
          B1, 2026-07-05: most Kiwix content is plain wiki articles and needs
          nothing more, but a "critical few" sources have a genuinely different
          ZIM content shape and earn a small dedicated extractor. Not a general
          plugin system — just a registry, generic by default.)
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
from collections.abc import Callable

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


# ── Per-source extraction stubs ────────────────────────────────────────────────
# Default (source not listed in _SOURCE_EXTRACTORS) = generic wiki-article path:
# fetch by external URL, extract a hint-guided section. Covers Vikidia, (Simple)
# Wikipedia, Wikibooks, and any future plain-article ZIM without new code.
#
# Add an entry here ONLY when a source's ZIM content shape genuinely differs from
# "a wiki article at a URL" — e.g. khanacademy's pages are video-embed shells (the
# real content is the subtitle transcript, fetched by internal ZIM path, not a
# URL). Keep each stub small and source-specific; this is a registry, not a
# framework — most sources should never need one.

def _extract_generic_article(reader: ZimReader, anchor: str, passage_hint: str) -> str | None:
    html_bytes = reader.get_by_url(anchor)
    if html_bytes is None:
        return None
    return reader.get_section(html_bytes, passage_hint)


def _extract_khanacademy_video(reader: ZimReader, anchor: str, passage_hint: str) -> str | None:
    # anchor is the ZIM-internal hashed entry path (KA has no recoverable external
    # URL); passage_hint is unused — the whole subtitle transcript is the passage.
    html_bytes = reader.get_by_path(anchor)
    if html_bytes is None:
        return None
    return reader.get_video_narration(html_bytes)


_SOURCE_EXTRACTORS: dict[str, Callable[[ZimReader, str, str], str | None]] = {
    "khanacademy": _extract_khanacademy_video,
}


def _extract_passage(reader: ZimReader, source: str, anchor: str, passage_hint: str) -> str | None:
    extractor = _SOURCE_EXTRACTORS.get(source, _extract_generic_article)
    return extractor(reader, anchor, passage_hint)


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

    # ── 5+6. Fetch + extract (generic wiki-article path, or a source's custom
    # extractor — see _SOURCE_EXTRACTORS above) ────────────────────────────────
    passage = _extract_passage(reader, source, anchor, passage_hint)
    if not passage or not passage.strip():
        logger.warning("resolve: empty passage for anchor=%r passage_hint=%r", anchor, passage_hint)
        return ""

    # ── 7. Cache and return ───────────────────────────────────────────────────
    grounding_cache.put(anchor, passage, cfg)
    return passage
