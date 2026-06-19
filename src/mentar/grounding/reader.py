"""Thin owned libzim reader: open a ZIM archive and extract article text.

Responsibilities:
    - open(zim_path) → ZimReader context
    - get_by_url(anchor_url) → raw HTML bytes or None
    - get_section(html_bytes, passage_hint) → plain text, hint-guided

Design notes:
    - Uses libzim (runtime dep, pinned in pyproject.toml).  No MCP server, no JSON-RPC.
    - Search / lookup logic adapted from OpenZIM MCP (cameronrye/openzim-mcp, MIT) as
      reference; re-implemented minimally for our anchor-resolution-only pilot path.
    - Hermit-AI (AGPL) = ideas only; no code copied.
    - This module is ~100-200 lines over libzim.  It never interprets passage content —
      it returns bytes/text verbatim; the prompt layer neutralises injections (SAFETY §1.5).

Spec: docs/design/W7_grounding_reader.md; SPEC §15 (layer-1 RAG).
"""

from __future__ import annotations

import html
import logging
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

logger = logging.getLogger(__name__)

# ── HTML tag stripper ─────────────────────────────────────────────────────────
# Minimal regex-based stripper: we only need plain-text paragraphs, not a full
# DOM; a proper parser is overkill for this narrow path.
_TAG_RE = re.compile(r"<[^>]+>")
_MULTI_BLANK_RE = re.compile(r"\n{3,}")
_HEADING_RE = re.compile(
    r"<h[1-6][^>]*>(.*?)</h[1-6]>", re.IGNORECASE | re.DOTALL
)
_PARA_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
_SECTION_HEADING_RE = re.compile(
    # h2–h6 only: the article TITLE is an <h1>, so matching it would truncate the lead
    # to the pre-title chrome (no paragraphs). Section headings start at <h2>.
    r"<(?:h[2-6])[^>]*>(.*?)</(?:h[2-6])>", re.IGNORECASE | re.DOTALL
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _strip_html(raw: str) -> str:
    """Remove HTML tags and unescape entities; return plain text."""
    text = _TAG_RE.sub(" ", raw)
    text = html.unescape(text)
    # Collapse whitespace runs to single spaces, but keep paragraph breaks.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = _MULTI_BLANK_RE.sub("\n\n", text)
    return text.strip()


_NOISE_BLOCK_RE = re.compile(r"<(script|style|table)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _drop_noise(html_content: str) -> str:
    """Remove structural HTML chrome (script/style/table blocks + comments) BEFORE text
    extraction. Strips non-content markup ONLY — never removes or alters visible passage
    words (SAFETY §1.5: passage content stays verbatim; filtering is the prompt layer's job).
    """
    content = _COMMENT_RE.sub(" ", html_content)
    content = _NOISE_BLOCK_RE.sub(" ", content)
    return content


def _anchor_to_zim_path(anchor_url: str) -> str:
    """Convert a wiki anchor URL to the ZIM A-namespace path.

    Wiki URLs like ``https://en.vikidia.org/wiki/Fraction`` map to ZIM path
    ``A/Fraction``.  We strip the ``/wiki/`` prefix and keep the article slug.
    Path components are URL-decoded (spaces → underscores in ZIM convention).

    Returns e.g. ``A/Fraction`` or ``A/Unit_fraction``.
    """
    parsed = urlparse(anchor_url)
    path = unquote(parsed.path)  # "/wiki/Unit_fraction"
    # Remove leading /wiki/ or /w/ style prefix
    for prefix in ("/wiki/", "/w/"):
        if path.startswith(prefix):
            path = path[len(prefix):]
            break
    else:
        # No recognised prefix — strip leading slash
        path = path.lstrip("/")
    # ZIM stores article pages under A/ namespace (OpenZIM convention)
    return f"A/{path}" if path else ""


def _extract_lead_section(html_content: str) -> str:
    """Extract the lead (opening) paragraphs before the first heading.

    Most wiki articles begin with an untitled lead section followed by headings.
    We collect all <p> tags that appear before the first <h2>/<h3>/… heading.
    """
    # Find position of first section heading
    first_heading = _SECTION_HEADING_RE.search(html_content)
    lead_html = html_content[: first_heading.start()] if first_heading else html_content

    # Collect paragraph text
    paras = [_strip_html(m.group(1)) for m in _PARA_RE.finditer(lead_html)]
    text = "\n\n".join(p for p in paras if p.strip())
    if not text:
        # Fallback: strip all tags from lead HTML
        text = _strip_html(lead_html)
    return text


def _extract_section_by_hint(html_content: str, passage_hint: str) -> str:
    """Extract the section whose heading best matches ``passage_hint``.

    Strategy (deterministic, no model call):
    1. Split on <h2>/<h3> headings.
    2. Score each section by word overlap with the hint.
    3. Return the best-matching section's paragraph text.
    4. Fall back to lead section if nothing matches well.
    """
    # Split into (heading_text, section_html) pairs
    parts = re.split(
        r"(<h[2-6][^>]*>.*?</h[2-6]>)", html_content, flags=re.IGNORECASE | re.DOTALL
    )
    # parts alternates: [pre_first_heading, heading1, body1, heading2, body2, ...]
    sections: list[tuple[str, str]] = []
    # Lead section (before first heading)
    if parts[0].strip():
        sections.append(("", parts[0]))
    i = 1
    while i + 1 < len(parts):
        heading_html = parts[i]
        body_html = parts[i + 1] if i + 1 < len(parts) else ""
        heading_text = _strip_html(heading_html).lower()
        sections.append((heading_text, body_html))
        i += 2

    if not sections:
        return _strip_html(html_content)

    # Score by hint word overlap
    hint_words = set(re.split(r"\W+", passage_hint.lower())) - {"", "the", "a", "an", "of", "and"}

    best_score = -1
    best_body = sections[0][1]  # default to lead section

    for heading_text, body_html in sections:
        if not heading_text:
            # Lead section — check body text for hints
            body_text_lower = _strip_html(body_html).lower()
        else:
            body_text_lower = heading_text

        score = sum(1 for w in hint_words if w in body_text_lower)
        if score > best_score:
            best_score = score
            best_body = body_html

    # Extract paragraphs from the best section
    paras = [_strip_html(m.group(1)) for m in _PARA_RE.finditer(best_body)]
    text = "\n\n".join(p for p in paras if p.strip())
    if not text:
        text = _strip_html(best_body)
    # Short/empty match (e.g. a stub heading) -> fall back to the lead section.
    if len(text.strip()) < 40:
        lead = _extract_lead_section(html_content)
        if len(lead.strip()) > len(text.strip()):
            return lead
    return text


# ── Public ZimReader class ────────────────────────────────────────────────────


class ZimReader:
    """Thin owned wrapper around ``libzim.reader.Archive``.

    Usage::

        reader = ZimReader(zim_path)   # raises FileNotFoundError if path absent
        html_bytes = reader.get_by_url("https://en.vikidia.org/wiki/Fraction")
        text = reader.get_section(html_bytes, "Opening section — fraction as part")
    """

    def __init__(self, zim_path: str | Path) -> None:
        """Open the ZIM archive.

        Args:
            zim_path: Path to the ``.zim`` file.

        Raises:
            FileNotFoundError: If ``zim_path`` does not exist.
            RuntimeError: If libzim cannot open the archive.
        """
        from libzim.reader import Archive  # deferred: libzim not in test-time import

        path = Path(zim_path)
        if not path.exists():
            raise FileNotFoundError(f"ZIM file not found: {path}")
        self._archive = Archive(path)
        self._zim_path = path
        logger.debug("ZimReader: opened %s (%d entries)", path.name, self._archive.all_entry_count)

    # ── Lookup ────────────────────────────────────────────────────────────────

    def get_by_url(self, anchor_url: str) -> bytes | None:
        """Resolve a wiki anchor URL to raw HTML bytes from the ZIM archive.

        Tries:
        1. ``A/<slug>`` path (ZIM A-namespace convention).
        2. Title lookup as fallback (handles alternative capitalisations).

        Args:
            anchor_url: Full wiki URL, e.g. ``https://en.vikidia.org/wiki/Fraction``.

        Returns:
            Raw HTML bytes of the article, or ``None`` if not found.
        """
        zim_path = _anchor_to_zim_path(anchor_url)
        if not zim_path:
            logger.warning("get_by_url: could not derive ZIM path from anchor %r", anchor_url)
            return None

        slug = zim_path[2:]  # strip "A/"

        # 1. Direct path lookup. Try the A/ namespace (older ZIM convention) AND the
        # bare slug (modern libzim 3.x ZIMs store articles at the root, no A/ prefix).
        entry = self._lookup_path(zim_path) or self._lookup_path(slug)

        # 2. Title-based fallback using the slug as title (handles capitalisation variants)
        if entry is None:
            title = slug.replace("_", " ")
            entry = self._lookup_title(title)

        if entry is None:
            logger.warning(
                "get_by_url: anchor %r not found in %s (tried path=%r, %r, title=%r)",
                anchor_url, self._zim_path.name, zim_path, slug, slug.replace("_", " "),
            )
            return None

        # Follow redirects
        while entry.is_redirect:
            entry = entry.get_redirect_entry()

        item = entry.get_item()
        return bytes(item.content)

    def get_section(self, html_bytes: bytes, passage_hint: str = "") -> str:
        """Extract a plain-text passage from raw HTML bytes.

        The passage is guided by ``passage_hint`` (a human description, e.g.
        "Opening section — fraction as part of something").

        This method returns the content **verbatim** after stripping HTML tags.
        It never interprets, executes, or filters passage content — that is the
        prompt layer's responsibility (SAFETY §1.5 / W2.3).

        Args:
            html_bytes: Raw HTML bytes from :meth:`get_by_url`.
            passage_hint: Human hint describing which section to prefer.

        Returns:
            Plain-text passage (may be empty if HTML contained no text).
        """
        html_content = html_bytes.decode("utf-8", errors="replace")
        # Drop structural chrome (infobox tables, scripts, styles) so real prose surfaces.
        html_content = _drop_noise(html_content)
        if passage_hint.strip():
            return _extract_section_by_hint(html_content, passage_hint)
        return _extract_lead_section(html_content)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _lookup_path(self, zim_path: str):
        """Return an Entry by ZIM path, or None on KeyError."""
        try:
            return self._archive.get_entry_by_path(zim_path)
        except KeyError:
            return None

    def _lookup_title(self, title: str):
        """Return an Entry by title, or None on KeyError."""
        try:
            return self._archive.get_entry_by_title(title)
        except KeyError:
            return None

    def __repr__(self) -> str:
        return f"ZimReader({self._zim_path!r})"
