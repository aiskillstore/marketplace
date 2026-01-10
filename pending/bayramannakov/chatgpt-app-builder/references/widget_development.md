# Widget Development Guide

Complete reference for building ChatGPT App widgets with React and the `window.openai` API.

## window.openai API Reference

The host injects `window.openai` into your widget iframe with these capabilities:

### Data Access

```typescript
// Tool input (arguments passed when tool was invoked)
const input = window.openai.toolInput;
// Type: Record<string, unknown>

// Tool output (structuredContent from response)
const output = window.openai.toolOutput;
// Type: Record<string, unknown>

// Response metadata (_meta from response, hidden from model)
const meta = window.openai.toolResponseMetadata;
// Type: Record<string, unknown>

// Persisted widget state
const state = window.openai.widgetState;
// Type: Record<string, unknown> | null
```

### State Management

```typescript
// Persist state (survives widget re-renders within same flow)
window.openai.setWidgetState({
  selectedId: "item-123",
  viewMode: "grid",
  filters: { status: "active" }
});
// Note: State is visible to model, keep under ~4k tokens
```

### Tool Invocation

```typescript
// Call another tool from the widget
await window.openai.callTool("myapp_refresh_items", {
  status: "active"
});
// Requires tool to have "openai/widgetAccessible": true

// Send a message as if user typed it
await window.openai.sendFollowUpMessage({
  prompt: "Now show me the completed items"
});
```

### File Operations

```typescript
// Upload a file
const { fileId } = await window.openai.uploadFile(file);
// Supports: image/png, image/jpeg, image/webp

// Get download URL for uploaded file
const { downloadUrl } = await window.openai.getFileDownloadUrl({ fileId });
img.src = downloadUrl;
```

### Layout Control

```typescript
// Report widget height for proper sizing
window.openai.notifyIntrinsicHeight(450);

// Request display mode change
await window.openai.requestDisplayMode({ mode: "fullscreen" });
// Modes: "inline", "expanded", "pip" (picture-in-picture), "fullscreen"

// Request modal dialog (host-controlled)
await window.openai.requestModal({ title: "Confirm" });

// Open external link (must be in redirect_domains CSP)
window.openai.openExternal({ href: "https://myapp.com/settings" });

// Close the widget
window.openai.requestClose();
```

### Context Signals

```typescript
// Theme (for dark mode support)
const theme = window.openai.theme; // "light" | "dark"

// Current display mode
const mode = window.openai.displayMode;

// Maximum height available
const maxHeight = window.openai.maxHeight;

// Safe area insets (for mobile)
const safeArea = window.openai.safeArea;

// User's locale
const locale = window.openai.locale; // e.g., "en-US"

// User agent info
const ua = window.openai.userAgent;

// View context (page context where widget is rendered)
const view = window.openai.view;
```

### Session Management

```typescript
// Widget session ID - persists state across conversational turns
// Available in tool response metadata from server
const widgetSessionId = toolResponseMetadata["openai/widgetSessionId"];

// Use widgetSessionId to associate widget state with server-side session
// Include in tool calls if you need to maintain server-side state:
await window.openai.callTool("myapp_action", {
  sessionId: widgetSessionId,
  action: "update"
});
```

---

## TypeScript Type Definitions

