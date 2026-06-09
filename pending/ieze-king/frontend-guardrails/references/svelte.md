# Svelte / SvelteKit implementation

How the universal principles map to Svelte. Read after detecting a Svelte or SvelteKit project.

## Reusability and components
- Extract repeated markup into `.svelte` components; extract repeated logic into plain JS/TS modules or custom stores.
- One component per file, PascalCase names. Keep components focused and small.
- Co-locate a component with its styles (scoped `<style>` block) — Svelte scopes styles by default, so no extra tooling needed.

## Separation of concerns
- Presentational components take props and dispatch events; data fetching and shared logic live in stores or a dedicated API module, not inline in component `<script>` blocks.
- SvelteKit: load data in `+page.server.ts` / `+layout.server.ts` (server) or `+page.ts` / `+layout.ts` (universal) — not directly inside components.

## Design tokens
- Centralize colors, typography, and spacing as CSS custom properties (`:root` variables) in a global stylesheet; reference them throughout, never hardcode raw values per component.
- Svelte's scoped styles can consume global CSS variables — use them as the single source of truth.

## State management
- Local state → reactive `let` variables with `$:` reactive declarations for derived values.
- Shared state → Svelte stores (`writable`, `readable`, `derived` from `svelte/store`). Subscribe with the `$store` auto-subscribe shorthand.
- Avoid creating a store for values that are local to one component — local reactivity handles that.
- Derive values with `$:` or `derived()` instead of duplicating state that falls out of sync.

## Navigation
- SvelteKit: use `<a href="...">` for standard links and `goto()` (from `$app/navigation`) for programmatic navigation. Use `<a>` rather than custom click handlers wherever possible — it's accessible and understood by crawlers.
- Centralize route structure in the `src/routes/` directory convention; avoid scattering navigation logic in components.

## Polish
- SvelteKit: set title, description, and Open Graph meta via `<svelte:head>` in each page component, or globally in `+layout.svelte`.
- Include the viewport meta tag in `app.html`.

## Security specifics
- Svelte auto-escapes interpolated values (`{variable}`) — do **not** bypass this with `{@html}` on untrusted content. If unavoidable, sanitize first (e.g. DOMPurify).
- SvelteKit: environment variables prefixed `PUBLIC_` (via `$env/static/public` or `$env/dynamic/public`) **ship to the browser** — never put secrets there. Server-only secrets go in non-prefixed env vars, accessed only in server-side files (`+page.server.ts`, `+server.ts`, hooks).
- Keep secret-bearing logic in `+page.server.ts` / `+server.ts` / `hooks.server.ts`, never in `+page.svelte` client code.
- Prefer httpOnly cookies for auth tokens over `localStorage` — SvelteKit's `cookies` API in server routes makes this straightforward.

## Correctness gotchas
- Clean up subscriptions and side effects in `onDestroy` (or use the `$` auto-subscribe shorthand which handles cleanup automatically). Manual `subscribe()` calls that aren't unsubscribed cause memory leaks.
- Reactive declarations (`$:`) re-run whenever their dependencies change — keep them free of side effects where possible; use `$: { }` blocks for intentional side-effect reactions.
- Render defensively: guard against `null`/`undefined`/empty data with `{#if}` before it loads; handle loading and error states with `{#await}` or SvelteKit's `+error.svelte`, not just the happy path.
- Stable `:key` values in `{#each}` (use `(item.id)` not index when the list reorders) to prevent DOM reuse bugs.
- SvelteKit form actions: prefer progressive enhancement with `use:enhance` so forms work without JavaScript.
