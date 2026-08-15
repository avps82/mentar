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

  // Prime the (often asynchronously-loaded) voice list as soon as this page
  // loads, not at the moment of the first click -- Chrome and others return
  // an EMPTY array from a cold getVoices() call and only populate it a
  // moment later. Without this, the very first read on a fresh page always
  // missed the saved voice (fell back to default) even though the choice
  // was correctly saved on the Settings page -- the click handler's own
  // getVoices() lookup just ran before the browser had loaded anything.
  window.speechSynthesis.getVoices();

  var STATE_IDLE = "idle";
  var STATE_SPEAKING = "speaking";
  var STATE_PAUSED = "paused";
  var state = STATE_IDLE;

  var ICON = { idle: "🔊", speaking: "⏸", paused: "▶️" };
  var LABEL = {
    idle: "Read aloud",
    speaking: "Pause reading",
    paused: "Resume reading",
  };

  // R12.1: two read-aloud buttons can coexist (question + feedback/explanation);
  // track which one owns the current utterance so state paints the right button.
  var activeBtn = null;
  var activeUtterance = null;

  function paint(btn) {
    if (!btn) return;
    btn.textContent = ICON[state];
    btn.setAttribute("aria-label", LABEL[state]);
    btn.setAttribute("title", LABEL[state]);
  }

  function reset() {
    state = STATE_IDLE;
    if (activeBtn) {
      paint(activeBtn); // harmless no-op if the htmx swap already detached it
      activeBtn = null;
    }
    activeUtterance = null;
  }

  // R12-fix (2026-07-19 feedback): feedback/explanation text carries emoji
  // (praise variants, the visual-modality help template's emoji diagrams) --
  // most speech engines vocalize them literally ("green square emoji"...).
  // Strip for the SPOKEN copy only; the visible text is untouched.
  var EMOJI_RE = new RegExp("[\\u200d\\ufe0f\\p{Extended_Pictographic}]", "gu");

  // 2026-08-14 (maintainer, listening): two things the engines get wrong on
  // OUR text specifically. Spoken copy only -- the visible text is untouched.
  //   1. An ALL-CAPS word looks like an acronym, so "READ"/"SAME" is spelled
  //      out letter by letter. Lowercase words of 2+ caps; single letters are
  //      left alone (the A/B/C/D choice labels must still be read as letters).
  //      ponytail: a GENUINE acronym in child-facing text would now be read as
  //      a word ("ncert"); no such text exists in the read-aloud surfaces
  //      (question, choices, feedback), so no exception list until one does.
  //   2. "→" is vocalized as "arrow". It's used as "gives/therefore" in method
  //      cards ("... digit 4? → 40") and category cards ("copper → conductor"),
  //      where no single English word fits both, so it becomes a PAUSE. Only
  //      the reported symbols are mapped -- the rest (×, ÷, =) are left to the
  //      engine rather than guessed at blind, since TTS can't be tested here.
  // Genuine acronyms and symbols, which the caps rule below must NOT lowercase:
  // an engine says "dee-en-ay" for DNA but reads "dna" as a nonsense word, and
  // "BB" is a genotype whose letters ARE the answer. Measured against the real
  // corpus 2026-08-15 (every generated question + choice across all 117 packs);
  // senior science introduced all three. A new acronym in new content needs a
  // line here -- tests/web/test_tts_speech_text.py pins these.
  var KEEP_CAPS = {DNA: 1, ATP: 1, BB: 1};

  function forSpeech(text) {
    return text
      .replace(EMOJI_RE, "")
      .replace(/[→⇒]/g, ",")
      .replace(/\b[A-Z]{2,}\b/g, function (w) { return KEEP_CAPS[w] ? w : w.toLowerCase(); })
      .replace(/\s+/g, " ")
      .trim();
  }

  function cancelCurrent() {
    // Detach the old utterance's handlers BEFORE cancel(): its onend fires
    // asynchronously and would otherwise reset()/repaint AFTER a new utterance
    // has already started, flipping the new button back to idle mid-speech.
    if (activeUtterance) {
      activeUtterance.onend = null;
      activeUtterance.onerror = null;
    }
    window.speechSynthesis.cancel();
  }

  // A new question swapped in (htmx replaced #turn-area, including the
  // button) -- without this, the previous question's audio keeps playing
  // OVER the new one. The fresh button already renders idle/🔊 by construction
  // (server-rendered default); only the audio + module state need resetting.
  document.body.addEventListener("htmx:afterSwap", function () {
    cancelCurrent();
    state = STATE_IDLE;
    activeBtn = null;
  });

  document.addEventListener("click", function (evt) {
    var btn = evt.target.closest(".tts-btn");
    if (!btn) return;

    // A DIFFERENT button clicked while speaking/paused: stop the old read and
    // fall through to start this block's read immediately (no second click).
    if (state !== STATE_IDLE && activeBtn && activeBtn !== btn) {
      cancelCurrent();
      var prev = activeBtn;
      state = STATE_IDLE;
      activeBtn = null;
      paint(prev); // repaint old button idle (safe if already swapped out)
    }

    if (state === STATE_IDLE) {
      cancelCurrent(); // clear any stale queue first

      var parts = [];
      // R12.1: read the clicked block (question OR feedback/explanation), not
      // always the question.
      var feedbackBlock = btn.closest(".feedback");
      if (feedbackBlock) {
        var f = feedbackBlock.querySelector(".msg-text");
        if (f) parts.push(f.textContent.trim());
        // The worked example now sits inside this bubble (2026-08-15). Read it too:
        // it is the part that actually explains the method, and a child who needs
        // read-aloud needs it most. Annotation lines are asides on the diagram, so
        // they are read after, not interleaved mid-sentence.
        var card = feedbackBlock.querySelector(".steps-pre");
        if (card) {
          card.querySelectorAll(".steps-pre-line").forEach(function (line) {
            var t = line.textContent.trim();
            if (t) parts.push(t);
          });
        }
      } else {
        var q = document.querySelector(".question-text");
        if (q) parts.push(q.textContent.trim());
        document.querySelectorAll(".choice-option").forEach(function (opt) {
          parts.push(opt.textContent.trim());
        });
      }
      var text = forSpeech(parts.join(". "));
      if (!text) return;

      var utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9; // slightly slower for a child listener
      var storedVoiceURI = null;
      try { storedVoiceURI = localStorage.getItem("mentar-tts-voice"); } catch (e) { /* storage unavailable */ }
      if (storedVoiceURI) {
        var match = window.speechSynthesis.getVoices().find(function (v) { return v.voiceURI === storedVoiceURI; });
        if (match) { utterance.voice = match; utterance.lang = match.lang; }
      }
      utterance.onend = reset;
      utterance.onerror = reset;
      window.speechSynthesis.speak(utterance);
      activeUtterance = utterance;
      activeBtn = btn;
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

  // Test seam only (tests/web/test_tts_speech_text.py runs this file under node
  // with a stub window). Nothing in the app reads this.
  window.MentarSpeech = { forSpeech: forSpeech };
})();
