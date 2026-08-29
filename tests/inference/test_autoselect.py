"""Tests for mentar.inference.autoselect + the vetted roster.

Selection logic is exercised offline by stubbing the gguf-parser sizing (_need_gb) and
runtime/AVX2 detection — no binary, no network.

Contract checks:
    - Roster loads, is rank-sorted, and every entry is installable (ollama_tag or hf GGUF).
    - select() picks the highest-ranked model that fits the given RAM; smaller RAM -> smaller model.
    - runtime auto = ollama if present else gguf; gguf filters to models with a GGUF.
    - reasoning model -> think:false warning; gguf + no-AVX2 -> rebuild warning.
    - Nothing fits -> smallest model + a warning (never crashes).

Inline smoke runner:
    python3 tests/inference/test_autoselect.py
"""

from __future__ import annotations

import pathlib
import sys
from types import SimpleNamespace

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.inference import autoselect as A  # noqa: E402


def _patch(monkeypatch, *, ollama: bool, avx2, need_per_b=1.0):
    """Stub sizing + detection. need_per_b GB per billion params."""
    def fake_need(model, runtime, n_ctx):
        return (model.get("params_b", 7) * need_per_b, True)
    setters = [
        ("_need_gb", fake_need),
        ("_has_avx2", lambda: avx2),
    ]
    for name, val in setters:
        (monkeypatch.setattr(A, name, val) if monkeypatch
         else setattr(A, name, val))
    which = (lambda x: "/usr/bin/ollama" if (x == "ollama" and ollama) else None)
    # Rebind autoselect's OWN `shutil` name (which() is its only use of it), never
    # `which` on the shared module object: patching the real module leaked past this
    # file -- monkeypatch is None here in practice, so the else-branch ran and stuck
    # -- and on 2026-08-14 it silently skipped a later test that checks for `node`.
    stub = SimpleNamespace(which=which)
    (monkeypatch.setattr(A, "shutil", stub) if monkeypatch
     else setattr(A, "shutil", stub))


def _roster():
    return A.load_roster()


def test_roster_valid():
    r = _roster()
    assert len(r) >= 3
    assert r == sorted(r, key=lambda m: m["rank"])           # rank-sorted
    ranks = [m["rank"] for m in r]
    assert len(ranks) == len(set(ranks))                      # unique ranks
    for m in r:
        assert m.get("id") and "params_b" in m
        assert m.get("ollama_tag") or (m.get("hf_repo") and m.get("hf_file"))


def test_picks_best_that_fits_big_ram(monkeypatch=None):
    _patch(monkeypatch, ollama=True, avx2=True)
    sel = A.select(_roster(), prefer="auto", ram_gb=32)
    assert sel.runtime == "ollama"
    assert sel.model["rank"] == 1 and sel.fits                # top model fits on 32 GB


def test_smaller_ram_picks_smaller(monkeypatch=None):
    _patch(monkeypatch, ollama=True, avx2=True)
    big = A.select(_roster(), prefer="auto", ram_gb=32).model
    small = A.select(_roster(), prefer="auto", ram_gb=6).model
    assert small["params_b"] <= big["params_b"]
    assert small["params_b"] * 1.0 <= 6 * A.COMFORT + 1e-9


def test_runtime_auto_falls_back_to_gguf(monkeypatch=None):
    _patch(monkeypatch, ollama=False, avx2=True)
    sel = A.select(_roster(), prefer="auto", ram_gb=16)
    assert sel.runtime == "gguf"
    assert sel.model.get("hf_repo") and sel.model.get("hf_file")   # gguf-installable


def test_reasoning_warns(monkeypatch=None):
    """A reasoning model must announce itself when selected.

    Was: pick at 64 GB and assume the top-ranked model is a reasoning one. That
    stopped being true on 2026-08-29 when gemma4-12b was demoted for returning
    empty content through Ollama's /v1 -- and the assumption failing is GOOD
    news (no reasoning model is auto-picked at any tier now), so the test must
    assert the WARNING, not the roster's shape. Same fix as the eval-class
    tests below."""
    _patch(monkeypatch, ollama=True, avx2=True)
    reasoning = [m for m in _roster() if m.get("reasoning")]
    assert reasoning, "roster has no reasoning model — this test is meaningless"
    sel = A.select(reasoning, prefer="auto", ram_gb=64)
    assert sel.model.get("reasoning")
    assert any("reasoning" in w for w in sel.warnings)


