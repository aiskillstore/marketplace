# React API Reference

> **Requirements**: `@opentui/react` uses `react-reconciler` 0.33 and requires
> **React ≥ 19.2**. Run `bun add react@latest react-dom@latest` before upgrading.

## Rendering

### createRoot(renderer)

Creates a React root for rendering.

```tsx
import { createCliRenderer } from "@opentui/core"
import { createRoot } from "@opentui/react"

const renderer = await createCliRenderer({
  exitOnCtrlC: false,  // Handle Ctrl+C yourself
})

const root = createRoot(renderer)
root.render(<App />)
```

## Hooks

### useRenderer()

Access the OpenTUI renderer instance.

```tsx
import { useRenderer } from "@opentui/react"
import { useEffect } from "react"

function App() {
  const renderer = useRenderer()
  
  useEffect(() => {
    // Access renderer properties
    console.log(`Terminal: ${renderer.width}x${renderer.height}`)
    
    // Show debug console
    renderer.console.show()
    
    // Access theme mode (dark/light based on terminal settings)
    console.log(`Theme: ${renderer.themeMode}`)  // "dark" | "light" | null
  }, [renderer])
  
  return <text>Hello</text>
}

// Listen for theme mode changes
function ThemedApp() {
  const renderer = useRenderer()
  const [theme, setTheme] = useState(renderer.themeMode ?? "dark")
  
  useEffect(() => {
    const handler = (mode: "dark" | "light") => setTheme(mode)
    renderer.on("theme_mode", handler)
    return () => renderer.off("theme_mode", handler)
  }, [renderer])
  
  return (
    <box backgroundColor={theme === "dark" ? "#1a1a2e" : "#ffffff"}>
      <text fg={theme === "dark" ? "#fff" : "#000"}>
        Current theme: {theme}
      </text>
    </box>
  )
}
```

### useKeyboard(handler, options?)

Handle keyboard events.

```tsx
import { useKeyboard, useRenderer } from "@opentui/react"

function App() {
  const renderer = useRenderer()
  
  useKeyboard((key) => {
    if (key.name === "escape") {
      renderer.destroy()  // Never use process.exit() directly!
    }
    if (key.ctrl && key.name === "s") {
      saveDocument()
    }
  })
  
  return <text>Press ESC to exit</text>
}

// With release events
function GameControls() {
  const [pressed, setPressed] = useState(new Set<string>())
  
  useKeyboard(
    (event) => {
      setPressed(keys => {
        const newKeys = new Set(keys)
        if (event.eventType === "release") {
          newKeys.delete(event.name)
        } else {
          newKeys.add(event.name)
        }
        return newKeys
      })
    },
    { release: true }  // Include release events
  )
  
  return <text>Pressed: {Array.from(pressed).join(", ")}</text>
}
```

**Options:**
- `release?: boolean` - Include key release events (default: false)

**KeyEvent properties:**
- `name: string` - Key name ("a", "escape", "f1", etc.)
- `sequence: string` - Raw escape sequence
- `ctrl: boolean` - Ctrl modifier
- `shift: boolean` - Shift modifier
- `meta: boolean` - Alt modifier
- `option: boolean` - Option modifier (macOS)
- `eventType: "press" | "release" | "repeat"`
- `repeated: boolean` - Key is being held

### useOnResize(callback)

Handle terminal resize events.

```tsx
import { useOnResize } from "@opentui/react"

function App() {
  useOnResize((width, height) => {
    console.log(`Resized to ${width}x${height}`)
  })
  
  return <text>Resize the terminal</text>
}
```

### useTerminalDimensions()

Get reactive terminal dimensions.

```tsx
import { useTerminalDimensions } from "@opentui/react"

function ResponsiveLayout() {
  const { width, height } = useTerminalDimensions()
  
  return (
    <box flexDirection={width > 80 ? "row" : "column"}>
      <box flexGrow={1}>
        <text>Width: {width}</text>
      </box>
      <box flexGrow={1}>
        <text>Height: {height}</text>
      </box>
    </box>
  )
}
```

### useTimeline(options?)

Create animations with the timeline system.

