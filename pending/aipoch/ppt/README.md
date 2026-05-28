# PPT Framework

A modern presentation framework based on HTML/CSS/JS, featuring a **pluggable architecture** with support for rich animation effects and interactive features.

## Directory Structure

```
ppt/
├── build_html.py              <- Static HTML build script
├── convert_to_pptx.py         <- PPTX conversion entry script
├── README.md                  <- Documentation
├── requirements.txt           <- Python dependencies
├── output/                    <- Export directory
└── framework/                 <- Framework source code
    ├── index.html             <- Presentation entry point
    ├── content/
    │   └── slides-data.js     <- 📝 Slide content (edit this file)
    ├── core/
    │   ├── registry.js        <- Component registry
    │   ├── engine.js          <- Rendering engine
    │   ├── navigation.js      <- Navigation control
    │   └── utils.js           <- Utility functions
    ├── components/
    │   ├── _base.js           <- Base components (badge, title, subtitle)
    │   ├── comparison.js      <- Comparison cards
    │   ├── terminal.js        <- Terminal code blocks
    │   ├── quote.js           <- Quote blocks
    │   ├── assumptions.js     <- Assumptions grid
    │   ├── timeline.js        <- Timeline
    │   ├── stats.js           <- Statistics
    │   ├── valueCards.js      <- Value cards
    │   ├── competitionBox.js  <- Competition analysis box
    │   ├── strategyBox.js     <- Strategy box
    │   └── ending.js          <- Ending slide
    ├── animations/
    │   ├── presets.js         <- Animation preset definitions
    │   └── animations.css     <- Animation styles
    ├── themes/
    │   └── default/
    │       ├── variables.css  <- 🎨 Theme variables (colors, fonts)
    │       └── components.css <- Component styles
    └── converter/             <- PPTX converter module
```

## Quick Start

### 1. View Presentation

Simply open `framework/index.html` in your browser to view the presentation.

### 2. Create Project

Create a new project file in the `projects/` directory, e.g., `my-project.js`:

```javascript
const SLIDES = [
    {
        badge: { icon: "✦", text: "Theme Tag" },
        title: { text: "Title Text", gradient: true },
        subtitle: "Subtitle description",
        clickHint: "Click to start",
        elements: [
            { step: 1, type: "comparison", ... },
            { step: 2, type: "quote", ... }
        ]
    }
];
```

### 3. Generate HTML and PPTX

```bash
# Install dependencies
pip install -r requirements.txt

# Generate HTML (supports multiple input methods)
python build_html.py helixlife-20260130                 # Project name (automatically looks in projects/)
python build_html.py projects/helixlife-20260130.js    # Full path
python build_html.py helixlife-20260130 -o my-ppt      # Specify output name

# Generate PPTX (also supports multiple input methods)
python convert_to_pptx.py helixlife-20260130           # Project name
python convert_to_pptx.py projects/helixlife-20260130.js -o custom  # Specify output name

# Output files are located in the output/ directory
```

## Component Types

| Component | Description |
|------|------|
| `comparison` | Left-right comparison cards |
| `terminal` | Terminal/Code blocks |
| `quote` | Quote blocks |
| `assumptions` | Assumptions grid (supports strike-through reveal) |
| `timeline` | Timeline (supports sequential activation) |
| `stats` | Statistics |
| `valueCards` | Value cards (supports sequential activation) |
| `competitionBox` | Competition analysis box |
| `strategyBox` | Strategy box |
| `ending` | Ending slide |

## Animation System

### Animation Presets

| Preset | Effect |
|------|------|
| `fadeIn` | Fade in |
| `slideUp` | Slide up from bottom |
| `slideDown` | Slide down from top |
| `slideLeft` | Slide in from right |
| `slideRight` | Slide in from left |
| `scaleIn` | Scale in |
| `zoomIn` | Zoom in |
| `flipIn` | Flip in |

### Configuration Priority

```
element.animation > slide.defaultAnimation > Component default animation
```

### Configuration Examples

```javascript
// Element level
{
    step: 2,
    type: "quote",
    animation: { preset: "scaleIn", duration: 800, delay: 200 },
    text: "..."
}

// Shorthand form
{
    step: 2,
    type: "quote",
    animation: "scaleIn",
    text: "..."
}
```

## Shortcuts

| Key | Function |
|------|------|
| `Space` / `→` / `Enter` | Next step |
| `←` / `Backspace` | Previous step |
| `Home` | First slide |
| `End` | Last slide |
| `F` / `F11` | Fullscreen |
| `G` | Overview |
| `B` | Black screen |
| `W` | White screen |
| `?` / `H` | Help |
| `1-9` + `Enter` | Jump to page |

## Extended Development

### Adding New Components

1. Create `framework/components/newComponent.js`:

```javascript
const newComponent = {
    meta: {
        name: 'newComponent',
        description: 'New Component',
        defaultAnimation: { preset: 'slideUp', duration: 500 }
    },
    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        return `<div class="new-component ${anim.className}" data-step="${data.step}">
            ${data.content}
        </div>`;
    }
};

function registerNewComponent() {
    Registry.registerComponent('newComponent', newComponent);
}
```

2. Add styles in `framework/themes/default/components.css`

3. Import and register in `framework/index.html`

### Adding New Themes

1. Create `framework/themes/yourTheme/variables.css`
2. Override CSS variable definitions

## Version

- **v3.0.0** - Pluggable architecture refactor, modular component system