def test_no_reasoning_model_is_ever_the_AUTO_pick(monkeypatch=None):
    """gemma4-12b was rank 1 and is unusable through Ollama's /v1 (ignores
    think:false -> empty content), so a fresh install on the runtime the docs
    recommend got a default that could not answer. Nothing reasoning-based
    should win the automatic pick at any RAM tier; explicit --model still works.
    """
    _patch(monkeypatch, ollama=True, avx2=True)
    for ram in (4, 6, 8, 16, 32, 64, 128):
        sel = A.select(_roster(), prefer="ollama", ram_gb=ram)
        assert not sel.model.get("reasoning"), (
            f"{ram}GB auto-picked {sel.model['id']}, a reasoning model")


def test_gguf_no_avx2_warns(monkeypatch=None):
    _patch(monkeypatch, ollama=False, avx2=False)
    sel = A.select(_roster(), prefer="gguf", ram_gb=16)
    assert sel.runtime == "gguf"
    assert any("AVX2" in w for w in sel.warnings)


def test_nothing_fits_picks_smallest(monkeypatch=None):
    _patch(monkeypatch, ollama=True, avx2=True)
    sel = A.select(_roster(), prefer="auto", ram_gb=0.4)           # below even the 0.5B (~0.5 GB)
    assert sel.model["params_b"] == min(m["params_b"] for m in _roster())
    assert not sel.fits and sel.warnings


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} autoselect tests passed.")


# ── Eval status must be stated, not implied (2026-08-15) ─────────────────────
# Auto-selection ranks by capability and filters by RAM. Neither is EVIDENCE. An
# 8 GB machine silently got phi4-mini (15/31 maths) or an ungraded model, with
# nothing on screen to distinguish that from the fully-graded pilot model.

# These three used to pick a model by RAM figure and HOPE the roster put the
# right eval class at that boundary. That coupling broke the day a fully-graded
# 4 GB model (qwen3.5-4b, 2026-08-26 eval) entered the roster: the 8 GB pick
# landed on it and the "maths-only" test failed for reasons that had nothing to
# do with the warning under test. (It only worked before because _patch's
# no-monkeypatch branch permanently sticks a fake _need_gb -- see its comment.)
# So: filter the roster to the eval class under test and give RAM headroom --
# the tests are about the WARNINGS a class carries, never about which class a
# RAM figure happens to buy.

def _by_eval(kind):
    from mentar.inference.autoselect import load_roster
    ms = [m for m in load_roster() if m.get("eval") == kind]
    assert ms, f"roster no longer has any eval={kind} model — test is meaningless"
    return ms


def test_ungraded_model_says_so_loudly():
    from mentar.inference.autoselect import select

    sel = select(_by_eval("ungraded"), prefer="ollama", ram_gb=64)
    assert sel.model.get("eval") == "ungraded", sel.model["id"]
    blob = " ".join(sel.warnings).lower()
    assert "never been through" in blob and "unmeasured" in blob, sel.warnings
    assert "not evaluated" in sel.reason.lower()


def test_maths_only_model_admits_safety_is_not_graded():
    from mentar.inference.autoselect import select

    sel = select(_by_eval("maths"), prefer="ollama", ram_gb=64)
    assert sel.model.get("eval") == "maths", sel.model["id"]
    assert any("SAFETY behaviour has not been graded" in w for w in sel.warnings), sel.warnings


def test_fully_graded_model_carries_no_eval_warning():
    """The warning must MEAN something -- if it fired for everything it would be
    noise and get ignored, which is how real warnings stop working."""
    from mentar.inference.autoselect import select

    sel = select(_by_eval("full"), prefer="ollama", ram_gb=64)
    assert sel.model.get("eval") == "full", sel.model["id"]
    blob = " ".join(sel.warnings).lower()
    assert "never been through" not in blob and "not been graded" not in blob


def test_every_roster_entry_declares_its_eval_status():
    """A new model added without a status must fail here rather than default to
    looking trustworthy."""
    from mentar.inference.autoselect import load_roster

    missing = [m["id"] for m in load_roster()
               if m.get("eval") not in ("full", "maths", "ungraded")]
    assert not missing, f"roster entries with no honest eval status: {missing}"