```tsx
import { useTimeline } from "@opentui/react"
import { useEffect, useState } from "react"

function AnimatedBox() {
  const [width, setWidth] = useState(0)
  
  const timeline = useTimeline({
    duration: 2000,
    loop: false,
  })
  
  useEffect(() => {
    timeline.add(
      { width: 0 },
      {
        width: 50,
        duration: 2000,
        ease: "easeOutQuad",
        onUpdate: (anim) => {
          setWidth(Math.round(anim.targets[0].width))
        },
      }
    )
  }, [timeline])
  
  return <box style={{ width, height: 3, backgroundColor: "#6a5acd" }} />
}
```

**Options:**
- `duration?: number` - Default duration (ms)
- `loop?: boolean` - Loop the timeline
- `autoplay?: boolean` - Auto-start (default: true)
- `onComplete?: () => void` - Completion callback
- `onPause?: () => void` - Pause callback

**Timeline methods:**
- `add(target, properties, startTime?)` - Add animation
- `play()` - Start playback
- `pause()` - Pause playback
- `restart()` - Restart from beginning

### usePaste(handler)

Subscribe to bracketed-paste events. `handler` receives a `PasteEvent` with raw
`bytes` (decode with `decodePasteBytes`). The callback is kept stable across
renders.

```tsx
import { usePaste } from "@opentui/react"
import { decodePasteBytes } from "@opentui/core"

function Editor() {
  usePaste((event) => {
    console.log("Pasted:", decodePasteBytes(event.bytes))
  })
  return <textarea focused />
}
```

### useFocus(handler) / useBlur(handler)

Fire when the terminal window gains or loses OS focus.

```tsx
import { useFocus, useBlur } from "@opentui/react"

useFocus(() => console.log("Terminal gained focus"))
useBlur(() => console.log("Terminal lost focus"))
```

### useSelectionHandler(handler)

Fire when the user finishes a text selection (mouse-up). `handler` receives a
`Selection` (from `@opentui/core`); use `selection.getSelectedText()`.

```tsx
import { useSelectionHandler } from "@opentui/react"

useSelectionHandler((selection) => {
  console.log("Selected:", selection.getSelectedText())
})
```

> These four hooks (`usePaste`, `useFocus`, `useBlur`, `useSelectionHandler`)
> mirror the Solid hooks and are available from `@opentui/react`.

## Components

Full props for every component live in the shared **[components](../components/REFERENCE.md)**
references. This section only covers what is **React-specific**; read the linked
category file for the complete prop list.

### JSX Element Names

React uses **hyphenated** tag names. Full props are in the linked file:

| Element | Full props |
|---------|-----------|
| `<text>`, `<span>`, `<strong>`, `<em>`, `<u>`, `<a>`, `<br>` | [text-display.md](../components/text-display.md) |
| `<box>`, `<scrollbox>` | [containers.md](../components/containers.md) |
| `<input>`, `<textarea>`, `<select>`, `<tab-select>` | [inputs.md](../components/inputs.md) |
| `<code>`, `<line-number>`, `<diff>`, `<markdown>` | [code-diff.md](../components/code-diff.md) |
| `<ascii-font>` | [text-display.md](../components/text-display.md) |

### Text Styling Uses Nested Tags (React-specific)

Style text with **nested modifier elements**, not props:

```tsx
<text fg="#FFFFFF" bg="#000000" selectable>
  <span fg="red">Red</span> <strong>Bold</strong> <em>Italic</em> <u>Underline</u>
  <br />
  <a href="https://...">Link</a>
</text>
```

> **Note**: Do NOT use `bold`, `italic`, `underline` as props on `<text>`. Use
> nested modifier tags like `<strong>`, `<em>`, `<u>` instead.

### Controlled Inputs (React-specific)

Inputs are controlled with `value` + `onChange` (single value), and use the
`focused` prop to receive keyboard input:

```tsx
<input value={value} onChange={setValue} focused />
<textarea value={text} onChange={setText} focused width={40} height={10} />

// Select/tab-select: onChange fires on navigation, onSelect on Enter
<select options={opts} onChange={(i, opt) => setSel(opt)} focused />
```

### Scrollbox `style` Nesting (React-specific)

`<scrollbox>` takes a nested `style` object (`rootOptions`, `wrapperOptions`,
`viewportOptions`, `contentOptions`, `scrollbarOptions`). See
[containers.md](../components/containers.md) for the full structure.

## Type Exports

```tsx
import type {
  // Component props
  TextProps,
  BoxProps,
  InputProps,
  SelectProps,
  
  // Hook types
  KeyEvent,
  
  // From core
  CliRenderer,
} from "@opentui/react"
```