### src/types/openai.d.ts
```typescript
interface OpenAIWidgetState {
  [key: string]: unknown;
}

interface OpenAIToolOutput {
  [key: string]: unknown;
}

interface OpenAIToolInput {
  [key: string]: unknown;
}

interface OpenAIResponseMetadata {
  [key: string]: unknown;
}

interface OpenAISafeArea {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

interface OpenAIUploadResult {
  fileId: string;
}

interface OpenAIDownloadResult {
  downloadUrl: string;
}

type DisplayMode = "inline" | "expanded" | "pip" | "fullscreen";
type Theme = "light" | "dark";

interface OpenAIGlobals {
  // Data
  toolInput: OpenAIToolInput;
  toolOutput: OpenAIToolOutput;
  toolResponseMetadata: OpenAIResponseMetadata;
  widgetState: OpenAIWidgetState | null;

  // Context
  theme: Theme;
  displayMode: DisplayMode;
  maxHeight: number;
  safeArea: OpenAISafeArea;
  locale: string;
  userAgent: string;

  // Actions
  setWidgetState: (state: OpenAIWidgetState) => void;
  callTool: (name: string, args: Record<string, unknown>) => Promise<void>;
  sendFollowUpMessage: (params: { prompt: string }) => Promise<void>;
  uploadFile: (file: File) => Promise<OpenAIUploadResult>;
  getFileDownloadUrl: (params: { fileId: string }) => Promise<OpenAIDownloadResult>;
  notifyIntrinsicHeight: (height: number) => void;
  requestDisplayMode: (params: { mode: DisplayMode }) => Promise<void>;
  requestModal: (params: { title: string }) => Promise<void>;
  requestClose: () => void;
  openExternal: (params: { href: string }) => void;
}

declare global {
  interface Window {
    openai: OpenAIGlobals;
  }
}

export {};
```

---

## React Hooks

### useOpenAI Hook (Reactive global access)
```typescript
import { useSyncExternalStore, useCallback } from "react";

type OpenAIKey = keyof typeof window.openai;

interface SetGlobalsEvent extends CustomEvent {
  detail: { globals: Partial<typeof window.openai> };
}

export function useOpenAI<K extends OpenAIKey>(key: K): typeof window.openai[K] {
  return useSyncExternalStore(
    (onChange) => {
      const handleSetGlobal = (event: Event) => {
        const customEvent = event as SetGlobalsEvent;
        if (customEvent.detail.globals[key] !== undefined) {
          onChange();
        }
      };
      window.addEventListener("openai:set_globals", handleSetGlobal, { passive: true });
      return () => window.removeEventListener("openai:set_globals", handleSetGlobal);
    },
    () => window.openai[key],
    () => window.openai[key]
  );
}
```

### useToolOutput Hook
```typescript
export function useToolOutput<T = Record<string, unknown>>(): T {
  return useOpenAI("toolOutput") as T;
}

// Usage
interface MyOutput {
  items: Array<{ id: string; title: string }>;
  total: number;
}

function ItemList() {
  const { items, total } = useToolOutput<MyOutput>();
  return (
    <div>
      <p>Showing {items.length} of {total}</p>
      {items.map(item => <div key={item.id}>{item.title}</div>)}
    </div>
  );
}
```

### useWidgetState Hook
```typescript
import { useState, useEffect, useCallback, SetStateAction } from "react";

export function useWidgetState<T extends Record<string, unknown>>(
  defaultState: T | (() => T)
): readonly [T, (state: SetStateAction<T>) => void] {
  const widgetStateFromWindow = useOpenAI("widgetState") as T | null;

  const [widgetState, _setWidgetState] = useState<T>(() => {
    if (widgetStateFromWindow) return widgetStateFromWindow;
    return typeof defaultState === "function" ? defaultState() : defaultState;
  });

  useEffect(() => {
    if (widgetStateFromWindow) {
      _setWidgetState(widgetStateFromWindow);
    }
  }, [widgetStateFromWindow]);

  const setWidgetState = useCallback(
    (state: SetStateAction<T>) => {
      _setWidgetState((prevState) => {
        const newState = typeof state === "function" ? state(prevState) : state;
        window.openai.setWidgetState(newState);
        return newState;
      });
    },
    []
  );

  return [widgetState, setWidgetState] as const;
}

// Usage
interface MyState {
  selectedId: string | null;
  filter: "all" | "active" | "completed";
}

function ItemList() {
  const [state, setState] = useWidgetState<MyState>({
    selectedId: null,
    filter: "all"
  });

  const selectItem = (id: string) => {
    setState(prev => ({ ...prev, selectedId: id }));
  };

  return (
    <div>
      <p>Selected: {state.selectedId}</p>
      {/* ... */}
    </div>
  );
}
```

