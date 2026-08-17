"""The three OKF bundles conform to the version they declare.

`docs/`, `curriculum/templates/` and `curriculum/visual_scaffolds/` are Open
Knowledge Format bundles (GoogleCloudPlatform/knowledge-catalog). They were
written against v0.1 and moved to v0.2 on 2026-08-18.

AGENTS.md says to re-derive any conformance claim from the spec text rather than
from what similar files look like — that inference was wrong once already
(DOC_AUDIT.md, 2026-07-23). This file is the executable half of that rule: the
bundles drifted a whole minor version before anyone noticed, because nothing
checked.

Deliberately OFFLINE. It asserts the repo matches the version it declares; it
does not fetch the spec. A test that reaches the network fails in a tunnel and
turns an upstream edit into a red build on an unrelated commit.

    python3 -m pytest tests/test_okf_conformance.py
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
BUNDLE_ROOTS = [
    REPO_ROOT / "docs",
    REPO_ROOT / "curriculum" / "templates",
    REPO_ROOT / "curriculum" / "visual_scaffolds",
]
RESERVED = {"index.md", "log.md"}
DECLARED_VERSION = "0.2"


def _frontmatter(text: str) -> dict | None:
    """The YAML block a document opens with, or None if it has none."""
    if not text.startswith("---"):
        return None
    parts = text.split("\n---\n", maxsplit=1)
    if len(parts) != 2:
        return None
    return yaml.safe_load(parts[0].removeprefix("---\n")) or {}


def _concept_docs():
    for root in BUNDLE_ROOTS:
        for path in sorted(root.rglob("*.md")):
            if path.name not in RESERVED:
                yield path


def test_each_bundle_root_declares_the_okf_version():
    """v0.2 §12: a bundle declares its target version via `okf_version` in the
    bundle-root index.md -- "the only place frontmatter is permitted in an
    index.md". Without it a consumer must guess, and this repo sat on v0.1 for
    two months precisely because nothing recorded which version it targeted.
    """
    for root in BUNDLE_ROOTS:
        index = root / "index.md"
        assert index.exists(), f"{root.name} has no bundle-root index.md"
        fm = _frontmatter(index.read_text(encoding="utf-8"))
        assert fm is not None, f"{index.relative_to(REPO_ROOT)} declares no okf_version"
        assert fm.get("okf_version") == DECLARED_VERSION, (
            f"{index.relative_to(REPO_ROOT)} declares {fm.get('okf_version')!r}, "
            f"expected {DECLARED_VERSION!r}"
        )
        assert set(fm) == {"okf_version"}, (
            f"{index.relative_to(REPO_ROOT)} carries more than okf_version: {sorted(fm)}"
        )


def test_nested_index_and_log_files_stay_bare():
    """The bundle-root exception is exactly that -- an exception. Every other
    reserved file is a heading plus a listing, and code relies on it: the
    template scan, the scaffold loader and web discovery all skip these by NAME,
    so a stray frontmatter block would never be parsed, just silently displayed.
    """
    offenders = []
    for root in BUNDLE_ROOTS:
        for path in sorted(root.rglob("*.md")):
            if path.name in RESERVED and path.parent != root:
                if path.read_text(encoding="utf-8").startswith("---"):
                    offenders.append(str(path.relative_to(REPO_ROOT)))
    assert not offenders, f"nested reserved files must carry no frontmatter: {offenders}"


def test_every_concept_document_declares_a_type():
    """`type` is the ONE required OKF field, unchanged from v0.1 to v0.2."""
    missing = []
    for path in _concept_docs():
        fm = _frontmatter(path.read_text(encoding="utf-8"))
        if not fm or not str(fm.get("type", "")).strip():
            missing.append(str(path.relative_to(REPO_ROOT)))
    assert not missing, f"concept documents with no `type:` field: {missing[:8]}"


def test_generated_when_present_names_an_actor():
    """v0.2 §5.2: `by` is REQUIRED inside `generated`. Existing files keep bare
    `timestamp:` on purpose -- the spec allows a consumer to fall back to it, and
    back-filling `by` across files written in many sessions would be inventing
    provenance. But any file that DOES adopt `generated` must carry the actor,
    or it is worse than the legacy field: structured and unattributed.
    """
    bad = []
    for path in _concept_docs():
        fm = _frontmatter(path.read_text(encoding="utf-8")) or {}
        gen = fm.get("generated")
        if gen is None:
            continue
        if not isinstance(gen, dict) or not str(gen.get("by", "")).strip():
            bad.append((str(path.relative_to(REPO_ROOT)), gen))
    assert not bad, f"`generated` without a `by` actor: {bad[:5]}"


@pytest.mark.parametrize("legacy", ["# Citations"])
def test_no_v0_1_citation_sections_remain(legacy):
    """v0.2 §5.1 moved provenance from a body `# Citations` heading into
    `sources:` frontmatter. This repo never used the body form; the check exists
    so re-introducing one is caught rather than silently left on v0.1."""
    offenders = [
        str(p.relative_to(REPO_ROOT))
        for p in _concept_docs()
        if any(line.strip() == legacy for line in p.read_text(encoding="utf-8").splitlines())
    ]
    assert not offenders, f"v0.1 `{legacy}` body sections -- move to `sources:`: {offenders}"
