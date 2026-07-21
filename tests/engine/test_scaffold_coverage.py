"""Brute-force scaffold coverage — every concept node in every shipped
curriculum template must have a matching visual scaffold.

If this test fails, add keywords to an existing scaffold or create a new
scaffold file in curriculum/visual_scaffolds/<subject>/.
"""
from __future__ import annotations

import pathlib
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.visual_scaffold import _scan_scaffold_dir, load_visual_scaffold

TEMPLATES = REPO / "curriculum" / "templates"
SCAFFOLD_ROOT = REPO / "curriculum" / "visual_scaffolds"


def test_every_concept_node_has_a_scaffold():
    _scan_scaffold_dir.cache_clear()
    missing = []
    for tmpl in sorted(TEMPLATES.glob("**/*.md")):
        if tmpl.name in ("index.md", "log.md"):
            continue
        text = tmpl.read_text(encoding="utf-8")
        parts = text.split("\n---\n", 1)
        raw = yaml.safe_load(parts[0].removeprefix("---\n")) or {}
        subject = raw.get("subject", "")
        tid = raw.get("template_id", tmpl.stem)
        for node in raw.get("concepts", []):
            label = node.get("label", "")
            if not load_visual_scaffold(SCAFFOLD_ROOT, subject, label):
                missing.append(f"[{tid}] {label!r} ({subject})")
    assert not missing, (
        "These concept nodes have no matching visual scaffold "
        f"(add keywords or a new file under curriculum/visual_scaffolds/):\n"
        + "\n".join(f"  {m}" for m in missing)
    )
