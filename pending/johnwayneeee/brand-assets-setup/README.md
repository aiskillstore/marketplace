# Brand Assets Setup

Generate and deploy a complete brand asset pack for a Next.js App Router project. This skill scans your project structure, detects brand colors, prints a detailed checklist with exact specifications, provides an AI-friendly generation prompt, and imports the generated assets with proper metadata configuration.

## When to Use

- "I need to add logo and icons to my Next.js project"
- "Setup favicon, OG image, and PWA icons"
- "Create a complete brand asset pack"
- "Generate favicons and app icons for Next.js"
- "Setup web app manifest and metadata"

## How It Works

### PHASE 1 — Discovery

The skill scans your Next.js project structure to understand the current state.

1. **Locate the Next.js app root** — finds `app/layout.tsx` or `src/app/layout.tsx`
2. **Check existing assets** — looks for existing favicons, icons, and OG images
3. **Read layout metadata** — notes existing metadata structure
4. **Detect brand colors** — extracts from CSS, Tailwind config, or theme configuration

### PHASE 2 — Asset Checklist

Prints a comprehensive checklist showing:
- **File specifications**: exact dimensions, format, background requirements
- **Placement paths**: where each asset belongs in your project
- **Design rules**: whether files need transparent or solid backgrounds
- **Detected brand colors**: automatically extracted from your project

#### Assets Generated (12 total)

**BROWSER FAVICON SET** (3 files)
- `favicon.ico` (16×16 + 32×32 + 48×48 multi-size, solid background)
- `favicon-16x16.png` and `favicon-32x32.png` (backups for legacy browsers)

**APP ICONS** (2 files)
- `icon.png` (32×32, transparent) — auto-detected by Next.js
- `apple-icon.png` (180×180, solid background) — iOS home screen

**PWA / ANDROID** (3 files)
- `icon-192.png` and `icon-512.png` (transparent) — for Android PWA
- `maskable-icon-512.png` (solid background) — Android adaptive icons

**SOCIAL / OG IMAGES** (2 files)
- `opengraph-image.png` (1200×630) — Facebook, Telegram, LinkedIn
- `twitter-image.png` (1200×630) — Twitter/X card

**LOGO FILES** (2 files)
- `logo.svg` (vector, transparent) — for light backgrounds
- `logo-dark.svg` (vector, transparent) — for dark backgrounds

### PHASE 2.5 — AI Generation Prompt

After the checklist, the skill provides a ready-to-copy prompt for image generation AI.

**The prompt includes:**
- Detailed specs for each file (size, format, background, placement)
- Brand color palette
- Generation rules (transparency, safe zones, banner layouts)
- Expected output format

**Workflow:**
1. Attach your logo image
2. Copy the prompt to Claude, ChatGPT, DALL-E, or similar
3. AI generates all 12 assets into a single folder
4. Provide the folder path back to the skill
5. Skill imports everything automatically

### PHASE 3 — Import

When you provide the generated assets folder, the skill:
1. Validates the folder and files
2. Copies files to correct Next.js locations
3. Cleans up the source folder

### PHASE 4 — Wire Metadata

Updates your `app/layout.tsx` (or `src/app/layout.tsx`) with proper Next.js metadata:
- Adds correct `viewport` export (required for streaming)
- Ensures `metadataBase`, `manifest`, `openGraph`, `twitter` are configured
- Does NOT duplicate auto-detected assets

### PHASE 5 — Create manifest.json

Generates `public/manifest.json` with:
- Project metadata
- Brand colors (background, theme)
- PWA icon references
- Display mode

### PHASE 6 — Validate next/image

If using `<Image>` from `next/image` for the logo:
- Ensures both `width` and `height` are specified
- Adds matching `style` props to prevent warnings

### PHASE 7 — Validation Instructions

Provides verification steps:
1. Hard refresh favicon in browser
2. Check OG preview on opengraph.xyz
3. Verify PWA manifest in DevTools
4. Test Apple icon on iPhone

## Key Features

✅ **Automatic color detection** — extracts brand colors from your CSS/config  
✅ **AI-friendly generation prompt** — copy-paste ready for any image AI  
✅ **Smart file placement** — routes files to correct Next.js locations  
✅ **Metadata wiring** — updates layout.tsx with Next.js 16+ patterns  
✅ **PWA ready** — generates manifest.json and all icon sizes  
✅ **Multi-format support** — favicon.ico, PNG, SVG for maximum compatibility  

## Next.js File Convention Reference

Files in `app/` (or `src/app/`) that Next.js auto-detects:

| File | Generates |
|------|-----------|
| `favicon.ico` | `<link rel="icon">` |
| `icon.png` | `<link rel="icon" type="image/png">` |
| `apple-icon.png` | `<link rel="apple-touch-icon">` |
| `opengraph-image.png` | `<meta property="og:image">` |
| `twitter-image.png` | `<meta name="twitter:image">` |

**Important**: Don't manually duplicate these in metadata — Next.js will create duplicate tags.

## Example Workflow

1. Run the skill in your Next.js project
2. Review the checklist and brand colors
3. Copy the AI prompt and attach your logo
4. Send to Claude, ChatGPT, or DALL-E
5. Receive a folder with all 12 assets
6. Provide the folder path back to skill
7. Skill imports everything and updates metadata
8. Verify using provided validation steps

## Troubleshooting

**Favicon not updating?**
- Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
- Clear cache: DevTools → Storage → Clear site data
- Verify file at `app/favicon.ico`

**OG image not showing?**
- Deploy to production/staging first
- Check preview on https://opengraph.xyz
- Verify file at `app/opengraph-image.png` (1200×630)

**PWA icons missing?**
- Open DevTools → Application → Manifest
- Verify `public/manifest.json` exists
- Check icon paths in manifest

## Related Resources

- [Next.js Metadata API](https://nextjs.org/docs/app/building-your-application/optimizing/metadata)
- [Web App Manifest](https://web.dev/add-manifest/)
- [favicon.ico Best Practices](https://realfavicongenerator.net/)
- [PWA Icons Guide](https://web.dev/favicon-best-practices/)
