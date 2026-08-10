# QA and iteration

Assume the first pass contains inconsistencies. Validate the set as a system and each asset as an individual deliverable.

## 1. Preflight before paid generation

- The Brandkit state script's `get_status` action was called in this turn
- Only the state slots required by this output were loaded
- Required approved slots exist for this output
- Every logo use points to the exact approved state asset ID
- Brand Lock exists and matches state revisions
- Requested output list, quantity, format, and dimensions are explicit
- Exact user copy is captured
- Authoritative logo/reference has one reusable ID
- Palette and typography decisions are resolved
- Editable versus rendered deliverables are distinguished
- Every generation call has a defined downstream purpose

Do not generate speculative extras. Do not treat todo completion, model preference, your own visual assessment, or generation success as user approval.

## 2. Set-level consistency matrix

Review all outputs together:

```text
Asset | Logo | Palette | Type | Grid/spacing | Shape/device | Format | Status
```

An asset passes only when it follows the same Brand Lock. Format-specific overrides must already be documented under `applications`; an unexplained difference is drift.

Check:

- Exact brand/product spelling
- Exact logo geometry and approved colorway
- Palette role consistency, not only approximate hue
- Approved display/body font pair, exact copy, and rendering fidelity
- Grid, outer margin, gutters, and alignment
- Borders, corner radii, shadows, shapes, and motif
- Density, hierarchy, and composition
- Exact copy and CTA
- Dimensions/aspect ratio
- Contrast and legibility

## 3. Evidence-based review

Review the outputs visually yourself (when your client shows them) for semantic checks:

- What appears inconsistent?
- Is the logo distorted?
- Does hierarchy match the intended concept?
- Do the assets feel like one system?

Use deterministic checks for measurable properties:

- Image/page dimensions
- Exact colors in editable sources
- Text contents
- Font references
- Element positions and sizes
- SVG attributes
- PPTX object structure
- Repeat seams
- File existence and output size

Do not accept a vision model's statement as proof of exact hex, font, spacing, or radius.

## 4. Module-specific checks

### Logo

- Compare against authoritative source
- New-logo selection contains exactly three editable SVGs
- All three use identical Recraft model, palette, background, aspect, and quality parameters
- Candidate prompts contain no text except explicitly requested monogram initials
- Selected mark and later wordmark are optically balanced as one lockup
- Check geometry, proportions, clear space, and small-size behavior

### Typography

- Verify the one approved font pair, source files, and Google Fonts links
- Confirm the sample was rendered with the real fonts and approved colors
- Check missing glyphs and required language coverage
- Confirm recipient installation requirements

### Editable templates

- Render PPTX/SVG/HTML to previews
- Check overflow, clipping, collisions, crop, contrast, and safe margins
- Confirm text, logo, shapes, and image placeholders are separate editable objects
- Search for placeholder/lorem text that should not ship
- Re-render after fixes; do not declare success after an uninspected first pass

### Mockups

- Compare the Seedream result with every scene/product/logo reference
- Confirm every output uses the user-approved aspect ratio
- For text-bearing mockups, compare GPT Image 2 output with the exact Seedream base and verify only the controlled branding/text application changed
- Verify placement, scale, alignment, clear space, color variant, and material application match the prompt exactly
- When an existing photograph was supplied, verify only requested branded surfaces changed
- Verify the selected color/black/white logo variant matches the material and production method
- Check physical perspective, folds, occlusion, print, and reflections
- Reject any corrupted or approximate logo
- Confirm one specific art-directed idea tied to the brand/category
- Reject generic marble/pedestal luxury scenes, arbitrary gradients, plastic sheen, excessive bloom, floating objects, meaningless props, and fake copy
- Compare material/composition craft with the approved Brand Lock and supplied references without copying a specific reference

### Social media graphics

- Verify exact copy, spelling, punctuation, and requested line breaks
- Verify platform/aspect ratio and requested output count
- Compare logo geometry/color with the approved variant
- Compare typography character with the approved specimen and font roles
- Reject pseudo-text, invented copy/CTA, extra logos, or palette drift
- For mockup-photo mode, confirm the base photo changed only on the target surface

## 5. Repair strategy

When an item fails:

1. Name the failed Brand Lock rule.
2. Decide whether the issue is generative or deterministic.
3. Keep the Brand Lock and all passing assets unchanged.
4. Regenerate/recompose only the failing asset.
5. Re-run its module checks and the set-level matrix.

Prefer a small deterministic correction over a full regeneration:

- Re-typeset incorrect copy
- Re-place the exact logo
- Correct a color token
- Resize/re-align an object
- Replace one generated background

If the user asks to change a core rule, update the Brand Lock version first, list affected assets, and revise only those assets after confirmation.

When logo, typography, or palette approval changes, remove every invalidated downstream element from the active deliverable set. Rebuild and re-approve those elements; never silently keep assets tied to older revisions.

Changing the palette also discards a generated logo because its candidate generation used that palette. Changing typography does not invalidate the symbol mark; it invalidates typography-dependent lockups, templates, decks, and Brandbooks only.

## 6. Stop conditions

Stop and disclose a limitation when:

- A generated logo cannot be reproduced faithfully as editable vector
- An image model repeatedly corrupts the official logo
- A custom font is unavailable or cannot be embedded
- The requested native editor format is unsupported
- Source files are too flattened to recover exact rules
- Required copy, dimensions, or authoritative asset identity remains ambiguous

Do not hide these limitations behind a flattened preview.

## 7. Delivery manifest

Return:

```text
Brand Lock version:
Concept:
Editable files:
Preview/final files:
Generated assets:
Required fonts:
Known limitations:
Variant names:
```

Use stable descriptive names such as:

```text
brand-carousel-4x5-v1.pptx
brand-carousel-4x5-v1-preview-01.png
brand-poster-a2-v1.svg
brand-mockup-tote-primary-v1.png
```

The user should be able to request "revise carousel card 3" without rerunning unrelated work.
