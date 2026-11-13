# Creative LUT Iteration

This workflow is for choosing a look with the user. It does not classify scene content or automatically match one shot to another.

## Candidate-first workflow

1. Clarify the intended look in visual terms: contrast, shadow and highlight color, saturation, warmth, black lift, and any colors to protect.
2. If the user supplies a reference image, use it as a style reference. Describe the visible color and tone choices; do not claim to recover the exact original grade or camera transform.
3. Create up to three deliberate candidates for the same look. Start from one base recipe and vary only one or two controls per round, such as strength and contrast or warmth and shadow tint.
4. Apply every candidate to the same user-selected image. For a video, use one to three frames the user identifies as representative; do not automatically classify or match every shot.
5. Create a side-by-side review sheet with scripts/compare_lut_candidates.py. Let the user choose the candidate before treating it as final.
6. Run scripts/validate_lut.py on the selected LUT and provide the selected .cube plus its preview. Include other candidates only when requested.

## What the preview does and does not show

The review sheet applies each LUT with the same trilinear preview code as the single-image preview script. It is a visual comparison aid, not a simulation of every editor, camera display, or export pipeline. The default photo path converts embedded ICC profiles to sRGB; untagged photos are assumed sRGB. For a technical conversion LUT, use a source-domain frame with explicit `--color-mode encoded-rgb`; this bypasses ICC and produces an untagged result requiring target-editor color management. The one-command creative package is sRGB-only.

Do not turn this workflow into per-shot correction. A creative LUT is one global color transform; exposure, white balance, mixed lighting, and subject-specific corrections belong in shot-level grading before or after the creative look.
