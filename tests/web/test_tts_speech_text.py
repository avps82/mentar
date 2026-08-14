"""tts.js's spoken-text normalization (2026-08-14, maintainer listened to a session).

Runs the real static/tts.js under node with a stub window/document — the logic is a
regex chain, and asserting on the file's text instead would prove nothing about what
it actually produces. Skipped where node isn't installed.

Fixes under test:
  - an ALL-CAPS word ("READ", "SAME") was spelled out letter by letter
  - "→" was vocalized as "arrow"
  - A/B/C/D choice letters must STILL be spoken as letters (not lowercased)

──────────────────────────────────────────────────────────────────────────────
Inline smoke runner (python3-runnable without pytest):
    python3 tests/web/test_tts_speech_text.py
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

TTS_JS = pathlib.Path(__file__).resolve().parents[2] / "src" / "mentar" / "web" / "static" / "tts.js"

_HARNESS = """
const fs = require("fs");
const noop = function () {};
const stubEl = {addEventListener: noop, querySelectorAll: function () { return []; }};
global.window = {speechSynthesis: {getVoices: function () { return []; }}};
global.document = {addEventListener: noop, body: stubEl, querySelectorAll: function () { return []; }};
global.localStorage = {getItem: function () { return null; }};
eval(fs.readFileSync(%s, "utf8"));
const cases = %s;
console.log(JSON.stringify(cases.map(window.MentarSpeech.forSpeech)));
"""


def _speak(cases: list[str]) -> list[str]:
    script = _HARNESS % (json.dumps(str(TTS_JS)), json.dumps(cases))
    out = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=True, timeout=30,
    ).stdout
    return json.loads(out)


def test_spoken_text_fixes_caps_and_arrows_but_keeps_choice_letters():
    if shutil.which("node") is None:
        import pytest
        pytest.skip("node not installed (tts.js is browser code)")

    caps, arrow, letters, emoji, dna, atp, genotype = _speak([
        "Which word means the SAME as 'happy'?",
        "In the number 41, what is the value of the digit 4? → 40",
        "A) cheerful. B) upset. C) tiny. D) giant",
        "Yes, that's it — great job! 🎉",
        "Which of these carries genetic information? A) DNA  B) haemoglobin",
        "Which of these is a PRODUCT of respiration? A) ATP energy  B) glucose",
        "Which of these is a GENOTYPE? A) BB  B) brown eyes",
    ])

    assert "same" in caps and "SAME" not in caps, caps
    assert "→" not in arrow and "40" in arrow, arrow
    # A/B/C/D are single letters -> untouched, so the child still hears "A", "B"...
    assert letters.startswith("A) cheerful"), letters
    assert "D) giant" in letters, letters
    assert "🎉" not in emoji, emoji

    # 2026-08-15 audit: senior science added GENUINE acronyms to the corpus
    # (DNA x66, ATP x90, BB x54 as a genotype). Lowercasing those makes the
    # engine read "dna"/"atp" as nonsense words and "BB" as a syllable, so they
    # are held in caps by name while emphasis words around them are not.
    assert "DNA" in dna and "genetic" in dna, dna
    assert "ATP" in atp and "product" in atp, atp        # ATP kept, PRODUCT lowered
    assert "BB" in genotype and "genotype" in genotype, genotype


if __name__ == "__main__":
    test_spoken_text_fixes_caps_and_arrows_but_keeps_choice_letters()
    print("  ✓ test_spoken_text_fixes_caps_and_arrows_but_keeps_choice_letters")
