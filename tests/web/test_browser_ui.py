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
        # isolation: the root conftest already points MENTAR_PACK_STATE at a
        # scratch path. Popping it did the OPPOSITE -- see conftest.py.
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
             # /dev/shm is small in a container; without this chromium can stall
             # or die on startup rather than fall back to disk. Classic CI flag.
             "--disable-dev-shm-usage",
             # Skip first-run work that is pure latency for a throwaway profile.
             "--no-first-run", "--no-default-browser-check",
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
            # 40s, not 15: a cold CI runner starting its first chromium exceeded
            # 15s and failed 1-of-8 (run 31950304893) -- and each test launches
            # its own browser, so adding a check adds a chance to hit it. This
            # returns the instant the file appears, so a fast machine pays
            # nothing for the larger ceiling.
            for _ in range(400):
                if port_file.exists() and "\n" in port_file.read_text():
                    break
                time.sleep(0.1)
            else:
                raise RuntimeError(
                    "chromium never reported a debugging port in 40s. Its stderr:\n"
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


def test_topic_strand_headings_group_the_rows_beneath_them():
    """The strand grouping shipped 2026-08-21 (maintainer: "Are we doing sub
    topics in topic selection??"). Route tests prove the HTML contains headings;
    only a browser proves each heading actually SITS ABOVE its own rows and that
    none render blank or collapsed.

    The pilot page in _PAGES has no strands, so the grouped path was never once
    rendered in a browser -- this covers it. Failure classes borrowed from ones
    this project shipped before: a heading repeating back-to-back (Singapore's
    21-headings-for-31-rows bug) and zero-height text."""
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.goto(server.url + "/topics?subject=au_acara_year3_maths")
        browser.wait_for("document.querySelectorAll('.strand-heading').length > 0")
        r = browser.js("""
            (() => {
              const heads = [...document.querySelectorAll('.strand-heading')];
              const rows  = [...document.querySelectorAll('.topic-row')];
              const invisible = heads.filter(h => {
                const b = h.getBoundingClientRect();
                return b.height < 8 || !h.textContent.trim();
              }).map(h => h.textContent.trim() || '(empty)');
              // every heading must be followed by at least one row before the next heading
              const tops = heads.map(h => h.getBoundingClientRect().top);
              const rowTops = rows.map(r => r.getBoundingClientRect().top);
              const barren = [];
              heads.forEach((h, i) => {
                const start = tops[i], end = (i + 1 < tops.length) ? tops[i + 1] : Infinity;
                if (!rowTops.some(t => t > start && t < end)) barren.push(h.textContent.trim());
              });
              const texts = heads.map(h => h.textContent.trim());
              const dup = texts.filter((t, i) => i && t === texts[i - 1]);
              return {n: heads.length, rows: rows.length, invisible, barren, dup};
            })()
        """)
        assert r["n"] >= 5, f"expected the year's strands, saw {r['n']} headings"
        assert r["rows"] >= r["n"], f"{r['rows']} rows under {r['n']} headings"
        assert not r["invisible"], f"headings that render blank/collapsed: {r['invisible']}"
        assert not r["barren"], f"headings with no topic beneath them: {r['barren']}"
        assert not r["dup"], f"a strand heading repeats back-to-back: {r['dup']}"
    finally:
        if browser:
            browser.close()
        server.stop()


_PAGES = ("/choose", "/learn", "/progress", "/parent", "/settings", "/setup",
          "/topics?subject=fractions",
          # a STRAND-GROUPED topics page: the pilot one above has no strands,
          # so without this the grouped layout escapes the viewport sweep.
          "/topics?subject=au_acara_year3_maths")

_PAGE_PROBE = """(() => {
  const out = {overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
               offenders: [], tiny: [], dupHeads: []};
  // An element inside a horizontally SCROLLABLE box legitimately has a rect wider
  // than the viewport -- it is clipped by that box and reachable by scrolling,
  // which is the whole point of .ascii-art / .steps-pre-wrap. Counting it as
  // "escaped the viewport" is a false positive: measured 2026-08-23, a
  // .steps-pre-diagram row reported right=608 on a 360px screen while its <pre>
  // ended at 329 and clipped it, with the page not scrolling at all.
  const containedByScroller = el => {
    for (let a = el.parentElement; a; a = a.parentElement) {
      const cs = getComputedStyle(a);
      if (/(auto|scroll|hidden)/.test(cs.overflowX)
          && a.getBoundingClientRect().right <= window.innerWidth + 1) return true;
    }
    return false;
  };
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) return;
    if ((r.right > window.innerWidth + 1 || r.left < -1) && !containedByScroller(el))
      out.offenders.push(el.tagName.toLowerCase() + '.' + (el.className || '').toString().split(' ')[0]);
  });
  // WCAG 2.5.8: 24x24 minimum. A control inside a <label> is targeted BY that
  // label (the mc4 radios are 17px inside a 720x50 label), so measure the label.
  document.querySelectorAll('a, button, select, summary, input:not([type=hidden])').forEach(el => {
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




def test_jump_to_a_topic_reaches_a_question_with_tappable_rows():
    """Jump-to-topic (docs/design/topic_jump_and_practice.md): the card's link
    must actually reach the topic list, the rows must be child-sized tap targets,
    and tapping one must land on a live question. Server tests prove the pin;
    only a browser proves the three-tap journey exists on screen."""
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.goto(server.url + "/choose")
        browser.wait_for("document.querySelectorAll('.topic-jump').length > 10")
        # Every card carries the affordance -- one link per card.
        counts = browser.js(
            "[document.querySelectorAll('.subject-card').length,"
            " document.querySelectorAll('.topic-jump').length]"
        )
        assert counts[0] == counts[1], f"cards vs jump-links mismatch: {counts}"

        browser.js("document.querySelector('.topic-jump').click()")
        browser.wait_for("document.querySelectorAll('.topic-row').length > 0")
        assert "/topics" in browser.js("location.pathname")

        # WCAG 2.5.8 wants 24px; a child-facing list should clear 44px.
        short = browser.js("""
            [...document.querySelectorAll('.topic-row')]
              .map(r => Math.round(r.getBoundingClientRect().height))
              .filter(h => h < 44)
        """)
        assert short == [], f"topic rows under 44px tall: {short}"

        browser.js("document.querySelector('.topic-row').click()")
        browser.wait_for("location.pathname === '/learn'")
        browser.wait_for("document.querySelector('.question-text') !== null")
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
            # 2026-08-20 (maintainer): the card is now DELIBERATELY a touch
            # smaller than the prose (0.95em) -- monospace at equal px reads
            # larger, so visual parity needs a smaller em. The 2026-08-15 rule
            # this supersedes was about INCONSISTENCY between presses; the
            # invariant kept from it is "close and stable", now as a band.
            assert shape["cardPx"] < shape["prosePx"], (
                f"card {shape['cardPx']}px vs prose {shape['prosePx']}px -- "
                "the card should render slightly smaller than the prose"
            )
            assert shape["cardPx"] >= 0.9 * shape["prosePx"], (
                f"card {shape['cardPx']}px vs prose {shape['prosePx']}px -- "
                "smaller, but this is a different-looking panel again"
            )
    finally:
        if browser:
            browser.close()
        server.stop()


def test_the_card_sits_between_the_lead_in_and_the_call_to_action():
    """2026-08-16 (maintainer): the worked-example card must render BETWEEN
    "Let's see how it's solved! 👇" and "Now you try it! ✏️", not after both --
    the card IS how it's solved, so the call to action has to follow it.

    Geometry, not DOM order, because the risk here is CSS: .feedback is a flex
    row and .msg-text carries `flex: 1`, so a second one without flex-basis:100%
    would sit BESIDE the first rather than below the card.
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
        browser.js("""
            [...document.querySelectorAll('button, a')]
              .find(b => /show me how/i.test(b.textContent))?.click()
        """)
        browser.wait_for("!!document.querySelector('.elaborate-form button')")
        browser.js("document.querySelector('.elaborate-form button').click()")
        browser.wait_for("!!document.querySelector('.feedback .steps-pre')", timeout=20)

        box = browser.js("""
            (() => {
                const fb = document.querySelector('.feedback');
                const g = el => { const r = el.getBoundingClientRect();
                                  return {top: r.top, left: r.left, h: r.height}; };
                const lead = fb.querySelector('.msg-text:not(.msg-tail)');
                const card = fb.querySelector('.steps-pre');
                const tail = fb.querySelector('.msg-tail');
                return {lead: lead && g(lead), card: card && g(card),
                        tail: tail && g(tail), tailText: tail && tail.textContent.trim()};
            })()
        """)
        assert box["lead"] and box["card"] and box["tail"], f"a piece is missing: {box}"
        assert "Now you try it" in box["tailText"], box["tailText"]
        assert box["card"]["top"] >= box["lead"]["top"] + box["lead"]["h"] - 2, (
            f"card is not below the lead-in: {box}"
        )
        assert box["tail"]["top"] >= box["card"]["top"] + box["card"]["h"] - 2, (
            f'"Now you try it" is not below the card: {box}'
        )
        assert abs(box["tail"]["left"] - box["card"]["left"]) < 40, (
            f"tail is squeezed beside the card instead of on its own row: {box}"
        )
    finally:
        if browser:
            browser.close()
        server.stop()


def test_read_aloud_never_speaks_the_diagram_ornament():
    """2026-08-17. Cards gained computed diagrams (a square array, a fraction
    bar, a hundred-grid, a labelled rectangle) and read-aloud spoke them
    verbatim -- five rows of "square square square...", or ten lines of
    box-drawing, straight after the answer. That lands on exactly the child who
    needs read-aloud most.

    Only a browser can prove this: the spoken string is assembled in tts.js.

    The card content is INJECTED rather than drawn, on purpose. A real draw gives
    a step grid as often as a method card, so the assertion could pass without
    ever meeting a diagram -- green because it tested nothing, the failure mode
    this suite exists to end.

    Stubs only SpeechSynthesisUtterance and the two methods used: replacing
    window.speechSynthesis wholesale breaks the module, which captures voices at
    load via getVoices().
    """
    _skip_unless_browser()
    ornament_rows = ["┌───┐", "│   │  4 cm", "□□□□□", "|████|    |", "[●●●] [●●●]"]
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.goto(server.url + "/")
        browser.js("""
            [...document.querySelectorAll('.subject-card, a')]
              .find(a => /fraction/i.test(a.textContent))?.click()
        """)
        browser.wait_for("!!document.querySelector('.question-text')")
        browser.js("""
            window.__spoken = [];
            window.SpeechSynthesisUtterance = function (t) { window.__spoken.push(t); this.text = t; };
            window.speechSynthesis.speak = function () {};
            window.speechSynthesis.cancel = function () {};
        """)
        rows = json.dumps(["Answer: 25", *ornament_rows, "5 rows of 5 = 25"])
        browser.js("""
            (() => {
                let fb = document.querySelector('.feedback');
                if (!fb) {
                    fb = document.createElement('div');
                    fb.className = 'feedback';
                    fb.innerHTML = '<button class="tts-btn" type="button">S</button>'
                                 + '<div class="msg-text">Here is how it works.</div>';
                    document.querySelector('#turn-area').prepend(fb);
                }
                const pre = document.createElement('pre');
                pre.className = 'steps-pre';
                pre.innerHTML = ROWS.map(
                    r => '<span class="steps-pre-line"></span>').join('');
                [...pre.children].forEach((el, i) => { el.textContent = ROWS[i]; });
                fb.appendChild(pre);
            })()
        """.replace("ROWS", rows))
        assert browser.js("!!document.querySelector('.feedback .steps-pre')")
        browser.js("document.querySelector('.feedback .tts-btn').click()")
        browser.wait_for("window.__spoken && window.__spoken.length > 0")

        spoken = browser.js("window.__spoken.join(' ')")
        bad = sorted({ch for ch in spoken if ch in "┌─┐│└┘█□●○|"})
        assert not bad, f"read-aloud speaks diagram characters {bad!r}: {spoken[:200]!r}"
        # An ornament row must be DROPPED, not merely blanked. Stripping the
        # characters alone leaves "Answer: 25. . 4 cm. . . [ ] [ ]. 5 rows..."
        # -- stray pauses and leftover brackets. Both halves of the fix are
        # load-bearing, so both are asserted.
        assert ". ." not in spoken, f"empty segments left by blanked rows: {spoken[:200]!r}"
        assert "[" not in spoken and "]" not in spoken, spoken[:200]
        # The picture is NARRATED, not dropped: its summary line survives...
        assert "5 rows of 5" in spoken, spoken[:200]
        # ...and so does a label sitting beside a rectangle wall.
        assert "4 cm" in spoken, spoken[:200]
    finally:
        if browser:
            browser.close()
        server.stop()


def test_a_question_picture_is_monospaced_below_the_text_and_never_clipped():
    """Visual-first (2026-08-21). Route tests prove the <pre> is in the HTML;
    only a browser proves the thing that matters — that its COLUMNS LINE UP.

    Deliberately does not assert font-family contains "mono": style.css records
    that the --font-mono token was once unset and the app silently ran on the
    browser's bare `monospace` fallback, so the name proves nothing. Rendering
    'iiii' and 'MMMM' and comparing widths is the real property.

    Also pins placement, because "tidy it inside .question-text" is a plausible
    future edit that would (a) reintroduce the proportional font and (b) make
    read-aloud start speaking ASCII art.

    The picture sits BELOW the question as of 2026-08-21 -- instruction first,
    then the material. Above, it was a context-free block of art at the top of
    the bubble."""
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.goto(server.url + "/topics?subject=fractions")
        browser.js("""(() => {const f = [...document.querySelectorAll('form')]
            .find(f => f.querySelector('[value=unit_fractions]'));
            f.querySelector('button').click();})()""")
        browser.wait_for("document.getElementById('help-btn')")
        r = browser.js("""
            (() => {
              const pre = document.querySelector('.question-visual');
              if (!pre) return {err: 'no .question-visual rendered'};
              const q = document.querySelector('.question-text');
              const pr = pre.getBoundingClientRect(), qr = q.getBoundingClientRect();
              const probe = document.createElement('pre');
              probe.className = 'ascii-art';
              probe.style.position = 'absolute'; probe.style.visibility = 'hidden';
              document.body.appendChild(probe);
              probe.textContent = 'iiii';
              const narrow = probe.getBoundingClientRect().width;
              probe.textContent = 'MMMM';
              const wide = probe.getBoundingClientRect().width;
              probe.remove();
              return {
                err: null,
                monospace: Math.abs(narrow - wide) < 0.5,
                below: qr.bottom <= pr.top + 1,
                insideQuestionText: q.contains(pre),
                clipped: pre.scrollWidth > pre.clientWidth + 1
                         && getComputedStyle(pre).overflowX !== 'auto',
                pageScrollsSideways:
                  document.documentElement.scrollWidth > window.innerWidth + 1,
              };
            })()
        """)
        assert not r["err"], r["err"]
        assert r["monospace"], "question picture is not monospaced — columns will not align"
        assert r["below"], "picture is not below the question text"
        assert not r["insideQuestionText"], (
            "picture moved inside .question-text — proportional font, and tts.js "
            "would start speaking the art"
        )
        assert not r["clipped"], "picture is clipped instead of scrollable"
        assert not r["pageScrollsSideways"], "the picture pushed the page sideways"
    finally:
        if browser:
            browser.close()
        server.stop()


def test_a_question_picture_gets_a_usable_width_on_a_real_phone():
    """Found 2026-08-21. Every "phone width" check in this file until now
    squeezed a CONTAINER (`main{max-width:360px}`) and left the viewport wide,
    so `@media` rules never fired and the numbers were fiction. This one sets
    real device metrics.

    At 360px the picture box gets ~270px of text at ~9.1px a character -- 29
    characters. It was 25 before .ascii-art's 18px side padding was cut to 8px
    on narrow screens: four characters, bought back from margin nobody needed,
    which is the difference between a 29-column clock face fitting and not.

    Asserts the BUDGET, not the padding, so any future way of finding the room
    is fine and only losing it fails.
    """
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.send("Emulation.setDeviceMetricsOverride",
                     width=360, height=740, deviceScaleFactor=1, mobile=True)
        browser.goto(server.url + "/topics?subject=fractions")
        browser.js("""(() => {const f = [...document.querySelectorAll('form')]
            .find(f => f.querySelector('[value=unit_fractions]'));
            f.querySelector('button').click();})()""")
        browser.wait_for("document.getElementById('help-btn')")
        r = browser.js("""
            (() => {
              const pre = document.querySelector('.question-visual');
              if (!pre) return {err: 'no .question-visual rendered'};
              const cs = getComputedStyle(pre);
              const text = pre.clientWidth - parseFloat(cs.paddingLeft)
                                           - parseFloat(cs.paddingRight);
              const probe = document.createElement('span');
              probe.style.cssText =
                'position:absolute;visibility:hidden;white-space:pre;left:-9999px';
              probe.style.font = cs.font;
              document.body.appendChild(probe);
              probe.textContent = 'M'.repeat(50);
              const per = probe.getBoundingClientRect().width / 50;
              probe.remove();
              return {err: null, innerWidth: window.innerWidth,
                      fits: Math.floor(text / per)};
            })()
        """)
        assert not r["err"], r["err"]
        assert r["innerWidth"] == 360, (
            f"device metrics did not apply — measured at {r['innerWidth']}px, so "
            f"this test would be the same fiction it was written to replace"
        )
        assert r["fits"] >= 29, (
            f"only {r['fits']} monospace characters fit the question picture on a "
            f"360px phone (was 29). A clock face is 30 columns and a two-way "
            f"table 35; losing width here starts them scrolling"
        )
    finally:
        if browser:
            browser.close()
        server.stop()


def test_a_card_diagram_keeps_its_columns_while_card_prose_still_wraps():
    """A method card can carry BOTH kinds of line and they need opposite
    treatment. Found 2026-08-22 by measuring, not by looking.

    `.steps-pre-wrap` exists because clipping chopped long sentences mid-word
    (2026-08-15), and wrapping is right for a sentence. It is wrong for a
    picture: every row of an 85-column comparison table wrapped into TWO visual
    lines on a 360px phone, so the columns the diagram is made of came out
    interleaved. 247 of 250 card-eligible scaffold diagrams are wider than that
    budget, so this was the common case.

    Diagram rows now carry `.steps-pre-diagram` and do not wrap; the card scrolls
    so they stay reachable. Prose rows are untouched. Both halves are asserted --
    a fix that stopped the prose wrapping would be the 2015-08-15 bug returning.
    """
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.send("Emulation.setDeviceMetricsOverride", width=360, height=740,
                     deviceScaleFactor=1, mobile=True)
        browser.goto(server.url + "/topics?subject=fractions")
        r = browser.js("""
            (() => {
              const host = document.querySelector('main') || document.body;
              const pre = document.createElement('pre');
              pre.className = 'steps-pre steps-pre-wrap';
              host.appendChild(pre);
              const add = (txt, cls) => {
                const s = document.createElement('span');
                s.className = cls; s.textContent = txt;
                pre.appendChild(s); pre.appendChild(document.createTextNode('\\n'));
                return s;
              };
              const unit = add('X', 'steps-pre-line').getBoundingClientRect().height;
              const wide = '"it\\'s raining cats and dogs"    animals falling    raining hard';
              const diagram = add(wide, 'steps-pre-diagram steps-pre-line');
              const prose = add('This is a long prose sentence of the kind a method card '
                              + 'carries, which must still wrap rather than scroll.',
                                'steps-pre-line');
              const res = {
                diagramLines: Math.round(diagram.getBoundingClientRect().height / unit),
                proseLines: Math.round(prose.getBoundingClientRect().height / unit),
                scrollable: pre.scrollWidth > pre.clientWidth + 1,
                overflowX: getComputedStyle(pre).overflowX,
                pageSideways: document.documentElement.scrollWidth > window.innerWidth + 1,
              };
              pre.remove();
              return res;
            })()
        """)
        assert r["diagramLines"] == 1, (
            f"a diagram row wrapped onto {r['diagramLines']} lines — its columns "
            f"are interleaved and the picture is unreadable"
        )
        assert r["proseLines"] > 1, (
            "card prose stopped wrapping — that is the mid-word clipping bug of "
            "2026-08-15 coming back"
        )
        assert r["scrollable"] and r["overflowX"] == "auto", (
            "the un-wrapped diagram must be reachable by scrolling, not cut off"
        )
        assert not r["pageSideways"], "the card pushed the whole page sideways"
    finally:
        if browser:
            browser.close()
        server.stop()


def test_every_page_is_laid_out_sanely_on_a_phone():
    """The same sweep as test_every_page_is_laid_out_sanely, at a REAL 360px
    mobile viewport.

    That test runs at the default headless window, which is desktop-sized, so
    until 2026-08-23 no page had ever been measured at the width a parent's
    phone actually uses -- and phone width is where content escapes a viewport,
    not desktop. The gap was invisible because squeezing a container is NOT the
    same as a narrow viewport: `@media` rules do not fire, so a container-squeeze
    check silently measures the desktop layout. Only device metrics change that.

    Passes today. It is here as a ratchet: the sweep that would have caught the
    card-diagram wrapping bug at 360px, had it been running.
    """
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.send("Emulation.setDeviceMetricsOverride", width=360, height=740,
                     deviceScaleFactor=1, mobile=True)
        browser.goto(server.url + "/topics?subject=fractions")
        browser.js("""(() => {const f = [...document.querySelectorAll('form')]
            .find(f => f.querySelector('[value=unit_fractions]'));
            f.querySelector('button').click();})()""")
        browser.wait_for("document.getElementById('help-btn')")
        problems = []
        # The STATES a child passes through, not just the URLs. A wrong answer and
        # an Explain-more press change the page more than any route does -- the
        # card, its picture and the re-ask all appear only here.
        # Driven by real POSTs, not by typing into the widget: this node renders
        # numeric num/den inputs, so setting "more" on a number input leaves it
        # empty and `required` silently blocks the submit -- the first version of
        # this walk measured the plain question twice and the assertion below is
        # what caught it.
        for label, answer in (("after a wrong answer", "1/99"),
                              ("help explanation", "help"),
                              ("explain-more card", "more")):
            browser.js(
                "(async () => { await fetch('/answer', {method:'POST',"
                " body:new URLSearchParams({answer: " + json.dumps(answer) + "}),"
                " credentials:'same-origin',"
                " headers:{'Content-Type':'application/x-www-form-urlencoded'}}); })()"
            )
            browser.wait_for("true")
            browser.goto(server.url + "/learn")
            r = browser.js(_PAGE_PROBE)
            if r["overflowX"]:
                problems.append(f"{label}: the page scrolls sideways on a phone")
            if r["offenders"]:
                problems.append(f"{label}: elements outside the viewport: {r['offenders'][:4]}")
        # Prove the walk REACHED the card, or the two turns above are measuring
        # the plain question twice and this loop is a silent no-op.
        assert browser.js("!!document.querySelector('.steps-pre')"), (
            "the explain-more card never rendered -- the state walk measured nothing"
        )
        for path in _PAGES:
            browser.goto(server.url + path)
            width = browser.js("window.innerWidth")
            # Two failures in one assertion, and the second is the subtle one:
            #   * device metrics silently not applying -- then this whole test
            #     measures the desktop layout it exists to stop trusting;
            #   * the PAGE widening the layout viewport past the device. Chrome
            #     grows innerWidth to fit overflowing content on a mobile
            #     viewport, so every scrollWidth-vs-innerWidth check then compares
            #     the page against its own overflow and passes. That is exactly
            #     how /parent's five-column Answers table pushed a 360px phone to
            #     370 while every sweep, including this file's, called it clean.
            assert width == 360, (
                f"viewport is {width}px, not 360 — either device metrics did not "
                f"apply, or {path} widened the layout viewport to fit content that "
                f"does not fit a phone (wrap it in an overflow-x:auto box)"
            )
            r = browser.js(_PAGE_PROBE)
            if r["overflowX"]:
                problems.append(f"{path}: the page scrolls sideways on a phone")
            if r["offenders"]:
                problems.append(f"{path}: elements outside the viewport: {r['offenders'][:4]}")
            if r["dupHeads"]:
                problems.append(f"{path}: a heading repeats back-to-back: {r['dupHeads'][:2]}")
        assert not problems, "\n".join(problems)
    finally:
        if browser:
            browser.close()
        server.stop()


def test_text_zoom_to_200_percent_does_not_push_the_page_sideways():
    """WCAG 1.4.10 (reflow): text at 200% must not force two-dimensional
    scrolling. Measured 2026-08-23 -- it did, on six of seven pages.

    The mechanism is worth knowing, because it hides from every other check:
    an overflowing row makes Chrome GROW the mobile layout viewport (360 -> 401,
    and /learn to 535), so a scrollWidth-vs-innerWidth test then compares the
    page against its already-widened self and passes. Asserting the viewport is
    still the width we asked for is the only thing that sees it.

    Cause was non-wrapping flex rows: .site-header (brand + settings needed 388px
    in a 336px box), .brand, .fraction-input and the mastery row. All four now
    wrap. A child who needs bigger type, or a parent with low vision, is the
    person this is for.
    """
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.send("Emulation.setDeviceMetricsOverride", width=360, height=740,
                     deviceScaleFactor=1, mobile=True)
        browser.goto(server.url + "/topics?subject=fractions")
        browser.js("""(() => {const f = [...document.querySelectorAll('form')]
            .find(f => f.querySelector('[value=unit_fractions]'));
            f.querySelector('button').click();})()""")
        browser.wait_for("document.getElementById('help-btn')")
        problems = []
        for path in ("/choose", "/learn", "/progress", "/parent", "/settings",
                     "/topics?subject=fractions"):
            for zoom in (150, 200):
                browser.goto(server.url + path)
                browser.js(f"document.documentElement.style.fontSize = '{zoom}%'")
                browser.wait_for("true")
                width = browser.js("window.innerWidth")
                if width != 360:
                    problems.append(
                        f"{path} at {zoom}% text widened the viewport to {width}px — "
                        f"the page scrolls sideways for anyone using text zoom"
                    )
        assert not problems, "\n".join(problems)
    finally:
        if browser:
            browser.close()
        server.stop()


def test_an_unreachable_backend_message_does_not_push_the_page_sideways():
    """The settings page reports backend failures like "Cannot reach
    http://192.168.1.10:4000/v1/chat/completions - connection refused". A URL is
    one unbreakable word, and measured 2026-08-23 it pushed a 360px phone to
    364px at NORMAL zoom and 693px at 200%.

    That is the settings page scrolling sideways at exactly the moment a family's
    model is unreachable and they are trying to read why -- the worst possible
    time for the page to be hard to use. Found because this message appears only
    when a backend check fails, so it never showed up in a sweep of the happy
    path; the zoom test caught it as a cross-test state difference.
    """
    _skip_unless_browser()
    long_error = ("Cannot reach http://192.168.1.10:4000/v1/chat/completions"
                  " - connection refused")
    server, browser = _Server(), None
    try:
        browser = _Browser()
        browser.send("Emulation.setDeviceMetricsOverride", width=360, height=740,
                     deviceScaleFactor=1, mobile=True)
        for zoom in (100, 200):
            browser.goto(server.url + "/settings")
            browser.js("document.getElementById('llm-status-line').textContent = "
                       + json.dumps(long_error))
            browser.js(f"document.documentElement.style.fontSize = '{zoom}%'")
            browser.wait_for("true")
            width = browser.js("window.innerWidth")
            assert width == 360, (
                f"a backend-error URL at {zoom}% text widened the viewport to "
                f"{width}px — the page scrolls sideways when the model is down"
            )
    finally:
        if browser:
            browser.close()
        server.stop()


def test_a_long_division_grid_is_reachable_on_a_phone_not_cut_off():
    """"Show human working" exists to show a child the standard algorithm. On a
    360px phone it was showing them about half of it.

    .steps-pre was overflow-x:hidden on the stated assumption that "the step
    grid's width is computed to fit" -- true on a desktop, false on a phone.
    Measured 2026-08-23: the long-division grid is 475px in a 293px box and the
    partial-products multiplication grid is 598px, so the right-hand side of the
    working was simply gone, with no way to reach it.

    Clipping is worse than the sideways scroll the module docstring rejected:
    scrolled content is reachable, clipped content is not. This asserts the child
    can actually get to the right edge, and that a desktop still needs no
    scrollbar at all.
    """
    _skip_unless_browser()
    server, browser = _Server(), None
    try:
        browser = _Browser()
        for width in (360, 1280):
            browser.send("Emulation.setDeviceMetricsOverride", width=width, height=900,
                         deviceScaleFactor=1, mobile=(width < 700))
            browser.goto(server.url + "/")
            browser.js(
                "(async () => { await fetch('/choose', {method:'POST',"
                " body:new URLSearchParams({subject:'au_acara_year4_maths',"
                " topic:'au4_division_facts'}), credentials:'same-origin',"
                " headers:{'Content-Type':'application/x-www-form-urlencoded'}}); })()")
            for answer in ("999999", "help", "more", "more"):
                browser.js(
                    "(async () => { await fetch('/answer', {method:'POST',"
                    " body:new URLSearchParams({answer: " + json.dumps(answer) + "}),"
                    " credentials:'same-origin',"
                    " headers:{'Content-Type':'application/x-www-form-urlencoded'}}); })()")
            browser.goto(server.url + "/learn")
            r = browser.js("""
                (() => {
                  const pre = document.querySelector('.steps-pre');
                  if (!pre) return {err: 'no step grid rendered'};
                  pre.scrollLeft = 99999;
                  return {clientW: pre.clientWidth, scrollW: pre.scrollWidth,
                          overflowX: getComputedStyle(pre).overflowX,
                          reachedRightEdge: pre.scrollLeft > 0,
                          pageSideways:
                            document.documentElement.scrollWidth > window.innerWidth + 1};
                })()
            """)
            assert not r.get("err"), f"{width}px: {r.get('err')}"
            assert r["overflowX"] != "hidden", (
                f"{width}px: the grid clips at {r['clientW']}px with "
                f"{r['scrollW']}px of working — the rest is unreachable"
            )
            assert not r["pageSideways"], f"{width}px: the grid pushed the page sideways"
            if r["scrollW"] > r["clientW"] + 1:
                assert r["reachedRightEdge"], (
                    f"{width}px: the grid overflows but will not scroll — a child "
                    f"cannot see the end of the working"
                )
            else:
                assert width > 700, f"{width}px: expected the grid to overflow a phone"
    finally:
        if browser:
            browser.close()
        server.stop()
