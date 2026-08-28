"""Fail on prose-doc references to repo paths that no longer exist.

Why this exists: three separate manual staleness audits (2026-07-22, 2026-07-23,
2026-08-11) each re-found the same mechanical class of rot — a doc naming a file
that had since been renamed or moved (`curriculum/templates/AU/` after the
AU_ACARA rename, `docs/HARDWARE.md` after it became `hardware-requirements.md`,
`curriculum/packs.py` after it became `.json`). A human re-reading every doc is
the expensive way to catch that; a path either resolves or it doesn't, so this
is the cheap way.

Deliberately narrow. It checks ONE thing — does this path resolve — and says
nothing about whether a doc's *claims* are true. Stale counts, stale status
markers, and stale prose still need a human. Keeping the scope this tight is
what lets it run in CI without false positives babysitting.

Known limitation, stated so nobody reads more guarantee into a green run than
is there: this resolves paths against the LOCAL working tree, not against what
a fresh clone would contain. A doc naming a gitignored-but-locally-present file
(e.g. `graphify-out/graph.json`, untracked since 2026-08-11) passes here and
would still be absent for someone who just cloned. That is acceptable when the
prose says the file is generated — ARCHITECTURE.md's graphify row does — but it
is NOT something this check enforces. If that class ever bites, the fix is a
`git check-ignore` pass over referenced paths; it was left out deliberately
rather than shipped as a rule that may be mostly noise.

    python3 -m mentar.tools.check_doc_paths          # report + exit 1 on findings
    python3 -m mentar.tools.check_doc_paths --list   # just list, always exit 0
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

PROSE_DIRS = ("docs", "compliance", "config", "eval")

# Docs exempt from the check, with the reason. DOC_AUDIT.md is the rename
# REGISTER -- recording "X was renamed to Y" necessarily names X, which no
# longer exists. Nearly every path it holds is intentionally historical, so
# checking it would be ~100% false positives and would grow an allowlist entry
# on every audit round. Its job is to be stale, accurately.
_EXEMPT_DOCS = {"DOC_AUDIT.md"}
TOP_LEVEL = ("AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md", "README.md", "SECURITY.md")

# Directories whose contents are never a doc-reference target.
# Skipped when SCANNING for docs to check. graphify-out/ is excluded from scanning
# (generated) but its files ARE valid reference targets, so it is not in _INDEX_SKIP.
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".venv",
             "_legacy", ".ruff_cache", "htmlcov", "graphify-out"}
_INDEX_SKIP = {".git", "node_modules", "__pycache__", ".pytest_cache", ".venv",
               ".ruff_cache", "htmlcov"}

_EXT = (".py", ".md", ".yaml", ".yml", ".json", ".toml", ".txt", ".html", ".css",
        ".js", ".sql", ".sh", ".jsonl")

_BACKTICK = re.compile(r"`([^`\n]+)`")
_MDLINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+)")

# A rename record -- `old.py` -> `new.py` -- names the OLD path on purpose. The
# left side is historical by construction, so it is not a broken reference. This
# is why changelog/audit rows can record renames without tripping the check.
_RENAME_ARROW = re.compile(r"`([^`\n]+)`\s*(?:→|->|=>)\s*`")

# Paths a doc may legitimately name that are created at RUNTIME, not committed --
# an absent file here is correct, not rot. Keep this list short and justified.
# Path PREFIXES that name where a run WRITES output. TESTS.md documents these as
# result destinations; they exist only after that step runs, so absence is correct.
_RUNTIME_PREFIXES = ("reports/", "eval/scores_", "eval/responses/")

# Paths belonging to a DIFFERENT repo/tool that Mentar docs legitimately cite.
# Not Mentar files, so their absence here says nothing about Mentar.
_EXTERNAL_PREFIXES = ("local-llm-infra/", "models/", "docs/OPEN-BUGS-")

_RUNTIME_ARTIFACTS = {
    "curriculum/pack_state.json",   # written on first Settings toggle (R10)
    "config/.env",                  # operator-created, never committed
    "eval/dataset_v1.jsonl",        # git-ignored eval data
    "config/inference.yaml",        # operator-written; config/inference.example.yaml is tracked
    "config/cloud_consent.yaml",    # written by the cloud-consent step (SAFETY §4.5), gitignored
    # graphify output (docs/design/R16_release_plan.md §graphify): generated into
    # graphify-out/ by a tool run, deliberately untracked.
    "graph.json", "graph.html", "manifest.json",
    # Per-machine agent settings: gitignored, holds the eval-host endpoint/token.
    ".claude/settings.local.json",
    # Eval run outputs, written under a run directory by eval/run_candidates.py.
    "result.json", "T2.3/result.json", "T2.5/result.json",
}

# Local-only developer tooling: gitignored ON PURPOSE, because these wrap the
# maintainer's own LAN model gateway and carry its endpoint -- the same reason the
# secret hook blocks config/inference.yaml. The docs are right to describe them
# (CLAUDE.md tells an agent to use them); they are simply not this repo's files.
#
# Before 2026-08-15 this list was unnecessary, because the checker walked the working
# tree and saw the maintainer's local copies. That is precisely what made the check
# useless: it passed here and failed for anyone with a clean clone.
_LOCAL_ONLY_TOOLING = {
    "tools/llm.sh",
    "tools/ask-local.sh",
    "llm.sh",
}

# Files a doc names as explicitly NOT existing (planned/abandoned), where the doc
# itself already says so. Listed here so the checker doesn't re-flag honest prose.
_KNOWN_ABSENT = {
    "docs/research/compliance/australia.md",       # marked "TODO" in overview.md
    "tests/test_session_fsm_invariants.py",        # SESSION_FSM.md says "(it doesn't)"
    "docs/bkt_notes.md",                           # never created; W3.3_bkt.md instead
    "src/mentar/web/static/turn.js",               # historical stopgap, replaced by htmx
    # TESTS.md T-task rows name the ORIGINAL PLAN's filenames; the coverage shipped
    # under different names. TESTS.md's translation note says so explicitly, and the
    # per-row mapping is flagged there as an open verification task.
    "tests/test_escalation_e2e.py",
    "tests/test_injection.py",
    "tests/test_jailbreak_regression.py",
    "tests/test_content_blocks.py",
    "tests/test_parent_gate.py",
    "tests/test_validator.py",
    "tests/test_false_confidence.py",
    "tests/fixtures/escalation_positive.txt",  # fixtures are inline in test_escalation.py
    "tests/fixtures/escalation_negative.txt",
    "tests/test_retry_cap.py",          # same planned-vs-actual class as above
    "tests/test_mandatory_recheck.py",
    "tests/test_transfer.py",
    "tests/test_hinted_discount.py",
    "tests/test_probe_trigger.py",
    "tests/test_probe_cap.py",
    "tests/test_probe_logging.py",
    "tests/test_modality.py",
    # Pre-repo source documents the test plan was derived from -- never in this repo.
    "mentar_project_spec.md",
    "mentar_phase0_entry_plan.md",
    # Year-subfolder curriculum layout: designed in MULTI_COUNTRY.md, deliberately
    # NOT built (deferred as YAGNI) -- the doc presents it as a proposal.
    "curriculum/templates/AU_ACARA/2023/year3_maths.md",
    # Named in C2 as a script to write IF Singapore authoring proceeds; C1's licence
    # finding redirected that work to SG_GENERIC, so it was never needed.
    "scripts/fetch_sg_syllabus.sh",
    # Folded into docs/SAFETY.md long ago; SAFETY.md L17 says "(folded in)" and
    # eu-ai-act.md now explains the redirect inline.
    "safety/guardrails.md",
    "safety/age-modes.md",
    "australia.md",                     # sibling-relative form of the TODO above
    "results.jsonl",                    # NIAH's own output file, written on run
    # R16 F0 documents this path's ABSENCE as the root cause of a bug it then fixed
    # (system-grunt.md lives at tools/, outside the hash-gated prompts/ registry).
    "prompts/system-grunt.md",
    "turn.js",                          # bare form of the replaced-stopgap entry above
    # OKF reserved FILENAMES -- AGENTS.md/DOC_AUDIT.md describe the convention
    # ("index.md and log.md are reserved"), they do not claim a specific file exists.
    "log.md",
    # PHASE0_STATUS.md's own text now says this file never existed (the pre-commit
    # hook is scripts/git-hooks/pre-commit via core.hooksPath).
    ".pre-commit-config.yaml",
    # A PROPOSED one-command installer, logged as an idea (marked with the watch
    # glyph, not built). Naming it is the proposal, not a claim.
    "install.sh",
    # Historical changelog reference to a status file from an earlier working style.
    "OVERNIGHT_STATUS.md",
    # SPEC.md marks this explicitly as an INTENDED doc ("intended repo: docs/research/").
    "mentar-safety-research-findings.md",
}


def _prose_docs() -> list[Path]:
    docs: list[Path] = []
    for d in PROSE_DIRS:
        root = REPO / d
        if root.exists():
            docs += [p for p in root.rglob("*.md")
                     if not any(part in SKIP_DIRS for part in p.parts)
                     and p.name not in _EXEMPT_DOCS]
    docs += [REPO / f for f in TOP_LEVEL if (REPO / f).exists()]
    return sorted(set(docs))


def _repo_index() -> tuple[set[str], set[str]]:
    """(every repo-relative file path, every basename) — as GIT sees it.

    Tracked files only, deliberately. This used to walk the working tree, which
    made the check unable to catch the very class it exists for: a doc naming a
    gitignored-but-locally-present file passed here and failed for anyone with a
    fresh clone. On 2026-08-15 that ran CI red on every push for a day -- docs
    referencing `tools/llm.sh`, `tools/ask-local.sh` and `config/inference.yaml`,
    all present on the maintainer's disk, none of them in the repo -- while the
    same test passed locally every time. Local and CI must see the same tree or
    the local run is worthless.

    Falls back to the working tree when git is unavailable (a source tarball, a
    vendored copy), because a wrong answer there is better than a crash.
    """
    import subprocess

    rels: set[str] = set()
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "ls-files"],
            capture_output=True, text=True, timeout=30, check=True,
        ).stdout
        rels = {line for line in out.splitlines() if line}
    except Exception:
        rels = set()

    if not rels:  # not a git checkout -- degrade to the old behaviour
        for p in REPO.rglob("*"):
            if any(part in _INDEX_SKIP for part in p.parts):
                continue
            if p.is_file():
                rels.add(str(p.relative_to(REPO)))

    names = {r.rsplit("/", 1)[-1] for r in rels}
    return rels, names


def _normalise(doc: Path, ref: str) -> str | None:
    """Resolve a doc-relative reference to a repo-relative path, or None if it
    escapes the repo (which is an environment reference, not a repo claim)."""
    import os

    base = doc.parent.relative_to(REPO)
    out = os.path.normpath(os.path.join(str(base), ref))
    return None if out.startswith("..") else out.replace(os.sep, "/")


def _is_tracked_dir(ref: str, rels: set[str]) -> bool:
    """A directory reference resolves if git tracks anything inside it."""
    prefix = ref.rstrip("/") + "/"
    return any(r.startswith(prefix) for r in rels)


def _looks_like_path(s: str) -> bool:
    s = s.strip()
    if not s or s.startswith(("http://", "https://", "$", "#", "-", "//", "@", "smb://")):
        return False
    if any(c in s for c in "*?<>|\"'`{}") or " " in s:
        return False
    # absolute paths outside the repo are environment references, not repo claims
    if s.startswith(("~/", "/opt/", "/tmp/", "/usr/", "/etc/", "/root/", "/mnt/", "/data/")):
        return False
    if s.endswith("/"):
        return False
    # `module.function` / `path::symbol` is an API reference, not a file path
    if "::" in s:
        return False
    # a numeric-enumeration shorthand ("year2/5/6_maths.md") is prose, not a path
    if re.search(r"/\d+(/\d+)+", s) or re.search(r"\d/\d", s):
        return False
    # a placeholder path ("tests/test_X.py") documents a pattern, not a file
    if re.search(r"[/_]([A-Z]|N|n)\.(py|md|json|jsonl)$", s):
        return False
    return s.endswith(_EXT) or ("/" in s and "." in s.rsplit("/", 1)[-1])


def _clean(ref: str) -> str:
    ref = ref.strip()
    # strip ONLY a leading "./" -- lstrip("./") would eat the dot of ".github/..."
    while ref.startswith("./"):
        ref = ref[2:]
    ref = re.sub(r"\(\)$", "", ref)               # foo.py::bar()  (post-:: split)
    ref = re.sub(r":\d+(-\d+)?$", "", ref)        # foo.py:123
    ref = re.sub(r":[A-Za-z_][\w.]*$", "", ref)   # foo.py:some_symbol
    return ref.rstrip(".,;:")


def find_broken(verbose: bool = False) -> list[tuple[str, int, str]]:
    rels, names = _repo_index()
    findings: list[tuple[str, int, str]] = []
    for doc in _prose_docs():
        text = doc.read_text(encoding="utf-8", errors="replace")
        seen: set[str] = set()
        for lineno, line in enumerate(text.splitlines(), 1):
            renamed_from = {m.group(1).strip() for m in _RENAME_ARROW.finditer(line)}
            for m in list(_BACKTICK.finditer(line)) + list(_MDLINK.finditer(line)):
                raw = m.group(1)
                if not _looks_like_path(raw):
                    continue
                if raw.strip() in renamed_from:
                    continue  # left side of a rename arrow: historical on purpose
                ref = _clean(raw)
                if not ref or ref in seen:
                    continue
                seen.add(ref)
                # match allowlists on the full ref OR its basename -- docs freely
                # write `pack_state.json` for `curriculum/pack_state.json`
                _base = ref.rsplit("/", 1)[-1]
                _allow = _RUNTIME_ARTIFACTS | _KNOWN_ABSENT | _LOCAL_ONLY_TOOLING
                if ref in _allow or _base in {a.rsplit("/", 1)[-1] for a in _allow}:
                    continue
                if ref.startswith(_RUNTIME_PREFIXES) or ref.startswith(_EXTERNAL_PREFIXES):
                    continue
                # a bare extension fragment (".md") is parsing debris, not a path
                if ref.startswith(".") and "/" not in ref and ref.count(".") == 1:
                    continue
                # `module.function` reads like a path but its tail is not a file ext
                if "/" in ref and not ref.endswith(_EXT):
                    continue
                # TESTS.md names test files flat by its own documented translation
                # note (see its "Code-path translation" section) -- resolve by basename
                if doc.name == "TESTS.md" and ref.startswith("tests/"):
                    if ref.rsplit("/", 1)[-1] in names:
                        continue
                # NB: resolved against TRACKED paths only -- the on-disk fallback that
                # used to be here is exactly what let untracked local files pass.
                # A doc-relative link ("../README.md") is normalised to a repo-relative
                # path first, then looked up the same way.
                rel_here = _normalise(doc, ref)
                if any(r in rels or _is_tracked_dir(r, rels) for r in (ref, rel_here) if r):
                    continue
                # a bare filename is prose shorthand ("the `bkt.py` module") -- fine
                # as long as SOMETHING in the tree has that basename
                if "/" not in ref and ref in names:
                    continue
                # a partial path ("engine/bkt.py" for "src/mentar/engine/bkt.py")
                if any(r.endswith("/" + ref) for r in rels):
                    continue
                findings.append((str(doc.relative_to(REPO)), lineno, ref))
    return findings


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    list_only = "--list" in argv
    findings = find_broken()
    if not findings:
        print("check_doc_paths: OK — every doc path reference resolves.")
        return 0
    print(f"check_doc_paths: {len(findings)} unresolved path reference(s) in prose docs:\n")
    for doc, lineno, ref in findings:
        print(f"  {doc}:{lineno}  ->  {ref}")
    print("\nEach is either (a) a rename the docs missed, (b) a genuinely planned-but-absent")
    print("file — add it to _KNOWN_ABSENT with the doc line that says so, or (c) a runtime")
    print("artifact — add it to _RUNTIME_ARTIFACTS.")
    return 0 if list_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
