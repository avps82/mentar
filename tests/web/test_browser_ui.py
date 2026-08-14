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
        self.proc = subprocess.Popen(
            ["chromium", "--headless", "--disable-gpu", "--no-sandbox",
             f"--user-data-dir={self.profile}", "--remote-debugging-port=0",
             "--remote-allow-origins=*", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        port_file = pathlib.Path(self.profile) / "DevToolsActivePort"
        for _ in range(150):
            if port_file.exists() and "\n" in port_file.read_text():
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("chromium never reported a debugging port")
        port = int(port_file.read_text().splitlines()[0])
        targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
        page = next(t for t in targets if t["type"] == "page")
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)
        self._id = 0

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
        finally:
            self.proc.terminate()
            self.proc.wait(timeout=10)


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
        browser.wait_for("document.querySelector('.curricula-master .hint').textContent.includes('Saved')")

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


if __name__ == "__main__":
    test_country_master_switch_turns_off_every_row_under_it()
    print("  ✓ test_country_master_switch_turns_off_every_row_under_it")
    test_idle_nudge_appears_on_a_live_question_then_stops()
    print("  ✓ test_idle_nudge_appears_on_a_live_question_then_stops")