### useTheme Hook
```typescript
export function useTheme(): "light" | "dark" {
  return useOpenAI("theme");
}

// Usage
function App() {
  const theme = useTheme();
  return (
    <div className={theme === "dark" ? "dark-mode" : "light-mode"}>
      {/* ... */}
    </div>
  );
}
```

---

## Component Patterns

### List with Actions
```typescript
interface Item {
  id: string;
  title: string;
  completed: boolean;
}

interface ListState {
  selectedId: string | null;
}

function ItemList() {
  const { items } = useToolOutput<{ items: Item[] }>();
  const [state, setState] = useWidgetState<ListState>({ selectedId: null });

  const handleComplete = async (id: string) => {
    await window.openai.callTool("myapp_complete_item", { id });
  };

  const handleSelect = (id: string) => {
    setState({ selectedId: id });
  };

  return (
    <ul className="item-list">
      {items.map(item => (
        <li
          key={item.id}
          className={state.selectedId === item.id ? "selected" : ""}
          onClick={() => handleSelect(item.id)}
        >
          <input
            type="checkbox"
            checked={item.completed}
            onChange={() => handleComplete(item.id)}
          />
          <span>{item.title}</span>
        </li>
      ))}
    </ul>
  );
}
```

### Dynamic Height
```typescript
import { useEffect, useRef } from "react";

function AutoHeightContainer({ children }: { children: React.ReactNode }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const updateHeight = () => {
      if (containerRef.current) {
        const height = containerRef.current.scrollHeight;
        window.openai.notifyIntrinsicHeight(height);
      }
    };

    updateHeight();

    const observer = new ResizeObserver(updateHeight);
    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return <div ref={containerRef}>{children}</div>;
}
```

### Fullscreen Toggle
```typescript
function FullscreenButton() {
  const displayMode = useOpenAI("displayMode");

  const toggleFullscreen = async () => {
    const newMode = displayMode === "fullscreen" ? "inline" : "fullscreen";
    await window.openai.requestDisplayMode({ mode: newMode });
  };

  return (
    <button onClick={toggleFullscreen}>
      {displayMode === "fullscreen" ? "Exit Fullscreen" : "Fullscreen"}
    </button>
  );
}
```

### External Link
```typescript
function ExternalLink({ href, children }: { href: string; children: React.ReactNode }) {
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    window.openai.openExternal({ href });
  };

  return (
    <a href={href} onClick={handleClick}>
      {children}
    </a>
  );
}
```

---

## Styling for ChatGPT Context

### Dark Mode Support

Use the Apps SDK UI gray scale for native ChatGPT look. See [Apps SDK UI Tokens](./apps_sdk_ui_tokens.md) for complete reference.

#### CSS Variable Architecture

Define semantic colors that adapt to theme:

```css
:root {
  /* Gray scale (Apps SDK UI) */
  --gray-0: #ffffff;
  --gray-100: #f5f5f5;
  --gray-200: #e5e5e5;
  --gray-400: #a3a3a3;
  --gray-500: #737373;
  --gray-700: #404040;
  --gray-800: #262626;
  --gray-900: #171717;
  --gray-1000: #0a0a0a;

  /* Semantic colors (light mode defaults) */
  --color-text: var(--gray-1000);
  --color-text-secondary: var(--gray-500);
  --color-text-tertiary: var(--gray-400);
  --color-bg: var(--gray-0);
  --color-bg-soft: var(--gray-100);
  --color-border: var(--gray-200);
}

/* Dark mode overrides - only change semantic colors */
.dark-mode {
  --color-text: var(--gray-0);
  --color-text-secondary: var(--gray-400);
  --color-text-tertiary: var(--gray-500);
  --color-bg: var(--gray-900);
  --color-bg-soft: var(--gray-800);
  --color-border: var(--gray-700);
}

/* Components use semantic colors - no dark mode overrides needed */
.card {
  background: var(--color-bg-soft);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}
```

#### Theme Detection

