---
type: Mentar Guide
title: Running Mentar Locally — Quick Start
description: Cross-platform (Windows/macOS/Linux) getting-started guide — local LLM setup, no cloud, no API key needed.
tags: [guide, setup, running, quick-start]
timestamp: "2026-07-23T00:00:00Z"
---

# Running Mentar locally — quick start (Windows / macOS / Linux)

A simple getting-started guide to run the Mentar tutor on your own machine. You'll run a
local LLM (no cloud, no API key needed) and talk to the tutor in the terminal or a browser.

> **TL;DR (macOS/Linux):** install Python → `git clone` → `./scripts/bootstrap.sh` →
> **`./mentar setup`** → `./mentar serve` (web UI at http://localhost:5000). For a quick
> terminal-only session instead: `./mentar run-session`. (Windows: see step 3.)
>
> Modern Python installs (Homebrew, Debian/Ubuntu system Python) refuse a bare `pip install`
> (PEP 668 `externally-managed-environment`) — always install into the venv `bootstrap.sh` creates,
> never system-wide.

---

## Download and run — no install (EXPERIMENTAL)

There is a single-file build for **Windows (x64)**, **macOS (Apple Silicon)** and
**Linux (x64)**, attached to the latest release. Download one file, run it, and Mentar
opens in your browser. No Python, no `git clone`, no virtual environment.

> **Intel Macs are not covered.** The macOS build is Apple Silicon only (the runner
> that produces it is arm64), so on an Intel Mac use the `./mentar setup` path below.

> **Read this before you rely on it.** These builds are experimental and they are
> **unsigned**, because code-signing certificates cost money Mentar does not have.
> What that means in practice:
>
> - **Windows** shows a blue "Windows protected your PC" box. *More info* →
>   *Run anyway*. Your antivirus may also quarantine it — single-file Python builds
>   are a shape malware also uses, and scanners judge the shape.
> - **macOS** refuses to open it on a double-click. Right-click → *Open* → *Open*, or
>   `xattr -d com.apple.quarantine ./mentar-macos-arm64`. macOS is the roughest of
>   the three; if you are comfortable with a terminal, the source install below is
>   genuinely easier on a Mac.
> - **macOS / Linux:** make it executable first — `chmod +x mentar-*`.
>
> Being asked to click past a security warning is a real cost, and you should weigh
> it. The source install below asks nothing of you that Python does not already ask.

```bash
chmod +x mentar-linux-x86_64
./mentar-linux-x86_64 --selftest    # confirms the download is complete and undamaged
./mentar-linux-x86_64               # starts Mentar and opens your browser
```

Every normal command still works: `./mentar-linux-x86_64 setup`,
`... serve --lan`, `... run-session`.

**The model is not in the download.** The binary is 26–41 MB (macOS 26, Windows 28,
Linux 41 — measured on the CI build). The language model is separate and is downloaded on
first run; it is a multi-gigabyte file, so the first run needs a reasonable connection and
some patience. It happens once — the model is kept and reused.

> **Undecided (2026-08-15):** the downloadable build will ship with **one fixed model**
> rather than the roster auto-selection the source install uses. Which model, and therefore
> the exact download size and the minimum RAM, is a maintainer decision that has not been
> made. No figure is quoted here until it is.

**Not included in the binary:** offline ZIM grounding (`libzim` has no reliable wheels
for every platform) and the offline BKT-fitting tools. Both are optional; Mentar
degrades gracefully without them. If you want grounding, install from source.

Where your family's data goes when running the binary — **not** next to the executable,
so it survives replacing the binary with a newer one:

| OS | Location |
|---|---|
| Windows | `%LOCALAPPDATA%\Mentar\` |
| macOS | `~/Library/Application Support/Mentar/` |
| Linux | `~/.local/share/mentar/` (or `$XDG_DATA_HOME/mentar`) |

Builds come from `.github/workflows/build-binary.yml` (GitHub-hosted runners). While
the binaries are experimental that workflow is **run on demand only** — its tag and
pull-request triggers are commented out, because three OS runners are the most
expensive thing in this repo's CI (macOS bills at 10x the minute rate). Re-enable the
tag trigger when the binaries are ready to ship. Mentar is AGPL-3.0-only: if you were
given a binary, you are entitled to the source it was built from.

---

## What a session looks like

| Year 5 Science | Year 12 Maths Methods |
|---|---|
| ![Year 5 science session](https://github.com/avps82/mentar/releases/download/v0.1.0-preview/demo_year5_science.gif) | ![Year 12 maths session](https://github.com/avps82/mentar/releases/download/v0.1.0-preview/demo_year12_quadratics.gif) |

Both recorded end-to-end against a locally-run model. Regenerate either with
`python3 scripts/record_demo.py --pack <pack> --topic <node>`.

## Fastest path: `./mentar setup`

After installing the package (steps 1–3 below), one command detects your hardware, picks the
best-fit **vetted** model, downloads it, writes `config/inference.yaml`, **installs the runtime it
needs, and verifies the model actually responds** before it says "Ready". (Windows: drop the `./`
prefix — activate the venv first, per step 3.)

```bash
./mentar setup            # auto: Ollama if installed, else GGUF (installs llama-cpp-python for you)
./mentar serve             # web UI (parent + child) at http://localhost:5000
# or, terminal-only:  ./mentar run-session
```

- It picks only from Mentar's vetted roster (`config/model_roster.yaml`) and sizes each model to
  your RAM with [gguf-parser](https://github.com/gpustack/gguf-parser-go) — no manual model choice.
- **It ends with a live check** — a 1-word test call to the model. If that fails, setup tells you
  (and exits non-zero) instead of leaving a config that can't serve. Re-check any time with
  **`python3 scripts/check_backend.py`** (prints the backend, target, and whether the model answers).
- **Easiest on macOS:** install [Ollama](https://ollama.com/download) *first* — then `./mentar setup`
  uses it (no compiling). Without Ollama or llama.app, setup falls back to the in-process GGUF
  runtime and will `pip install llama-cpp-python` (a compiled package — needs Xcode CLT on a Mac;
  can take a few minutes).
- Preview without downloading: `./mentar setup --dry-run`. Force a runtime:
  `--runtime auto|ollama|llama_app|gguf|vllm`. Override the model: `--model gemma2:9b`.
- **Runtime auto-order:** Ollama → **llama.app** → in-process GGUF. [llama.app](https://llama.app)
  is the official llama.cpp distro (`curl -LsSf https://llama.app/install.sh | sh`); its installer
  auto-picks a prebuilt binary matched to your **CPU instruction set + GPU**, so it Just Works on
  older (pre-AVX2) CPUs with no source build. `./mentar setup --runtime llama_app` downloads the
  GGUF and writes the config to talk to `llama serve` (it then prints the `llama serve …` command
  to start). On very old CPUs the portable prebuilt is slower than a native source build — see the
  GGUF section below for the perf path.

Prefer to do it by hand? The manual steps (4–6) below still work.

---

## Alternative: a cloud AI account (opt-in, parent-consent-gated)

If you already pay OpenAI or Anthropic, you can point Mentar at that account instead of
running a model locally. **Read this first:** with a cloud backend, your child's typed
lesson answers and the tutor's replies are sent to the provider on every turn, under
YOUR account — you become the data operator for that flow, and the usual "everything
stays on this computer" promise no longer fully applies (SAFETY.md §4.5). Setup makes
you acknowledge exactly that (a checkbox AND typing AGREE) before anything is saved.

```bash
./mentar setup --runtime openai --model gpt-5.2-mini   --api-key sk-...     # OpenAI
./mentar setup --runtime claude --model claude-sonnet-5 --api-key sk-ant-... # Anthropic
# both need --accept-cloud-terms when run non-interactively
```

Or use the web page: `./mentar serve` → the setup page's **Option C**. The key goes into
the gitignored `config/.env`, never into a tracked file; the acknowledgment is recorded
in `config/cloud_consent.yaml`.

### Using your ChatGPT subscription instead of an API key (EXPERIMENTAL)

If you pay for ChatGPT Plus/Pro, Mentar can use that instead of a separate paid API
key — press **Sign in with ChatGPT** on the setup page (or run `mentar chatgpt-login`),
then choose the ChatGPT option. A browser opens, you sign in, and the tokens are stored
locally in `config/chatgpt_auth.json` (gitignored) and refreshed automatically.

**Understand the trade before you rely on it.** OpenAI does not officially support
other apps using a ChatGPT sign-in — it is what several developer tools do, and it
**may stop working at any time**. It is also **not yet verified end-to-end**: the
sign-in, token refresh and consent flow are all tested, but the wire format of the
call itself was written from published descriptions rather than a capture of our own,
because the maintainer has no ChatGPT subscription. If you have one and it fails,
`scripts/capture_codex_probe.py` produces exactly the (redacted) evidence needed to
fix it — please open an issue with it. Your plan's usage limits also apply,
so a heavy session can hit a cap mid-lesson. For dependable capacity, use an API key.

**There is no Claude equivalent, and there will not be one soon.** Anthropic explicitly
prohibits (and technically blocks) using a Claude Pro/Max subscription from third-party
tools — so Claude works with an API key only. That asymmetry is theirs, not ours.

**To turn it off:** re-run setup with a local runtime (the header strip on every page
shows when a cloud backend is active). To revoke fully, also delete the key line from
`config/.env` and rotate the key at the provider.

## Alternative: point at a remote OpenAI-compatible proxy (LiteLLM / vLLM)

No local model at all — if you already run an OpenAI-compatible endpoint (e.g. a **LiteLLM**
proxy, or vLLM), just point Mentar at it. This is the same provider path as everything else
(only `base_url` / `model` / `api_key` differ), so there's nothing to download or compile.

Set `config/inference.yaml`:
```yaml
backend: vllm
vllm:
  base_url: "http://<host>:4000/v1"      # your LiteLLM/vLLM endpoint (must end in /v1)
  model: "gemma2:9b"                      # the name the proxy exposes it under
  api_key: "${MENTAR_VLLM_API_KEY}"       # resolved from config/.env (below) or the environment
generation: { temperature: 0.3, max_tokens: 1200 }   # timeout: omit — it scales with max_tokens
```
Put the **token in a local `config/.env`** (gitignored — it persists across terminals, no shell
`export` needed). Mentar auto-loads it when reading the config:
```bash
# config/.env   (NEVER committed — covered by .gitignore + the pre-commit secret guard)
MENTAR_VLLM_API_KEY=sk-...your-token...
```
Then just:
```bash
python3 scripts/check_backend.py        # expect: ✓ Backend LIVE
./mentar serve
```

> **How it resolves:** `${VAR}` in the config is filled from `config/.env` first, then the process
> environment (a real shell/service env var still wins). A `401` from the proxy means the key is
> missing/wrong in **both** — check `config/.env`.

---

## 1. Prerequisites

| Need | Notes |
|------|-------|
| **Python 3.11+** | 3.11, 3.12 or 3.13. Check: `python --version` (Windows) / `python3 --version` (macOS/Linux). |
| **git** | to clone the repo. |
| **Ollama** | the easiest local LLM runner — https://ollama.com/download (Windows / macOS / Linux). |
| **~6–8 GB free disk** | for one model (e.g. `gemma2:9b` ≈ 5.4 GB). |
| **≥ 16 GB RAM recommended** | a 9B model needs ~6–8 GB free while running. |

---

## 2. Get the code

```bash
git clone https://github.com/avps82/mentar.git
cd mentar
```

## 3. Create a virtual environment & install

**macOS / Linux**
```bash
./scripts/bootstrap.sh
```
Creates `.venv` and installs the package into it (`dev` + `web` extras). Modern Python installs
(Homebrew, Debian/Ubuntu system Python) refuse a bare system-wide `pip install` (PEP 668
`externally-managed-environment`) — this is why the venv step isn't optional. Use the repo-root
`./mentar` wrapper afterwards (step 6) and you never need to `source .venv/bin/activate` just to
run the CLI — it execs `.venv/bin/mentar` directly. (You still need to activate, or prefix with
`.venv/bin/`, to run `pytest`/`ruff` in the same shell.)

**Windows (PowerShell)**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1      # if blocked: Set-ExecutionPolicy -Scope Process RemoteSigned
pip install -e ".[web]"
```
This installs the `mentar` command (no `./mentar` wrapper on Windows — it's a bash script).
Add `.[dev]` too if you want to run the tests.

## 4. Install a local model with Ollama

Install Ollama (link above), then pull a model. Ollama starts a server at
`http://localhost:11434` automatically.

```bash
ollama pull gemma2:9b        # good default for 16 GB machines (incl. MacBook Pro M1 16 GB)
# smaller / faster alternatives:
ollama pull qwen2.5:3b       # ~2 GB, runs on almost anything
ollama pull phi4-mini         # ~2.2 GB
```

### Where Ollama stores models (per OS)

| OS | Default model directory |
|----|--------------------------|
| **macOS** | `~/.ollama/models` |
| **Linux** | `~/.ollama/models` (or `/usr/share/ollama/.ollama/models` if Ollama runs as a system service) |
| **Windows** | `C:\Users\<you>\.ollama\models` |

To store models elsewhere (e.g. an external drive), set `OLLAMA_MODELS` before starting Ollama:
- macOS/Linux: `export OLLAMA_MODELS=/path/to/models`
- Windows (PowerShell): `setx OLLAMA_MODELS "D:\ollama\models"` (then restart Ollama)

## 5. Configure Mentar

Copy the example config to the real (git-ignored) one and point it at Ollama:

**macOS / Linux**
```bash
cp config/inference.example.yaml config/inference.yaml
```
**Windows (PowerShell)**
```powershell
copy config\inference.example.yaml config\inference.yaml
```

Edit `config/inference.yaml` so the top looks like this:

```yaml
backend: ollama

ollama:
  base_url: "http://localhost:11434"
  model: "gemma2:9b"          # must match the tag you pulled

generation:
  temperature: 0.3
  max_tokens: 1200            # the backend default; setup used to write 512, which
                              # silently halved it and truncated real replies
  # timeout: omit it. The default scales with max_tokens (~5 tok/s + 30s), because
  # a flat 120s is a remote-API assumption a slow local machine cannot meet.
  #
  # A "thinking"/reasoning model is NOT recommended locally: on Ollama's /v1 the
  # think:false flag below is IGNORED (measured 2026-08-25), so the reasoning
  # cannot be switched off and `content` comes back empty. Prefer gemma2-9b.
  # extra_body:
  #   think: false
```

## 6. Run it

macOS/Linux: `./mentar` (no activation needed). Windows, or if you've activated `.venv` yourself:
drop the `./` — plain `mentar`.

**Web app** — the full product (child tutor + parent oversight). Then open http://localhost:5000:
```bash
./mentar serve            # child: / and /progress ; parent: /parent
```

### Using it on a tablet (ADVANCED — not the default)

**The default is one computer.** `./mentar serve` binds `127.0.0.1`, so only the
machine you started it on can open it. That is the supported setup: a desktop or
laptop, one browser, nothing reachable from anywhere else.

An **iPad or Android tablet cannot host Mentar itself** — the local model needs
real RAM and a CPU/GPU that a tablet does not give you, and iOS has no usable
Python. So the tablet is a *screen*, and the computer stays the *brain*:

```bash
./mentar serve --lan          # ADVANCED: also reachable from your home network
```

It prints the address to open in the tablet's browser (`http://<your-ip>:5000`)
and, before serving, exactly what that means:

- **Still entirely local** — no cloud, no accounts, nothing leaves your network.
- **Lessons go to the network; the grown-up pages do not.** The parent view,
  settings and setup stay on the computer running Mentar, so nothing else on the
  Wi-Fi can read your child's progress or change the app. Open those on the
  computer itself. There is no password anywhere — this is a boundary, not a
  login, so there is nothing to guess, share or forget.
- `--expose-admin` lifts that if you decide your home network *is* your boundary.
  It prints a blunter warning, because then anything on the Wi-Fi can read the
  transcripts and change the settings.
- Use it on a home network you trust, never on public or shared Wi-Fi.
- **Windows** will ask whether to allow Python through the firewall. Allow it for
  **private** networks only.

`--lan` uses waitress (installed with the `web` extra) rather than Flask's
development server, which must never be exposed to a network. If waitress is
missing, `--lan` refuses to start instead of quietly falling back.

**Terminal session** — headless, quick dev/testing (no parent UI):
```bash
./mentar run-session
```
Type answers when prompted; type `?` for help, `stop` to end.

That's it — the curriculum and question bank ship with the repo, so it works out of the box.

---

## Testing setup — `gemma2:9b` + grounding (verified 2026-06-27)

The reference config for product testing: the W1.3 pilot pick (`gemma2:9b`) with offline grounding
wired to the pilot ZIMs. Full-stack web smoke verified — `/`, `/progress`, `/parent` all serve, the
assent line shows, and `gemma2:9b` returns a clean **grounded** Help explanation.

**0. Install with the `grounding` extra.** Grounding needs `libzim`, which is optional (the base
install doesn't pull it — it's lazy + degrades gracefully). On **Apple Silicon use Python 3.13** —
`libzim`'s prebuilt arm64 wheel only exists for cp313/macOS ≥13; on 3.11/3.12 there's no wheel and
the source build usually fails (or `brew install libzim` first).
```bash
.venv/bin/pip install -e ".[web,setup,grounding]"
```

**1. Get the two pilot ZIMs onto a persistent, writable dir** (the read-only NAS mount won't do):
```bash
python3 scripts/fetch_zim.py --preset vikidia --preset wikipedia_simple --dest /path/to/zims
```

**2. Run `./mentar setup` with the ZIM dir exported.** It **auto-picks the best-fit vetted model for
your machine's RAM** (gguf-parser sizing — no manual model choice), picks the runtime (Ollama →
llama.app → in-process GGUF, all llama.cpp under the hood), and writes the **complete**
`config/inference.yaml` including the full `grounding` block (zim_dir **+** the pilot `sources`):
```bash
MENTAR_ZIM_DIR=/path/to/zims ./mentar setup       # auto-picks a model sized to your RAM
./mentar serve            # → http://127.0.0.1:5000   (child: / and /progress ; parent: /parent)
```

That's the whole flow — no hand-editing. `./mentar setup` writes the `grounding.sources` block for
you (a config with only `zim_dir` resolves every passage to `""` silently, so setup never emits a
partial block). Preview the pick without downloading: `./mentar setup --dry-run`.

> **Want to reproduce the exact pilot pick?** `gemma2:9b` is the W1.3 pilot model. To make your
> test results match what the pilot ships, **pin it** (needs ≥16 GB RAM; on smaller machines drop
> the flag and let auto-pick size a model that fits):
> ```bash
> MENTAR_ZIM_DIR=/path/to/zims ./mentar setup --model gemma2:9b
> ```

---

## Using a local GGUF directly (advanced, no Ollama)

Instead of Ollama you can run a `.gguf` file in-process via `llama-cpp-python`
(`pip install llama-cpp-python`). Put the model anywhere and set its **path** in the config —
note the per-OS path style (YAML: use forward slashes, or escape backslashes on Windows):

```yaml
backend: llamacpp
llamacpp:
  mode: in_process
  # macOS / Linux:
  model_path: "/Users/you/models/gemma-2-9b-it-Q4_K_M.gguf"     # macOS
  # model_path: "/home/you/models/gemma-2-9b-it-Q4_K_M.gguf"    # Linux
  # Windows (either form works):
  # model_path: "C:/Users/you/models/gemma-2-9b-it-Q4_K_M.gguf"
  # model_path: "models/gemma-2-9b-it-Q4_K_M.gguf"              # relative to the repo root
  n_ctx: 4096
  n_gpu_layers: 0     # raise to offload layers to a GPU (Metal/CUDA); 0 = CPU only
```

> **Older CPUs (pre-AVX2):** stock `llama-cpp-python` wheels may crash with `Illegal
> instruction`. Rebuild from source: `CMAKE_ARGS="-DGGML_NATIVE=ON -DGGML_AVX2=OFF" pip install
> llama-cpp-python --no-binary llama-cpp-python --force-reinstall`. (Needs `pip install cmake`.)

---

## Per-machine notes

> **Verified testing config:** use the [Testing setup — `gemma2:9b` + grounding](#testing-setup--gemma29b--grounding-verified-2026-06-27)
> above as the reference for product testing on any of these machines. `gemma2:9b` is the W1.3
> pilot pick; pair it with the Vikidia + Simple-WP ZIMs and the `grounding.sources` block.

- **MacBook Pro M1 16 GB:** Ollama uses the Apple Metal GPU automatically. `gemma2:9b` (~6 GB)
  runs comfortably and leaves headroom; a 12B (~8 GB) also fits but is tighter. No extra setup.
  Recommended for testing — the verified config above runs as-is.
- **Windows:** Ollama uses your GPU if available, otherwise CPU. Use the PowerShell commands above.
- **Linux:** as shown. For NVIDIA GPUs Ollama uses CUDA automatically.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `no inference config found` | You skipped step 5 — create `config/inference.yaml`. |
| Empty / blank tutor replies | A reasoning model is spending the whole budget on hidden reasoning and returning empty `content`. **`think: false` does NOT fix this on Ollama** — measured 2026-08-25, Ollama's OpenAI-compatible `/v1` ignores the flag (`think=false` and `think=true` were identical, both empty). Use a non-reasoning model: `./mentar setup --model gemma2-9b`. Setup now names this failure explicitly. |
| `Connection refused` / timeouts | Ollama isn't running. Open the Ollama app, or run `ollama serve`. |
| Model not found | The `model:` in the config doesn't match a pulled tag — run `ollama list`. |
| First reply is slow | The model is loading into memory; later turns are faster. |
| **Every** reply is slow | Local speed is capped by memory bandwidth, not CPU. Measured on a base M1 (68 GB/s): a 12B model runs ~7.25 tok/s — a full reply takes minutes, and that is the hardware ceiling with Metal working correctly (`ollama ps` will say 100% GPU). A smaller model is the only fix: `gemma2-9b` is ~1.5x faster and the only other safety-graded option. |
| `Illegal instruction` (GGUF path) | Pre-AVX2 CPU — rebuild `llama-cpp-python` from source (see box above). |
| `mentar: bad interpreter: …/.venv/bin/pythonX.Y: no such file or directory` | The venv's Python was upgraded/removed (e.g. a Homebrew patch bump), so the venv dangles. Recreate it: `rm -rf .venv && ./scripts/bootstrap.sh` (installs `grounding` too if you add it to the extras in that script, or run `.venv/bin/pip install -e ".[web,setup,grounding]"` after). |
| `401` from the proxy (LiteLLM/vLLM) | The token is missing/wrong. Put it in `config/.env` as `MENTAR_VLLM_API_KEY=sk-…` (gitignored, auto-loaded) — no shell `export` needed. A real env var still overrides it. |
| `command not found: mentar` / `externally-managed-environment` | You ran bare `mentar`/`pip install` without a venv. Use `./scripts/bootstrap.sh` then `./mentar ...` (macOS/Linux) — see step 3. |

## Optional: offline grounding (ZIM)

You can skip this for a first run — grounding degrades gracefully (no ZIM file → the tutor
just doesn't add a source passage). To enable it later, see
`docs/design/W7_grounding_reader.md` and the `grounding:` block in `config/inference.example.yaml`.
