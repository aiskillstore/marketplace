# Brandkit intake

Parse the user's first message, supplied files, local paths, and approved state before asking anything. Treat this as a gap checklist, not a mandatory questionnaire.

Ask one compact ordinary chat message containing only unanswered fields that materially block the requested output. Never repeat known information. If there are no blocking gaps, skip intake.

## Core gaps

1. **Name** — “What is the name of your brand or product?”
2. **Context** — “What does it offer, who is it for, and what positioning or values must it communicate?”
3. **Identity route** — “Are we creating a new identity or preserving and extending existing assets?”
4. **Preferences** — “What colors, fonts, mood, references, or avoid rules should guide it?”

The three optional visual axes are:

- Restrained ↔ Expressive
- Geometric ↔ Organic
- Familiar ↔ Experimental

Accept natural language such as “mostly expressive and organic.” Do not force numeric ratings.

## Existing or partial identity

When needed official assets were not supplied, ask the user to attach them or give readable local paths. Keep these roles distinct:

- official logos and marks — SVG preferred; PNG, JPG, WebP, or PDF accepted
- official fonts — TTF, OTF, WOFF, or WOFF2
- palette and guidelines — PDF, PPTX, CSS, JSON, SVG, or images
- other official materials — packaging, templates, graphics, or application examples
- inspiration references — visually useful but never authoritative

Ask only for the categories needed by the requested output. Do not mix inspiration with official assets. For a new identity, invite inspiration only when it would materially help.

After analysis, immediately save every user-declared official foundation element with the matching action:

- `lock_authoritative_logo`
- `lock_authoritative_palette`
- `lock_authoritative_typography`

Do not wait for combined Essential Kit approval to lock supplied assets.

## Parse the answer

Build this internal brief:

```text
name:
offering:
industry/category:
audience:
positioning/key values:
identity route:
visual preferences:
visual_axes:
  restrained_expressive:
  geometric_organic:
  familiar_experimental:
official logo assets:
official font assets:
official palette/guideline assets:
other official assets:
inspiration:
requested deliverables:
```

Normalize each visual axis to 0–100:

- strongly first = 0
- mostly first = 25
- balanced or unspecified = 50
- mostly second = 75
- strongly second = 100

Persist the normalized values through `set_visual_axes` using the exact wrapper from [state payloads](state-payloads.md). Do not pass the axes as the top-level object.

Do not interrogate the user about every reference. If they give no explanation, use its overall character as a taste signal without copying its logo, artwork, layout, or distinctive device.

## Route

- **New identity** — create only the foundation slots needed by the deliverables in the first request.
- **Existing/partial identity** — analyze and independently lock supplied official elements, then identify only missing required slots.
- Existing-assets route with no assets — ask once for the files or local paths that must be preserved.

Describe missing elements naturally. Keep first-message deliverables in scope and continue them as soon as their required slots are approved.
