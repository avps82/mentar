/*
 * Owned voice picker for the browser's built-in speechSynthesis (R5). Reads
 * getVoices() -- lazily populated on some browsers, hence the onvoiceschanged
 * re-run -- and persists the choice to localStorage under the SAME key
 * tts.js reads to pick the tutor's read-aloud voice.
 */
(function () {
    "use strict";

    if ("speechSynthesis" in window) {
        const voiceSelect = document.getElementById("voice-select");
        const testVoiceBtn = document.getElementById("test-voice-btn");
        const emptyHint = document.getElementById("voice-empty-hint");

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
                }

                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(utterance);
            });
        }
    }
})();