```javascript
function updateTheme() {
  const theme = window.openai?.theme || 'light';
  document.body.classList.toggle('dark-mode', theme === 'dark');
}

// Initial setup
updateTheme();

// Listen for theme changes from ChatGPT
window.addEventListener('openai:set_globals', updateTheme);
```

#### React Hook

```typescript
function useTheme(): 'light' | 'dark' {
  const [theme, setTheme] = useState<'light' | 'dark'>(
    () => (window as any).openai?.theme || 'light'
  );

  useEffect(() => {
    const handler = () => {
      setTheme((window as any).openai?.theme || 'light');
    };
    window.addEventListener('openai:set_globals', handler);
    return () => window.removeEventListener('openai:set_globals', handler);
  }, []);

  return theme;
}

// Usage
function App() {
  const theme = useTheme();

  useEffect(() => {
    document.body.classList.toggle('dark-mode', theme === 'dark');
  }, [theme]);

  return <div className="widget">...</div>;
}
```

#### Key Principle

Only override semantic color variables (not gray scale values) in dark mode. This ensures:
- Consistent colors across all components
- Single place to manage theme
- No component-specific dark mode overrides needed

### Responsive Layout
```css
.widget-container {
  padding: 16px;
  max-width: 100%;
}

/* Compact for inline mode */
.inline .widget-container {
  padding: 12px;
}

/* Full width for fullscreen */
.fullscreen .widget-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

/* Mobile adjustments */
@media (max-width: 480px) {
  .widget-container {
    padding: 12px;
  }
}
```

### ChatGPT-Compatible Typography
```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.5;
}

h1 { font-size: 1.5rem; font-weight: 600; }
h2 { font-size: 1.25rem; font-weight: 600; }
h3 { font-size: 1rem; font-weight: 600; }

button {
  font-family: inherit;
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  background: var(--accent-color, #0066cc);
  color: white;
}

button:hover {
  opacity: 0.9;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

---

## Localization

```typescript
import { useMemo } from "react";

const messages: Record<string, Record<string, string>> = {
  "en-US": {
    "items.empty": "No items found",
    "items.loading": "Loading...",
    "actions.complete": "Mark complete",
    "actions.delete": "Delete"
  },
  "es-ES": {
    "items.empty": "No se encontraron elementos",
    "items.loading": "Cargando...",
    "actions.complete": "Marcar como completado",
    "actions.delete": "Eliminar"
  }
};

export function useTranslation() {
  const locale = useOpenAI("locale");

  return useMemo(() => {
    const currentMessages = messages[locale] || messages["en-US"];
    return (key: string) => currentMessages[key] || key;
  }, [locale]);
}

// Usage
function EmptyState() {
  const t = useTranslation();
  return <p>{t("items.empty")}</p>;
}
```

---

## OpenAI Apps SDK UI Library

OpenAI provides a pre-built React component library for building widgets: `@openai/apps-sdk-ui`

### Installation

```bash
npm install @openai/apps-sdk-ui
```

### Usage

```typescript
import { Button, List, Card } from "@openai/apps-sdk-ui";

