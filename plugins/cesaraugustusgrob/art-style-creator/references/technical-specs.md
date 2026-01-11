# Technical Specifications

## Table of Contents
1. [Resolution and Format](#resolution-and-format)
2. [Color Modes](#color-modes)
3. [File Formats](#file-formats)
4. [Technical Specification Format](#technical-specification-format)

---

## Resolution and Format

### Resolution Standards

| Type | Standard | High | Print |
|------|----------|------|-------|
| **Web/Screen** | 72 DPI | 144 DPI (Retina) | N/A |
| **Print** | 150 DPI | 300 DPI | 300+ DPI |
| **Game Assets** | Power of 2 (512, 1024, 2048, 4096) | | |

### Common Canvas Sizes

| Use Case | Dimensions | Aspect Ratio |
|----------|------------|--------------|
| **HD Screen** | 1920 × 1080 | 16:9 |
| **4K Screen** | 3840 × 2160 | 16:9 |
| **Square (Social)** | 1080 × 1080 | 1:1 |
| **Portrait (Mobile)** | 1080 × 1920 | 9:16 |
| **US Letter** | 2550 × 3300 (300dpi) | ~3:4 |
| **A4** | 2480 × 3508 (300dpi) | ~1:√2 |

### Game Asset Sizes

| Asset Type | Common Sizes | Notes |
|------------|--------------|-------|
| **Character sprites** | 64, 128, 256, 512 | Power of 2 preferred |
| **Icons** | 32, 64, 128 | Square |
| **UI elements** | Variable | Scale with resolution |
| **Tilesets** | 16, 32, 64 per tile | Consistent tile size |
| **Backgrounds** | 1920×1080, 2048×2048 | Match target resolution |

---

## Color Modes

| Mode | Use Case | Notes |
|------|----------|-------|
| **RGB** | Screen display | Additive color, digital work |
| **CMYK** | Print | Subtractive color, printing |
| **sRGB** | Web standard | Most compatible |
| **Adobe RGB** | Professional | Wider gamut |
| **Indexed** | Pixel art, GIF | Limited palette |

### Color Depth

| Depth | Colors | Use Case |
|-------|--------|----------|
| **8-bit** | 256 colors | Indexed/pixel art, GIF |
| **16-bit** | 65,536 | High color |
| **24-bit** | 16.7 million | True color (standard) |
| **32-bit** | 16.7M + alpha | True color with transparency |

---

## File Formats

| Format | Best For | Supports | Notes |
|--------|----------|----------|-------|
| **PSD** | Working files | Layers, full editing | Adobe standard |
| **PNG** | Web, transparency | Lossless, alpha | Best for UI/sprites |
| **JPG** | Photos, web | Lossy, small size | No transparency |
| **SVG** | Vector graphics | Scalable, code-based | Web vectors |
| **GIF** | Animation, simple graphics | Animation, indexed | 256 color limit |
| **TIFF** | Print, archive | Lossless, large | Professional print |
| **WebP** | Web optimization | Modern, efficient | Smaller than PNG/JPG |
| **AVIF** | Modern web | Excellent compression | Limited support |

### Format Selection Guide

| Need | Recommended Format |
|------|-------------------|
| Editable working file | PSD, TIFF |
| Web image with transparency | PNG, WebP |
| Web photo | JPG, WebP |
| Scalable graphic | SVG |
| Simple animation | GIF, APNG |
| Game sprite | PNG |
| Print | TIFF, PDF |

---

## Technical Specification Format

```
TECHNICAL SPECIFICATIONS: [Project Name]

CANVAS:
- Working resolution: [Dimensions] at [DPI]
- Final output: [Dimensions] at [DPI]
- Aspect ratio: [Ratio]
- Color mode: [RGB / CMYK / Indexed]
- Color profile: [sRGB / Adobe RGB / Other]

FILE MANAGEMENT:
- Working format: [PSD / AI / etc.]
- Export formats: [List with use cases]
- Naming convention: [Pattern]
- Layer organization: [System]

ASSET SPECIFICATIONS:
- Character sprites: [Size]
- Environment tiles: [Size]
- UI elements: [Size]
- Icons: [Size]

TECHNICAL CONSTRAINTS:
- Max file size: [If applicable]
- Performance considerations: [If applicable]
- Platform requirements: [If applicable]
```

### Common Naming Conventions

```
Characters:   char_[name]_[state]_[frame].png
              char_hero_idle_01.png

UI Elements:  ui_[category]_[element]_[state].png
              ui_btn_primary_hover.png

Backgrounds:  bg_[location]_[layer].png
              bg_forest_midground.png

Icons:        icon_[category]_[name]_[size].png
              icon_item_sword_64.png

Tiles:        tile_[tileset]_[type]_[variant].png
              tile_grass_corner_01.png
```
