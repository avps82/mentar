/*
 * Owned voice picker for the browser's built-in speechSynthesis (R5). Reads
 * getVoices() -- lazily populated on some browsers, hence the onvoiceschanged
 * re-run -- and persists the choice to localStorage under the SAME key
 * tts.js reads to pick the tutor's read-aloud voice.
 */
(function () {
    "use strict";

    // ── Local LLM connectivity check (settings-page follow-up) ─────────────
    function checkLlmStatus() {
        var statusLine = document.getElementById("llm-status-line");
        if (!statusLine) return;

        statusLine.textContent = "Checking…";

        fetch("/settings/llm-status")
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.ok) {
                    statusLine.textContent = "🟢 Connected (" + data.model + ", " + data.latency_ms + "ms)";
                } else if (data.ok === null) {
                    // In-process model: nothing to probe over HTTP.
                    statusLine.textContent = "ℹ️ " + data.error;
                } else {
                    statusLine.textContent = "🔴 Not reachable at " + data.base_url + " (" + data.error + ")";
                }
            })
            .catch(function () {
                statusLine.textContent = "🔴 Could not check status.";
            });
    }

    if (document.getElementById("llm-status-line")) {
        checkLlmStatus();
    }

    var recheckBtn = document.getElementById("llm-recheck-btn");
    if (recheckBtn) {
        recheckBtn.addEventListener("click", function () {
            checkLlmStatus();
        });
    }

    // ── Curricula: on/off toggle for in-repo packs (R10) ────────────────────
    function loadCurricula() {
        var container = document.getElementById("curricula-toggle-list");
        if (!container) return;

        fetch("/settings/curricula")
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                container.innerHTML = "";
                if (!data.curricula || data.curricula.length === 0) {
                    container.textContent = "No curricula found.";
                    return;
                }

                data.curricula.forEach(function (c) {
                    var row = document.createElement("div");
                    row.style.marginBottom = "12px";

                    var label = document.createElement("strong");
                    label.textContent = c.label;

                    var btn = document.createElement("button");
                    btn.style.marginLeft = "10px";
                    function paint() {
                        btn.textContent = c.enabled ? "On — turn off" : "Off — turn on";
                    }
                    paint();
                    var status = document.createElement("span");
                    status.className = "hint";
                    status.style.marginLeft = "10px";

                    btn.onclick = function () {
                        var action = c.enabled ? "disable" : "enable";
                        fetch("/settings/curricula/" + encodeURIComponent(c.key) + "/" + action, {
                            method: "POST",
                        }).then(function (r) {
                            return r.json();
                        }).then(function (res) {
                            if (res.ok) {
                                c.enabled = res.enabled;
                                paint();
                                status.textContent = "Saved — restart Mentar to apply.";
                            } else {
                                status.textContent = "Error: " + res.error;
                            }
                        });
                    };

                    row.appendChild(label);
                    row.appendChild(btn);
                    row.appendChild(status);
                    container.appendChild(row);
                });
            })
            .catch(function () {
                container.textContent = "Could not load curricula.";
            });
    }

    if (document.getElementById("curricula-toggle-list")) {
        loadCurricula();
    }

    // ── Downloadable REMOTE packs (R8, dormant) ─────────────────────────────
    // Empty today -- every authored pack ships in-repo and is toggled above.
    // Renders nothing when there are none, rather than a confusing message.
    function loadCurriculumPacks() {
        var container = document.getElementById("curriculum-packs-list");
        if (!container) return;

        fetch("/settings/curriculum-packs")
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                container.innerHTML = "";
                if (!data.packs || data.packs.length === 0) {
                    return;  // dormant -- show nothing
                }

                data.packs.forEach(function (pack) {
                    var div = document.createElement("div");
                    div.style.marginBottom = "20px";

                    var title = document.createElement("strong");
                    title.textContent = pack.label;

                    var desc = document.createElement("p");
                    desc.textContent = pack.description;

                    var lic = document.createElement("p");
                    var licSmall = document.createElement("small");
                    licSmall.textContent = pack.licence;
                    lic.appendChild(licSmall);

                    var btn = document.createElement("button");
                    var action = pack.installed ? "uninstall" : "install";
                    btn.textContent = pack.installed ? "Uninstall" : "⬇️ Download";
                    btn.onclick = function () {
                        fetch("/settings/curriculum-packs/" + pack.id + "/" + action, {
                            method: "POST",
                        }).then(function (r) {
                            return r.json();
                        }).then(function (res) {
                            var status = document.createElement("p");
                            status.textContent = res.ok
                                ? "Done — restart Mentar to see the change."
                                : "Error: " + res.error;
                            div.appendChild(status);
                        });
                    };

                    div.appendChild(title);
                    div.appendChild(desc);
                    div.appendChild(lic);
                    div.appendChild(btn);
                    container.appendChild(div);
                });
            })
            .catch(function () {
                container.textContent = "Could not load curriculum packs.";
            });
    }

    if (document.getElementById("curriculum-packs-list")) {
        loadCurriculumPacks();
    }

    if ("speechSynthesis" in window) {
        const voiceSelect = document.getElementById("voice-select");
        const testVoiceBtn = document.getElementById("test-voice-btn");
        const emptyHint = document.getElementById("voice-empty-hint");
        const savedHint = document.getElementById("voice-saved-hint");
        let savedHintTimer = null;

        function populateVoices() {
            const voices = window.speechSynthesis.getVoices();
            if (voiceSelect && voices.length > 0) {
                voiceSelect.innerHTML = "";

                voices.forEach(function (voice) {
                    const option = document.createElement("option");
                    option.value = voice.voiceURI;
                    option.textContent = voice.name + (voice.lang ? " (" + voice.lang + ")" : "");
                    voiceSelect.appendChild(option);
                });

                if (emptyHint) {
                    emptyHint.style.display = "none";
                }

                try {
                    const savedVoice = localStorage.getItem("mentar-tts-voice");
                    if (savedVoice && voiceSelect.options.length > 0) {
                        for (let i = 0; i < voiceSelect.options.length; i++) {
                            if (voiceSelect.options[i].value === savedVoice) {
                                voiceSelect.selectedIndex = i;
                                break;
                            }
                        }
                    }
                } catch (e) {
                    // storage unavailable -- silently skip restoring the saved choice
                }
            } else if (voiceSelect && voices.length === 0 && emptyHint) {
                emptyHint.style.display = "block";
            }
        }

        populateVoices();
        window.speechSynthesis.onvoiceschanged = function () {
            populateVoices();
        };

        if (voiceSelect) {
            voiceSelect.addEventListener("change", function () {
                try {
                    localStorage.setItem("mentar-tts-voice", this.value);
                } catch (e) {
                    // storage unavailable
                }
                // No explicit Save button -- this flash is the only feedback
                // that the choice actually persisted (auto-save on change).
                if (savedHint) {
                    savedHint.style.display = "inline";
                    clearTimeout(savedHintTimer);
                    savedHintTimer = setTimeout(function () {
                        savedHint.style.display = "none";
                    }, 2000);
                }
            });
        }

        if (testVoiceBtn) {
            testVoiceBtn.addEventListener("click", function () {
                const utterance = new SpeechSynthesisUtterance(
                    "This is how I will sound when reading a question."
                );
                const selectedValue = voiceSelect ? voiceSelect.value : "";

                const voices = window.speechSynthesis.getVoices();
                const selectedVoice = voices.find(function (v) {
                    return v.voiceURI === selectedValue;
                });

                if (selectedVoice) {
                    utterance.voice = selectedVoice;
                    utterance.lang = selectedVoice.lang;
                }

                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(utterance);
            });
        }
    }
})();
