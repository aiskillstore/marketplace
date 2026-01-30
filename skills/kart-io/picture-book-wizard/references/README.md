# References Directory

This directory contains all reference materials, configuration files, templates, examples, and documentation for the Picture Book Wizard skill.

## Directory Structure

```
references/
├── config/                    # Configuration files (organized by category)
│   ├── core/                  # Core configuration (11 files)
│   │   ├── characters.md      # 4 main protagonist profiles
│   │   ├── styles.md          # 18 visual styles across 4 categories
│   │   ├── scenes.md          # 12 scene environments with Observable Elements
│   │   ├── age-system.md      # Age-driven content specifications (3-12 years)
│   │   ├── rendering.md       # Technical rendering + watermark system
│   │   ├── story-flow.md      # Multi-page story patterns + cover design
│   │   ├── content-safety-validation.md  # Forbidden content rules
│   │   ├── style-assistant.md           # Style recommendation system
│   │   ├── character-advisor.md         # Character recommendation system
│   │   ├── character-extension.md       # Adding new characters guide
│   │   └── learning-objectives.md       # Learning objectives (legacy)
│   │
│   ├── cclp/                  # Character Consistency Lock Protocol (2 files)
│   │   ├── character-consistency-lock.md  # CCLP 4.0 protocol
│   │   └── CCLP-FLEXIBILITY.md           # Three-tier flexibility system
│   │
│   ├── animals/               # Animal character system (5 files)
│   │   ├── animal-characters.md  # Animal character overview
│   │   ├── animal-cclp.md       # Animal CCLP rules
│   │   ├── animal-cat.md        # Cat character template
│   │   ├── animal-dog.md        # Dog character template
│   │   └── animal-bear.md       # Bear character template
│   │
│   └── advanced/              # Advanced configuration (7 files)
│       ├── story-soul.md              # Emotion, Theme, Narrative, Pacing, Color
│       ├── supporting-characters.md   # Family/animal character anchors
│       ├── relationship-dynamics.md   # Multi-character interaction patterns
│       ├── scene-matching.md          # Extended scene intelligent matching
│       ├── reality-validation.md      # Scientific accuracy validation
│       ├── visual-effects.md          # Special visual effects
│       └── scenes-chinese-culture.md  # Chinese cultural scene research
│
├── guides/                    # Documentation and guides
│   ├── usage-guide.md         # Complete usage guide (English)
│   ├── usage-guide-zh.md      # Complete usage guide (Chinese)
│   ├── design.md              # Architecture documentation (English)
│   ├── design-zh.md           # Architecture documentation (Chinese)
│   ├── extending.md           # Extension guide (English)
│   ├── extending-zh.md        # Extension guide (Chinese)
│   ├── WATERMARK-TROUBLESHOOTING.md     # Watermark fix strategies
│   ├── MULTI-CHARACTER-PROMPT-FIX.md    # Multi-character fix guide
│   ├── CCLP-ENFORCEMENT-ENHANCED.md     # CCLP 4.0 implementation details
│   └── ARCHITECTURE-DESIGN-ANALYSIS.md  # Architecture analysis
│
├── examples/                  # Reference examples
│   ├── clay-meadow.md                           # Single-page: clay + meadow
│   ├── clay-meadow-3pages.md                    # Multi-page: 3-page story arc
│   ├── clay-forest-xiaoming.md                  # Single-page: Xiaoming character
│   ├── clay-pond-reflection-optimized.md        # Water reflection techniques
│   ├── ink-forest.md                            # Chinese ink style
│   ├── paper-cut-festival.md                    # Paper-cutting style
│   ├── nianhua-kitchen.md                       # Nianhua style + Grandma
│   ├── nianhua-kitchen-xiaoming-3pages-complete.md  # Complete multi-page demo
│   ├── tech-stars.md                            # Tech style (specialized)
│   └── multi-character-usage-examples.md        # Multi-character examples
│
├── REFERENCE.md               # Quick reference guide
└── FORMS.md                   # Form templates
```

## Quick Navigation

### For New Users
1. Start with `SKILL.md` (main file) for quick start guide
2. Read `guides/usage-guide.md` for complete documentation

### For Content Generation
- **Styles**: `config/core/styles.md` - All 18 visual styles
- **Scenes**: `config/core/scenes.md` - 12 scene environments
- **Characters**: `config/core/characters.md` - 4 protagonists
- **Age System**: `config/core/age-system.md` - Age-driven content

### For Multi-Page Stories
- **CCLP Protocol**: `config/cclp/character-consistency-lock.md`
- **Flexibility Levels**: `config/cclp/CCLP-FLEXIBILITY.md`
- **Story Patterns**: `config/core/story-flow.md`

### For Multi-Character Stories
- **Supporting Characters**: `config/advanced/supporting-characters.md`
- **Relationship Dynamics**: `config/advanced/relationship-dynamics.md`
- **Fix Guide**: `guides/MULTI-CHARACTER-PROMPT-FIX.md`

### For Extension
- **Adding Styles**: `guides/extending.md`
- **Adding Characters**: `config/core/character-extension.md`
- **Adding Scenes**: `config/core/scenes.md`

## File Count Summary

| Directory | Files | Purpose |
|-----------|-------|---------|
| `config/core/` | 11 | Essential configuration |
| `config/cclp/` | 2 | Character consistency |
| `config/animals/` | 5 | Animal characters |
| `config/advanced/` | 7 | Advanced features |
| `guides/` | 10 | Documentation |
| `examples/` | 10 | Reference examples |
| **Total** | **45** | - |

---

*Last updated: 2026-01-18*
