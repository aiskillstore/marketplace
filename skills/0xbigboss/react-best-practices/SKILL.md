---
name: react-best-practices
description: Use when reading or writing React components (.tsx, .jsx files with React imports).
---

# React Best Practices

## Pair with TypeScript

When working with React, always load both this skill and `typescript-best-practices` together. TypeScript patterns (type-first development, discriminated unions, Zod validation) apply to React code.

## Core Principle: Effects Are Escape Hatches

Effects let you "step outside" React to synchronize with external systems. **Most component logic should NOT use Effects.** Before writing an Effect, ask: "Is there a way to do this without an Effect?"

## Decision Tree

1. **Need to respond to user interaction?** Use event handler
2. **Need computed value from props/state?** Calculate during render
3. **Need cached expensive calculation?** Use `useMemo`
4. **Need to reset state on prop change?** Use `key` prop
5. **Need to synchronize with external system?** Use Effect with cleanup
6. **Need non-reactive code in Effect?** Use `useEffectEvent`
7. **Need mutable value that doesn't trigger render?** Use ref

## When to Use Effects

Synchronizing with **external systems**: browser APIs (WebSocket, IntersectionObserver), third-party non-React libraries, window/document event listeners, non-React DOM elements (video, maps).

## When NOT to Use Effects

- Derived state — calculate during render
- Expensive calculations — use `useMemo`
- Resetting state on prop change — use `key` prop
- Responding to user events — use event handlers
- Notifying parent of state changes — update both in the same event handler
- Chains of effects — calculate derived state and update in one event handler

## Refs

- Use for values that don't affect rendering (timer IDs, DOM node references)
- Never read or write `ref.current` during render; only in event handlers and effects
- Use ref callbacks (not `useRef` in loops) for dynamic lists
- Use `useImperativeHandle` to limit what parent can access

## Custom Hooks

- Share logic, not state — each call gets an independent state instance
- Name `useXxx` only if it actually calls other hooks; otherwise use a regular function
- Avoid lifecycle hooks (`useMount`, `useEffectOnce`) — use `useEffect` directly so the linter catches missing deps
- Keep focused on a single concrete use case

## Component Patterns

- Controlled: parent owns state; uncontrolled: component owns state
- Prefer composition with `children` over prop drilling
- Treat boolean props that switch large component trees (`isEditing`, `isThread`, `hideAttachments`) as a composition smell; prefer separate composed components for distinct use cases
- For complex reusable UI, prefer compound components with provider-scoped state/actions over monolithic components with many optional props
- Use Context for scoped component families as well as truly global state, when it defines a local interface consumed by descendants
- Render JSX directly for UI variation; avoid config-array mini-frameworks unless the config is real domain data
- Lift the provider boundary when sibling or external controls need access to the same state/actions
- Use `flushSync` when you need to read the DOM synchronously after a state update

See `react-patterns.md` for code examples and detailed patterns.
