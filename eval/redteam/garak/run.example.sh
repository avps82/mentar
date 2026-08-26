#!/usr/bin/env bash
# Garak red-team run against Mentar's OpenAI-compatible endpoint (run-only; see README.md).
# Garak is NOT a Mentar dependency — install it in its own venv: pip install garak
set -euo pipefail

# --- configure ---------------------------------------------------------------
: "${OPENAI_BASE_URL:?set OPENAI_BASE_URL, e.g. http://192.168.1.10:4000/v1 (or http://localhost:11434/v1 for Ollama)}"
: "${OPENAI_API_KEY:=${MENTAR_VLLM_API_KEY:-no-key}}"   # Mentar's token; local servers accept any
export OPENAI_API_KEY
export GARAK_TELEMETRY=0                                  # do not phone home (verify)

MODEL="${MENTAR_MODEL:-gemma2:9b}"
PROBES="${GARAK_PROBES:-promptinject,dan,encoding,latentinjection,leakreplay}"

echo "Garak -> ${OPENAI_BASE_URL}  model=${MODEL}"
echo "probes: ${PROBES}"

garak \
  --model_type openai \
  --model_name "${MODEL}" \
  --probes "${PROBES}" \
  --report_prefix mentar_garak

echo "Done. Triage findings into safety/escalation.py + eval/redteam/prompt_injection.jsonl,"
echo "and judge against the FSM wrapper, not the raw model alone."
