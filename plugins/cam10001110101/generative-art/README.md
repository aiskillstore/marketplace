# Generative Art Skill

Creates Art Blocks-style generative art using p5.js with seeded randomness and interactive exploration.

## Structure

```
generative-art/
├── SKILL.md                       # Skill instructions for Claude
├── templates/
│   ├── viewer.html               # Complete artifact template (USE THIS)
│   └── generator_template.js     # p5.js patterns reference
└── README.md                     # This file
```

## How It Works

**Two-step process:**
1. **Algorithmic Philosophy** - Create a computational aesthetic manifesto
2. **Single HTML Artifact** - Implement as self-contained interactive art

## The Artifact

The output is a **single HTML file** that:
- Works immediately in claude.ai artifacts
- Contains everything inline (no external files except p5.js CDN)
- Includes interactive parameter controls
- Has seed navigation (prev/next/random)
- Allows downloading variations as PNG

See `templates/viewer.html` for the complete working example.

## Key Concepts

- **Seeded Randomness**: Same seed = same art (Art Blocks pattern)
- **Parametric**: Adjust values in real-time to explore variations
- **Self-Contained**: No setup, no server, just open and run
- **Reproducible**: Every seed generates unique but consistent output

## Examples of Generative Patterns

See `templates/generator_template.js` for code examples:
- Flow fields (Perlin noise + particles)
- Recursive branching (trees, lightning)
- Circle packing / Voronoi
- Particle systems with forces
- Noise-based terrain

## For Users

When you ask Claude to create generative art:
- It will first create an algorithmic philosophy
- Then implement it as an interactive HTML artifact
- You can explore different variations by changing the seed
- Adjust parameters to fine-tune the aesthetic
- Download your favorite variations

## For Developers

The `viewer.html` template is the blueprint. All generative art artifacts should:
1. Load p5.js from CDN
2. Define parameters at the top
3. Implement setup() and draw()
4. Include UI controls for parameters
5. Have seed navigation built-in
6. Be completely self-contained (no imports except p5.js)
