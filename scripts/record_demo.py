#!/usr/bin/env python3
"""Record a short animated GIF of a real Mentar session, for launch pages.

    python3 scripts/record_demo.py            # uses whatever backend is configured
    python3 scripts/record_demo.py --stub     # no model needed; LLM prose is FAKE

Drives the real web app in headless Chromium over CDP and screenshots the
sequence that shows what makes Mentar different:

    pick a subject -> a question -> a WRONG answer -> the gentle retry ->
    "Show me how" -> the computed worked example

Writes ``docs/img/demo.gif`` plus the individual frames beside it.

WHICH PARTS ARE REAL
    The questions, the answer checking, the retry and the worked-example card
    are all deterministic engine output — they are real in every run, including
    --stub. Only the tutor's PROSE comes from the model.

    So: --stub produces a structurally honest recording with placeholder
    wording, which is fine for checking layout and timing but MUST NOT be
    published as if a model wrote it. For anything public, run WITHOUT --stub
    on a machine with a working backend (`mentar setup` first).

The script says which mode it ran in, and stamps the GIF's own metadata, so a
stub recording cannot be mistaken for a real one later.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys
import tempfile
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests" / "web"))

OUT_DIR = REPO / "docs" / "img"
PORT = int(os.environ.get("MENTAR_DEMO_PORT", "5099"))
BASE = f"http://127.0.0.1:{PORT}"


def _start_server(stub: bool) -> subprocess.Popen:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src")
    env.setdefault("MENTAR_DB_PATH", str(pathlib.Path(tempfile.mkdtemp()) / "demo.db"))
    code = (
        # _SETUP_GATE_BYPASS is a module attribute (not an env var): without it
        # every route redirects to /setup and the recording is one page long.
        "import mentar.web.app as A; A._SETUP_GATE_BYPASS = True;"
        # Deliberately SUBJECT-AGNOSTIC. A fixed subject-specific hint (the
        # first draft said "the bottom number of each fraction") appears under
        # whatever question the engine actually drew — it read as nonsense over
        # "98 + 87" and would have looked like a broken product on a launch page.
        + ("A._llm_call_cached = lambda m: "
           "'Not quite — have another look at the working, then try again.';"
           if stub else "")
        + f"A.app.run(port={PORT}, threaded=True)"
    )
    proc = subprocess.Popen([sys.executable, "-c", code], env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    import urllib.error
    import urllib.request
    for _ in range(200):
        if proc.poll() is not None:
            raise RuntimeError("demo server died on startup:\n"
                               + (proc.stderr.read().decode(errors="replace")[-1500:]))
        try:
            urllib.request.urlopen(BASE + "/", timeout=1)
            return proc
        except urllib.error.HTTPError:
            return proc          # any HTTP answer means it is listening
        except Exception:
            time.sleep(0.1)
    proc.kill()
    raise RuntimeError(f"demo server never came up on {BASE}")


def _shot(browser, frames: list, hold: int = 1) -> None:
    """Capture the viewport; `hold` repeats it to slow that beat down."""
    import base64
    import io

    from PIL import Image

    data = browser.send("Page.captureScreenshot", format="png")["data"]
    img = Image.open(io.BytesIO(base64.b64decode(data))).convert("P", palette=1)
    frames.extend([img] * max(1, hold))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stub", action="store_true",
                    help="run without a model; the tutor's PROSE will be fake")
    ap.add_argument("--width", type=int, default=900)
    ap.add_argument("--height", type=int, default=1000)
    args = ap.parse_args()

    from test_browser_ui import _Browser  # the tests' own CDP client

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    server = _start_server(args.stub)
    browser = None
    frames: list = []
    try:
        browser = _Browser()
        browser.send("Emulation.setDeviceMetricsOverride", width=args.width,
                     height=args.height, deviceScaleFactor=1, mobile=False)

        browser.goto(BASE + "/")
        browser.wait_for("document.querySelectorAll('a,button').length > 0")
        _shot(browser, frames, hold=3)                      # the picker

        # The picker is a set of FORMS posting to /choose (not links) — submit
        # the first one, exactly as tapping a subject card does.
        browser.js("(()=>{const f=document.querySelector('form[action=\"/choose\"]');"
                   "if(f) f.submit();})()")
        time.sleep(2.0)
        browser.wait_for("document.querySelector('.question-text, .question') !== null", timeout=30)
        _shot(browser, frames, hold=4)                      # the question

        # A deliberately wrong answer, so the gentle retry is on screen.
        browser.js("(()=>{const i=document.querySelector('input[name=answer]');"
                   "if(i){i.focus();i.value='99';"
                   "i.dispatchEvent(new Event('input',{bubbles:true}));}"
                   "const b=[...document.querySelectorAll('button')]"
                   ".find(x=>/send/i.test(x.textContent));if(b)b.click();})()")
        time.sleep(3.0)
        _shot(browser, frames, hold=4)                      # gentle retry

        # The payoff: "Show me the working" reveals the COMPUTED worked example
        # — engine output, correct by construction, and the thing that makes the
        # never-grades architecture visible in one screen.
        browser.js("(()=>{const b=[...document.querySelectorAll('button,a')]"
                   ".find(x=>/show me the working/i.test(x.textContent));"
                   "if(b)b.click();})()")
        time.sleep(3.0)
        _shot(browser, frames, hold=8)
        browser.js("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.8)
        _shot(browser, frames, hold=8)                      # the working itself

        if not browser.js("/\\d/.test(document.body.innerText) && "
                          "document.querySelectorAll('pre, .steps-pre').length > 0"):
            print("  ! no computed working appeared — the payoff frame may be empty",
                  file=sys.stderr)

        if len(frames) < 4:
            raise RuntimeError("captured too few frames — the flow did not advance")

        for i, f in enumerate(frames[:: max(1, len(frames) // 6)]):
            f.save(OUT_DIR / f"demo_frame_{i}.png")
        gif = OUT_DIR / "demo.gif"
        frames[0].save(gif, save_all=True, append_images=frames[1:],
                       duration=700, loop=0, optimize=True,
                       comment=b"mentar demo (STUBBED PROSE)" if args.stub
                       else b"mentar demo (live model)")
        size = gif.stat().st_size / 1024
        print(f"\n✓ {gif}  ({size:.0f} KB, {len(frames)} frames)")
        print(f"  frames: {OUT_DIR}/demo_frame_*.png")
        if args.stub:
            print("\n⚠ --stub: the tutor's PROSE in this recording is a hard-coded")
            print("  placeholder, not model output. Questions, marking, the retry and")
            print("  the worked example ARE real engine output. Do NOT publish this as")
            print("  a demo of the model — re-run without --stub on a machine with a")
            print("  working backend for anything public.")
        return 0
    finally:
        if browser is not None:
            browser.close()
        server.terminate()
        try:
            server.wait(timeout=10)
        except Exception:
            server.kill()


if __name__ == "__main__":
    raise SystemExit(main())
