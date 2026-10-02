---
name: react-best-practices
description: Builds and reviews React components, hooks, state, data loading, and rendering performance. Use for React correctness, effect cleanup, slow renders, or unresponsive component interactions. TanStack-specific API work and React Three Fiber scenes have separate workflows.
---

# React correctness and rendering

Inspect the installed React version, framework, data layer, and compiler configuration before choosing APIs. Preserve those choices unless changing them is part of the task.

## Select the relevant path

For a slow interaction, expensive render, long list, or memoization decision, read [rendering performance](references/rendering-performance.md). For ordinary component work, use the guidance below; profiling the whole application is not a prerequisite for a small edit.

## State and effects

- Keep state with the components that own it. Derive values during render rather than synchronizing duplicate state with effects.
- Use stable component definitions and keys that preserve identity across reordering. A component defined inside another component is recreated and can reset state.
- Use effects to synchronize with external systems. Include reactive dependencies and clean up subscriptions, timers, and pending work; restructure unnecessary dependencies instead of hiding them from the linter.
- Handle user actions in event handlers. Use functional updates when the next state depends on the previous state.
- Keep transient values in refs when they do not need to render. Do not replace state needed for controlled input or visible feedback simply to suppress renders.

## Data and delivery

Use the project's framework loaders, server components, or query library when appropriate. If a fetch effect is needed, handle races, cancellation, errors, and loading. Do not introduce a data library solely to avoid one effect.

Start independent requests together when their failure semantics allow it. Avoid parent/child fetch waterfalls. Preserve loading, empty, failure, and stale-data states.

Lazy-load heavy optional UI when it improves initial delivery. Inspect actual chunk output before changing import style; a barrel import is not automatically expensive. Changes to TanStack query keys or mutations should follow the installed TanStack API.

## Version-sensitive features

- React 19 Actions can coordinate async form submission. Use the documented `useActionState` / `useFormStatus` boundaries and provide error handling; an Action does not make arbitrary failures disappear.
- Use `useOptimistic` inside its action/transition context. Treat optimistic UI as provisional and reconcile failed or concurrent writes.
- Client `use()` reads need a stable promise from an appropriate cache/framework; avoid creating a new fetch promise during every render.
- Ref-as-prop is a React 19 capability. Preserve older compatibility requirements.
- React Compiler is a separate build tool, not a consequence of installing React 19. Verify it is configured and covers the measured work before replacing memoization.
- Confirm the installed version/channel supports React view transitions. Do not mix its transition ownership with direct `document.startViewTransition` calls on the same update. Retain reduced-motion behavior and a supported fallback.

## Verify

Exercise the affected interaction and relevant loading/error states. Run the project's applicable lint, typecheck, build, and tests. For performance changes, compare the same interaction before and after using the method in the linked reference.

## References and attribution

- [React documentation](https://react.dev/learn) and [effect guidance](https://react.dev/learn/you-might-not-need-an-effect).
- [React Compiler installation](https://react.dev/learn/react-compiler/installation).
- Adapted in part from [Vercel agent skills](https://github.com/vercel-labs/agent-skills) (MIT), with the former `react-rendering-performance` workflow consolidated into this skill.
