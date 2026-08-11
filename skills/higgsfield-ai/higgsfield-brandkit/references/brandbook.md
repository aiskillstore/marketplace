# Brandbook

Create the canonical Brandbook only after logo, palette, and typography are each approved. Never ask for an additional combined Essential Kit approval.

## Required inputs

Read the approved kit from the durable local state file:

```bash
python3 "$SKILL_ROOT/scripts/brandkit.py" state \
  --state-file "$BRANDKIT_STATE" --action get_essential_kit
```

Require:

- approved logo SVG
- approved palette
- approved display/body typography
- approved brand concept/summary copy supplied by the user
- optional approved mockups

Do not invent mission, values, claims, product variants, prices, statistics, or brand-story copy.

## Canonical template

The bundled builder owns this fixed PPTX source and its versioned layout contract:

```text
https://docs.google.com/presentation/d/1rAfUJ-PbZ4S-h3puYSUHpE5UIcdKyRw1/export/pptx
```

Do not inspect, recreate, or edit the template manually. The build requires network access to that URL plus any approved public font or asset URLs.

## Build

First read [prerequisites](prerequisites.md). Check the complete Brandbook toolchain and ask before installing anything missing.

Write this JSON under `"$BRANDKIT_WORKDIR"`, replacing values but preserving keys and nesting:

```json
{
  "brand_name": "Northline",
  "concept_summary": "A precise identity built around directional movement and calm technical confidence.",
  "palette_summary": "Ink and Paper establish clarity while Signal Blue marks moments of action.",
  "secondary_logo_url": "",
  "mockups": [
    {
      "path": "/absolute/path/to/approved-mockup.png"
    }
  ],
  "revision": 1
}
```

Run once in the foreground:

```bash
python3 "$SKILL_ROOT/scripts/brandkit.py" brandbook-build \
  --state-file "$BRANDKIT_STATE" \
  --input "$BRANDKIT_WORKDIR/brandbook.json" \
  --output-dir "$BRANDKIT_WORKDIR/brandbook"
```

The builder reads the separately approved slots from state, downloads only the fixed template, resolves the exact approved fonts, creates the PPTX, converts those exact bytes with LibreOffice, and verifies the PDF fonts with Fontconfig and Poppler. Do not duplicate foundation slots in the input. Do not substitute ReportLab, a custom slide generator, or a different template after failure.

## Fixed seven-slide structure

Preserve the template's slide size, masters, layout, margins, grids, text positions, image zones, hierarchy, font sizes, spacing, crop, rotation, and stacking order except for these conditional rules.

1. **Cover** — “Brand Guidelines” and the real brand/product name.
2. **Branding concept** — approved concept summary and palette rationale.
3. **Primary logo** — exact approved SVG.
4. **Logo system** — primary plus an approved secondary/reverse variant only when supplied or requested. Remove the unused secondary slot and label; never invent one.
5. **Primary palette** — approved swatches, names, RGB, hex, independent readable label contrast, and no decorative redesign.
6. **Typography** — approved display/body fonts rendered at equal specimen sizes and aligned positions, with neither clipped nor substituted.
7. **Mockups** — two approved mockups per slide.

Mockup conditions:

- no approved mockups: remove slide 7
- one: keep the first zone and remove the second
- two: keep one mockup slide
- more than two: duplicate the exact mockup slide for each additional pair

Never place generated-but-unapproved work in the Brandbook.

## Brand-specific styling

- Replace template colors and fonts with approved values.
- Keep every slide title on one line in the approved display font and at least 3:1 contrast against its background.
- Keep body copy in the approved body font without auto-shrinking.
- Preserve the approved logo geometry; never stretch or redraw it.
- Crop mockups into template slots without independent width/height stretching.
- Use approved copy only and add no new decorative sections.

## QA

Before delivery:

1. Render every slide.
2. Check clipping, overflow, font substitution, crops, contrast, and alignment.
3. Verify logo geometry, palette values, and absence of placeholder text.
4. Confirm the PDF visually matches the PPTX.

Use stable names:

```text
<brand>-brand-guidelines-v<revision>.pptx
<brand>-brand-guidelines-v<revision>.pdf
```

If the template, font, or conversion contract fails, report the concrete error and stop. Do not retry a deterministic mismatch or offer an improvised fallback. The editable PPTX still requires the approved fonts on the recipient's machine even after PDF verification passes.

## Delivery and approval

Return only:

1. one clickable local PPTX link
2. one clickable local PDF link
3. one concise warning naming the display/body fonts the user must install, with official links when known

Do not show page cards, contact sheets, or QA screenshots. Wait for explicit approval, then save the Brandbook element with `required_slots` equal to `["logo", "palette", "typography"]`.
