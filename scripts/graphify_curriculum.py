#!/usr/bin/env python3
"""Build a knowledge graph over curriculum content (templates + visual
scaffolds) using the LOCAL LLM (gemma4:12b via tools/llm.sh) for semantic
extraction, instead of graphify's default Gemini-API/Claude-subagent backend.

Why this exists (2026-07-25): an ad-hoc manual audit of every curriculum
node's "explain" method (docs/EXPLAIN_METHOD_AUDIT.md) found 5 real gaps
(scaffold-routing bugs, inconsistent step-grid eligibility) that a code-only
graphify pass (AST, no curriculum content indexed) could never have
surfaced. This script closes that gap by running graphify's OWN extraction
schema (see references/extraction-spec.md in the graphify skill) against
gemma4:12b directly, keeping the pipeline entirely local.

Output is gitignored (graphify-out/curriculum/) -- regenerate on demand or
in CI; never committed, matching the maintainer's explicit choice not to
bloat repo history with a graph that changes on every curriculum edit.

Usage:
    python3 scripts/graphify_curriculum.py                    # curriculum/ only
    python3 scripts/graphify_curriculum.py --include-docs      # + docs/
    python3 scripts/graphify_curriculum.py --model gemma2:9b   # different local model

Requires MENTAR_VLLM_API_KEY (or LOCAL_LLM_API_KEY) in the environment, same
as tools/llm.sh / the /gemma skill.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LLM_SH = REPO_ROOT / "tools" / "llm.sh"

_RESERVED_NAMES = {"index.md", "log.md"}  # OKF bundle manifests -- not concepts

_EXTRACTION_RULES = """You are a knowledge-graph extraction engine. Read the files below and extract
a knowledge graph fragment. Output ONLY valid JSON matching the schema at the
end -- no explanation, no markdown fences, no preamble, nothing before or
after the JSON object.

Rules:
- EXTRACTED: relationship explicit in source (a link, an explicit reference)
- INFERRED: reasonable inference (shared topic, implied prerequisite)
- AMBIGUOUS: uncertain -- flag for review, do not omit
- Extract named concepts, entities, and relationships. For rationale (WHY a
  design choice was made) store it as a `rationale` attribute on the
  relevant concept node -- do NOT create a separate rationale node.
- `file_type` MUST be one of exactly: code, document, paper, image, rationale, concept.
  For curriculum/visual-scaffold files, use "document" for index/overview files
  and "concept" for a single curriculum node or scaffold topic.
