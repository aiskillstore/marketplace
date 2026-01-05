---
name: nano-image-generator
description: "Generate images using Nano Banana Pro (Gemini 3 Pro Preview). Use when creating app icons, logos, UI graphics, marketing banners, social media images, illustrations, diagrams, or any visual assets. Supports reference images for style transfer and character consistency. Triggers include phrases like 'generate an image', 'create a graphic', 'make an icon', 'design a logo', 'create a banner', 'same style as', 'keep the style', or any request needing visual content."
---

# Nano Image Generator

Generate images using Nano Banana Pro (Gemini 3 Pro Preview) for any visual asset needs. Supports **reference images** for style transfer and character consistency.

## Quick Start

```bash
# Basic generation
python scripts/generate_image.py "A friendly robot mascot waving" --output ./mascot.png

# With style reference (keep same visual style)
python scripts/generate_image.py "Same style, new content" --ref ./reference.jpg --output ./new.png
```

## Script Usage

```bash
python scripts/generate_image.py <prompt> --output <path> [options]
```

**Required:**
- `prompt` - Image description
- `--output, -o` - Output file path

**Options:**
- `--aspect, -a` - Aspect ratio (default: `1:1`)
  - Square: `1:1`
  - Portrait: `2:3`, `3:4`, `4:5`, `9:16`
  - Landscape: `3:2`, `4:3`, `5:4`, `16:9`, `21:9`
- `--size, -s` - Resolution: `1K`, `2K` (default), `4K`
- `--ref, -r` - Reference image (can use multiple times, max 14)

## Reference Images

Gemini supports up to **14 reference images** for:

### Style Transfer
Keep the visual style (colors, textures, mood) from a reference:
```bash
python scripts/generate_image.py "New scene with mountains, same visual style as reference" \
  --ref ./style-reference.jpg --output ./styled-mountains.png
```

### Character Consistency
Maintain character appearance across multiple images:
```bash
python scripts/generate_image.py "Same character now in a forest setting" \
  --ref ./character.png --output ./character-forest.png
```

### Multi-Image Fusion
Combine elements from multiple references:
```bash
python scripts/generate_image.py "Combine the style of first image with subject of second" \
  --ref ./style.png --ref ./subject.png --output ./combined.png
```

### Serial Image Generation (Batch Workflow)
For generating a series with consistent style:
1. Generate first image
2. Use first image as `--ref` for subsequent images
3. Each new image inherits the established style

```bash
# Generate cover
python scripts/generate_image.py "Tech knowledge card cover" -o ./01-cover.png

# Generate subsequent cards with style reference
python scripts/generate_image.py "Card 2 content, same style" --ref ./01-cover.png -o ./02-card.png
python scripts/generate_image.py "Card 3 content, same style" --ref ./01-cover.png -o ./03-card.png
```

## Workflow

1. **Determine output location** - Place images where contextually appropriate:
   - App icons → `./assets/icons/`
   - Marketing → `./marketing/`
   - UI elements → `./src/assets/`
   - General → `./generated/`

2. **Craft effective prompts** - Be specific and descriptive:
   - Include style: "flat design", "3D rendered", "watercolor", "minimalist"
   - Include context: "for a mobile app", "website hero image"
   - Include details: colors, mood, composition
   - For references: mention "same style as reference" or "keep the visual style"

3. **Choose appropriate settings:**
   - Icons/logos → `--aspect 1:1`
   - Banners/headers → `--aspect 16:9` or `21:9`
   - Mobile screens → `--aspect 9:16`
   - Xiaohongshu cards → `--aspect 3:4`
   - Photos → `--aspect 3:2` or `4:3`

## Examples

**App icon:**
```bash
python scripts/generate_image.py "Minimalist flat design app icon of a lightning bolt, purple gradient background, modern iOS style" \
  --output ./assets/app-icon.png --aspect 1:1
```

**Marketing banner:**
```bash
python scripts/generate_image.py "Professional website hero banner for a productivity app, abstract geometric shapes, blue and white color scheme" \
  --output ./public/images/hero-banner.png --aspect 16:9
```

**Xiaohongshu knowledge card:**
```bash
python scripts/generate_image.py "Tech knowledge card, dark blue purple gradient, neon cyan accents, code block style, Chinese text '标题'" \
  --output ./xiaohongshu/card.png --aspect 3:4
```

**Style transfer:**
```bash
python scripts/generate_image.py "Transform this photo into watercolor painting style" \
  --ref ./photo.jpg --output ./watercolor.png
```

**Character in new scene:**
```bash
python scripts/generate_image.py "Same character from reference, now sitting in a cafe, warm lighting" \
  --ref ./character.png --output ./character-cafe.png --aspect 3:2
```

## Prompt Tips

- **Be specific** - "A red apple on a wooden table" vs "an apple"
- **Include style** - "in the style of pixel art" or "photorealistic"
- **Mention purpose** - "for a children's book" affects the output style
- **Describe composition** - "centered", "rule of thirds", "close-up"
- **Specify colors** - Explicit color palettes yield better results
- **Reference prompts** - Use "same style as reference", "keep the visual aesthetic", "match the color palette"
- **Avoid** - Don't ask for complex text in images (use overlays instead)

## Limitations

- Maximum 14 reference images per request
- Text rendering may be imperfect (better to overlay text separately)
- Very specific brand logos may not reproduce exactly
