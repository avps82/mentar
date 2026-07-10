/*
 * Owned light/dark theme toggle (nice-to-have per U-92 discussion). No deps,
 * no external fetch: reads a saved preference or the OS setting, persists
 * the user's explicit choice in localStorage.
 */
(function () {
  var KEY = "mentar-theme";
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* storage unavailable */ }
  var prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  var theme = saved || (prefersDark ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", theme);

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.querySelector(".theme-toggle");
    if (!btn) return;
    btn.textContent = theme === "dark" ? "☀️ Light" : "🌙 Dark";
    btn.addEventListener("click", function () {
      theme = theme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", theme);
      btn.textContent = theme === "dark" ? "☀️ Light" : "🌙 Dark";
      try { localStorage.setItem(KEY, theme); } catch (e) { /* storage unavailable */ }
    });
  });
})();
