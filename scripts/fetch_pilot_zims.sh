#!/usr/bin/env bash
# fetch_pilot_zims.sh — Download pilot ZIM files for Mentar grounding (W7).
#
# Downloads:
#   - Vikidia EN (all, no pictures) — primary child-appropriate source
#   - Simple English Wikipedia (all, no pictures) — backup source
#
# Output dir: ${MENTAR_ZIM_DIR:-./zims}
# ZIM files are GITIGNORED (*.zim in .gitignore). Never commit them.
#
# Usage:
#   bash scripts/fetch_pilot_zims.sh
#   MENTAR_ZIM_DIR=/data/zims bash scripts/fetch_pilot_zims.sh
#
# Kiwix download library: https://download.kiwix.org/zim/
# These URLs point to the most recent stable release of each ZIM.
# Update version strings after a new Kiwix release by checking:
#   https://download.kiwix.org/zim/vikidia/
#   https://download.kiwix.org/zim/wikipedia/
#
# Spec: docs/design/W7_grounding_reader.md (ZIM acquisition / W7.4).

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────────

ZIM_DIR="${MENTAR_ZIM_DIR:-./zims}"

# Kiwix CDN base URL
KIWIX_BASE="https://download.kiwix.org/zim"

# ZIM filenames (update version date after new Kiwix releases)
VIKIDIA_FILE="vikidia_en_all_nopic_2024-09.zim"
SIMPLE_WIKI_FILE="wikipedia_en_simple_all_nopic_2024-09.zim"

# Destination filenames (what config/inference.example.yaml expects)
VIKIDIA_DEST="vikidia_en_all_nopic.zim"
SIMPLE_WIKI_DEST="wikipedia_en_simple_all.zim"

# ── Helpers ──────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No colour

info()    { echo -e "${GREEN}[fetch-zims]${NC} $*"; }
warn()    { echo -e "${YELLOW}[fetch-zims] WARN:${NC} $*"; }
die()     { echo -e "${RED}[fetch-zims] ERROR:${NC} $*" >&2; exit 1; }

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "$1 is required but not installed."
}

download() {
    local url="$1"
    local dest="$2"
    local label="$3"

    if [[ -f "$dest" ]]; then
        info "$label already downloaded at $dest — skipping."
        return 0
    fi

    info "Downloading $label ..."
    info "  URL:  $url"
    info "  Dest: $dest"

    # Prefer wget (progress bar); fall back to curl
    if command -v wget >/dev/null 2>&1; then
        wget --no-verbose --show-progress -O "${dest}.tmp" "$url"
    elif command -v curl >/dev/null 2>&1; then
        curl -L --progress-bar -o "${dest}.tmp" "$url"
    else
        die "Neither wget nor curl found. Install one and retry."
    fi

    mv "${dest}.tmp" "$dest"
    info "$label downloaded: $(du -sh "$dest" | cut -f1)"
}

# ── Main ─────────────────────────────────────────────────────────────────────

info "Pilot ZIM download script (W7.4)"
info "ZIM_DIR=${ZIM_DIR}"
echo ""

mkdir -p "${ZIM_DIR}"

# 1. Vikidia EN (all articles, no pictures) — ~200 MB
download \
    "${KIWIX_BASE}/vikidia/${VIKIDIA_FILE}" \
    "${ZIM_DIR}/${VIKIDIA_DEST}" \
    "Vikidia EN (no-pic)"

# 2. Simple English Wikipedia (all articles, no pictures) — ~900 MB
download \
    "${KIWIX_BASE}/wikipedia/${SIMPLE_WIKI_FILE}" \
    "${ZIM_DIR}/${SIMPLE_WIKI_DEST}" \
    "Simple English Wikipedia (no-pic)"

echo ""
info "Done. ZIMs are in ${ZIM_DIR}/"
info ""
info "Next steps:"
info "  1. Set MENTAR_ZIM_DIR=${ZIM_DIR} in your environment (or config/inference.yaml)."
info "  2. Run:  pytest tests/grounding/  (uses fixture ZIM, not these downloads)"
info "  3. For live end-to-end:  python3 -c \""
info "       from mentar.grounding import resolve_grounding"
info "       import yaml, pathlib"
info "       cfg = yaml.safe_load(pathlib.Path('config/inference.yaml').read_text())['grounding']"
info "       node = {'source': 'vikidia', 'anchor': 'https://en.vikidia.org/wiki/Fraction',"
info "               'passage_hint': 'Opening section — fraction as part of something'}"
info "       print(resolve_grounding(node, cfg))"
info "     \""
