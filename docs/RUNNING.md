# Running Mentar locally — quick start (Windows / macOS / Linux)

A simple getting-started guide to run the Mentar tutor on your own machine. You'll run a
local LLM (no cloud, no API key needed) and talk to the tutor in the terminal or a browser.

> **TL;DR:** install Python → `pip install -e ".[web,setup]"` → **`mentar setup`** → `mentar run-session`.

---

## Fastest path: `mentar setup`

After installing the package (steps 1–3 below), one command detects your hardware, picks the
best-fit **vetted** model, downloads it, and writes `config/inference.yaml` for you:

```bash
mentar setup            # auto: uses Ollama if installed, else downloads a GGUF to run in-process
mentar run-session      # start tutoring
```

- It picks only from Mentar's vetted roster (`config/model_roster.yaml`) and sizes each model to
  your RAM with [gguf-parser](https://github.com/gpustack/gguf-parser-go) — no manual model choice.
- Preview without downloading: `mentar setup --dry-run`. Force a runtime:
  `--runtime ollama|llama_app|gguf`. Override the model: `--model gemma2:9b`.
- **Runtime auto-order:** Ollama → **llama.app** → in-process GGUF. [llama.app](https://llama.app)
  is the official llama.cpp distro (`curl -LsSf https://llama.app/install.sh | sh`); its installer
  auto-picks a prebuilt binary matched to your **CPU instruction set + GPU**, so it Just Works on
  older (pre-AVX2) CPUs with no source build. `mentar setup --runtime llama_app` downloads the
  GGUF and writes the config to talk to `llama serve` (it then prints the `llama serve …` command
  to start). On very old CPUs the portable prebuilt is slower than a native source build — see the
  GGUF section below for the perf path.

Prefer to do it by hand? The manual steps (4–6) below still work.

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
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[web]"
```

**Windows (PowerShell)**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1      # if blocked: Set-ExecutionPolicy -Scope Process RemoteSigned
pip install -e ".[web]"
```

This installs the `mentar` command. (`.[web]` adds the Flask web app; add `.[dev]` too if you
want to run the tests.)

## 4. Install a local model with Ollama

Install Ollama (link above), then pull a model. Ollama starts a server at
`http://localhost:11434` automatically.

```bash
ollama pull gemma2:9b        # good default for 16 GB machines (incl. MacBook Pro M1 16 GB)
# smaller / faster alternatives:
ollama pull qwen2.5:3b       # ~2 GB, runs on almost anything
ollama pull phi3.5           # ~2.2 GB
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
  max_tokens: 512
  # If you use a "thinking"/reasoning model (it pauses then answers), uncomment:
  # extra_body:
  #   think: false            # otherwise replies can come back empty/truncated
```

## 6. Run it

**Terminal tutor session**
```bash
mentar run-session
# or:  python -m mentar.cli run-session
```
Type answers when prompted; type `?` for help, `stop` to end.

**Web app** (then open http://localhost:5000)
```bash
python -m mentar.web.app
```

That's it — the curriculum and question bank ship with the repo, so it works out of the box.

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

- **MacBook Pro M1 16 GB:** Ollama uses the Apple Metal GPU automatically. `gemma2:9b` (~6 GB)
  runs comfortably and leaves headroom; a 12B (~8 GB) also fits but is tighter. No extra setup.
- **Windows:** Ollama uses your GPU if available, otherwise CPU. Use the PowerShell commands above.
- **Linux:** as shown. For NVIDIA GPUs Ollama uses CUDA automatically.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `no inference config found` | You skipped step 5 — create `config/inference.yaml`. |
| Empty / blank tutor replies | Your model is a reasoning model — set `generation.extra_body.think: false`. |
| `Connection refused` / timeouts | Ollama isn't running. Open the Ollama app, or run `ollama serve`. |
| Model not found | The `model:` in the config doesn't match a pulled tag — run `ollama list`. |
| First reply is slow | The model is loading into memory; later turns are faster. |
| `Illegal instruction` (GGUF path) | Pre-AVX2 CPU — rebuild `llama-cpp-python` from source (see box above). |

## Optional: offline grounding (ZIM)

You can skip this for a first run — grounding degrades gracefully (no ZIM file → the tutor
just doesn't add a source passage). To enable it later, see
`docs/design/W7_grounding_reader.md` and the `grounding:` block in `config/inference.example.yaml`.
