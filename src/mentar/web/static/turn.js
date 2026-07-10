/*
 * Owned, zero-dependency progressive enhancement for the answer form (U-90).
 * No CDN, no build step, no third-party code — see docs/design/UI_REQUIREMENTS.md §5.
 * Intercepts the POST /answer submit and swaps the question text in place instead
 * of a full page reload. Any failure (no fetch, network error, unexpected reply)
 * falls back to a normal form submit, so the app works identically with JS off.
 */
document.addEventListener("DOMContentLoaded", function () {
  var form = document.querySelector('form[action="/answer"]');
  if (!form || typeof window.fetch !== "function") return;

  var questionEl = document.querySelector(".question");
  var input = form.querySelector('input[name="answer"]');

  form.addEventListener("submit", function (evt) {
    evt.preventDefault();
    fetch(form.action, {
      method: "POST",
      body: new URLSearchParams(new FormData(form)),
      headers: { "X-Requested-With": "fetch" },
    })
      .then(function (resp) { return resp.json(); })
      .then(function (data) {
        if (data.redirect) {
          window.location.href = data.redirect;
        } else if (data.full_html) {
          document.open();
          document.write(data.full_html);
          document.close();
        } else if (questionEl && typeof data.question === "string") {
          questionEl.textContent = data.question;
          if (input) {
            input.value = "";
            input.focus();
          }
        } else {
          form.submit();
        }
      })
      .catch(function () {
        form.submit();
      });
  });
});
