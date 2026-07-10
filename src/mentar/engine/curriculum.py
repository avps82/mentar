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


def derive_subject_key(path: Path, meta: dict) -> str:
    """The web subject/session key for a template -- fully automatic, no
    per-template authoring step: the DIRECTORY is the namespace. A template
    directly under templates/_pilot/ (the original, pre-namespaced pilot
    content) keys off its filename alone, matching the keys already baked
    into existing session cookies ("fractions", "arithmetic", "science").
    Any OTHER directory (AU/, and any future US/, UK/, ...) auto-prefixes
    with its own lowercased name, so "AU/year3_maths.md" always becomes
    "au_year3_maths" with zero manual input -- drop a file in the right
    folder and the correct, collision-free key falls out. `subject_key:`
    front matter, if present, wins outright (verified: none of the 5
    shipped templates need it under this rule -- see
    tests/engine/test_template_catalog.py)."""
    if meta.get("subject_key"):
        return meta["subject_key"]
    path = Path(path)
    stem = path.stem
    parent = path.parent.name
    return stem if parent == "_pilot" else f"{parent.lower()}_{stem}"


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
            "concept": node.get("label", nid),
            "answer_type": verifier.get("answer_type", "free_text"),
            "checker": verifier.get("checker", "none"),
            "expected_answer": seeds[0] if seeds else "",
            "grounding": node.get("grounding", {}),
            "prerequisites": node.get("prereqs", []),
            "bkt_priors": node.get("bkt_priors"),
        }
    return curriculum
