# Generate Assets Reference

## Configuration
Ensure `REPLICATE_API_TOKEN` is set in your environment (`.env`, `.env.local`, or `.env.production`).

## Model Details

### FLUX 1.1 Pro
- **Model**: `black-forest-labs/flux-1.1-pro`
- **Capabilities**: High-quality image generation with excellent prompt understanding
- **Best For**: Product photography, interfaces, transformations, feature showcases

## Parameters

### Aspect Ratios
Common aspect ratios for different use cases:

- **`1:1`**: Square images, feature cards, social media
- **`16:9`**: Hero sections, wide banners, desktop previews (default)
- **`4:3`**: Traditional displays, feature showcases
- **`9:16`**: Mobile previews, vertical content
- **`21:9`**: Ultra-wide hero sections, cinematic views

### Output Format
- **WebP**: Optimized for web, smaller file sizes, good quality
- Automatically optimized with sharp before saving

### Quality Settings
- **output_quality**: 80 (default) - Balance between quality and file size
  - Range: 1-100
  - Higher = better quality but larger files
  - Recommended: 80 for web assets

### Safety Tolerance
- **safety_tolerance**: 2 (default)
  - Range: 1-5
  - Higher = more permissive content filtering
  - Default (2) is suitable for most business use cases

### Prompt Upsampling
- **prompt_upsampling**: true (default)
  - Enhances prompt understanding
  - Recommended to keep enabled for best results

## Prompt Enhancement

The script automatically enhances your base prompt with:

### Automatic Additions
- **Modern UI Elements**: Playful interface components, glassmorphism effects, neomorphic design
- **Background Patterns**: Randomly selects from:
  - Subtle dot patterns
  - Geometric grid patterns
  - Triangle patterns
  - Star patterns
  - Gradient backgrounds (radial, linear)
- **Theme-Aware Styling**: Inspired by project's design system (from `globals.css`)
- **Decorative Elements**: For larger images (hero, transformation):
  - Subtle stars
  - Geometric dots
  - Elegant lines
  - Floating shapes
  - Particle effects
- **Style Modifiers**: Professional, high quality, subtle, elegant, contemporary

### Prompt Engineering Tips

**You can use simple prompts** - the script will enhance them automatically:
- Simple: "dashboard interface"
- Enhanced: "dashboard interface, modern minimalist design, subtle gradients, soft shadows, rounded corners, clean lines, subtle dot pattern, modern UI elements, playful interface components, smooth animations, glassmorphism effects, subtle stars, professional, high quality, subtle, elegant, contemporary design"

**For best results**, still include key details:
1. **Be Specific**: Mention main subject and purpose
   - Good: "SaaS analytics dashboard showing user metrics"
   - Bad: "dashboard"

2. **Include Context**: Mention the use case
   - Good: "hero section showing product interface"
   - Bad: "interface"

3. **Let the script enhance**: Don't worry about adding all style details - the script handles that!

## Size Intelligence

The script automatically handles image sizing:

### Existing Images
- **Auto-Detection**: If replacing an existing image, automatically detects its dimensions
- **Aspect Ratio Matching**: Calculates and uses the correct aspect ratio
- **Size Preservation**: Maintains the same dimensions as the original

### New Images
- **Default Sizes by Type**:
  - Hero: 1920x1080 (16:9)
  - Feature: 1024x1024 (1:1)
  - Transformation: 1920x1080 (16:9)
  - Foreground: 512x512 (1:1)
- **Aspect Ratio Defaults**:
  - Hero: 16:9
  - Feature: 1:1
  - Transformation: 16:9
  - Foreground: 1:1

## Transparent Backgrounds

For smaller assets or foreground elements:
- Set `transparent` parameter to `"true"`
- Uses `bria/remove-background` model (same as logo generator)
- Automatically removes background while preserving alpha channel
- Best for: Icons, decorative elements, foreground assets

## File Organization

Assets are organized by purpose:
- `public/assets/images/hero/` - Hero section images
- `public/assets/images/features/` - Feature showcase images
- `public/assets/images/transformations/` - Before/after, process images
- `public/assets/images/foreground/` - Transparent foreground assets
- `public/assets/images/` - General assets

## Usage in Components

Reference generated assets in components:

```tsx
import Image from "next/image";

<Image
  src="/assets/images/hero/dashboard-hero.webp"
  alt="Dashboard preview"
  width={1920}
  height={1080}
  className="rounded-lg"
/>
```

## Optimization

All generated images are automatically optimized:
- Converted to WebP format
- Resized to match existing images or appropriate defaults
- Compressed for web delivery (quality: 80, effort: 6)
- Maintains visual quality while reducing file size
- Transparent backgrounds preserved when requested

