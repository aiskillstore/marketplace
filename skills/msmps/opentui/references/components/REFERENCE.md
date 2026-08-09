# OpenTUI Components

Reference for all OpenTUI components, organized by category. Components are available in all three frameworks (Core, React, Solid) with slight API differences.

## When to Use

Use this reference when you need to find the right component category or compare naming across Core, React, and Solid.

## Component Categories

| Category | Components | File |
|----------|------------|------|
| Text & Display | text, ascii-font, styled text, qr-code | [text-display.md](./text-display.md) |
| Containers | box, scrollbox, scrollbar, borders | [containers.md](./containers.md) |
| Inputs | input, textarea, select, tab-select, slider | [inputs.md](./inputs.md) |
| Code & Diff | code, line-number, diff, markdown, text-table | [code-diff.md](./code-diff.md) |

## Component Chooser

```
Need a component?
├─ Styled text, ASCII art, or QR code -> text-display.md
├─ Containers, borders, scrolling, scrollbar -> containers.md
├─ Forms, input controls, sliders -> inputs.md
└─ Code blocks, diffs, line numbers, markdown -> code-diff.md
```

## Component Naming

Components have different names across frameworks:

| Concept | Core (Class) | React (JSX) | Solid (JSX) |
|---------|--------------|-------------|-------------|
| Text | `TextRenderable` | `<text>` | `<text>` |
| Box | `BoxRenderable` | `<box>` | `<box>` |
| ScrollBox | `ScrollBoxRenderable` | `<scrollbox>` | `<scrollbox>` |
| Input | `InputRenderable` | `<input>` | `<input>` |
| Textarea | `TextareaRenderable` | `<textarea>` | `<textarea>` |
| Select | `SelectRenderable` | `<select>` | `<select>` |
| Tab Select | `TabSelectRenderable` | `<tab-select>` | `<tab_select>` |
| ASCII Font | `ASCIIFontRenderable` | `<ascii-font>` | `<ascii_font>` |
| Code | `CodeRenderable` | `<code>` | `<code>` |
| Line Number | `LineNumberRenderable` | `<line-number>` | `<line_number>` |
| Diff | `DiffRenderable` | `<diff>` | `<diff>` |
| Markdown | `MarkdownRenderable` | `<markdown>` | `<markdown>` |
| TextTable | `TextTableRenderable` | N/A (Core only) | N/A (Core only) |
| Slider | `SliderRenderable` | N/A (Core only) | N/A (Core only) |
| ScrollBar | `ScrollBarRenderable` | N/A (Core only) | N/A (Core only) |
| FrameBuffer | `FrameBufferRenderable` | N/A (Core + construct) | N/A (Core + construct) |
| QR Code | `QRCodeRenderable` | `<qr-code>` * | `<qr_code>` * |

**Note**: Solid uses underscores (`tab_select`) while React uses hyphens (`tab-select`). `TextTableRenderable` is used internally by `MarkdownRenderable` for table rendering and is also available as a standalone Core component. `SliderRenderable` and `ScrollBarRenderable` do not yet expose a construct/JSX API — use the Core class. `FrameBufferRenderable` is Core-only with a `FrameBuffer({...})` construct wrapper (no reconciler JSX element). `* QRCodeRenderable` ships in the separate `@opentui/qrcode` package and requires `registerQRCode()` before the JSX element is available (see [text-display.md](./text-display.md)).

## Common Properties

All components share these layout properties (see [Layout](../layout/REFERENCE.md)):

```tsx
// Positioning
position="relative" | "absolute"
left, top, right, bottom

// Dimensions
width, height
minWidth, maxWidth, minHeight, maxHeight

// Flexbox
flexDirection, flexGrow, flexShrink, flexBasis
justifyContent, alignItems, alignSelf
flexWrap, gap

// Spacing
padding, paddingTop, paddingRight, paddingBottom, paddingLeft
paddingX, paddingY              // Axis shorthand (horizontal/vertical)
margin, marginTop, marginRight, marginBottom, marginLeft
marginX, marginY                // Axis shorthand (horizontal/vertical)

// Display
display="flex" | "none"
overflow="visible" | "hidden" | "scroll"
zIndex
```

## Quick Examples

### Core (Imperative)

```typescript
import { createCliRenderer, TextRenderable, BoxRenderable } from "@opentui/core"

const renderer = await createCliRenderer()

const box = new BoxRenderable(renderer, {
  id: "container",
  border: true,
  padding: 2,
})

const text = new TextRenderable(renderer, {
  id: "greeting",
  content: "Hello!",
  fg: "#00FF00",
})

box.add(text)
renderer.root.add(box)
```

### React

```tsx
import { createCliRenderer } from "@opentui/core"
import { createRoot } from "@opentui/react"

function App() {
  return (
    <box border padding={2}>
      <text fg="#00FF00">Hello!</text>
    </box>
  )
}

const renderer = await createCliRenderer()
createRoot(renderer).render(<App />)
```

### Solid

```tsx
import { render } from "@opentui/solid"

function App() {
  return (
    <box border padding={2}>
      <text fg="#00FF00">Hello!</text>
    </box>
  )
}

render(() => <App />)
```

## See Also

- [Core API](../core/api.md) - Imperative component classes
- [React API](../react/api.md) - React component props
- [Solid API](../solid/api.md) - Solid component props
- [Layout](../layout/REFERENCE.md) - Layout system details
