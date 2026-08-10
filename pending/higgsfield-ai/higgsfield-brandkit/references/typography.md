# Typography

Build a usable type system, not a list of attractive font names.

## 1. Existing or user-owned font

If the user supplies `.otf`, `.ttf`, `.woff`, or `.woff2`:

1. Inspect family/style names, weights, variable axes, language coverage, and metadata using available font tools.
2. Record the file as authoritative in the Brand Lock.
3. Use the font in deterministic SVG/PPTX/HTML layouts when supported.
4. Tell the user the font must be installed in their editor/device.

Do not redistribute the font, assert that its license permits a use, or package it with final deliverables unless the user explicitly requests that and confirms permission.

If the existing identity names a proprietary font but no file is supplied, preserve the name as an observed rule and propose a Google Fonts substitute or companion. Do not silently claim the substitute is the original.

## 2. Google Fonts recommendations

When no usable brand font is supplied, propose 2–3 distinct Google Fonts pairs that fit the brief and any approved palette/logo slots.

Every option must use a unique display/body combination. Do not repeat or swap the same two families across boards.

Verify each family is currently available in Google Fonts. Font discovery is not market research; use the official library/source rather than trend articles.

Evaluate:

- Match to supplied positioning, audience, and tone
- Display versus body readability
- Distinctiveness without sacrificing practical use
- Available weights, italics, optical sizes, widths, and variable axes
- Required languages, scripts, and diacritics
- Legibility at the intended poster/carousel/deck sizes
- Compatibility between headline and body anatomy
- Whether one family with multiple styles is stronger than an unnecessary second family

Avoid recommending a decorative font for body copy. Do not pair two families that compete in contrast, width, or personality. One family with useful contrast between weights/styles is valid when it is the stronger system.

## 3. Show the typography

Load `brandkit-design-brain.md` and run `PROPOSE_TYPOGRAPHY`, then render one board per font pair with `python3 "$SKILL_ROOT/scripts/brandkit.py" preview` using:

- The proposed display/body pair
- Standard or brand-relevant headline/body sample text
- The approved palette when available
- The approved mark in `logo_svg` when available
- The same font files used in later SVG/PPTX/HTML work
- One shared `text_color` for both display and body text; it must differ from `background_color`

The user-facing result includes a local PNG preview and editable HTML path, plus:

```text
Display font:
Body font:
Why this pair:
Google Fonts download links (or supplied-font note):
Install/use caveat:
```

Do not rely on links alone—the rendered specimen is required. Do not use an image model to fake typography.

After showing the assets, send a normal message inviting the user to take their time and comment. Do not use a multiple-choice gate.

When the user selects a pair, immediately save it through the Brandkit state script's `approve_typography` action. Do not require a combined review or unrelated logo/palette approval.

## 4. Keep the system simple

- Name the display and body/utility family.
- Name the exact files/weights used in the rendered sample.
- Include fallbacks and language coverage only when relevant.
- Use no more than two families.

Do not create a user-facing type-role table, line-height system, letter-spacing specification, or exhaustive scale at this stage. Individual templates may choose practical sizes while preserving the approved pair.

## 5. Deterministic typography rule

If exact typography matters, do not bake final text into a photographic generation. Generate the background/scene without final copy and add text in SVG/PPTX/HTML using the actual font.

Use the Brandkit renderer for concept/type previews. GPT Image 2 typography is not evidence of font choice or exact letterforms.

## 6. Editable output caveats

- PPTX references fonts but does not reliably embed custom fonts.
- SVG text remains editable only when kept as text and the font is installed.
- Outlined SVG preserves appearance but text is no longer editable.
- HTML/CSS can self-host a permitted webfont or use Google Fonts; include fallbacks.
- Imported PPTX/SVG may shift in Canva or Figma.

Include these caveats in delivery when they apply.
