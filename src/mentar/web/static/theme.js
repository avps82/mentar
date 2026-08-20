/*
 * Owned theme mechanism (U-92). No deps, no external fetch: reads a saved
 * preference or the OS setting, persists the child's explicit choice in
 * localStorage.
 *
 * A theme is nothing but a [data-theme="<name>"] block in style.css -- the
 * browser is the theme engine, so there is no loader, no manifest, no fetch.
 * THEMES below is the single place the list lives; the Settings picker renders
 * itself from this array, so adding a theme is "add a CSS block + one entry".
 *
 * Back-compat (2026-08-14): this used to be a binary light/dark toggle writing
 * "light"/"dark" to the SAME key. Those are simply the first two entries now,
 * so an existing saved value keeps working with zero migration.
 */
(function () {
  var KEY = "mentar-theme";

  // name = the [data-theme] value AND the stored value; label/emoji are the
  // child-facing identity (a child picks "Space", not "dark mode 2").
  var THEMES = [
    { name: "light", label: "Daylight", emoji: "☀️" },
    { name: "dark", label: "Midnight", emoji: "🌙" },
    { name: "ocean", label: "Ocean", emoji: "🌊" },
    { name: "space", label: "Space", emoji: "🚀" },
    { name: "forest", label: "Forest", emoji: "🌿" },
    { name: "sunshine", label: "Sunshine", emoji: "🌻" }
  ];

  function isKnown(name) {
    for (var i = 0; i < THEMES.length; i++) {
      if (THEMES[i].name === name) return true;
    }
    return false;
  }

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* storage unavailable */ }
  // An unknown saved value (hand-edited storage, or a theme removed in a later
  // version) must not leave the page unstyled -- fall back as if nothing were saved.
  // Default = Sunshine (maintainer, 2026-08-20: "set desert theme colours as
  // default"). Deliberately unconditional -- a dark-OS machine still opens in
  // the warm desert look; Midnight stays one tap away in Settings.
  var theme = (saved && isKnown(saved)) ? saved : "sunshine";
  document.documentElement.setAttribute("data-theme", theme);

  function apply(name) {
    theme = name;
    document.documentElement.setAttribute("data-theme", name);
    try { localStorage.setItem(KEY, name); } catch (e) { /* storage unavailable */ }
  }

  // Exposed for the Settings picker (same file would be simpler, but settings.js
  // owns every other Settings control -- keeping theme STATE here means this
  // file stays "the only place theme state is written").
  window.mentarTheme = {
    themes: THEMES,
    current: function () { return theme; },
    apply: apply
  };

  document.addEventListener("DOMContentLoaded", function () {
    var host = document.querySelector("#theme-picker");
    if (!host) return;
    host.innerHTML = "";
    var buttons = [];

    function markCurrent() {
      for (var i = 0; i < buttons.length; i++) {
        var isOn = buttons[i].getAttribute("data-theme-name") === theme;
        buttons[i].classList.toggle("is-active", isOn);
        // aria-pressed carries the state for a screen reader; the checkmark and
        // the border carry it visually -- colour is never the only signal.
        buttons[i].setAttribute("aria-pressed", isOn ? "true" : "false");
      }
    }

    THEMES.forEach(function (t) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "theme-swatch";
      btn.setAttribute("data-theme-name", t.name);
      btn.setAttribute("aria-label", "Use the " + t.label + " theme");

      // The dot previews the theme's own --primary. It is set from a scoped
      // [data-theme] wrapper rather than a hardcoded hex, so a palette edit in
      // style.css is reflected here automatically and can never drift.
      var dot = document.createElement("span");
      dot.className = "theme-swatch-dot";
      dot.setAttribute("data-theme", t.name);

      var face = document.createElement("span");
      face.className = "theme-swatch-face";
      face.textContent = t.emoji;

      var label = document.createElement("span");
      label.className = "theme-swatch-label";
      label.textContent = t.label;

      btn.appendChild(dot);
      btn.appendChild(face);
      btn.appendChild(label);
      btn.addEventListener("click", function () {
        apply(t.name);
        markCurrent();
      });
      host.appendChild(btn);
      buttons.push(btn);
    });

    markCurrent();
  });
})();
