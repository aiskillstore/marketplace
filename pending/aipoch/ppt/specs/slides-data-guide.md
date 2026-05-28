# Slide Data Construction Guide

> Last Updated: 2026-01-29

This document explains how to write the `slides-data.js` file to create presentations.

## Directory Structure

```
ppt/
├── build_html.py          # Build static HTML
├── convert_to_pptx.py     # Convert to PPTX
├── projects/              # Directory for project data files
│   └── your-project.js    # Your slide data
├── framework/             # Framework source code
│   └── content/
│       └── slides-data.js # Currently used data (read during build)
└── output/                # Output directory
```

## Basic Structure

```javascript
const SLIDES = [
    {
        // Slide configuration
        badge: { icon: "*", text: "BADGE TEXT" },
        title: { text: "Title Text", gradient: true },
        subtitle: "Subtitle description",
        clickHint: "Click hint text",
        
        // Content elements array
        elements: [
            { step: 1, type: "component type", /* component parameters */ },
            { step: 2, type: "component type", /* component parameters */ }
        ]
    },
    // More slides...
];
```

## Slide Properties

| Property | Type | Required | Description |
|------|------|------|------|
| `badge` | object | No | Top badge `{ icon, text }` |
| `title` | object | Yes | Title `{ text, gradient? }` |
| `subtitle` | string | No | Subtitle |
| `clickHint` | string | No | Bottom hint text |
| `defaultAnimation` | object | No | Default animation configuration for this page |
| `elements` | array | Yes | Content elements array |

## Component Types

### 1. comparison - Comparison Card

Left-right two-column comparison layout.

```javascript
{
    step: 1,
    type: "comparison",
    style: "width: 90%;",  // Optional style
    left: {
        icon: "o",
        title: "Left Title",
        items: ["Item 1", "Item 2", "Item 3"]
    },
    right: {
        icon: "O",
        title: "Right Title",
        items: ["Item 1", "Item 2", "Item 3"]
    }
}
```

### 2. terminal - Terminal Code Block

Simulates terminal/command line display.

```javascript
{
    step: 2,
    type: "terminal",
    style: "max-width: 600px;",
    content: [
        { type: "prompt", text: "$ " },
        { type: "text", text: "command " },
        { type: "highlight", text: "argument" },
        { type: "cursor" }
    ]
}
```

**content types:**
- `prompt`: Command prompt
- `text`: Plain text
- `highlight`: Highlighted text
- `cursor`: Cursor

### 3. quote - Quote Block

Highlights quoted content.

```javascript
{
    step: 3,
    type: "quote",
    style: "border-left: 4px solid var(--accent-coral);",
    text: "Quoted text content",
    textStyle: "font-size: 1.5rem;",  // Optional
    gradient: true,  // Optional, gradient text
    author: { icon: "*", text: "Author signature" }
}
```

### 4. assumptions - Assumptions Grid

Displays content where old assumptions are broken, supports strikethrough reveal effect.

```javascript
{
    step: 1,
    type: "assumptions",
    style: "gap: 2vmin;",
    revealStep: 2,  // Reveal new content at this step
    items: [
        { old: "X Old Assumption 1", new: "-> New Reality 1" },
        { old: "X Old Assumption 2", new: "-> New Reality 2" }
    ]
}
```

### 5. timeline - Timeline

Displays phased progress.

```javascript
{
    step: 1,
    type: "timeline",
    items: [
        { activeStep: 1, badge: "Phase 1", icon: "o", title: "Phase 1", desc: "Description", case: "Case" },
        { activeStep: 2, badge: "Phase 2", icon: "=", title: "Phase 2", desc: "Description", case: "Case" },
        { activeStep: 3, badge: "Phase 3", icon: "O", iconFilled: true, title: "Phase 3", desc: "Description", case: "Case" }
    ]
}
```

**item properties:**
- `activeStep`: Which step activates this item
- `badge`: Phase label
- `badgeCurrent`: Whether to mark as current phase
- `icon`: Icon character
- `iconFilled`: Whether to fill the icon
- `title`: Title
- `desc`: Description
- `case`: Case study/description

### 6. stats - Statistics

Displays key metrics.

```javascript
{
    step: 5,
    type: "stats",
    items: [
        { icon: "+", value: "100%", label: "Metric Description 1" },
        { icon: "*", value: "50K", label: "Metric Description 2" },
        { icon: "#", value: "24/7", label: "Metric Description 3" }
    ]
}
```

### 7. valueCards - Value Cards

Displays core value points, supports sequential activation.

```javascript
{
    step: 1,
    type: "valueCards",
    items: [
        { activeStep: 1, icon: "+", title: "Value 1", desc: "Description text" },
        { activeStep: 2, icon: "-", title: "Value 2", desc: "Description text" },
        { activeStep: 3, icon: "*", title: "Value 3", desc: "Description text" }
    ]
}
```

### 8. competitionBox - Competition Analysis Box

Displays analysis of competitive factors.

```javascript
{
    step: 4,
    type: "competitionBox",
    title: "Title Text",
    items: ["Point 1", "Point 2", "Point 3"],
    conclusion: "Conclusion > Comparison"
}
```

