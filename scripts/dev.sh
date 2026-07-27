#!/usr/bin/env bash
# One-click local dev: fetch Scholar (opt-in), build the CV, export site data,
# and spin up the Astro dev server if it isn't already running.
#
# Usage:
#   ./scripts/dev.sh                  # full run, start website
#   ./scripts/dev.sh --no-scholar     # skip Scholar fetch
#   ./scripts/dev.sh --no-compile     # render LaTeX but don't run xelatex
#   SCHOLAR_ID=XXXX ./scripts/dev.sh  # override Scholar ID
#
# Requires: conda env 'cv' (conda activate cv && poetry install), xelatex, node/npm.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# ── Conda ────────────────────────────────────────────────────────────────────
CONDA_BASE="$(conda info --base 2>/dev/null || true)"
if [ -n "$CONDA_BASE" ]; then
    source "$CONDA_BASE/etc/profile.d/conda.sh"
    conda activate cv
else
    echo "Warning: conda not found — assuming 'cv' is already on PATH"
fi

# ── Flags ────────────────────────────────────────────────────────────────────
SCHOLAR_ID="${SCHOLAR_ID:---kj4bcAAAAJ}"
FETCH_SCHOLAR=true
NO_COMPILE=false

for arg in "$@"; do
    case "$arg" in
        --no-scholar) FETCH_SCHOLAR=false ;;
        --no-compile) NO_COMPILE=true ;;
    esac
done

COMPILE_FLAG=""
$NO_COMPILE && COMPILE_FLAG="--no-compile"

# ── Scholar (best-effort) ────────────────────────────────────────────────────
if $FETCH_SCHOLAR; then
    echo "==> Fetching Scholar metrics (ID: $SCHOLAR_ID)…"
    cv scholar --scholar-id "$SCHOLAR_ID" || echo "  Scholar fetch failed — continuing with cached data"
fi

# ── CV ───────────────────────────────────────────────────────────────────────
echo "==> Building CV…"
# shellcheck disable=SC2086
cv build-cv $COMPILE_FLAG

# ── Site data ────────────────────────────────────────────────────────────────
echo "==> Exporting site data…"
cv build-site

# ── Astro dev server ─────────────────────────────────────────────────────────
cd "$ROOT/website"
if lsof -ti :4321 >/dev/null 2>&1 || lsof -ti :4322 >/dev/null 2>&1; then
    echo "==> Dev server already running — refresh your browser"
else
    echo "==> Starting Astro dev server…"
    npm run dev &
    echo "    → http://localhost:4321/"
fi
