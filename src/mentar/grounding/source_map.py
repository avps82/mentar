"""Source-enum → ZIM-file mapping and anchor-host scope guard.

Responsibilities:
    - Map a ``source`` enum value (vikidia | wikipedia_simple | wikibooks | …)
      to the configured ZIM file path.
    - Enforce the scope guard: a node's ``source`` must match the anchor's
      hostname AND the configured ZIM for that source.  A ``vikidia`` node must
      never resolve out of the vikidia ZIM.

Spec: docs/design/W7_grounding_reader.md (Scope guard row in module contract).
"""

from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# ── Canonical host suffixes per source ───────────────────────────────────────
# We check that the anchor hostname *ends with* the canonical suffix for the
# declared source.  This blocks cross-source roaming without coupling us to a
# single subdomain variant.
_SOURCE_HOST_SUFFIXES: dict[str, tuple[str, ...]] = {
    "vikidia": ("vikidia.org",),
    "wikipedia_simple": ("simple.wikipedia.org",),
    "wikibooks": ("wikibooks.org",),
    # parent_upload and builtin have no network anchor — guard is relaxed for them.
    "parent_upload": (),
    "builtin": (),
}


class ScopeError(ValueError):
    """Raised when a node's anchor host does not match its declared source."""


def get_zim_path(source: str, cfg: dict) -> str | None:
    """Return the configured ZIM *location* for ``source``, or ``None`` if unconfigured.

    The ``sources`` entry may be a **structured spec** (``{project, lang,
    selection?, flavour?, pin?}`` — the newest matching file in ``zim_dir`` is
    chosen automatically, latest ``YYYY-MM`` wins) or a plain **filename string**
    (used as-is). The resulting location may be a local path, a mounted-NAS path,
    or an SMB URL/UNC depending on ``zim_dir`` —
    :func:`mentar.grounding.sources.materialize_zim` turns it into a local path.

    Args:
        source: Source enum string from the curriculum node (e.g. ``"vikidia"``).
        cfg:    The ``grounding:`` config block (``zim_dir``, ``sources`` sub-dict).

    Returns:
        The joined location string if the source resolves to a file, else ``None``.
    """
    from mentar.grounding.sources import join_location, resolve_filename

    zim_dir = cfg.get("zim_dir", "") or "."
    spec = (cfg.get("sources") or {}).get(source)
    if not spec:
        logger.debug("get_zim_path: source %r not in config.grounding.sources", source)
        return None
    filename = resolve_filename(spec, zim_dir, cfg)
    if not filename:
        logger.warning("get_zim_path: no ZIM file resolved for source %r in %r", source, zim_dir)
        return None
    return join_location(zim_dir, filename)


def check_scope(source: str, anchor: str) -> None:
    """Verify that ``anchor``'s hostname matches ``source``'s expected host(s).

    Args:
        source: Declared source enum (e.g. ``"vikidia"``).
        anchor: The anchor URL from the curriculum node.

    Raises:
        ScopeError: If the anchor host does not match the expected source hosts.
    """
    suffixes = _SOURCE_HOST_SUFFIXES.get(source)
    if suffixes is None:
        # Unknown source — reject for safety
        raise ScopeError(
            f"Unknown source {source!r}; expected one of {sorted(_SOURCE_HOST_SUFFIXES)}"
        )
    if not suffixes:
        # Sources without a network anchor (parent_upload, builtin) — no URL check needed
        return

    parsed = urlparse(anchor)
    host = parsed.netloc.lower()
    if not any(host == s or host.endswith("." + s) for s in suffixes):
        raise ScopeError(
            f"Scope violation: source={source!r} but anchor host={host!r} "
            f"(expected host matching {suffixes})"
        )


def resolve_zim(source: str, anchor: str, cfg: dict) -> str | None:
    """Validate scope and return the ZIM *location* for ``source``.

    Combines :func:`check_scope` and :func:`get_zim_path`.  Returns ``None``
    (with a logged warning) instead of raising on scope errors so callers can
    apply the degradation contract; the ScopeError is logged but swallowed here.

    Args:
        source: Source enum string.
        anchor: Full wiki URL from the curriculum node.
        cfg:    Grounding config block.

    Returns:
        The ZIM location string (local / mounted / SMB), or ``None`` on scope
        error / missing config.
    """
    try:
        check_scope(source, anchor)
    except ScopeError as exc:
        logger.warning("resolve_zim: %s — returning None (degradation path)", exc)
        return None
    return get_zim_path(source, cfg)
