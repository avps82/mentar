# config/ — runtime configuration

Holds inference/backend configuration. **Real secrets never get committed** — two layers
of protection back that up.

## Setup

```bash
cp config/inference.example.yaml config/inference.yaml   # gitignored
# edit config/inference.yaml with your vLLM endpoint / model / keys
```

Prefer environment variables for secrets (the example uses `${MENTAR_VLLM_API_KEY}` etc.);
inline a real key only in `config/inference.yaml`, never in the `.example` file.

## Secret safeguard (do this once per clone)

```bash
git config core.hooksPath scripts/git-hooks
```

This activates `scripts/git-hooks/pre-commit`, which blocks any commit that contains:
- secret-like **filenames** (`.env`, `*.key`, `*.pem`, `config/inference.yaml`,
  `config/*.local.*`, `*secret*`, `secrets/…`) — even if added with `git add -f`; and
- secret-like **content** in added lines (private-key headers, `AIza…`/`sk-…`/`xox…`
  tokens, `api_key`/`secret`/`token`/`password = …` assignments).

`.gitignore` already excludes these paths (first layer); the hook is the backstop
(second layer) and also catches inline secrets pasted into otherwise-tracked files.

Genuine false positive? `git commit --no-verify` (use sparingly).

## What's gitignored here

`config/inference.yaml`, `config/*.local.*`, `config/secrets.*` — ignored.
`config/*.example.*` — committed (templates only, no real values).
