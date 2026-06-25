# CLAUDE.md

All project guidance is tool-neutral and lives in **[AGENTS.md](AGENTS.md)** — read that first
(setup, commands, src-layout, the pytest+ruff gate, and the protected-path RULES).

Claude-specific notes:
- **Memory is dual-located** — write to BOTH `~/.claude/projects/.../memory/` AND the repo's
  `.claude-memory/` on every memory change (the maintainer reviews via a network drive).
- **`gemma` skill** — delegate well-specified grunt coding to local `gemma4:12b`, then review its
  output (spec → gemma drafts → you verify). `gemma4:12b` is eval-host-only; it needs
  `MENTAR_VLLM_BASE_URL`/`MENTAR_VLLM_API_KEY` in the session.
- Commit trailer: `Co-Authored-By` only — **no `Claude-Session` URL trailer**.
