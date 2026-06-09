# Vue / Nuxt implementation

How the universal principles map to Vue. Read after detecting a Vue or Nuxt project.

## Reusability and components
- Extract repeated template blocks into Single File Components (`.vue`); extract repeated logic into composables (`useX`).
- One component per file, PascalCase names. Keep components focused.

## Separation of concerns
- Presentational components take props and emit events; composables hold logic and data access.
- Data fetching lives in composables or a dedicated API module, not inline in templates.

## Design tokens
- Centralize colors, typography, and spacing as CSS variables or a theme config; reference them, never hardcode raw values per component.
- If using a UI framework (Vuetify, etc.), configure its theme rather than overriding ad hoc.

## State management
- Local state → `ref`/`reactive` in the component. Shared state → Pinia stores.
- Use `computed` to derive values instead of duplicating state.
- Avoid deep prop-drilling — use a store or `provide`/`inject` for genuinely shared values.

## Navigation
- Use Vue Router with centralized route definitions; navigate with `<RouterLink>` / `router.push`, consistently.
- Nuxt: use file-based routing and `<NuxtLink>`.

## Polish
- Nuxt: set title, favicon, and meta via `useHead` / `app.head` config.
- Plain Vue: set them in `index.html` and update title per route via the router.

## Security specifics
- Public runtime config in Nuxt (`runtimeConfig.public`) **ships to the browser** — never put secrets there. Server-only secrets go in `runtimeConfig` (private) and are used only in server routes.
- Avoid `v-html` with untrusted content; sanitize before use.
- Nuxt: keep secret-bearing logic in `server/` routes, never in client components.
- Prefer httpOnly cookies for auth tokens over `localStorage`.

## Correctness gotchas
- Clean up side effects: clear timers, remove listeners, and stop watchers/subscriptions in `onUnmounted` (or via `watchEffect`'s stop handle). Prevents memory leaks.
- Render defensively: guard against `null`/`undefined`/empty data with `v-if`/optional chaining before it loads; handle loading and error states, not just the happy path.
- Stable `:key` values in `v-for` (not index when items reorder).
