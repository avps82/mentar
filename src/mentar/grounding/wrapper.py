"""Grounding passage wrapper: return inner text for {{grounding_passage}}.

SAFETY §1.5 / W2.3 contract (grounding-as-data):
    The <<<GROUNDING_BEGIN>>> / <<<GROUNDING_END>>> markers already live in
    ``prompts/system_prompt.md``.  This module returns the **inner text only** —
    it never double-wraps.  The prompt layer is the exclusive owner of the
    markers; this module merely enforces the length bound and ensures a clean
    return value.

Safety principle:
    The reader returns passage content **verbatim as data**.  This module does
    NOT strip, filter, or interpret the passage — it only length-bounds it.
    Prompt injection resistance is handled by the system prompt's marker framing
    (SAFETY §1.5).  Stripping "suspicious" strings here would be a security
    theatre that silently corrupts legitimate educational content.

Spec: docs/design/W7_grounding_reader.md (Safety row + wrapper.py row).
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_DEFAULT_MAX_CHARS = 1200


def wrap_passage(passage: str, cfg: dict) -> str:
    """Length-bound ``passage`` and return the inner text for ``{{grounding_passage}}``.

    Args:
        passage: Raw plain-text passage resolved by the reader (may be "").
        cfg:     The ``grounding:`` config block (for ``max_passage_chars``).

    Returns:
        The passage, truncated to ``max_passage_chars`` if needed.  Returns ""
        on empty / whitespace-only input.  Never raises.
    """
    if not passage or not passage.strip():
        return ""

    max_chars: int = int(cfg.get("max_passage_chars", _DEFAULT_MAX_CHARS))

    # Length-bound (SPEC §15 / config contract)
    if len(passage) > max_chars:
        passage = passage[:max_chars].rstrip()
        logger.debug("wrap_passage: truncated to %d chars", max_chars)

    return passage
