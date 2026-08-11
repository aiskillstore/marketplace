# Local visual reviews

Show every Brandkit review directly in chat when the client can render local images. Always provide the editable local file path as well.

## Publishing an HTML review board

`brandkit.py preview` returns persistent local HTML paths. For every board:

1. Screenshot it to PNG with Playwright:

   ```bash
   npx --yes playwright@1.62.1 screenshot \
     --viewport-size=1200,900 --wait-for-timeout=2000 --full-page \
     "file://$PWD/brandkit/reviews/<board>.html" \
     "$PWD/brandkit/reviews/<board>.png"
   ```

2. Inspect the PNG. Verify the intended font loaded, nothing is clipped, and text/background contrast is readable.
3. Show the PNG inline when the client supports local image rendering. Otherwise provide the absolute PNG path.
4. Provide the absolute HTML path as the editable review file.

Use this structure:

```markdown
### Option 1 — <name>
![<name> board](/absolute/path/to/board.png)
[Open editable HTML](/absolute/path/to/board.html)
```

For 2–3 options, stack the complete blocks in one response. Never send filenames without enough context to identify the option. Ask for ordinary chat feedback and stop.

Before writing preview input, load [exact preview payloads](preview-payloads.md).

## Recraft SVG logo review

The preview script does not create or compare logos. Show the three Recraft results directly:

```markdown
### Candidate 1 — <short name>
![Logo candidate 1](<Recraft SVG URL>)
[Download SVG](<Recraft SVG URL>)
```

If the client cannot render the SVG URL, download the exact SVG locally and rasterize a review-only PNG with `rsvg-convert`. Keep the original SVG untouched as the downloadable asset.

```bash
rsvg-convert --format png --width 2048 --height 2048 --keep-aspect-ratio \
  --output "$BRANDKIT_WORKDIR/logo/candidate-1-preview.png" \
  "$BRANDKIT_WORKDIR/logo/candidate-1.svg"
```

Never redraw, normalize, recolor, or otherwise alter a candidate during review.

## Logo export review

When `logo-export` creates SVG/PNG pairs:

- Show each PNG inline or provide its absolute path.
- Link/provide every requested SVG and PNG path.
- State that the SVG geometry fingerprint is unchanged.
- Never label a raster PNG as editable vector output.

## Review messages

After palette review:

> Take your time. Reply with the palette you prefer and any colors you want changed.

After logo review:

> Take your time reviewing the three marks. Reply with the direction you prefer and any shape or balance changes.

After typography review:

> Review how each type pair works with the selected mark and palette. Reply with your preferred direction or changes.

Each review ends the turn. Never continue to the next stage until the user responds.
