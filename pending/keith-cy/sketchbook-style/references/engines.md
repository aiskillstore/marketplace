# Engine notes (measured 2026-10-17)

Same prompt (A-04 Webb telescope, round-4 CORE, seed 45, 1024×1024) on all three engines, then `inkpost.py`:

| Engine | Time | Peak memory | Ink coverage after inkpost | Look |
| --- | --- | --- | --- | --- |
| Qwen-Image 2.1 Q6, 20 steps, CFG 1 | 120 s (M3 Ultra) | ComfyUI | 0.25 | Scrappy double lines, recognisable honeycomb mirror + sunshield. Best. |
| FLUX.2 klein 4B 8-bit, 4 steps | 90 s | 10.2 GB | 0.18 | Bold, chunky, cartoon-like; mirror became a dark soccer-ball dish; comic speed lines. Usable for sub-style A only. |
| Z-Image Turbo 8-bit, 9 steps | 256 s | 7.6 GB | 0.26 (incl. border) | Fine-pen etching look, dark page border/frame around the paper, octagonal dish. Weakest. |

Qwen CFG test: CFG 1 ~120–135 s, CFG 3 with the negative prompt ~230 s; CFG 3 gave heavier black masses and a more rendered, illustration-like finish. Keep CFG 1 and put every "no …" in the positive prompt.

`scripts/comfygen.py` takes the shared mkdir lock `$GPU_LOCK` per image and never removes a live holder's lock (a dead pid's lock is cleared). If the server returns HTTP 502, restart ComfyUI.

Waiting tip: `pgrep -f "comfygen.py jobs.json"` matches the waiting shell's own command line; use a bracket pattern like `pgrep -f "[c]omfygen.py"`.

## Line weight and coverage, measured (2026-10-18, scripts/measure.py)

Drawing's bounding box scaled to 1024 px. Stroke = median width at ridge pixels (fills excluded); solid = share of ink in areas thicker than 24 px.

| Set | Stroke | Coverage | Solid |
| --- | --- | --- | --- |
| Reference set, all 87 | 5 px (0.49 %) | 0.155 | 0.05 |
| Reference A (12 bold pages) | 7 px (0.68 %) | 0.33 | 0.33 |
| Reference B / C / D / E | 5 / 3 / 1 / 5 px | 0.16 / 0.13 / 0.10 / 0.165 | 0.03 / 0.01 / 0 / 0.05 |
| Ours, pen variant (13) | 1 px (0.10 %), p90 3 px | 0.12 | 0.02 |
| Ours, marker variant (13) | 5 px (0.49 %), p10–p90 1–9 px | 0.24 | 0.45 |
| Ours marker A / B / C / D / E | 9 / 7 / 4 / 1 / 5 px | 0.35 / 0.29 / 0.19 / 0.09 / 0.14 | 0.55 / 0.55 / 0.40 / 0.04 / 0.30 |

An early eyeball estimate of the reference pages' line width (1.5–2.5 % of the width) was too high: only the heaviest page reaches 1.66 %; the typical bold page is 0.68 %. Marker solid share is still higher than the reference pages — Qwen fills screens and visors even when told "one or two dark parts".

## Variant ink (2026-10-18)

| Set | Stroke | Coverage | Solid |
| --- | --- | --- | --- |
| Ours, ink variant (13) | 3 px | 0.40 (p10 0.30, p90 0.55) | 0.77 (p90 0.83) |
| Ours ink A / B / C / D / E | 5 / 3 / 4 / 3 / 4 px | 0.57 / 0.40 / 0.36 / 0.29 / 0.40 | 0.80 / 0.79 / 0.64 / 0.24 / 0.75 |

The ink line "stroke" reads low because dry-brush skips and rough edges fragment the thin parts while the thick parts count as solid; judge ink by coverage and solid share. The target is coverage 0.35–0.5 and solid 0.5–0.7: coverage is in range, solid share runs above it.
