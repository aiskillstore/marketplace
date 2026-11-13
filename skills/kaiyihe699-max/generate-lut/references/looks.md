# Creative Look Presets

Use these mappings when converting style language into `generate_cube_lut.py` parameters.

## Presets

`neutral`: Identity-style LUT for testing pipelines.

`cinematic-teal-orange`: Teal/cyan shadows, warm highlights, moderate contrast, slightly reduced saturation. Good for trailers, travel, and dramatic edits.

`soft-portrait`: Gentle contrast, warm highlights, slightly lifted blacks, restrained saturation. Good for faces, lifestyle, wedding, and beauty work.

`warm-film`: Warm highlights, mild cool shadows, soft shoulder, subtle black lift. Good for nostalgic editorial and daylight footage.

`cool-commercial`: Clean cool bias, crisp contrast, controlled saturation. Good for tech, product, architecture, and polished brand work.

`moody-green`: Deeper contrast, green/cyan shadows, muted warmth. Good for atmospheric interiors and stylized night scenes.

`bleach-bypass`: High contrast, low saturation, dense highlights. Good for gritty action and documentary looks.

`kodak-print-ish`: Warm print-like highlights, solid blacks, moderate saturation. This is only an inspired creative preset, not a film stock emulation.

`fuji-soft-ish`: Softer contrast, slightly cooler greens, pleasant highlight warmth. This is only an inspired creative preset, not a film stock emulation.

`custom`: Use explicit controls instead of a preset. Good when the user gives exact words like "lower contrast, slightly warmer, 20% less saturation".

## Translation Hints

"Film", "cinematic", "movie", "blockbuster": start with `cinematic-teal-orange` or `warm-film`.

"Portrait", "skin", "wedding", "beauty": start with `soft-portrait` and leave default skin protection enabled (disable only with `--no-protect-skin`).

"Product", "commercial", "clean", "modern": start with `cool-commercial`.

"Gritty", "war", "silver", "desaturated": start with `bleach-bypass`.

"Moody", "green", "night", "suspense": start with `moody-green`.

Increase `--strength` for a stronger look; tune `--contrast`, `--saturation`, `--warmth`, `--exposure`, and `--lift` for client-specific refinements.

Custom shadow, middle and highlight RGB offsets are available via `--shadow-tint R G B`, `--mid-tint R G B`, `--highlight-tint R G B`; use smooth modest offsets. `--bleach` controls additional silver/desaturation mixing. All are saved by the one-command recipe exporter.
