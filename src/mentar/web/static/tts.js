/*
 * Owned text-to-speech for the question + choices, via the browser's built-in
 * speechSynthesis (local voices, no network, no deps — U-80/U-81). Uses event
 * delegation on document so the 🔊 button keeps working after every htmx swap
 * of #turn-area with zero re-binding. Fails silent where speechSynthesis is
 * unavailable (button hidden).
 */
(function () {
  if (!("speechSynthesis" in window)) {
    document.addEventListener("DOMContentLoaded", function () {
      document.querySelectorAll(".tts-btn").forEach(function (b) { b.style.display = "none"; });
    });
    return;
  }

  document.addEventListener("click", function (evt) {
    var btn = evt.target.closest(".tts-btn");
    if (!btn) return;

    window.speechSynthesis.cancel(); // stop any previous read-out first

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
    window.speechSynthesis.speak(utterance);
  });
})();
