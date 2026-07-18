"""Curriculum template loader — parses a pilot template's YAML front matter into
the controller's curriculum dict.

Lives in engine/ (not web/) so the CLI's headless `run-session` doesn't have to
import mentar.web.app (and its hard Flask dependency) just to load a template
(A17 — layering hygiene; REVIEW §8.3).
"""

from __future__ import annotations

from pathlib import Path

import yaml


def load_template_subject(path: Path) -> str:
    """Return a template's `subject:` front-matter field (e.g. "mathematics",
    "science"), defaulting to "maths" if absent. A7: used to fill the system
    prompt's {{subject}}/{{scope_line}} slots so a science session's prompt
    doesn't hardcode "fractions"."""
    text = Path(path).read_text(encoding="utf-8")
    parts = text.split("\n---\n", maxsplit=1)
    raw = yaml.safe_load(parts[0])
    return raw.get("subject") or "maths"


def load_template_meta(path: Path) -> dict:
    """R3.1: the front-matter fields the web picker/progress catalog needs to
    render a template WITHOUT hardcoding it in web/app.py -- adding a new
    year/template becomes "drop a .md file in", not a code change. Missing
    optional keys come back as None; the caller decides fallbacks."""
    text = Path(path).read_text(encoding="utf-8")
    parts = text.split("\n---\n", maxsplit=1)
    raw = yaml.safe_load(parts[0]) or {}
    return {
        "template_id": raw.get("template_id"),
        "country": raw.get("country"),
        "year_level": raw.get("year_level"),
        "subject": raw.get("subject"),
        "label": raw.get("label"),
        "icon": raw.get("icon"),
        "description": raw.get("description"),
        "item_source": raw.get("item_source"),
        # Rarely-needed escape hatch -- derive_subject_key() below handles the
        # normal case fully automatically; a template only needs this if the
        # automatic rule genuinely collides with something.
        "subject_key": raw.get("subject_key"),
    }


def _authority_dir_name(path: Path) -> str:
    """The name of the directory directly under templates/ that owns *path*
    -- the "authority" directory (e.g. AU_ACARA, IN_GENERIC, _pilot) -- even
    if the file itself sits one or more publication-year subfolders deeper
    (templates/<AUTHORITY>/<year>/*.md; not built yet, MULTI_COUNTRY.md §2b
    reserves the shape). Walks up from the file until it finds the ancestor
    whose OWN parent is literally named "templates"; falls back to the
    immediate parent if no such ancestor exists (e.g. a path outside a real
    templates/ tree, as some unit tests construct)."""
    d = path.parent
    while d.parent.name != "templates" and d.parent != d:
        d = d.parent
    return d.name if d.parent.name == "templates" else path.parent.name


def derive_subject_key(path: Path, meta: dict) -> str:
    """The web subject/session key for a template -- fully automatic, no
    per-template authoring step: the AUTHORITY DIRECTORY is the namespace
    (R-MC: resolved via `_authority_dir_name`, not just the immediate
    parent, so a future per-year subfolder can't silently change a
    template's key and orphan its session cookies / pack_state.json
    entries). A template directly under templates/_pilot/ (the original,
    pre-namespaced pilot content) keys off its filename alone, matching the
    keys already baked into existing session cookies ("fractions",
    "arithmetic", "science"). Any OTHER authority directory (AU_ACARA/, and
    any future US/, UK/, ...) auto-prefixes with its own lowercased name, so
    "AU_ACARA/year3_maths.md" always becomes "au_acara_year3_maths" with
    zero manual input -- drop a file in the right folder and the correct,
    collision-free key falls out. `subject_key:` front matter, if present,
    wins outright (verified: none of the shipped templates need it under
    this rule -- see tests/engine/test_template_catalog.py)."""
    if meta.get("subject_key"):
        return meta["subject_key"]
    path = Path(path)
    stem = path.stem
    authority = _authority_dir_name(path)
    return stem if authority == "_pilot" else f"{authority.lower()}_{stem}"


def load_curriculum(path: Path) -> dict:
    """Convert a pilot template's YAML front matter into the controller's curriculum dict."""
    # The file is a YAML block followed by Markdown narrative (after a --- divider).
    # Extract only the first YAML document (everything before the second ---).
    text = Path(path).read_text(encoding="utf-8")
    parts = text.split("\n---\n", maxsplit=1)
    raw = yaml.safe_load(parts[0])
    curriculum = {}
    for node in raw.get("concepts", []):
        nid = node["id"]
        verifier = node.get("verifier", {})
        seeds = node.get("transfer_seeds", [])
        curriculum[nid] = {
            # R6.2: key matches the YAML source field name (was "concept",
            # a naming mismatch). skill_id is a machine key, never shown to
            # a human; every human-facing surface renders display_name,
            # sourced once here, never re-derived in a template.
            "label": node.get("label", nid),
            "answer_type": verifier.get("answer_type", "free_text"),
            "checker": verifier.get("checker", "none"),
            "expected_answer": seeds[0] if seeds else "",
            "grounding": node.get("grounding", {}),
            "prerequisites": node.get("prereqs", []),
            "bkt_priors": node.get("bkt_priors"),
        }
    return curriculum
