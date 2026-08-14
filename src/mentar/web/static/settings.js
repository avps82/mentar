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
    // 2026-08-14 (maintainer: "settings is still a mess... use tabs"): ONE TAB
    // PER COUNTRY, each panel opening with that country's master switch, grades
    // under it. Before this, all 71 packs from every country were stacked in one
    // scrolling column with <h3>/<h4> headings.
    //
    // "General" is the group for the country-less pilot/practice packs; it sorts
    // last (same posture as the picker's "Try-out topics"). The backend already
    // sorts each country's packs grade-then-subject, so grouping here only adds
    // the sub-heading -- never re-sort grade strings in JS ("Year 10" < "Year 2").
    var COUNTRY_NAMES = {
        AU: "🇦🇺 Australia",
        IN: "🇮🇳 India",
        SG: "🇸🇬 Singapore",
        US: "🇺🇸 United States",
        General: "🧪 General",
    };
    var activeCountry = null;  // survives a re-render (a toggle refetches the list)

    function switchWidget(checked, ariaLabel) {
        // R12.2: a real switch widget (native checkbox), not a text button.
        var sw = document.createElement("label");
        sw.className = "switch";
        var input = document.createElement("input");
        input.type = "checkbox";
        input.checked = checked;
        input.setAttribute("aria-label", ariaLabel);
        var slider = document.createElement("span");
        slider.className = "slider";
        sw.appendChild(input);
        sw.appendChild(slider);
        return sw;
    }

    function packRow(c, onSaved) {
        var row = document.createElement("div");
        row.className = "curricula-row";

        var label = document.createElement("strong");
        label.textContent = c.label;

        var sw = switchWidget(c.enabled, "Turn " + c.label + " on or off");
        var input = sw.querySelector("input");

        var status = document.createElement("span");
        status.className = "hint";

        input.onchange = function () {
            var action = input.checked ? "enable" : "disable";
            fetch("/settings/curricula/" + encodeURIComponent(c.key) + "/" + action, {
                method: "POST",
            }).then(function (r) {
                return r.json();
            }).then(function (res) {
                if (res.ok) {
                    c.enabled = res.enabled;
                    input.checked = res.enabled;
                    status.textContent = "Saved — restart Mentar to apply.";
                    onSaved();
                } else {
                    // Never show a state the server rejected.
                    status.textContent = "Error: " + res.error;
                    input.checked = c.enabled;
                }
            }).catch(function () {
                status.textContent = "Error: could not save.";
                input.checked = c.enabled;
            });
        };

        row.appendChild(label);
        row.appendChild(sw);
        row.appendChild(status);
        return row;
    }

    function countryPanel(country, packs, reload) {
        var panel = document.createElement("div");
        panel.className = "tab-panel";
        panel.id = "curricula-panel";
        panel.setAttribute("role", "tabpanel");
        panel.setAttribute("aria-labelledby", "curricula-tab-" + country);

        // The master switch, FIRST -- the whole country on or off in one call.
        var master = document.createElement("div");
        master.className = "curricula-master";
        var masterLabel = document.createElement("strong");
        masterLabel.textContent = "Use the " + COUNTRY_NAMES[country].replace(/^\S+\s/, "") +
            " curriculum";
        var enabledCount = packs.filter(function (c) { return c.enabled; }).length;
        var masterSw = switchWidget(enabledCount > 0, "Turn the whole " + country + " curriculum on or off");
        var masterInput = masterSw.querySelector("input");
        // Native tri-state: SOME on shows a dash, not a lie in either direction.
        masterInput.indeterminate = enabledCount > 0 && enabledCount < packs.length;
        var masterStatus = document.createElement("span");
        masterStatus.className = "hint";

        masterInput.onchange = function () {
            var action = masterInput.checked ? "enable" : "disable";
            fetch("/settings/curricula/country/" + encodeURIComponent(country) + "/" + action, {
                method: "POST",
            }).then(function (r) {
                return r.json();
            }).then(function (res) {
                if (res.ok) {
                    reload();  // server is the truth -- re-render every row from it
                } else {
                    masterStatus.textContent = "Error: " + res.error;
                    masterInput.checked = enabledCount > 0;
                }
            }).catch(function () {
                masterStatus.textContent = "Error: could not save.";
                masterInput.checked = enabledCount > 0;
            });
        };

        master.appendChild(masterLabel);
        master.appendChild(masterSw);
        master.appendChild(masterStatus);
        panel.appendChild(master);

        var lastGrade = null;
        packs.forEach(function (c) {
            var grade = c.year_level || "";
            if (grade !== lastGrade) {
                var gradeHeading = document.createElement("h4");
                gradeHeading.className = "curricula-grade-heading";
                gradeHeading.textContent = grade || "General";
                panel.appendChild(gradeHeading);
                lastGrade = grade;
            }
            panel.appendChild(packRow(c, function () {
                // A single pack changed -- repaint the master switch's tri-state
                // without discarding the "Saved" hints already on screen.
                var on = packs.filter(function (p) { return p.enabled; }).length;
                masterInput.checked = on > 0;
                masterInput.indeterminate = on > 0 && on < packs.length;
            }));
        });
        return panel;
    }

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

                var groups = {};
                data.curricula.forEach(function (c) {
                    var key = c.country || "General";
                    if (!COUNTRY_NAMES[key]) COUNTRY_NAMES[key] = key;  // a new pack's country
                    if (!groups[key]) groups[key] = [];
                    groups[key].push(c);
                });
                var countries = Object.keys(groups).sort(function (a, b) {
                    if (a === "General") return 1;      // try-out packs last
                    if (b === "General") return -1;
                    return COUNTRY_NAMES[a].localeCompare(COUNTRY_NAMES[b]);
                });
                if (countries.indexOf(activeCountry) === -1) activeCountry = countries[0];

                var tablist = document.createElement("div");
                tablist.className = "tabs";
                tablist.setAttribute("role", "tablist");
                tablist.setAttribute("aria-label", "Curriculum country");

                countries.forEach(function (country) {
                    var tab = document.createElement("button");
                    tab.type = "button";
                    tab.className = "tab-btn";
                    tab.id = "curricula-tab-" + country;
                    tab.textContent = COUNTRY_NAMES[country];
                    tab.setAttribute("role", "tab");
                    tab.setAttribute("aria-controls", "curricula-panel");
                    var selected = country === activeCountry;
                    tab.setAttribute("aria-selected", selected ? "true" : "false");
                    tab.tabIndex = selected ? 0 : -1;  // roving tabindex (ARIA tabs pattern)
                    tab.onclick = function () {
                        activeCountry = country;
                        render();
                        var fresh = document.getElementById("curricula-tab-" + country);
                        if (fresh) fresh.focus();
                    };
                    tab.onkeydown = function (evt) {
                        var step = evt.key === "ArrowRight" ? 1 : (evt.key === "ArrowLeft" ? -1 : 0);
                        if (!step) return;
                        evt.preventDefault();
                        var i = countries.indexOf(activeCountry);
                        activeCountry = countries[(i + step + countries.length) % countries.length];
                        render();
                        var next = document.getElementById("curricula-tab-" + activeCountry);
                        if (next) next.focus();
                    };
                    tablist.appendChild(tab);
                });

                function render() {
                    container.innerHTML = "";
                    Array.prototype.forEach.call(tablist.children, function (tab) {
                        var selected = tab.id === "curricula-tab-" + activeCountry;
                        tab.setAttribute("aria-selected", selected ? "true" : "false");
                        tab.tabIndex = selected ? 0 : -1;
                    });
                    container.appendChild(tablist);
                    container.appendChild(
                        countryPanel(activeCountry, groups[activeCountry], loadCurricula)
                    );
                }
                render();
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
