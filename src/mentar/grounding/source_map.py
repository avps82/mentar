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


def get_zim_path(source: str, cfg: dict) -> Path | None:
    """Return the absolute ZIM file path for ``source``, or ``None`` if unconfigured.

    Args:
        source: Source enum string from the curriculum node (e.g. ``"vikidia"``).
        cfg:    The ``grounding:`` config block (``zim_dir``, ``sources`` sub-dict).

    Returns:
        Resolved :class:`~pathlib.Path` if the source is configured, else ``None``.
    """
    zim_dir = cfg.get("zim_dir", "")
    sources_map: dict = cfg.get("sources", {})
    filename = sources_map.get(source)
    if not filename:
        logger.debug("get_zim_path: source %r not in config.grounding.sources", source)
        return None
    zim_dir_path = Path(zim_dir).expanduser() if zim_dir else Path(".")
    return zim_dir_path / filename


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


def resolve_zim(source: str, anchor: str, cfg: dict) -> Path | None:
    """Validate scope and return the ZIM path for ``source``.

    Combines :func:`check_scope` and :func:`get_zim_path`.  Returns ``None``
    (with a logged warning) instead of raising on scope errors so callers can
    apply the degradation contract; the ScopeError is logged but swallowed here.

    Args:
        source: Source enum string.
        anchor: Full wiki URL from the curriculum node.
        cfg:    Grounding config block.

    Returns:
        Resolved :class:`~pathlib.Path`, or ``None`` on scope error / missing config.
    """
    try:
        check_scope(source, anchor)
    except ScopeError as exc:
        logger.warning("resolve_zim: %s — returning None (degradation path)", exc)
        return None
    return get_zim_path(source, cfg)
