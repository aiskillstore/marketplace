---
name: neural-ui
description: Build and migrate Angular applications with Neural UI v2 using verified public APIs, Signal Forms, controlled state, themes and accessible standalone components. Use for @neural-ui/core v2 implementation or debugging; excludes Neural UI v1 APIs and Neural Native.
license: MIT
compatibility: Angular 22 and @neural-ui/core 2.0.1. Portable Agent Skills instructions for Codex, Claude Code and compatible agents. No MCP or paid AI service required by this skill.
metadata:
  author: PedroMorenoTrujillo
  version: "0.1.0"
  neural-ui-version: "2.0.1"
---

# Neural UI v2

Implement against the installed package's public contracts. This skill's verified baseline is **@neural-ui/core 2.0.1 with Angular 22**. Read package.json and the lockfile first. If versions differ, inspect the installed exports and declarations and report the gap; do not silently apply another version's API or change dependencies without task authorization.

## Working rules

1. Identify the component and state owner before writing a binding. Load the relevant reference below and only the required [API entrypoint](references/api/index.md). For long API files, search the exact symbol heading and read the relevant sections instead of loading the entire file.
2. Verify the exact export, selector, input, output and payload in that entrypoint. The published declarations and package exports take precedence over documentation or remembered examples. A physically exported internal entrypoint is not a supported consumer API.
3. Never invent components, aliases, models, events, CSS tokens or providers. Never deep-import implementation files, use internal entrypoints, or bypass errors with schemas, casts to any, forced peers or disabled template checking. When the contract cannot support a request, explain the gap and use application-owned Angular/HTML logic where appropriate.
4. Prefer standalone components, signals, explicit types and OnPush. Import each Neural component from its public secondary entrypoint; root exports are configuration and shared types. Import FormField from Angular forms/signals, not Neural form-field.
5. Distinguish editable models from proposals and lifecycle notifications. Accept proposals by updating the same application signal supplied as input; read the actual payload instead of assuming every Change event is a value. Do not use two-way binding unless that pair is documented.
6. Compile the consuming Angular application and exercise the affected interaction. Report compilation, browser integration and agent behavior testing separately. Do not claim an agent integration test from static checks alone.

## Load only what the task needs

| Task | Reference | Compiled example |
| --- | --- | --- |
| Install, global styles, peers, icons | [Installation](references/installation.md) | — |
| Choose a component or import | [Components](references/components.md), then [API index](references/api/index.md) | — |
| Forms and Signal Forms | [Forms](references/forms.md) | [forms.ts](examples/forms.ts) |
| Controlled state, tables, navigation, overlays | [State ownership](references/state.md) | [table.ts](examples/table.ts), [navigation.ts](examples/navigation.ts), [overlays.ts](examples/overlays.ts) |
| Themes, presets and tokens | [Theming](references/theming.md) | [theme.ts](examples/theme.ts) |
| Layouts and accessibility | [Layout and accessibility](references/layout-accessibility.md) | — |
| SSR, hydration and deterministic state | [SSR](references/ssr.md) | — |
| Upgrade existing v1 application | [Migration](references/migration.md) | — |
| A later Neural release or stale example | [Version maintenance](references/versioning.md) | — |

Examples are complete standalone components, imported directly by the repository's strict Angular SSR integration fixture. Copy only the relevant example and adapt its domain model. They illustrate supported contracts, not a replacement for checking the user's installed version.
