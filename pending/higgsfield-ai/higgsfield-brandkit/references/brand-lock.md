# Brand Lock

The Brand Lock is the single source of truth for every requested graphic. Create it after intake and asset analysis, before paid generation.

It is not a new brand strategy document. It records supplied context, measured rules, and the minimum proposed visual decisions needed for this job.

## Lock states

Mark each field as one of:

- `fixed` — supplied or approved; never change without explicit permission.
- `proposed` — fills a missing visual rule; may be revised.
- `not_applicable` — intentionally absent.
- `unknown` — unresolved and unsafe to invent.

Also attach an evidence label from `asset-analysis.md`: `source-declared`, `measured`, `visually-observed`, or `inferred`.

## Canonical shape

Use this structure internally. Keep it compact enough to copy relevant blocks verbatim into generation prompts.

```json
{
  "version": 1,
  "brand_context": {
    "name": "",
    "offering": "",
    "industry": "",
    "positioning": "",
    "audience": "",
    "tone": []
  },
  "concept": {
    "name": "",
    "visual_premise": "",
    "research_principles": [],
    "reference_preferences": [],
    "avoid": []
  },
  "visual_axes": {
    "restrained_expressive": 50,
    "geometric_organic": 50,
    "familiar_experimental": 50
  },
  "authoritative_assets": {
    "logo": {
      "origin": "user_supplied | brandkit_generated",
      "source": "",
      "upload_or_job_id": "",
      "variants": {
        "color": "",
        "black": "",
        "white": ""
      },
      "status": "fixed"
    },
    "fonts": [],
    "references": []
  },
  "palette": {
    "origin": "user_supplied | brandkit_generated",
    "primary": [],
    "accent": [],
    "neutral": [],
    "semantic_roles": {},
    "forbidden": []
  },
  "typography": {
    "origin": "user_supplied | brandkit_generated",
    "display": {},
    "body": {},
    "fallbacks": [],
    "font_links": [],
    "specimen_svg": ""
  },
  "layout": {
    "grid": "",
    "margins": "",
    "spacing_scale": [],
    "alignment": "",
    "density": ""
  },
  "shape_language": {
    "corner_radii": [],
    "borders": [],
    "shadows": [],
    "forms": []
  },
  "graphic_devices": {
    "motifs": [],
    "patterns": [],
    "textures": [],
    "rules": []
  },
  "composition": {
    "hierarchy": "",
    "logo_placement": [],
    "image_behavior": "",
    "text_behavior": ""
  },
  "applications": {},
  "unknowns": []
}
```

For each exact token, retain its state, evidence, and source when ambiguity exists. Do not bloat every obvious field with metadata.

## Required minimum

Before paid generation, the lock must contain the fields that the requested output actually uses:

- Exact brand/product spelling
- Requested deliverables and formats
- Logo source when the output uses a logo, or explicit `not_applicable`
- Palette behavior when the output uses color (exact colors when supplied)
- An approved display/body typography system only when readable text appears
- Composition/hierarchy and shape rules relevant to the requested asset
- At least two concrete avoid rules

If a missing value would materially affect a paid generation, ask once. If it only affects a reversible layout detail, make a `proposed` decision.

## Prompt lock block

For every image-model call, include one compact block:

```text
[BRAND LOCK — DO NOT DEVIATE]
Brand spelling: <exact>
Authoritative logo: <reference index/id and preservation instruction>
Palette: <exact hex + role>
Typography: <exact font/style when rendered>
Layout: <grid/alignment/spacing>
Shape language: <radius/border/forms>
Graphic device: <motif/pattern rule>
Must preserve: <fixed invariants>
Never: <forbidden treatments>
```

Repeat the block verbatim across related assets. Change only the asset-specific content, dimensions, and composition section.

## Reference discipline

- Keep one authoritative absolute local path or remote ID and reuse it everywhere.
- Reference a prior generated output by its original job ID; do not download and re-upload it unless the receiving tool requires a file.
- Label references by role in prompts: `Image 1: official logo`, `Image 2: approved base scene`.
- State what each reference controls and what it must not control.
- For an existing logo, require exact preservation of spelling, geometry, proportions, and colors. Prefer deterministic placement/compositing when the logo does not need to interact physically with the scene.

## Per-format overrides

Store format differences under `applications`, not by changing core tokens. Examples:

- A carousel may use tighter spacing than a deck.
- A poster may use the display font at extreme scale.
- A light kraft/paper/cardboard mockup uses the approved black logo.
- A dark mockup uses the approved white reverse logo.
- Embossing, debossing, foil, stamps, engraving, and one-color printing use an approved monochrome logo, never the full-color mark.

An override must name its format and cannot contradict a fixed core rule.

## Project-local approval persistence

The working Brand Lock may contain draft concept language, but final approvals live only in the local `"$BRANDKIT_STATE"` file.

- Call the Brandkit state script's `get_status` action at the start of every Brandkit turn, then load only the module needed by the active stage.
- Lock user-supplied official slots immediately with the matching `lock_authoritative_*` action and persist normalized axes with `set_visual_axes`.
- Save each generated selection immediately through `approve_logo`, `approve_palette`, or `approve_typography`.
- Save final downstream elements only through `approve_brandbook_element` after user approval, with the exact `required_slots` used.
- Do not duplicate Brandkit approval state in user memory, chat prose, or another state file.
- Do not infer approval from generated recency, todo completion, model ranking, or your own visual assessment.

When the user revises one rule:

1. Save only the revised approved slot through the Brandkit state script.
2. Keep every unrelated approved slot unchanged.
3. Respect the returned list of invalidated downstream elements.
4. Identify actual dependents from their `required_slots`.
5. Regenerate/recompose only affected outputs and request approval again.
