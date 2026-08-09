# Keymap (@opentui/keymap)

A host-agnostic key binding, command, and sequence engine for both terminal
(OpenTUI) and browser (DOM) hosts. It is a **separate package** from
`@opentui/core`, shipped as `@opentui/keymap`, and is **pure JavaScript** — it
imports in Node.js with **no Bun and no native FFI required** (only creating a
native OpenTUI renderer needs FFI).

## When to Use

Use keymap when you need declarative, layered keybindings with commands, leader
keys, multi-key sequences (`dd`, `<leader>s`), counts (`{count}j`), or ex-style
commands — instead of hand-rolling `useKeyboard`/`keyInput` handlers.

## Install

```bash
bun add @opentui/keymap
```

## Entry Points

| Import | Purpose |
|--------|---------|
| `@opentui/keymap` | Main engine: `Keymap`, key stringifiers, shared types |
| `@opentui/keymap/addons` | Universal addons (parser stages, metadata, diagnostics, sequences, ex-commands) |
| `@opentui/keymap/addons/opentui` | Universal addons + OpenTUI base-layout & edit-buffer helpers |
| `@opentui/keymap/extras` | Config/formatting helpers (`commandBindings`, `createBindingLookup`, `formatKeySequence`, `formatCommandBindings`) |
| `@opentui/keymap/extras/graph` | `getGraphSnapshot()` for debug/graph UIs |
| `@opentui/keymap/testing` | Fake host + diagnostics for addon tests |
| `@opentui/keymap/opentui` | OpenTUI terminal host adapter |
| `@opentui/keymap/html` | DOM host adapter |
| `@opentui/keymap/react` | React provider/hooks |
| `@opentui/keymap/solid` | Solid provider/hooks |

## Quick Start (Terminal)

```typescript
import { createCliRenderer } from "@opentui/core"
import { createDefaultOpenTuiKeymap } from "@opentui/keymap/opentui"

const renderer = await createCliRenderer()
const keymap = createDefaultOpenTuiKeymap(renderer)

keymap.registerLayer({
  commands: [{ name: "quit", run() { renderer.destroy() } }],
  bindings: [{ key: "q", cmd: "quit" }],
})
```

Construction options:
- Bare: `new Keymap(host)`
- Host helpers: `createOpenTuiKeymap(renderer)` / `createHtmlKeymap(root)`
- With default addons: `createDefaultOpenTuiKeymap(renderer)` / `createDefaultHtmlKeymap(root)`

## Binding Shape

A binding has a required `key`, plus optional fields:

```typescript
{
  key: "ctrl+x",          // string ("dd", "<leader>s", "{count}j") or stroke object { name: "return", ctrl: true }
  cmd: "quit",            // command name to run
  event: "press",         // "press" (default) | "release"
  preventDefault: true,   // default true
  fallthrough: false,     // default false
  // ...custom addon fields
}
```

## Core API (Keymap instance)

- **Register** (each returns a disposer): `registerLayer()`, `registerToken()`,
  `registerSequencePattern()`, `registerLayerFields()`, `registerBindingFields()`,
  `registerCommandFields()`, plus parser/expander/transformer/resolver
  `prepend*/append*` stages.
- **Dispatch/execute**: `runCommand()`, `dispatchCommand()`,
  `intercept("key" | "key:after" | "raw", fn)`.
- **Query**: `getActiveKeys(options?)`, `getCommands()`, `getCommandEntries()`,
  `getCommandBindings()`, `getPendingSequence()`, `hasPendingSequence()`,
  `clearPendingSequence()`, `popPendingSequence()`.
- **Data/state**: `setData(name, value)`, `getData(name)`; events via
  `on("state" | "pendingSequence" | "dispatch" | "warning" | "error", fn)`.
- **Key helpers**: `parseKeySequence()`, `formatKey()`, `createKeyMatcher()`,
  `getHostMetadata()`; exported `stringifyKeyStroke()` / `stringifyKeySequence()`.

## Shipped Addons

`registerDefaultKeys()`, `registerLeader()`, `registerTimedLeader()`,
`registerModBindings()`, `registerCommaBindings()`, `registerEmacsBindings()`,
`registerExCommands()`, `registerNeovimDisambiguation()`,
`registerMetadataFields()`, `registerEnabledFields()`; OpenTUI-specific
`registerBaseLayoutFallback()`, `createTextareaBindings()`,
`registerManagedTextareaLayer()`, `registerEditBufferCommands()`.

## React

```tsx
import { KeymapProvider, useKeymap, useBindings, useActiveKeys } from "@opentui/keymap/react"

// Provide a pre-created Keymap<Renderable, KeyEvent>, then:
useBindings((keymap) => keymap.registerLayer({ /* ... */ }), [deps])
const active = useActiveKeys()
```

Exports: `KeymapProvider`, `useKeymap()`, `useBindings(createLayer, deps?)`,
`useActiveKeys(options?)`, `usePendingSequence()`, `reactiveMatcherFromStore()`.

## Solid

The Solid adapter (`@opentui/keymap/solid`) exposes an equivalent provider and
hooks that consume a pre-created `Keymap`.

## Keymap vs Keyboard

- **Keyboard** (`keyboard/REFERENCE.md`, `useKeyboard`/`keyInput`): low-level raw
  key events. Best for simple, one-off shortcuts.
- **Keymap** (this file): declarative layered bindings, commands, sequences,
  leader keys, and counts. Best for editor-style keymaps and larger apps.
