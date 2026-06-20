# Output Risk Profile

Skill: `yao-meta-skill`

## Why This Exists

Generated skills often fail in small output details: generic headings, cluttered citations, fragile screenshots, weak Markdown rendering, or missing execution assumptions. This profile predicts the most likely output mistakes before the skill is used heavily.

## Matched Risk Families

### Markdown readability
- Matched keywords: md, report, doc
- Score: `3`

### Citation and footnote clutter
- Matched keywords: source, reference
- Score: `2`

### Screenshot and visual capture
- Matched keywords: capture
- Score: `1`

### Code and command safety
- Matched keywords: script
- Score: `1`

### Tone and specificity
- Matched keywords: summary
- Score: `1`

## Likely Output Mistakes

- Tables can render as dense grids with weak hierarchy or poor mobile readability.
- Long bullets can make the output look complete while hiding the actual decision logic.
- Footnote markers or dense citation notes can interrupt the reading flow.
- Evidence can be over-attached to obvious statements and under-attached to risky claims.
- Screenshots can be captured from the wrong state, wrong viewport, or wrong crop.
- Missing screenshots can cause the skill to invent visual references instead of declaring the gap.

## Output Constraints To Apply

- Use tables only when comparison is the main job; otherwise prefer compact cards or grouped bullets.
- Keep table cells short and move explanations below the table.
- Attach citations only to claims that need evidence, not to every sentence.
- Group source notes at the end of a section when inline markers would hurt readability.
- Never invent a screenshot; state when visual evidence is missing.
- Record the source, viewport, and crop intent for any screenshot-dependent output.

## Self-Repair Checks

- Preview whether each table still reads well when columns are narrow.
- Convert any table with paragraph-length cells into bullets or cards.
- Remove decorative citations that do not support a material claim.
- Move repeated source explanations into one compact source note.
- Check that every screenshot reference points to a real provided or generated asset.
- Reword any visual instruction that depends on an unseen screen state.

## Reviewer Note

Use this report before deepening the package and again before approving example outputs.
