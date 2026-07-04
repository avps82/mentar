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
