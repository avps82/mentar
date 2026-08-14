"""T1 — autoselect runtime ordering for the llama.app runtime.

Auto = Ollama → llama.app (`llama serve`) → in-process GGUF. Explicit prefer is honoured
(and warns if the binary is absent). gguf/llama_app candidates must carry a GGUF.

Inline smoke runner:
    python3 tests/inference/test_autoselect_llama_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

import mentar.inference.autoselect as A  # noqa: E402


def _patch(present: set[str]) -> None:
    """Simulate which() availability + deterministic sizing/AVX detection (module attrs).

    Rebinds autoselect's OWN `shutil` name, never `shutil.which` on the shared module
    object: the latter leaked for the rest of the pytest session (no teardown here),
    and on 2026-08-14 it silently skipped a later test that checks for `node`.
    autoselect uses shutil for which() only (two call sites).
    """
    A.shutil = SimpleNamespace(
        which=lambda name: f"/usr/bin/{name}" if name in present else None
    )
    A._need_gb = lambda model, runtime, n_ctx: (float(model.get("params_b", 7)), True)
    A._has_avx2 = lambda: True


ROSTER = A.load_roster()


def test_auto_prefers_llama_app_when_no_ollama():
    _patch({"llama"})
    sel = A.select(ROSTER, prefer="auto", ram_gb=32)
    assert sel.runtime == "llama_app"
    assert sel.model.get("hf_repo") and sel.model.get("hf_file")


def test_auto_prefers_ollama_over_llama_app():
    _patch({"ollama", "llama"})
    assert A.select(ROSTER, prefer="auto", ram_gb=32).runtime == "ollama"


def test_auto_falls_to_gguf_when_neither():
    _patch(set())
    sel = A.select(ROSTER, prefer="auto", ram_gb=32)
    assert sel.runtime == "gguf"
    assert sel.model.get("hf_repo") and sel.model.get("hf_file")


def test_prefer_llama_app_explicit_warns_when_absent():
    _patch(set())
    sel = A.select(ROSTER, prefer="llama_app", ram_gb=32)
    assert sel.runtime == "llama_app"
    assert any("llama" in w.lower() for w in sel.warnings)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} llama_app autoselect tests passed.")
