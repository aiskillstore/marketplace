# Merchandise

Create merchandise as soon as the slots its artwork uses are approved.

Require `get_logo`. Read `get_palette` for spot-color/application decisions and `get_typography` only when exact copy appears; do not require unused slots.

Collect item type, printable area, production method, material color, sizes, quantity of variants, and exact copy.

Create production artwork deterministically in SVG. Use the exact approved logo and approved graphic devices; do not ask an image model to redraw them. Respect spot-color, embroidery, screen-print, and minimum-stroke constraints provided by the user or supplier.

Use `mockups.md` only for presentation imagery after the production artwork is approved. Keep artwork and mockup as separate deliverables and separate state elements.

Save approved production artwork with its actual `required_slots` (usually `["logo"]` or `["logo","palette"]`); save any mockup separately.

Check dimensions, color count, contrast against material, minimum detail size, and artwork/mockup consistency before approval.
