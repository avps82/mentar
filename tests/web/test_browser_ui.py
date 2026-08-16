"""Headless-Chromium checks for the two UI behaviours nothing else can prove.

Everything else in tests/web/ exercises Flask routes: it can prove what the
SERVER did, never what the browser then does with it. Two 2026-08-14 fixes live
entirely on the far side of that line, and both were shipped reasoned-but-unseen
until the maintainer asked for real verification:

  1. The Settings country master switch. The server side was always test-covered;
     the reported bug ("the country toggle doesn't disable all the subjects under
     it") was in the JS, which re-fetched the listing and repainted from a
     possibly-cached response.
  2. The idle nudge on "💡 Show me how" (nudge.js). A timer, a class and a
     caption -- there is no HTTP request to assert on.

Driven over the Chrome DevTools Protocol with websocket-client; no selenium,
no playwright, no npm. Skips cleanly where chromium or websocket-client is
absent, so CI without a browser stays green rather than silently passing a test
that never ran.

    python3 tests/web/test_browser_ui.py
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))


def _skip_unless_browser():
    import pytest

    for mod in ("flask", "websocket"):
        try:
            __import__(mod)
        except ImportError:
            pytest.skip(f"{mod} not installed")
    if shutil.which("chromium") is None:
        pytest.skip("chromium not installed (browser checks are opt-in on the host)")


class _Server:
    """The real app on an ephemeral port, every pack enabled, LLM stubbed."""

    def __init__(self):
        import importlib

        from werkzeug.serving import make_server

        os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "browser.db")
        os.environ.pop("MENTAR_PACK_STATE", None)
        import mentar.web.app as app_mod
        app_mod = importlib.reload(app_mod)
        # Country tabs need country packs, and the default is General-only.
        state = pathlib.Path(tempfile.mkdtemp()) / "pack_state.json"
        state.write_text(
            json.dumps({"enabled": [p["key"] for p in app_mod._all_packs_with_state()]}),
            encoding="utf-8",
        )
        os.environ["MENTAR_PACK_STATE"] = str(state)
        app_mod = importlib.reload(app_mod)
        app_mod._llm_call_cached = lambda messages: "stub tutor reply"
        app_mod._SETUP_GATE_BYPASS = True

        self.app_mod = app_mod
        self.state_path = state
        self._srv = make_server("127.0.0.1", 0, app_mod.app, threaded=True)
        self.url = f"http://127.0.0.1:{self._srv.server_port}"
        self._thread = threading.Thread(target=self._srv.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        self._srv.shutdown()
        self._thread.join(timeout=5)


class _Browser:
    """A very small CDP client: navigate, evaluate, advance virtual time."""

    def __init__(self):
        import websocket

        self.profile = tempfile.mkdtemp()
        # stderr is captured rather than discarded: when chromium fails to come
        # up, its own message is the only thing that says why (a snap-confined
        # binary refusing --user-data-dir, a missing shared library, ...). It
        # used to go to DEVNULL, so CI showed a bare timeout and no cause.
        self._stderr = tempfile.NamedTemporaryFile(  # noqa: SIM115 -- lives as long as the browser
            prefix="chromium-stderr-", suffix=".log", delete=False, mode="w+",
        )
        self.proc = subprocess.Popen(
            ["chromium", "--headless", "--disable-gpu", "--no-sandbox",
             f"--user-data-dir={self.profile}", "--remote-debugging-port=0",
             "--remote-allow-origins=*", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=self._stderr,
        )
        # Everything after the spawn must clean the process up on failure. A
        # chromium left running per failed connect is a leak CI would accumulate
        # silently -- found in this session's own audit: a browser spawned by a
        # scratchpad probe whose websocket handshake raised was still alive 37
        # minutes later.
        try:
            port_file = pathlib.Path(self.profile) / "DevToolsActivePort"
            for _ in range(150):
                if port_file.exists() and "\n" in port_file.read_text():
                    break
                time.sleep(0.1)
            else:
                raise RuntimeError(
                    "chromium never reported a debugging port in 15s. Its stderr:\n"
                    + self._read_stderr()
                )
            port = int(port_file.read_text().splitlines()[0])
            # DevToolsActivePort appears BEFORE the about:blank page target is
            # registered, so /json can answer with an empty list or with only
            # non-page targets for a moment. Taking the first response raised a
            # bare StopIteration out of the `next()` -- flaky by machine speed,
            # and it failed exactly once in seven on a CI runner (2026-08-16).
            # Poll for the page instead of assuming it is already there.
            page, targets = None, []
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json") as r:
                        targets = json.load(r)
                except Exception:
                    targets = []
                page = next((t for t in targets if t.get("type") == "page"), None)
                if page:
                    break
                time.sleep(0.1)
            if page is None:
                raise RuntimeError(
                    "chromium reported a debugging port but never a page target in 15s. "
                    f"Last /json response: {targets!r}. Its stderr:\n" + self._read_stderr()
                )
            self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)
        except Exception:
            # Clean up, but NEVER let a cleanup failure replace the real error.
            # It did: headless chromium can ignore SIGTERM, so proc.wait(timeout=10)
            # raised TimeoutExpired and CI reported *that* instead of the startup
            # failure underneath it -- an unreadable red with the cause discarded
            # (2026-08-16). kill() rather than terminate(), and swallow whatever
            # cleanup throws so the original exception propagates.
            try:
                self.proc.kill()
                self.proc.wait(timeout=10)
            except Exception:
                pass
            raise
        self._id = 0

    def _read_stderr(self) -> str:
        try:
            self._stderr.flush()
            return pathlib.Path(self._stderr.name).read_text(errors="replace")[-2000:] or "(empty)"
        except Exception as exc:  # pragma: no cover -- diagnostics must never mask the real error
            return f"(could not read chromium stderr: {exc!r})"

    def send(self, method, **params):
        self._id += 1
        self.ws.send(json.dumps({"id": self._id, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self._id:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    def js(self, expression):
        r = self.send("Runtime.evaluate", expression=expression,
                      returnByValue=True, awaitPromise=True)
        result = r.get("result", {})
        if result.get("subtype") == "error" or "exceptionDetails" in r:
            raise RuntimeError(f"JS error: {r}")
        return result.get("value")

    def goto(self, url):
        self.send("Page.navigate", url=url)
        self.wait_for("document.readyState === 'complete'")

    def wait_for(self, expression, timeout=15.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.js(f"!!({expression})"):
                return True
            time.sleep(0.1)
        raise AssertionError(f"timed out waiting for: {expression}")

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass          # a dead socket must never stop us killing the browser
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=10)
        shutil.rmtree(self.profile, ignore_errors=True)
        # The captured-stderr file is delete=False (it must outlive the process
        # so a startup failure can be read back), so close it here.
        try:
            self._stderr.close()
            pathlib.Path(self._stderr.name).unlink(missing_ok=True)
        except Exception:
            pass


def test_country_master_switch_turns_off_every_row_under_it():
    """The maintainer-reported bug, in a real browser: flip a country's master
    switch and every per-grade switch in that panel must visibly follow -- and the
    SERVER must agree, so a UI that lies about what it saved still fails."""
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.goto(server.url + "/settings")
        browser.wait_for("document.querySelectorAll('#curricula-toggle-list .tab-btn').length > 1")

        # Open Australia's tab (the biggest pack -- 25 templates behind one switch).
        browser.js("""
            [...document.querySelectorAll('.tab-btn')]
              .find(b => b.textContent.includes('Australia')).click()
        """)
        browser.wait_for("document.querySelectorAll('.curricula-row input').length > 5")
        rows_before = browser.js("""
            [...document.querySelectorAll('.curricula-row input')].filter(i => i.checked).length
        """)
        assert rows_before > 5, f"expected AU's rows to start on, got {rows_before}"

        browser.js("document.querySelector('.curricula-master input').click()")
        # Wording changed 2026-08-15: a toggle applies live, so it no longer says
        # "restart Mentar to apply" and no longer reports a bulk count.
        browser.wait_for(
            "document.querySelector('.curricula-master .hint').textContent.includes('Off')"
        )

        still_on = browser.js(
            "[...document.querySelectorAll('.curricula-row input')].filter(i => i.checked).length"
        )
        assert still_on == 0, f"{still_on} of AU's per-grade switches stayed on after the master went off"
        assert browser.js("document.querySelector('.curricula-master input').indeterminate") is False

        # ...and the server really has them off (a UI that lies must not pass).
        listing = json.load(urllib.request.urlopen(server.url + "/settings/curricula"))
        au = [c for c in listing["curricula"] if c["country"] == "AU"]
        assert au and not any(c["enabled"] for c in au), "server still reports AU packs enabled"
        others = [c for c in listing["curricula"] if c["country"] not in (None, "AU")]
        assert all(c["enabled"] for c in others), "the master switch reached outside its own country"
    finally:
        if browser:
            browser.close()
        server.stop()


def test_a_toggle_shows_it_is_working_before_it_says_on_or_off():
    """2026-08-15 (maintainer): "when toggle happens... maybe a spinner next to it
    before ON or OFF".

    A toggle re-scans every curriculum template server-side (~1.4s). Silent for that
    long reads as broken, and the natural response to a broken switch is to click it
    again -- which races a rescan already in flight. So the switch must LOOK busy and
    must not be clickable while it is.

    Measured in a real browser because the whole bug is about what is on screen
    during the gap; nothing about the code shows it.
    """
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.goto(server.url + "/settings")
        browser.wait_for("document.querySelectorAll('#curricula-toggle-list .tab-btn').length > 1")
        browser.js("""
            [...document.querySelectorAll('.tab-btn')]
              .find(b => b.textContent.includes('Australia')).click()
        """)
        browser.wait_for("document.querySelectorAll('.curricula-row input').length > 5")

        # Click and read the state in the SAME evaluation, before the fetch resolves.
        during = browser.js("""
            (() => {
                const row = document.querySelector('.curricula-row');
                row.querySelector('input').click();
                return {
                    busy: row.querySelector('.hint').classList.contains('toggle-busy'),
                    text: row.querySelector('.hint').textContent,
                    locked: row.querySelector('input').disabled,
                };
            })()
        """)
        assert during["busy"], "no spinner while the toggle was in flight"
        assert "Saving" in during["text"], during["text"]
        assert during["locked"], "the switch stayed clickable mid-flight -- a second click races it"

        browser.wait_for(
            "!document.querySelector('.curricula-row .hint').classList.contains('toggle-busy')"
        )
        after = browser.js("""
            (() => {
                const row = document.querySelector('.curricula-row');
                return {text: row.querySelector('.hint').textContent,
                        locked: row.querySelector('input').disabled};
            })()
        """)
        assert after["text"] in ("On", "Off"), after["text"]
        assert not after["locked"], "the switch must be usable again once saved"
    finally:
        if browser:
            browser.close()
        server.stop()


def test_idle_nudge_appears_on_a_live_question_then_stops():
    """nudge.js: with a question on screen and no input, the "💡 Show me how"
    button is drawn to the child's attention -- once, then again, then never.

    Virtual time fast-forwards the 20s/45s timers, so this costs no wall clock.
    """
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.goto(server.url + "/")
        browser.js("""
            [...document.querySelectorAll('button[type=submit]')]
              .find(b => b.closest('form').querySelector('[value=fractions]')).click()
        """)
        browser.wait_for("document.getElementById('help-btn')")
        assert browser.js("document.getElementById('nudge-hint').hidden") is True, "quiet at first"
        assert browser.js("document.getElementById('help-btn').textContent") == "💡 Show me how"

        # Advance ~22s of page time: the first nudge fires, the second has not.
        browser.send("Emulation.setVirtualTimePolicy",
                     policy="advance", budget=22000, waitForNavigation=False)
        browser.wait_for("!document.getElementById('nudge-hint').hidden")
        assert browser.js("document.getElementById('help-btn').classList.contains('is-nudging')")
        first = browser.js("document.getElementById('nudge-hint').textContent")
        assert "Show me how" in first, first

        # Typing an answer is a sign of life: everything resets and goes quiet.
        browser.js("""
            (() => { const el = document.querySelector('#turn-area input, #turn-area textarea');
                     el.focus(); el.dispatchEvent(new Event('input', {bubbles: true})); })()
        """)
        browser.wait_for("document.getElementById('nudge-hint').hidden")
        assert not browser.js("document.getElementById('help-btn').classList.contains('is-nudging')")
    finally:
        if browser:
            browser.close()
        server.stop()


def test_pressing_show_me_how_shows_that_something_is_happening():
    """2026-08-15 (maintainer): "Show me how doesn't show something is happening
    once clicked. This leads to double click as there is no indicator... kids will
    do this a lot more times." Both cues are asserted WHILE the request is still
    in flight, with the model call held open, which is the only moment they exist.
    """
    _skip_unless_browser()
    import threading

    server, browser = _Server(), None
    release = threading.Event()

    def slow_llm(messages):
        release.wait(timeout=10)
        return "explanation"

    server.app_mod._llm_call_cached = slow_llm
    try:
        browser = _Browser()
        browser.goto(server.url + "/choose")
        browser.js("""(() => {const f=[...document.querySelectorAll('form')]
            .find(f => f.querySelector('[value=fractions]')); f.querySelector('button').click();})()""")
        browser.wait_for("document.getElementById('help-btn')")

        assert browser.js("getComputedStyle(document.getElementById('thinking')).display") == "none"
        assert browser.js("document.getElementById('help-btn').disabled") is False

        browser.js("document.getElementById('help-btn').click()")
        # In flight: the shared line is visible and the pressed button is out of action.
        browser.wait_for("getComputedStyle(document.getElementById('thinking')).display !== 'none'")
        assert browser.js("document.getElementById('help-btn').disabled") is True, (
            "the button a child just pressed must not accept a second press"
        )
        assert browser.js("document.getElementById('help-btn').classList.contains('htmx-request')")
        assert "thinking" in browser.js("document.getElementById('thinking').textContent").lower()

        release.set()
        # ...and it all clears once the turn lands.
        browser.wait_for("getComputedStyle(document.getElementById('thinking')).display === 'none'")
        assert browser.js("document.getElementById('help-btn').disabled") is False
    finally:
        release.set()
        if browser:
            browser.close()
        server.stop()


def test_picker_cards_in_a_row_are_the_same_height():
    """2026-08-15 audit, maintainer-reported ("these cards are not even sized,
    looks odd") and then MEASURED: 33 of 40 rows held cards of different heights
    (210 / 225 / 240px). Each card is wrapped in its own <form>, so the form is
    the grid item -- the grid stretched the form and the button inside kept its
    content height. Only a browser can see this; no server test can."""
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.goto(server.url + "/choose")
        browser.wait_for("document.querySelectorAll('.subject-card').length > 10")
        uneven = browser.js("""
            (() => {
              const rows = {};
              document.querySelectorAll('.subject-card').forEach(c => {
                const r = c.getBoundingClientRect();
                (rows[Math.round(r.top)] = rows[Math.round(r.top)] || []).push(Math.round(r.height));
              });
              return Object.entries(rows)
                .filter(([, hs]) => new Set(hs).size > 1)
                .map(([top, hs]) => top + ': ' + hs.join('/'));
            })()
        """)
        assert uneven == [], f"rows with mismatched card heights: {uneven[:5]}"
    finally:
        if browser:
            browser.close()
        server.stop()


_PAGES = ("/choose", "/learn", "/progress", "/parent", "/settings", "/setup")

_PAGE_PROBE = """(() => {
  const out = {overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
               offenders: [], tiny: [], dupHeads: []};
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) return;
    if (r.right > window.innerWidth + 1 || r.left < -1)
      out.offenders.push(el.tagName.toLowerCase() + '.' + (el.className || '').toString().split(' ')[0]);
  });
  // WCAG 2.5.8: 24x24 minimum. A control inside a <label> is targeted BY that
  // label (the mc4 radios are 17px inside a 720x50 label), so measure the label.
  document.querySelectorAll('a, button, select, input:not([type=hidden])').forEach(el => {
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const label = el.closest('label');
    const box = label ? label.getBoundingClientRect() : r;
    if (box.height < 24 || box.width < 24)
      out.tiny.push(((el.textContent || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 30))
                    + ' ' + Math.round(box.width) + 'x' + Math.round(box.height));
  });
  const heads = [...document.querySelectorAll('h1,h2,h3,h4')].map(h => h.textContent.trim());
  heads.forEach((h, i) => { if (i && h === heads[i-1]) out.dupHeads.push(h); });
  out.offenders = [...new Set(out.offenders)];
  return out;})()"""


def test_every_page_is_laid_out_sanely():
    """One measured sweep of every screen, for the failure classes this project
    has actually shipped: content escaping the viewport, a heading repeating
    because rows were mis-sorted (Singapore rendered 21 headings for 31 rows),
    and interactive targets under WCAG 2.5.8's 24x24 minimum (footer links were
    15px tall, Settings buttons 21px -- on a tablet, for a child).

    No route test can see any of it: the server sent correct HTML every time."""
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        # start a session so /learn and /progress have real content to measure
        browser.goto(server.url + "/choose")
        browser.js("""(() => {const f = [...document.querySelectorAll('form')]
            .find(f => f.querySelector('[value=au_acara_year11_chemistry]'));
            f.querySelector('button').click();})()""")
        browser.wait_for("document.getElementById('help-btn')")

        problems = []
        for path in _PAGES:
            browser.goto(server.url + path)
            if path == "/settings":
                browser.wait_for("document.querySelectorAll('.tab-btn').length > 1")
            r = browser.js(_PAGE_PROBE)
            if r["overflowX"]:
                problems.append(f"{path}: the page scrolls horizontally")
            if r["offenders"]:
                problems.append(f"{path}: elements outside the viewport: {r['offenders'][:4]}")
            if r["dupHeads"]:
                problems.append(f"{path}: a heading repeats back-to-back: {r['dupHeads'][:3]}")
            if r["tiny"]:
                problems.append(f"{path}: targets under 24x24: {r['tiny'][:5]}")
        assert not problems, "\n".join(problems)
    finally:
        if browser:
            browser.close()
        server.stop()


if __name__ == "__main__":
    test_country_master_switch_turns_off_every_row_under_it()
    print("  ✓ test_country_master_switch_turns_off_every_row_under_it")
    test_idle_nudge_appears_on_a_live_question_then_stops()
    print("  ✓ test_idle_nudge_appears_on_a_live_question_then_stops")
    test_picker_cards_in_a_row_are_the_same_height()
    print("  ✓ test_picker_cards_in_a_row_are_the_same_height")
    test_pressing_show_me_how_shows_that_something_is_happening()
    print("  ✓ test_pressing_show_me_how_shows_that_something_is_happening")
    test_every_page_is_laid_out_sanely()
    print("  ✓ test_every_page_is_laid_out_sanely")


def test_the_worked_example_sits_inside_the_bubble_and_matches_its_text_size():
    """2026-08-15 (maintainer, two screenshots): consecutive Explain-more presses
    "look completely different... font size is definitely different", and the card
    had no read-aloud button -- "the explain more should be inside the top card box
    and have an audio in it".

    Two causes, both only visible on screen:
      * the card rendered as a SEPARATE box after the bubble, so it read as an
        unrelated panel rather than more of the same explanation;
      * .steps-pre-line is 1.4rem -- right for long-division digit columns, but
        applied to prose sitting under a ~1rem bubble it looked like another feature.

    Measured, not asserted from CSS: computed font sizes from the live page.
    """
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.goto(server.url + "/")
        browser.js("""
            [...document.querySelectorAll('.subject-card, a')]
              .find(a => /fraction/i.test(a.textContent))?.click()
        """)
        browser.wait_for("!!document.querySelector('.question-text')")
        # Ask for help, then unpack it -- the two presses from the report.
        browser.js("""
            [...document.querySelectorAll('button, a')]
              .find(b => /show me how/i.test(b.textContent))?.click()
        """)
        # Wait for the ELABORATE FORM, not `.feedback`: the first turn already
        # renders a .feedback bubble (the welcome message), so waiting on that
        # returned instantly, the querySelector below ran before the help
        # response landed, and `if (f)` swallowed the null -- the click never
        # happened and the test timed out 20s later pointing at .steps-pre.
        browser.wait_for("!!document.querySelector('.elaborate-form button')")
        browser.js("document.querySelector('.elaborate-form button').click()")
        browser.wait_for("!!document.querySelector('.feedback .steps-pre')", timeout=20)

        shape = browser.js("""
            (() => {
                const fb = document.querySelector('.feedback');
                const card = fb.querySelector('.steps-pre');
                const line = card.querySelector('.steps-pre-line');
                const prose = fb.querySelector('.msg-text');
                return {
                    nested: !!card,
                    hasSpeaker: !!fb.querySelector('.tts-btn'),
                    cardPx: line ? parseFloat(getComputedStyle(line).fontSize) : null,
                    prosePx: parseFloat(getComputedStyle(prose).fontSize),
                    wrap: card.classList.contains('steps-pre-wrap'),
                };
            })()
        """)
        assert shape["nested"], "the card must render INSIDE .feedback, not as a separate box"
        assert shape["hasSpeaker"], "the bubble holding the card must offer read-aloud"
        if shape["wrap"]:   # a method card; a step GRID keeps its large digits
            assert shape["cardPx"] == shape["prosePx"], (
                f"card {shape['cardPx']}px vs prose {shape['prosePx']}px -- "
                "the size mismatch the maintainer screenshotted"
            )
    finally:
        if browser:
            browser.close()
        server.stop()
