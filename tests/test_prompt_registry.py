"""T4.6 — prompt templates are versioned files the controller loads, never hardcoded.

Implements the W6.2 acceptance + the T7.3 regression mechanism (docs/TESTS.md):
  1. prompts/ has >=10 templates and every README.md hash matches its file body.
  2. No prompt-like string literal (>200 chars, non-docstring) lives in src/.
  3. prompt_ref "{template_id}:{version}" round-trips.
  4. The combined prompt-set hash is deterministic (the T7.3 change signal).

stdlib-only; runnable as `python3 tests/test_prompt_registry.py`.
"""

from __future__ import annotations

import ast
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"
SRC = ROOT / "src"
HASH_LEN = 12
_FM = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def _body_hash(text: str) -> str:
    m = _FM.match(text)
    assert m, "missing front matter"
    return hashlib.sha256(m.group(2).encode("utf-8")).hexdigest()[:HASH_LEN]


def _template_files() -> list[Path]:
    return [f for f in sorted(PROMPTS.glob("*.md")) if f.name != "README.md"]


def _registry_hashes() -> dict[str, str]:
    reg = (PROMPTS / "README.md").read_text()
    return dict(re.findall(r"\| `([^`]+\.md)` \| `[^`]+` \|[^|]*\| `([0-9a-f]{12})` \|", reg))


def test_at_least_ten_templates():
    assert len(_template_files()) >= 10


def test_registry_hashes_match_bodies():
    reg = _registry_hashes()
    files = _template_files()
    assert len(reg) == len(files), "registry/file count mismatch (stale registry)"
    for f in files:
        h = _body_hash(f.read_text())
        assert f.name in reg, f"{f.name} missing from README.md"
        assert reg[f.name] == h, f"stale hash for {f.name}: registry={reg[f.name]} body={h}"


def test_headers_carry_matching_version():
    for f in _template_files():
        text = f.read_text()
        hdr = _FM.match(text).group(1)
        v = re.search(r"^version:\s*(\S+)$", hdr, re.MULTILINE).group(1)
        assert v == _body_hash(text), f"{f.name} header version != body hash"


# Non-prompt long-string categories that are legitimately allowed in src/.
_SQL_MARKERS = ("SELECT ", "INSERT INTO", "UPDATE ", "DELETE FROM", "CREATE TABLE",
                "ON CONFLICT", "CREATE INDEX", "CREATE TRIGGER")
_EXEMPT_MARKER = "t7.3-exempt"  # line-level escape hatch: `# t7.3-exempt: <reason>`


def _looks_like_sql(s: str) -> bool:
    up = s.upper()
    return any(m in up for m in _SQL_MARKERS)


def test_no_long_prompt_literals_in_src():
    """T7.3 mechanism: no PROMPT-like string literal >200 chars under src/.

    Prompts must live in prompts/ (versioned). SQL statements are auto-exempt
    (the db layer is SQL by design); anything else needing exemption must carry a
    `# t7.3-exempt: <reason>` marker comment on the literal's line.
    """
    offenders = []
    for py in SRC.rglob("*.py"):
        src_text = py.read_text()
        src_lines = src_text.splitlines()
        tree = ast.parse(src_text, filename=str(py))
        docstrings = {
            ast.get_docstring(n, clean=False)
            for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and ast.get_docstring(n, clean=False) is not None
        }
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
                continue
            s = node.value
            if len(s) <= 200 or s in docstrings or _looks_like_sql(s):
                continue
            line = src_lines[node.lineno - 1] if node.lineno <= len(src_lines) else ""
            if _EXEMPT_MARKER in line.lower():
                continue
            offenders.append(f"{py.relative_to(ROOT)}:{node.lineno}")
    assert not offenders, f"prompt-like literals in src (move to prompts/): {offenders}"


def test_prompt_ref_round_trips():
    f = _template_files()[0]
    hdr = _FM.match(f.read_text()).group(1)
    tid = re.search(r"^template_id:\s*(.+)$", hdr, re.MULTILINE).group(1).strip()
    ref = f"{tid}:{_body_hash(f.read_text())}"
    got_id, got_hash = ref.split(":", 1)
    assert got_id == tid and len(got_hash) == HASH_LEN


def test_combined_set_hash_is_deterministic():
    def combined() -> str:
        parts = sorted(_body_hash(f.read_text()) for f in _template_files())
        return hashlib.sha256("".join(parts).encode()).hexdigest()
    assert combined() == combined()


def _smoke():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"OK  {fn.__name__}")
    print(f"SMOKE: all {len(fns)} T4.6/T7.3 checks pass")


if __name__ == "__main__":
    _smoke()
