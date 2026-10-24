#!/bin/bash
# Local fallback for the sketchbook style, under the shared GPU lock.
#   localgen.sh flux|zimage "<prompt>" out.png [seed] [width] [height]
# FLUX.2 klein 4B 8-bit: 4 steps. Z-Image Turbo 8-bit: 9 steps.
set -e
ENGINE=$1; PROMPT=$2; OUT=$3; SEED=${4:-7}; W=${5:-1024}; H=${6:-1024}
M=${MODELS:?set MODELS to the folder holding the FLUX.2 klein / Z-Image models}
case "$ENGINE" in
  flux)   CMD=$HOME/.local/bin/mflux-generate-flux2;        MODEL=$M/flux2-klein-4b-8bit; BASE=flux2-klein-4b; STEPS=4 ;;
  zimage) CMD=$HOME/.local/bin/mflux-generate-z-image-turbo; MODEL=$M/z-image-turbo-8bit;  BASE=z-image-turbo;  STEPS=9 ;;
  *) echo "engine: flux or zimage"; exit 2 ;;
esac
[ -e "$MODEL" ] || { echo "model missing: $MODEL"; exit 1; }
L=${GPU_LOCK:-/tmp/sketchbook-gpu.lock}
take() { while ! mkdir "$L" 2>/dev/null; do
    pid=$(awk '{print $2}' "$L/owner" 2>/dev/null)
    if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then rm -f "$L/owner"; rmdir "$L" 2>/dev/null; continue; fi
    sleep 3; done; echo "sketchbook $$ $(date +%s)" > "$L/owner"; }
give() { grep -q "^sketchbook $$ " "$L/owner" 2>/dev/null && { rm -f "$L/owner"; rmdir "$L"; }; true; }
TMP=$(mktemp -d); printf '%s' "$PROMPT" > "$TMP/prompt.txt"
take; trap 'give; rm -rf "$TMP"' EXIT
T0=$(date +%s)
"$CMD" --model "$MODEL" --base-model "$BASE" --prompt-file "$TMP/prompt.txt" --width "$W" --height "$H" --steps "$STEPS" --seed "$SEED" --output "$OUT"
echo "done $OUT $(( $(date +%s) - T0 )) s"
