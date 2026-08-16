#!/bin/bash
# ----------------------------------------------------------------------------
# pricewin-hotel-deal-finder — first-run installer for the agentic version.
# Idempotent.
# ----------------------------------------------------------------------------
set -euo pipefail

cd "$(dirname "$0")"

echo "[pricewin-hotel-deal-finder] Installing Node deps (locked versions)..."
if [ -f package-lock.json ]; then
  npm ci --omit=dev --no-audit --no-fund
else
  npm install --omit=dev --no-audit --no-fund
fi

echo "[pricewin-hotel-deal-finder] Downloading Chromium for Patchright (one-time, ~200MB)..."
npx --yes patchright install chromium

echo "[pricewin-hotel-deal-finder] Done."
echo
echo "First-time usage: the agent will discover selectors live for each site"
echo "and locale (~2-3 minutes per source) and cache them at"
echo "  ~/.cache/pricewin-hotel-deal-finder/selectors.json"
echo "Subsequent searches reuse the cache and complete in ~30 seconds."
