"""Thin wrapper around gpustack's gguf-parser — cross-OS device-fit estimation.

gguf-parser (https://github.com/gpustack/gguf-parser-go, MIT) is a single static binary that
parses a GGUF (local, remote HF, or Ollama-registry — header-only, no full download) and
estimates its memory footprint. We use it to answer "how much RAM does this model need to run
here?" so `mentar setup` can pick the best-fit model — WITHOUT us hand-writing cross-OS
hardware detection.

We size the **CPU-only floor** (`--gpu-layers 0`) at Mentar's real context size: RAM is the
universal constraint across Windows/macOS/Linux, and a GPU (handled by Ollama at runtime) only
makes a fitting model faster. If the binary can't be obtained or run, callers fall back to a
pure-Python heuristic — setup always works.

Public API:
    estimate_ram_gb(ref, n_ctx=4096) -> float | None      # CPU-only RAM need, or None
    total_ram_gb() -> float | None                        # detected device RAM
"""

from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import stat
import subprocess
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

GGUF_PARSER_VERSION = "v0.24.1"
_RELEASE = "https://github.com/gpustack/gguf-parser-go/releases/download"
_BIN_DIR = Path(os.environ.get("MENTAR_BIN_DIR", str(Path.home() / ".mentar" / "bin")))


def _asset_name() -> str | None:
    """gguf-parser release asset for this OS/arch, or None if unsupported."""
    sysname = platform.system().lower()           # darwin | linux | windows
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "amd64" if machine in ("x86_64", "amd64") else None
    if arch is None or sysname not in ("darwin", "linux", "windows"):
        return None
    name = f"gguf-parser-{sysname}-{arch}"
    return name + ".exe" if sysname == "windows" else name


def _find_binary() -> str | None:
    """Locate gguf-parser: explicit env -> PATH -> cached -> lazy download. Best-effort."""
    env = os.environ.get("MENTAR_GGUF_PARSER")
    if env and Path(env).exists():
        return env
    on_path = shutil.which("gguf-parser")
    if on_path:
        return on_path

    asset = _asset_name()
    if asset is None:
        logger.warning("gguf-parser: unsupported platform %s/%s", platform.system(), platform.machine())
        return None
    cached = _BIN_DIR / asset
    if cached.exists():
        return str(cached)

    # Lazy download (pinned version).
    url = f"{_RELEASE}/{GGUF_PARSER_VERSION}/{asset}"
    try:
        _BIN_DIR.mkdir(parents=True, exist_ok=True)
        tmp = cached.with_suffix(cached.suffix + ".part")
        logger.info("gguf-parser: downloading %s", url)
        with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f)
        tmp.replace(cached)
        cached.chmod(cached.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        return str(cached)
    except Exception as exc:
        logger.warning("gguf-parser: download failed (%s) — falling back to heuristic", exc)
        return None


def _ref_args(ref: dict) -> list[str] | None:
    """Map a model ref to gguf-parser source flags."""
    if ref.get("path"):
        return ["--path", str(ref["path"])]
    if ref.get("ol_model"):
        return ["--ol-model", ref["ol_model"]]
    if ref.get("hf_repo") and ref.get("hf_file"):
        return ["--hf-repo", ref["hf_repo"], "--hf-file", ref["hf_file"]]
    return None


def estimate_ram_gb(ref: dict, n_ctx: int = 4096) -> float | None:
    """CPU-only RAM (GB) needed to run the model at ``n_ctx``, via gguf-parser.

    ``ref`` is one of: {"path": ...}, {"ol_model": tag}, {"hf_repo":.., "hf_file":..}.
    Returns None if gguf-parser is unavailable or the estimate can't be read (caller
    should fall back to a heuristic).
    """
    binary = _find_binary()
    args = _ref_args(ref)
    if not binary or not args:
        return None
    # --no-mmap: count the weights as resident RAM. Without it gguf-parser excludes
    # memory-mapped weights, badly under-reporting the real footprint (e.g. 2.7 vs 9.2 GB
    # for a 9B Q4). The resident number is the correct conservative "will it run well" floor.
    cmd = [binary, *args, "--ctx-size", str(n_ctx), "--gpu-layers", "0",
           "--no-mmap", "--estimate", "--json"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=90, check=True).stdout
        item = json.loads(out)["estimate"]["items"][0]
        # CPU-only (gpu-layers 0): the whole model sits in system RAM (nonuma).
        return round(item["ram"]["nonuma"] / 1e9, 3)
    except Exception as exc:
        logger.warning("gguf-parser estimate failed for %r: %s", ref, exc)
        return None


def total_ram_gb() -> float | None:
    """Detected total system RAM in GB (psutil if present, else POSIX stdlib)."""
    try:
        import psutil
        return round(psutil.virtual_memory().total / 1e9, 1)
    except Exception:
        pass
    try:
        return round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1e9, 1)
    except Exception:
        return None
