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

---

# Grounding / ZIM sources (the `grounding:` block)

Mentar grounds the tutor in **vetted offline sources** so a small local model re-explains
*from* a passage instead of hallucinating (SPEC §15 layer-1 RAG). Those sources are **ZIM
files** — the offline web-archive format used by [Kiwix](https://kiwix.org). Grounding is
**text-only** by design; images/animation/interactive graphs are a separate presentation
concern (see `docs/design/media_and_interactivity.md`, W6.5/W7.6).

Full contract: `docs/design/W7_grounding_reader.md`.

## ZIM filename grammar

Kiwix names every ZIM as:

```
<project>_<lang>_<selection>_<flavour>_<YYYY-MM>.zim
```

| Part | Meaning | Examples |
|------|---------|----------|
| `project` | the source project | `vikidia`, `wikipedia`, `wikibooks`, `gutenberg`, `phet` |
| `lang` | language code | `en`, `fr`, `ace`, … |
| `selection` | scope: whole project or a subject slice | `all`, `simple_all`, `astronomy`, `medicine` |
| `flavour` | how much is included | `maxi` (text **+ images**), `nopic` (**text only**, smallest), `mini` (intros only) |
| `YYYY-MM` | build date | `2026-04` |

e.g. `wikipedia_en_astronomy_maxi_2026-02.zim`, `vikidia_en_all_nopic_2026-04.zim`.

**For grounding a text model, prefer `nopic`** — it's the smallest and we don't use images.

## How a source is configured (auto-latest)

In `grounding.sources`, the **key is the curriculum `source:` enum**; the value declares the
ZIM by its parts. The reader then **auto-selects the newest matching file in `zim_dir`** (latest
`YYYY-MM` wins), so you don't rename or re-pin on every Kiwix update:

```yaml
sources:
  vikidia:          { project: vikidia,   lang: en, selection: all,        flavour: nopic }
  wikipedia_simple: { project: wikipedia, lang: en, selection: simple_all, flavour: nopic }
```

- **Pin a build** when you want reproducibility: `pin: "2026-02"` (a date) or
  `pin: "vikidia_en_all_nopic_2026-04.zim"` (an exact filename).
- **Plain string** is still accepted as an exact filename (no auto-latest): `wikibooks: "wikibooks_en_all_nopic_2025-12.zim"`.

## Where ZIMs live (`zim_dir`)

| Form | Example | Needs |
|------|---------|-------|
| Local dir | `/data/zims` | nothing |
| **Mounted NAS / share** | `/mnt/nas/zims`, `Z:\zims` | mount it in the OS — libzim reads it directly |
| **SMB URL / UNC** | `smb://nas/share/zims`, `\\nas\share\zims` | the `[nas]` extra (`pip install 'mentar[nas]'`); the ZIM is copied once to `zim_cache_dir` because libzim needs a local file |

Mounting the share is the simplest path and needs **no** `smb:` config. Use `smb://` only when
you can't mount.

## Downloading — `scripts/fetch_zim.py`

Resolves the **newest** ZIM from a Kiwix mirror and downloads to local / NAS / `smb://`:

```bash
# everything declared in your config (recommended — one source of truth):
python3 scripts/fetch_zim.py --config config/inference.yaml --dest /mnt/nas/zims

# a named preset:
python3 scripts/fetch_zim.py --preset vikidia --preset wikipedia_simple --dest /mnt/nas/zims

# straight to an SMB share:
python3 scripts/fetch_zim.py --preset khan-academy --dest smb://nas/share/zims \
    --smb-user me --smb-pass 'secret'

# anything, by project subpath + filename regex (newest match wins):
python3 scripts/fetch_zim.py --project gutenberg --match 'gutenberg_en_all_.*\.zim$'
```

Browse a project's available builds at `https://download.kiwix.org/zim/<project>/`.

## Mirrors & fallbacks

`fetch_zim.py` tries these mirror bases **in order** until one serves the index/file:

1. `https://download.kiwix.org/zim` (redirects to a nearby mirror)
2. `https://master.download.kiwix.org/zim`
3. `https://lbo.download.kiwix.org/zim`
4. `https://mirror.accum.se/mirror/kiwix.org/zim`
5. `https://ftp.fau.de/kiwix/zim`

Override with `--mirror <url>` (repeatable) to force a fast/regional mirror. **Future:** switch
discovery to the Kiwix OPDS catalog (`library.kiwix.org`) for global/auto listing — not built yet.

**Runtime fallback:** if a ZIM is missing/unreadable at tutoring time, the reader returns an
**empty passage** (logs a warning) and the turn continues degraded — it never crashes (SAFETY §1.5).

## Other sources & licences

Check the licence before relying on a source — it gates whether content can ship beyond local use.

| Project | `project` | Licence | Notes |
|---------|-----------|---------|-------|
| **Vikidia** (kids' encyclopaedia) | `vikidia` | CC BY-SA 3.0 | pilot primary; child-appropriate |
| **Simple English Wikipedia** | `wikipedia` (`simple_all`) | CC BY-SA 4.0 | pilot backup |
| **Wikipedia** (full, any subject/lang) | `wikipedia` | CC BY-SA 4.0 | subject slices via `selection`; anchors on `<lang>.wikipedia.org` |
| **Wikibooks** | `wikibooks` | CC BY-SA | textbooks |
| **Project Gutenberg** | `gutenberg` | mostly public domain | classic texts |
| **PhET** (interactive sims) | `phet` | **CC BY** | interactive HTML5; would need W7.6 vetting to surface to a child |
| **Khan Academy** | `other` (verify path) | **CC BY-NC-SA** ⚠️ | **NC = non-commercial**: fine for local/personal use, **not** a commercial/hosted edition (SPEC §24 #18). |

Preset project subpaths for Khan/PhET are best-effort — if a fetch misses, browse the mirror and
pass `--project/--match`.

## Adding a new source

1. Add a `grounding.sources.<enum>` entry (structured spec or exact filename).
2. If its anchors are on a **new host** (e.g. a full-Wikipedia subject lives on
   `en.wikipedia.org`, not `simple.wikipedia.org`), add that host to the scope guard in
   `src/mentar/grounding/source_map.py` (`_SOURCE_HOST_SUFFIXES`) — otherwise the scope guard
   rejects the anchor and grounding degrades to empty.
3. Point the curriculum node's `grounding.source:` at the new enum.
4. Download it: `python3 scripts/fetch_zim.py --config config/inference.yaml --dest <zim_dir>`.
