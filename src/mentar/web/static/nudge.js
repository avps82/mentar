/*
 * Idle nudge for the "💡 Show me how" button (2026-08-14 maintainer ask: "we
 * need to nudge the kid to look for assistance when they need to, that was the
 * point of this").
 *
 * The Help loop IS the teaching in this app -- a button no child presses makes
 * the whole scaffolding machinery dead code. Nothing detected the one state
 * that matters: a question on screen and a child who has stopped moving. (A
 * WRONG answer already auto-helps in the FSM, so that path needs no nudge.)
 *
 * Design constraints, all deliberate:
 *   - Two nudges, then silence. A permanently sparkling button is wallpaper,
 *     and repeated nagging teaches a child to tune it out.
 *   - Each pulse runs for a few seconds and stops; the caption stays.
 *   - Any keystroke, choice, click or htmx swap resets everything.
 *   - prefers-reduced-motion gets a static outline instead of the pulse (see
 *     style.css) -- the cue still exists, the animation doesn't.
 *   - The timer is behaviour data about a child: it lives in this page only.
 *     Nothing is recorded, transmitted, or written to the DB.
 */
(function () {
  var FIRST_MS = 20000;
  var SECOND_MS = 45000;   // measured from the same reset, not from the first nudge
  var PULSE_MS = 4200;     // ~3 pulses, then the button goes quiet again

  var CAPTIONS = [
    "Not sure? Tap 💡 Show me how and we'll work through it together.",
    "It's always OK to ask — asking still counts as getting it right.",
  ];

  var btn = document.getElementById("help-btn");
  var caption = document.getElementById("nudge-hint");
  if (!btn || !caption) return;

  var timers = [];

  function clearTimers() {
    timers.forEach(clearTimeout);
    timers = [];
  }

  function quiet() {
    clearTimers();
    btn.classList.remove("is-nudging");
    caption.hidden = true;
    caption.textContent = "";
  }

  function nudge(index) {
    // Only nudge while a question is actually answerable -- never on a turn
    // that has no answer widget (end of session, frozen/escalated screen).
    if (!document.querySelector("#turn-area form")) return;
    caption.textContent = CAPTIONS[index];
    caption.hidden = false;
    btn.classList.add("is-nudging");
    timers.push(setTimeout(function () {
      btn.classList.remove("is-nudging");
    }, PULSE_MS));
  }

  function arm() {
    quiet();
    timers.push(setTimeout(function () { nudge(0); }, FIRST_MS));
    timers.push(setTimeout(function () { nudge(1); }, SECOND_MS));
  }

  // A fresh turn swapped in: the child is looking at a new question.
  document.body.addEventListener("htmx:afterSwap", arm);
  // Any sign of life resets the clock. Delegated on document, so it keeps
  // working after every swap replaces the widget (same reason tts.js does).
  ["input", "change", "click", "keydown"].forEach(function (evt) {
    document.addEventListener(evt, function (e) {
      if (e.target && e.target.closest && e.target.closest("#help-btn")) {
        quiet();      // they took the hint -- stop nudging, don't re-arm
        return;
      }
      arm();
    });
  });

  arm();
})();
