# Color palette

Palette creation is part of the Essential Kit.

## Route

1. Read intake and supplied assets.
2. Follow `brandkit-design-brain.md` with action `PROPOSE_PALETTES`.
3. Produce three meaningfully different, defensible options.
4. Render them through `python3 "$SKILL_ROOT/scripts/brandkit.py" preview`.
5. Present them per `inline-widgets.md` (local board PNGs plus editable HTML paths).
6. Wait for the user's selection or revision feedback.

Each option must include:

- 3–6 named colors with exact hex values
- explicit roles (background, text, primary, accent, support)
- rationale linked to Creative DNA
- one central visual mechanism
- rough logo-mechanism ideas for the next stage
- contrast-safe text/background relationship

Do not select the palette for the user. When the user selects it, immediately save that exact palette through the Brandkit state script's `approve_palette` action. Do not wait for logo, typography, or a combined review.

For later reuse, read it with the Brandkit state script's `get_palette` action.
