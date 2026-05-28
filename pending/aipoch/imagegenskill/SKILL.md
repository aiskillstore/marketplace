---
name: imagegenskill
description: Generate renderable, scientific-style SVG graphics directly from natural-language requirements (no image models). Use when users ask for an image/picture/scientific diagram/visualization poster or explicitly request SVG output for web-embeddable vector graphics.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need **scientific-looking diagrams/posters** (laboratory poster aesthetic) generated from a short natural-language brief.
- The user requests **SVG output** specifically (e.g., “output SVG”, “vector graphic”, “embeddable in a web page”).
- You want **language-to-image** results without using diffusion/LLM image models, prioritizing **interpretable structure** over photorealism.
- You need **repeatable, parameter-controlled** visuals (seed/palette/structure) for research notes, slides, or documentation.
- You want a **structured visualization** (grids, networks, waveforms, symbol rings) rather than an illustrative drawing.

## Key Features

- Converts a natural-language brief into a **renderable SVG** with a scientific, restrained visual style.
- Multiple built-in styles via `STYLE`:
  - `lab-atlas` (default): calm, stable, laboratory map feel
  - `signal-loom`: denser spectral waveforms, stronger texture
  - `lattice-field`: prominent lattice grids, denser nodes
- Produces **SVG + JSON metadata** (e.g., `prompt`, `seed`, `palette`) for traceability.
- Writes a convenience preview file: `output/svggen/latest.svg`.
- Tunable density and composition controls (e.g., nodes, noise, bands, rings).

## Dependencies

- Python `3.8+`

> Note: No third-party Python packages are specified in the provided documentation. If `scripts/svg_gen.py` imports external libraries, add them here with exact versions.

## Example Usage

```bash
# 1) Create the brief (UTF-8)
mkdir -p input
cat > input/brief.txt << 'EOF'
Scientific poster-style SVG: "Graph topology in latent space".
Include a calm lab-atlas aesthetic, visible grid + network + waveform layers,
and a few symbol rings. Use restrained colors, high text readability.
Keywords: latent space, manifold, spectral bands, topology.
EOF

# 2) (Optional) Edit configuration at the top of the generator script
#    - STYLE (lab-atlas | signal-loom | lattice-field)
#    - canvas width/height
#    - density parameters (node_count, noise_points, band_count, ring_density)
# Example:
# sed -i 's/^STYLE = .*/STYLE = "lab-atlas"/' scripts/svg_gen.py

# 3) Run generation
python scripts/svg_gen.py

# 4) View output
# Primary output directory:
ls -la output/svggen/
# Quick preview file:
# open output/svggen/latest.svg   (macOS)
# xdg-open output/svggen/latest.svg (Linux)
# start output/svggen/latest.svg  (Windows)
```

Expected outputs:

- `output/svggen/latest.svg` (latest render for quick preview)
- `output/svggen/<name>.svg` (generated SVG)
- `output/svggen/<name>.json` (metadata: includes `prompt`, `seed`, `palette`)

## Implementation Details

### Workflow

1. Write requirements to `input/brief.txt` (UTF-8).
2. Adjust the configuration section at the top of `scripts/svg_gen.py` (e.g., `STYLE`, canvas dimensions, density parameters).
3. Run `python scripts/svg_gen.py`.
4. Open `output/svggen/latest.svg` to inspect the result.

### Prompt / Brief Guidelines

- Use clear research semantics: **field**, **object**, **structure**, **atmosphere**, **keywords**.
- English technical terms are allowed (e.g., `latent space`, `graph topology`) and should remain unchanged.
- Keep the brief concise; the script maps text into structural elements and symbols.

### Composition & Quality Criteria

- **Text readability**: ensure key labels (e.g., prompt/mode text if present) are not obscured.
- **Structural hierarchy**: at least **three layers** should be simultaneously visible, chosen from:
  - grid
  - waveform / spectral bands
  - network / nodes
  - symbol rings
- **Style consistency**: avoid overly saturated colors; maintain scientific visual restraint.

### Tuning / Troubleshooting Parameters

- Output too dense: decrease `node_count` or `noise_points`.
- Output too empty: increase `band_count` or `ring_density`.
- Style mismatch: switch `STYLE` and regenerate.

### Primary Entry Point

- Generator script: `scripts/svg_gen.py`