### 9. strategyBox - Strategy Box

Displays strategic decisions.

```javascript
{
    step: 5,
    type: "strategyBox",
    title: "Strategy Title",
    items: [
        { type: "wrong", text: "Things not to do" },
        { type: "wrong", text: "Other things not to do" },
        { type: "right", text: "Things to do" }
    ],
    final: { arrow: "->", text: "Final Goal" }
}
```

### 10. ending - Ending Page

Presentation ending page.

```javascript
{
    step: 6,
    type: "ending",
    icon: "*",
    message: "Closing remarks",
    thanks: "THANKS FOR WATCHING"
}
```

## Animation Configuration

### Animation Presets

| Preset | Effect |
|------|------|
| `fadeIn` | Fade in |
| `slideUp` | Slide in from bottom |
| `slideDown` | Slide in from top |
| `slideLeft` | Slide in from right |
| `slideRight` | Slide in from left |
| `scaleIn` | Scale in |
| `zoomIn` | Zoom in |
| `flipIn` | Flip in |

### Configuration Method

```javascript
// Slide level - Default animation for all elements
{
    defaultAnimation: { preset: "slideUp", duration: 500 },
    elements: [...]
}

// Element level - Individual element animation
{
    step: 1,
    type: "quote",
    animation: { preset: "scaleIn", duration: 800, delay: 200 }
}

// Shorthand form
{
    step: 1,
    type: "quote",
    animation: "scaleIn"
}
```

### Animation Parameters

| Parameter | Type | Description |
|------|------|------|
| `preset` | string | Animation preset name |
| `duration` | number | Animation duration (ms) |
| `delay` | number | Animation delay (ms) |
| `easing` | string | Easing function |
| `stagger` | number | Sequential delay interval for list items (ms) |

## PPTX Conversion Notes

Since the PPTX converter uses a simplified JS parser, please follow these rules:

### Avoid Using

1. **Special Unicode Symbols**
   - Prohibited: emoji (🚀📝), special geometric symbols (✦◈◆◇●○◐◑)
   - Alternative: Use ASCII characters (`*`, `+`, `-`, `#`, `@`, `o`, `O`, `=`)

2. **Chinese Quotation Marks**
   - Prohibited: 「」『』""''
   - Alternative: Use standard quotation marks or omit them entirely

3. **Single Quotes Inside Strings**
   - Prohibited: `"Entering 'Action' Year"` (Single quotes will be converted to double quotes, breaking the JSON)
   - Alternative: `"Entering Doers Year"` or use other expressions

4. **Comments Inside Arrays**
   - Prohibited: Using `// comments` inside the SLIDES array
   - Alternative: Place comments outside the array or at the top of the file

### Recommended Icon Characters

```javascript
// Icons suitable for PPTX conversion
icon: "*"   // Asterisk
icon: "+"   // Plus
icon: "-"   // Minus
icon: "#"   // Hash
icon: "@"   // At symbol
icon: "o"   // Lowercase o (hollow circle)
icon: "O"   // Uppercase O (solid circle)
icon: "="   // Equals sign (semi-filled)
icon: ">"   // Arrow
icon: "[x]" // Checkbox
```

## Build and Conversion

### 1. Prepare Data File

Copy the data file to `framework/content/slides-data.js`:

```powershell
Copy-Item projects\your-project.js framework\content\slides-data.js -Force
```

### 2. Generate HTML

```powershell
python build_html.py --output your-project
```

Output: `output/your-project.html`

### 3. Generate PPTX

```powershell
python convert_to_pptx.py --output your-project
```

Output: `output/your-project.pptx`

### Command Line Arguments

**build_html.py:**
- `--output, -o`: Output filename
- `--minify, -m`: Minify output
- `--separate-data, -d`: Separate data output

**convert_to_pptx.py:**
- `--html, -H`: HTML source file path
- `--data, -d`: Data file path
- `--output, -o`: Output filename

## Full Example

```javascript
const SLIDES = [
    {
        badge: { icon: "*", text: "EXAMPLE 2026" },
        title: { text: "Presentation Title", gradient: true },
        subtitle: "Subtitle description text",
        clickHint: "Click to start",
        elements: [
            {
                step: 1,
                type: "comparison",
                left: {
                    icon: "o",
                    title: "Before",
                    items: ["Old Way 1", "Old Way 2"]
                },
                right: {
                    icon: "O",
                    title: "After",
                    items: ["New Way 1", "New Way 2"]
                }
            },
            {
                step: 2,
                type: "quote",
                text: "Core viewpoint quote text",
                author: { icon: "*", text: "Author Name" }
            }
        ]
    },
    {
        badge: { icon: "+", text: "CONCLUSION" },
        title: { text: "Summary" },
        elements: [
            {
                step: 1,
                type: "ending",
                icon: "*",
                message: "Thanks for watching",
                thanks: "THE END"
            }
        ]
    }
];
```

## Debugging Tips

1. **HTML-First Testing**: Generate HTML with `build_html.py` first to verify content and animations in the browser.
2. **Check PPTX Parsing**: If PPTX conversion fails, check if prohibited characters were used.
3. **Check the Console**: The browser console will display component registration and rendering information.