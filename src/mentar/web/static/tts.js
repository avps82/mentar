/*
 * Owned text-to-speech for the question + choices, via the browser's built-in
 * speechSynthesis (local voices, no network, no deps — U-80/U-81). Uses event
 * delegation on document so the button keeps working after every htmx swap of
 * #turn-area with zero re-binding. Fails silent where speechSynthesis is
 * unavailable (button hidden).
 *
 * R2.2: three-state button (idle 🔊 -> speaking ⏸ -> paused ▶️ -> speaking...)
 * via speechSynthesis.pause()/resume(), instead of restarting from the top on
 * every click. State lives HERE (module scope), not on the button element --
 * every htmx swap of #turn-area REPLACES the button, so per-element state
 * would be lost on every swap regardless of what it held.
 */
(function () {
  if (!("speechSynthesis" in window)) {
    document.addEventListener("DOMContentLoaded", function () {
      document.querySelectorAll(".tts-btn").forEach(function (b) { b.style.display = "none"; });
    });
    return;
  }

  var STATE_IDLE = "idle";
  var STATE_SPEAKING = "speaking";
  var STATE_PAUSED = "paused";
  var state = STATE_IDLE;

  var ICON = { idle: "🔊", speaking: "⏸", paused: "▶️" };
  var LABEL = {
    idle: "Read the question aloud",
    speaking: "Pause reading",
    paused: "Resume reading",
  };

  function paint(btn) {
    btn.textContent = ICON[state];
    btn.setAttribute("aria-label", LABEL[state]);
    btn.setAttribute("title", LABEL[state]);
  }

  function reset() {
    state = STATE_IDLE;
    var btn = document.querySelector(".tts-btn");
    if (btn) paint(btn);
  }

  // A new question swapped in (htmx replaced #turn-area, including the
  // button) -- without this, the previous question's audio keeps playing
  // OVER the new one. The fresh button already renders idle/🔊 by construction
  // (server-rendered default); only the audio + module state need resetting.
  document.body.addEventListener("htmx:afterSwap", function () {
    window.speechSynthesis.cancel();
    state = STATE_IDLE;
  });

  document.addEventListener("click", function (evt) {
    var btn = evt.target.closest(".tts-btn");
    if (!btn) return;

    if (state === STATE_IDLE) {
      window.speechSynthesis.cancel(); // clear any stale queue first

      var parts = [];
      var q = document.querySelector(".question-text");
      if (q) parts.push(q.textContent.trim());
      document.querySelectorAll(".choice-option").forEach(function (opt) {
        parts.push(opt.textContent.trim());
      });
      var text = parts.join(". ").replace(/\s+/g, " ").trim();
      if (!text) return;

      var utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9; // slightly slower for a child listener
      utterance.onend = reset;
      utterance.onerror = reset;
      window.speechSynthesis.speak(utterance);
      state = STATE_SPEAKING;
      paint(btn);
    } else if (state === STATE_SPEAKING) {
      // Known ceiling: speechSynthesis.pause() is unreliable on some mobile
      // browsers (may behave as a full stop rather than a true pause) --
      // acceptable for the desktop/tablet pilot; no workaround attempted.
      window.speechSynthesis.pause();
      state = STATE_PAUSED;
      paint(btn);
    } else if (state === STATE_PAUSED) {
      window.speechSynthesis.resume();
      state = STATE_SPEAKING;
      paint(btn);
    }
  });
})();
