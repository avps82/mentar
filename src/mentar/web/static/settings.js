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
