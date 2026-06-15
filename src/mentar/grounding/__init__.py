"""Grounding / ZIM-reader module: resolve a curriculum node's grounding block to a passage.

Primary path (pilot scope, anchor-resolution only):
    resolve_grounding(node_grounding, cfg) -> str
        node_grounding: dict with keys source, anchor, passage_hint (from curriculum YAML)
        cfg:            dict from config/inference.yaml grounding: block
        returns:        inner passage text for {{grounding_passage}}, or "" on any failure

Degradation contract (SAFETY §1.5 / SPEC §15):
    ZIM missing | anchor not found | empty passage → returns "", logs a warning, NEVER raises.
    A grounding failure must never crash a tutoring turn.

Scope: anchor-resolution only (pilot). Title-prediction / BM25 / embeddings deferred to W7.5.
Deps:  libzim (runtime, pinned). OpenZIM MCP (MIT) = reference only. No MCP server, no JSON-RPC.
Spec:  docs/design/W7_grounding_reader.md; SPEC §15 (layer-1 RAG); SAFETY §1.5 (grounding-as-data).
"""

from __future__ import annotations

import logging

from mentar.grounding.resolve import resolve_grounding_inner
from mentar.grounding.wrapper import wrap_passage

logger = logging.getLogger(__name__)

__all__ = ["resolve_grounding"]


def resolve_grounding(node_grounding: dict, cfg: dict) -> str:
    """Resolve a curriculum node's grounding block to a plain passage string.

    This is the single entry-point the dialogue controller calls.  It honours the
    degradation contract: any failure returns "" — never an exception — so a missing
    or broken ZIM never crashes a tutoring turn.

    Args:
        node_grounding: The ``grounding:`` sub-dict from a curriculum concept node,
                        with keys ``source``, ``anchor``, ``passage_hint``.
        cfg:            The ``grounding:`` section of ``config/inference.yaml``
                        (loaded by the caller; env-vars already expanded).

    Returns:
        Inner passage text ready for ``{{grounding_passage}}`` — empty string on
        any failure (degradation contract).
    """
    # Type guard: a node may lack a grounding block entirely (None / malformed).
    # Handle it before the try so the except handler can safely read .get() below.
    if not isinstance(node_grounding, dict):
        logger.warning(
            "resolve_grounding: node_grounding is not a dict (%s) — returning empty passage",
            type(node_grounding).__name__,
        )
        return ""

    try:
        raw = resolve_grounding_inner(node_grounding, cfg)
        return wrap_passage(raw, cfg)
    except Exception:
        logger.warning(
            "resolve_grounding: unexpected error for anchor=%r — returning empty passage",
            node_grounding.get("anchor", "<unknown>"),
            exc_info=True,
        )
        return ""