- If a file has YAML frontmatter (--- ... ---), copy its fields (title, type,
  subject, answer_type, topic_keywords, item_source) onto the node as extra
  attributes -- these matter for later queries (e.g. "which nodes share an
  item_source", "which nodes' labels overlap a scaffold's topic_keywords").
- confidence_score is REQUIRED on every edge, never 0.5 as a default:
  EXTRACTED = 1.0 always. INFERRED: pick exactly one of 0.95/0.85/0.75/0.65/0.55
  (never a value outside this set). AMBIGUOUS: 0.1-0.3.
- Node ID format: lowercase, only [a-z0-9_], no dots or slashes. Format:
  {stem}_{entity} where stem is the full repo-relative path with extension
  dropped, each segment lowercased and non-alphanumeric chars replaced with
  `_`, joined with `_`. Example: curriculum/templates/AU_ACARA/year5_maths.md
  concept "au5_add_sub_decimals" -> id
  curriculum_templates_au_acara_year5_maths_au5_add_sub_decimals.
  Never append chunk numbers or sequence suffixes to an ID.

Generate the extraction JSON matching this schema exactly (single JSON object,
no other text):
{"nodes":[{"id":"...","label":"Human Readable Name","file_type":"document|concept","source_file":"<path verbatim>","source_location":null,"source_url":null,"captured_at":null,"author":null,"contributor":null}],"edges":[{"source":"node_id","target":"node_id","relation":"references|conceptually_related_to|shares_data_with|semantically_similar_to|rationale_for","confidence":"EXTRACTED|INFERRED|AMBIGUOUS","confidence_score":1.0,"source_file":"<path verbatim>","source_location":null,"weight":1.0}],"hyperedges":[]}
"""


def _collect_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for base in paths:
        if not base.is_dir():
            continue
        for p in sorted(base.glob("**/*.md")):
            if p.name in _RESERVED_NAMES:
                continue
            files.append(p)
    return files


def _chunk(files: list[Path], size: int) -> list[list[Path]]:
    return [files[i:i + size] for i in range(0, len(files), size)]


def _build_prompt(chunk: list[Path], chunk_num: int, total_chunks: int) -> str:
    parts = [f"Chunk {chunk_num} of {total_chunks}.\n"]
    for p in chunk:
        rel = p.relative_to(REPO_ROOT)
        try:
            text = p.read_text(encoding="utf-8")
        except Exception as e:
            text = f"<could not read: {e}>"
        parts.append(f"\n--- FILE: {rel} ---\n{text}\n")
    parts.append("\n" + _EXTRACTION_RULES)
    return "".join(parts)


def _call_llm(model: str, prompt: str, max_tokens: int, timeout: int) -> dict | None:
    env_note = "" if LLM_SH.exists() else " (tools/llm.sh missing)"
    if not LLM_SH.exists():
        print(f"ERROR: {LLM_SH} not found{env_note}", file=sys.stderr)
        return None
    env = {**os.environ, "LLM_MAX_TOKENS": str(max_tokens)}
    try:
        result = subprocess.run(
            [str(LLM_SH), model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=str(REPO_ROOT),
        )
    except subprocess.TimeoutExpired:
        print(f"WARNING: chunk timed out after {timeout}s, skipping", file=sys.stderr)
        return None
    if result.returncode != 0:
        print(f"WARNING: llm.sh failed: {result.stderr.strip()[:300]}", file=sys.stderr)
        return None
    raw = result.stdout.strip()
    # Defensive: strip markdown fences even though the prompt forbids them --
    # smaller local models don't always follow instructions perfectly.
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0]
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"WARNING: chunk produced invalid JSON ({e}), skipping. First 200 chars: {raw[:200]!r}",
              file=sys.stderr)
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="gemma4:12b", help="local model to use (default: gemma4:12b)")
    ap.add_argument("--include-docs", action="store_true", help="also scan docs/ (default: curriculum/ only)")
    ap.add_argument("--chunk-size", type=int, default=8, help="files per LLM call (default: 8)")
    ap.add_argument("--max-tokens", type=int, default=8000, help="LLM_MAX_TOKENS per call (default: 8000)")
    ap.add_argument("--timeout", type=int, default=180, help="seconds per chunk call (default: 180)")
    ap.add_argument("--output-dir", default="graphify-out/curriculum", help="where to write graph outputs")
    args = ap.parse_args()

    if not (os.environ.get("MENTAR_VLLM_API_KEY") or os.environ.get("LOCAL_LLM_API_KEY")):
        print("ERROR: set MENTAR_VLLM_API_KEY (see tools/llm.sh) before running.", file=sys.stderr)
        return 2

    scan_paths = [REPO_ROOT / "curriculum"]
    if args.include_docs:
        scan_paths.append(REPO_ROOT / "docs")

    files = _collect_files(scan_paths)
    if not files:
        print("No files found to scan.", file=sys.stderr)
        return 1
    chunks = _chunk(files, args.chunk_size)
    print(f"Scanning {len(files)} files in {len(chunks)} chunks (model={args.model})")

    all_nodes: list[dict] = []
    all_edges: list[dict] = []
    all_hyperedges: list[dict] = []
    seen_ids: set[str] = set()
    failed_chunks = 0

    for i, chunk in enumerate(chunks, start=1):
        print(f"  chunk {i}/{len(chunks)} ({len(chunk)} files)...", end=" ", flush=True)
        prompt = _build_prompt(chunk, i, len(chunks))
        result = _call_llm(args.model, prompt, args.max_tokens, args.timeout)
        if result is None:
            failed_chunks += 1
            print("FAILED")
            continue
        nodes = result.get("nodes", [])
        edges = result.get("edges", [])
        hyperedges = result.get("hyperedges", [])
        new_nodes = 0
        for n in nodes:
            if n.get("id") and n["id"] not in seen_ids:
                seen_ids.add(n["id"])
                all_nodes.append(n)
                new_nodes += 1
        all_edges.extend(edges)
        all_hyperedges.extend(hyperedges)
        print(f"+{new_nodes} nodes, +{len(edges)} edges")

    if failed_chunks:
        print(f"\n{failed_chunks}/{len(chunks)} chunks failed -- graph is INCOMPLETE. "
              f"Not a silent gap: this line is the record of it.", file=sys.stderr)

    if not all_nodes:
        print("ERROR: no nodes extracted -- refusing to write an empty graph.", file=sys.stderr)
        return 1

    extraction = {"nodes": all_nodes, "edges": all_edges, "hyperedges": all_hyperedges,
                  "input_tokens": 0, "output_tokens": 0}

    graphify_python = _resolve_graphify_python()
    out_dir = REPO_ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    extraction_path = out_dir / ".extraction.json"
    extraction_path.write_text(json.dumps(extraction, ensure_ascii=False), encoding="utf-8")

    build_script = f"""
import json
from pathlib import Path
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json

extraction = json.loads(Path({str(extraction_path)!r}).read_text(encoding="utf-8"))
G = build_from_json(extraction, root={str(REPO_ROOT)!r}, directed=False)
if G.number_of_nodes() == 0:
    print("ERROR: graph is empty")
    raise SystemExit(1)
communities = cluster(G)
cohesion = score_all(G, communities)
gods = god_nodes(G)
surprises = surprising_connections(G, communities)
labels = {{cid: f"Community {{cid}}" for cid in communities}}
questions = suggest_questions(G, communities, labels)
wrote = to_json(G, communities, {str(out_dir / "graph.json")!r}, force=True, community_labels=labels)
detection = {{"total_files": {len(files)}, "total_words": 0, "files": {{"document": []}}, "skipped_sensitive": []}}
report = generate(G, communities, cohesion, labels, gods, surprises, detection,
                   {{"input": 0, "output": 0}}, {str(REPO_ROOT)!r}, suggested_questions=questions)
Path({str(out_dir / "CURRICULUM_GRAPH_REPORT.md")!r}).write_text(report, encoding="utf-8")
print(f"Graph: {{G.number_of_nodes()}} nodes, {{G.number_of_edges()}} edges, {{len(communities)}} communities")
"""
    result = subprocess.run([graphify_python, "-c", build_script], capture_output=True, text=True)
    print(result.stdout, end="")
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return 1

    extraction_path.unlink(missing_ok=True)
    print(f"\nOutputs in {out_dir}/ (gitignored -- regenerate on demand or in CI):")
    print("  graph.json")
    print("  CURRICULUM_GRAPH_REPORT.md")
    return 0


def _resolve_graphify_python() -> str:
    import shutil
    graphify_bin = shutil.which("graphify")
    if graphify_bin:
        with open(graphify_bin) as f:
            shebang = f.readline().strip().lstrip("#!")
            if shebang and Path(shebang).exists():
                return shebang
    return sys.executable


if __name__ == "__main__":
    raise SystemExit(main())
