"""Hardware-aware model selection from Mentar's vetted roster.

Picks the highest-ranked *vetted* model that fits the detected machine, choosing a runtime
(Ollama if available, else in-process GGUF). All cross-OS device sizing is delegated to
gguf-parser (with a pure-Python heuristic fallback); the only thing we own here is the
selection *policy* over the safety/pedagogy-vetted roster.

Public API:
    load_roster(path=None) -> list[dict]
    select(roster, prefer="auto", n_ctx=4096, ram_gb=None) -> Selection
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from mentar.inference import ggufparser
from mentar.paths import bundle_root

logger = logging.getLogger(__name__)

COMFORT = 0.8          # require the model to fit within 80% of RAM (headroom for the OS/app)
_OVERHEAD_GB = 1.5     # heuristic runtime overhead when gguf-parser is unavailable


def _default_roster_path() -> Path:
    return bundle_root() / "config" / "model_roster.yaml"  # shipped, read-only


def load_roster(path: str | Path | None = None) -> list[dict]:
    import yaml
    p = Path(path) if path else _default_roster_path()
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    models = data.get("models", [])
    return sorted(models, key=lambda m: m.get("rank", 9999))


@dataclass
class Selection:
    model: dict                       # the chosen roster entry
    runtime: str                      # "ollama" | "gguf"
    est_ram_gb: float | None          # estimated CPU-only RAM need
    total_ram_gb: float | None        # detected device RAM
    fits: bool
    reason: str
    warnings: list[str] = field(default_factory=list)


def _has_avx2() -> bool | None:
    """True/False if known, None if undetectable."""
    try:
        import cpuinfo
        return "avx2" in cpuinfo.get_cpu_info().get("flags", [])
    except Exception:
        pass
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            return "avx2" in f.read()
    except Exception:
        return None


def _ref_for(model: dict, runtime: str) -> dict:
    """gguf-parser ref for sizing: prefer the artifact the chosen runtime will actually use."""
    if runtime in ("gguf", "llama_app") and model.get("hf_repo") and model.get("hf_file"):
        return {"hf_repo": model["hf_repo"], "hf_file": model["hf_file"]}
    if model.get("ol_model") or model.get("ollama_tag"):
        return {"ol_model": model.get("ollama_tag") or model.get("ol_model")}
    if model.get("hf_repo") and model.get("hf_file"):
        return {"hf_repo": model["hf_repo"], "hf_file": model["hf_file"]}
    return {}


def _need_gb(model: dict, runtime: str, n_ctx: int) -> tuple[float, bool]:
    """(estimated RAM need, used_gguf_parser?). Falls back to the heuristic."""
    est = ggufparser.estimate_ram_gb(_ref_for(model, runtime), n_ctx=n_ctx)
    if est is not None:
        return est, True
    heuristic = float(model.get("min_ram_gb", model.get("params_b", 7) * 0.6 + _OVERHEAD_GB))
    return heuristic, False


def select(roster: list[dict], prefer: str = "auto", n_ctx: int = 4096,
           ram_gb: float | None = None) -> Selection:
    """Choose the best-fitting vetted model + runtime for this machine."""
    warnings: list[str] = []

    ollama_avail = shutil.which("ollama") is not None
    llama_app_avail = shutil.which("llama") is not None
    if prefer in ("ollama", "llama_app", "gguf"):
        runtime = prefer
    else:  # auto — prefer Ollama, then llama.app (`llama serve`), then in-process GGUF
        runtime = "ollama" if ollama_avail else ("llama_app" if llama_app_avail else "gguf")
    if runtime == "ollama" and not ollama_avail:
        warnings.append("Ollama not found on PATH — install it, or run setup with --runtime gguf.")
    if runtime == "llama_app" and not llama_app_avail:
        warnings.append("llama (llama.app) not found on PATH — install from https://llama.app, "
                        "or run setup with --runtime gguf.")

    total = ram_gb if ram_gb is not None else ggufparser.total_ram_gb()
    if total is None:
        warnings.append("Could not detect system RAM — picking a conservative small model.")

    # Candidates the chosen runtime can actually install. Both gguf (in-process) and
    # llama_app (`llama serve -m <gguf>`) need a local GGUF; ollama uses its own registry tag.
    candidates = list(roster)
    if runtime in ("gguf", "llama_app"):
        candidates = [m for m in roster if m.get("hf_repo") and m.get("hf_file")]
        if not candidates:
            raise ValueError(f"No roster model has a GGUF (hf_repo/hf_file) for the {runtime} runtime.")

    smallest = min(candidates, key=lambda m: m.get("params_b", 0))
    chosen, est, used_parser, fits = None, None, False, False

    for m in candidates:                       # roster is rank-sorted (best first)
        need, used = _need_gb(m, runtime, n_ctx)
        if total is None:
            continue                           # can't compare; handled below
        if need <= total * COMFORT:
            chosen, est, used_parser, fits = m, need, used, True
            break

    if chosen is None:
        # Nothing fit (or RAM unknown): take the smallest, warn.
        chosen = smallest
        est, used_parser = _need_gb(chosen, runtime, n_ctx)
        fits = total is not None and est <= total * COMFORT
        if total is not None and not fits:
            warnings.append(
                f"Even the smallest vetted model (~{est} GB) may not fit {total} GB RAM — "
                "expect slow or failed runs."
            )

    sizer = "gguf-parser" if used_parser else "heuristic"
    graded = {"full": "fully evaluated", "maths": "maths-only evaluation",
              "ungraded": "NOT EVALUATED"}.get(chosen.get("eval", "ungraded"), "unknown")
    reason = (
        f"{chosen['id']} via {runtime}: needs ~{est} GB ({sizer}), "
        f"RAM {total or '?'} GB, ctx {n_ctx} — {graded}."
    )

    # How well the chosen model is actually PROVEN, said out loud (2026-08-15).
    # Selection is ranked by capability and filtered by RAM; neither is evidence.
    # Before this, an 8 GB machine quietly got phi4-mini (15/31 maths) or a model
    # that had never been evaluated, and nothing on screen distinguished that from
    # the fully-graded pilot model. A parent cannot judge what they are not told.
    status = chosen.get("eval", "ungraded")
    detail = chosen.get("eval_note", "")
    if status == "ungraded":
        warnings.append(
            f"{chosen['id']} has NEVER been through Mentar's evaluation suite — its "
            "teaching quality and safety behaviour are unmeasured. It is offered because "
            "it fits this machine, not because it is known to work."
        )
    elif status == "maths":
        warnings.append(
            f"{chosen['id']}: {detail}. Its SAFETY behaviour has not been graded — only "
            "gemma2-9b and gemma4-12b have full grades (docs/EVAL_RESULTS.md)."
        )

    if chosen.get("reasoning"):
        warnings.append(f"{chosen['id']} is a reasoning model — think:false will be set.")
    if runtime == "gguf" and _has_avx2() is False:
        warnings.append(
            "CPU lacks AVX2 — stock llama-cpp-python may crash (Illegal instruction); "
            "build from source (-DGGML_NATIVE=ON -DGGML_AVX2=OFF). See docs/hardware-requirements.md."
        )

    return Selection(model=chosen, runtime=runtime, est_ram_gb=est, total_ram_gb=total,
                     fits=fits, reason=reason, warnings=warnings)
