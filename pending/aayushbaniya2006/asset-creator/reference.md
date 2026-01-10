# Asset Creator Reference

## Configuration
Ensure `OPENAI_API_KEY` is set in your environment (`.env` or session).

## Prompt Engineering
To get the best results for SaaS assets:

- **Style**: "Minimalist, flat, vector style, clean lines, corporate memphis, tech blue color palette"
- **Background**: "White background" or "Transparent background" (note: DALL-E returns rectangular images, transparency usually requires post-processing, but "white background" makes it easier to blend).
- **Composition**: "Centered, wide angle, isometric view"

## Helper Script
The script uses `openai` SDK node method `images.generate`.

### Defaults
- **Model**: `dall-e-3`
- **Size**: `1024x1024`
- **Quality**: `hd`

### Code
See `.claude/skills/asset-creator/scripts/generate-image.ts` for the implementation.

