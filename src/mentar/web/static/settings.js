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
        var btn = document.getElementById("llm-recheck-btn");

        // 2026-08-14 (maintainer: "check again is not doing anything"): the check
        // now asks the model to generate, which can take a cold load's worth of
        // seconds, and a re-check often returns the SAME text -- so say it's
        // running, block a second click, and stamp the time so an unchanged
        // answer still visibly updates.
        statusLine.textContent = "Checking… (this can take a moment if the model has to load)";
        if (btn) btn.disabled = true;

        fetch("/settings/llm-status")
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                var at = data.checked_at ? " · checked " + data.checked_at : "";
                if (data.ok) {
                    statusLine.textContent = "🟢 Connected (" + data.model + ", " + data.latency_ms + "ms)" + at;
                } else if (data.ok === null) {
                    // In-process model: nothing to probe over HTTP.
                    statusLine.textContent = "ℹ️ " + data.error;
                } else {
                    statusLine.textContent = "🔴 " + data.model + " not answering at " +
                        data.base_url + " (" + data.error + ")" + at;
                }
            })
            .catch(function () {
                statusLine.textContent = "🔴 Could not check status.";
            })
            .then(function () {
                if (btn) btn.disabled = false;
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
    // Filled from /settings/curricula -- the server owns this map (app.py
    // COUNTRY_NAMES) so the picker and this page can never drift apart.
    var COUNTRY_NAMES = {};

    // Flags as inline SVG, NOT emoji (2026-08-15, maintainer on Windows: "country
    // has AU Australia??? Why AU?? There should be a Australian flag").
    //
    // The emoji were there and correct -- 🇦🇺 is U+1F1E6 U+1F1FA, a pair of regional
    // indicators. WINDOWS HAS NO FLAG GLYPHS: Segoe UI Emoji ships none, so every
    // browser on Windows falls back to drawing the two letters. macOS showed a flag,
    // Windows showed "AU", from identical markup. Nothing in our data was wrong and
    // no amount of fixing it would have helped -- the glyph does not exist there.
    //
    // These are deliberately SIMPLIFIED: recognisable at 18px, no attempt at exact
    // heraldry (the Union Jack canton in particular is approximated). They are drawn,
    // not fetched -- U-80 forbids a CDN, and an offline tutor cannot depend on one.
    var FLAGS = {
        AU: '<svg viewBox="0 0 60 30" class="flag" aria-hidden="true">' +
            '<rect width="60" height="30" fill="#00247d"/>' +
            '<path d="M0 0l30 15M30 0L0 15" stroke="#fff" stroke-width="3"/>' +
            '<path d="M0 0l30 15M30 0L0 15" stroke="#cf142b" stroke-width="1.6"/>' +
            '<path d="M15 0v15M0 7.5h30" stroke="#fff" stroke-width="5"/>' +
            '<path d="M15 0v15M0 7.5h30" stroke="#cf142b" stroke-width="3"/>' +
            '<g fill="#fff"><circle cx="15" cy="23" r="2.6"/><circle cx="45" cy="7" r="1.5"/>' +
            '<circle cx="52" cy="14" r="1.5"/><circle cx="45" cy="23" r="1.5"/>' +
            '<circle cx="38" cy="15" r="1.2"/><circle cx="47" cy="17" r="0.9"/></g></svg>',
        IN: '<svg viewBox="0 0 60 30" class="flag" aria-hidden="true">' +
            '<rect width="60" height="10" fill="#ff9933"/>' +
            '<rect y="10" width="60" height="10" fill="#fff"/>' +
            '<rect y="20" width="60" height="10" fill="#138808"/>' +
            '<circle cx="30" cy="15" r="4" fill="none" stroke="#000080" stroke-width="1.2"/>' +
            '<circle cx="30" cy="15" r="1" fill="#000080"/></svg>',
        SG: '<svg viewBox="0 0 60 30" class="flag" aria-hidden="true">' +
            '<rect width="60" height="15" fill="#ed2939"/>' +
            '<rect y="15" width="60" height="15" fill="#fff"/>' +
            '<path d="M18 7.5a6 6 0 1 1-6-6 7.2 7.2 0 0 0 0 12 6 6 0 0 1 6-6z" fill="#fff"/>' +
            '<g fill="#fff"><circle cx="21" cy="4" r="1.1"/><circle cx="25" cy="7" r="1.1"/>' +
            '<circle cx="23.5" cy="11.5" r="1.1"/><circle cx="18.5" cy="11.5" r="1.1"/>' +
            '<circle cx="17" cy="7" r="1.1"/></g></svg>',
        US: '<svg viewBox="0 0 60 30" class="flag" aria-hidden="true">' +
            '<rect width="60" height="30" fill="#fff"/>' +
            '<g fill="#b22234"><rect width="60" height="2.3"/><rect y="4.6" width="60" height="2.3"/>' +
            '<rect y="9.2" width="60" height="2.3"/><rect y="13.8" width="60" height="2.3"/>' +
            '<rect y="18.4" width="60" height="2.3"/><rect y="23" width="60" height="2.3"/>' +
            '<rect y="27.6" width="60" height="2.3"/></g>' +
            '<rect width="24" height="16.1" fill="#3c3b6e"/>' +
            '<g fill="#fff"><circle cx="4" cy="4" r="1"/><circle cx="12" cy="4" r="1"/>' +
            '<circle cx="20" cy="4" r="1"/><circle cx="8" cy="8" r="1"/><circle cx="16" cy="8" r="1"/>' +
            '<circle cx="4" cy="12" r="1"/><circle cx="12" cy="12" r="1"/>' +
            '<circle cx="20" cy="12" r="1"/></g></svg>',
        General: '<svg viewBox="0 0 60 30" class="flag" aria-hidden="true">' +
            '<rect width="60" height="30" fill="#8a8f98" rx="3"/>' +
            '<circle cx="30" cy="15" r="7" fill="none" stroke="#fff" stroke-width="2"/>' +
            '<path d="M30 8v14M23 15h14" stroke="#fff" stroke-width="2"/></svg>',
    };

    function countryLabelHtml(code) {
        var name = COUNTRY_NAMES[code] || code;
        return (FLAGS[code] || "") + "<span>" + name + "</span>";
    }
    var activeCountry = null;  // survives a re-render (switching tabs rebuilds the panel)
    var activeCountries = [];  // countries switched on, from the server (see /settings/curricula)

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
                    status.textContent = res.enabled ? "On" : "Off";
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
        return {row: row, input: input, pack: c};
    }

    function countryPanel(country, packs) {
        var panel = document.createElement("div");
        panel.className = "tab-panel";
        panel.id = "curricula-panel";
        panel.setAttribute("role", "tabpanel");
        panel.setAttribute("aria-labelledby", "curricula-tab-" + country);

        // The master switch, FIRST -- the whole country on or off in one call.
        var master = document.createElement("div");
        master.className = "curricula-master";
        var masterLabel = document.createElement("strong");
        masterLabel.textContent = "Use the " + (COUNTRY_NAMES[country] || country) + " curriculum";
        var enabledCount = packs.filter(function (c) { return c.enabled; }).length;
        // From the server's OWN record of which countries are on -- not inferred from
        // "any pack enabled", which would read as off the moment a parent switches a
        // country on and has not picked a year yet (the normal state now).
        var countryOn = activeCountries.indexOf(country) !== -1 || enabledCount > 0;
        var masterSw = switchWidget(countryOn, "Turn the " + country + " curriculum on or off");
        var masterInput = masterSw.querySelector("input");
        // Native tri-state: SOME on shows a dash, not a lie in either direction.
        // No tri-state any more: ON no longer means "all of them", so a dash would be
        // describing a state that is now simply normal.
        masterInput.indeterminate = false;
        var masterStatus = document.createElement("span");
        masterStatus.className = "hint";

        // Every per-grade switch in this panel, so the master can move them all in
        // place. 2026-08-14 (maintainer: "the country toggle doesn't disable all the
        // subjects under it"): this used to re-fetch the listing and rebuild the
        // panel, which left the rows showing their old state -- a GET with no
        // cache headers can be served from the browser's cache, so the "truth" the
        // rebuild painted was the state from before the POST. The server has already
        // confirmed what it did, so repaint from that instead of asking again.
        var rowSwitches = [];

        // When a country is off, its years are visible but not interactive -- the
        // parent can see what is on offer without being able to half-enable a
        // country. Nothing is hidden; hidden options are how a parent concludes the
        // curriculum they were promised is missing.
        function setPanelEnabled(on) {
            rowSwitches.forEach(function (row) {
                row.input.disabled = !on;
            });
            panel.classList.toggle("country-off", !on);
        }

        masterInput.onchange = function () {
            var action = masterInput.checked ? "enable" : "disable";
            var wasOn = enabledCount > 0;
            fetch("/settings/curricula/country/" + encodeURIComponent(country) + "/" + action, {
                method: "POST",
            }).then(function (r) {
                return r.json();
            }).then(function (res) {
                if (res.ok) {
                    // ON reveals the years and subjects; it does NOT switch them on
                    // (maintainer 2026-08-15: "the parent will turn on what they
                    // want"). Bulk-enabling ~25 packs turned a master switch into a
                    // chore generator -- turn it on, then hunt through every year
                    // turning off what you did not ask for. OFF still clears them all,
                    // because "none of this" is one intent worth one click.
                    if (!res.enabled) {
                        rowSwitches.forEach(function (row) {
                            row.pack.enabled = false;
                            row.input.checked = false;
                        });
                    }
                    enabledCount = res.count;
                    masterInput.indeterminate = false;
                    setPanelEnabled(res.enabled);
                    masterStatus.textContent = res.enabled
                        ? "On — now choose the years you want below."
                        : "Off — everything for this country is turned off.";
                } else {
                    masterStatus.textContent = "Error: " + res.error;
                    masterInput.checked = wasOn;
                }
            }).catch(function () {
                masterStatus.textContent = "Error: could not save.";
                masterInput.checked = wasOn;
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
            var built = packRow(c, function () {
                // A single pack changed. The master switch is NOT recomputed from the
                // row states: a country stays on when a parent turns its last year
                // off, because they chose the country deliberately and un-choosing it
                // is a separate act. Turning the master off is the way to say "none".
                enabledCount = packs.filter(function (p) { return p.enabled; }).length;
            });
            rowSwitches.push(built);
            panel.appendChild(built.row);
        });
        setPanelEnabled(countryOn);   // first paint, not only after a toggle
        return panel;
    }

    function loadCurricula() {
        var container = document.getElementById("curricula-toggle-list");
        if (!container) return;

        fetch("/settings/curricula", {cache: "no-store"})
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                activeCountries = data.active_countries || [];
                COUNTRY_NAMES = data.country_names || {};
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
                    return (COUNTRY_NAMES[a] || a).localeCompare(COUNTRY_NAMES[b] || b);
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
                    tab.innerHTML = countryLabelHtml(country);
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
                    container.appendChild(countryPanel(activeCountry, groups[activeCountry]));
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