function MyWidget() {
  return (
    <div>
      <List items={items} />
      <Button onClick={handleAction}>Take Action</Button>
    </div>
  );
}
```

### Storybook Documentation

View all available components and their props:
- [Apps SDK UI Storybook](https://openai.github.io/apps-sdk-ui)

### Benefits

- Pre-styled to match ChatGPT's design
- Built-in dark mode support
- Accessible components
- Consistent with other ChatGPT apps

---

## Best Practices

1. **Keep state minimal** - Widget state is visible to model, keep under 4k tokens
2. **Handle null states** - `widgetState` can be null on first render
3. **Report height changes** - Call `notifyIntrinsicHeight` when content changes
4. **Support dark mode** - Use `useTheme()` and CSS variables
5. **Be responsive** - Widget runs on mobile too
6. **Handle loading states** - Show feedback during tool calls
7. **Validate CSP** - Ensure all external domains are in widgetCSP
8. **Consider using @openai/apps-sdk-ui** - Pre-built components save time

---

## Common Widget Gotchas

### SVG Animation: CSS vs Attributes

CSS styles **override** SVG presentation attributes. This causes subtle bugs with dynamic SVG animations.

**Problem:** Setting SVG attributes doesn't work when CSS is present:

```javascript
// ❌ WRONG - CSS styles override this!
progressFill.setAttribute('stroke-dashoffset', offset);
```

**Solution:** Use `.style` property to modify CSS directly:

```javascript
// ✅ CORRECT - Modifies computed style, triggers CSS transition
progressFill.style.strokeDashoffset = offset;
```

**Why:** When both an SVG attribute and CSS rule target the same property, CSS wins. `setAttribute()` changes the attribute, but the CSS rule still takes precedence.

### SVG Progress Ring: Clockwise from Top

To make a circular progress ring fill clockwise from 12 o'clock:

```html
<svg viewBox="0 0 100 100" class="circular-progress">
  <circle class="progress-bg" cx="50" cy="50" r="45" pathLength="100"/>
  <circle class="progress-fill" cx="50" cy="50" r="45" pathLength="100"/>
</svg>
```

```css
.circular-progress {
  transform: rotate(-90deg);  /* Start from 12 o'clock instead of 3 o'clock */
}

.progress-fill {
  fill: none;
  stroke: var(--accent-color);
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 100;      /* With pathLength=100, this is the full circle */
  stroke-dashoffset: 75;      /* 100 - 25 = showing 25% */
  transition: stroke-dashoffset 0.4s ease-out;
}
```

**Key trick:** `pathLength="100"` on the SVG circle makes dasharray/dashoffset math simple:
- `stroke-dashoffset: 100` = 0% filled
- `stroke-dashoffset: 0` = 100% filled
- `stroke-dashoffset: 100 - percent` = percent% filled

### Dark Mode: Gray Scale Inversion

> **⚠️ This catches everyone the first time.**

The Apps SDK UI gray scale **inverts** in dark mode:

| Variable | Light Mode | Dark Mode |
|----------|------------|-----------|
| `--gray-100` | Light (#f5f5f5) | **Dark** (#1a1a1a) |
| `--gray-900` | Dark (#171717) | **Light** (#ededed) |

**Problem:** If you use `--gray-100` thinking it's "light gray," it becomes dark gray in dark mode - potentially invisible on a dark background.

**Solution:** Use the **same variable** for both modes - it auto-inverts:

```css
/* ✅ CORRECT - Works in both modes automatically */
.progress-fill {
  stroke: var(--gray-900);  /* Dark in light mode, light in dark mode */
}

/* ❌ WRONG - Don't create mode-specific overrides for gray values */
.dark-mode .progress-fill {
  stroke: var(--gray-100);  /* Don't do this! */
}
```

**Mental model:** Think of gray scale as "contrast level" not "lightness":
- `--gray-900` = high contrast (visible against background)
- `--gray-100` = low contrast (subtle, background-ish)

The gray scale maintains this semantic meaning in both modes.

### Loading State Re-initialization Bug

**Problem:** Loading animation resets every time the widget re-renders during loading phase.

**Cause:** Calling initialization function on every render:

```javascript
// ❌ WRONG - Reinitializes on every render
function render() {
  if (viewType === 'loading') {
    initLoadingAnimation();  // Called repeatedly!
  }
}
```

**Solution:** Guard against re-initialization:

```javascript
let loadingInitialized = false;

function initLoadingAnimation() {
  // Guard: don't reinitialize if already running
  if (loadingInitialized) return;
  loadingInitialized = true;

  // Set up timers, intervals, etc.
}

// Reset when loading completes
function onDataReceived() {
  loadingInitialized = false;
}
```

Or with React:

```typescript
const [isLoading, setIsLoading] = useState(true);
const loadingRef = useRef(false);

useEffect(() => {
  if (isLoading && !loadingRef.current) {
    loadingRef.current = true;
    // Initialize loading animation once
  }
}, [isLoading]);
```
