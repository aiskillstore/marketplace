# React / Next.js implementation

How the universal principles map to React. Read after detecting a React or Next.js project.

## Reusability and components
- Extract repeated JSX into components; extract repeated logic into custom hooks (`useX`).
- One component per file, named in PascalCase. Keep components small and focused.
- Co-locate a component with its styles and tests.

## Separation of concerns
- Presentational components render UI from props; container/hook logic handles data and state.
- Data fetching lives in hooks or a dedicated API module — not inline inside presentational JSX.

## Design tokens
- Tailwind: define tokens in `tailwind.config` (theme colors, fontFamily, spacing) and use utility classes; never arbitrary hex like `bg-[#3b82f6]` scattered around.
- CSS variables / CSS-in-JS: centralize in a theme; reference variables, not raw values.

## State management
- Local UI state → `useState`/`useReducer`. Cross-cutting shared state → the project's store (Zustand, Redux Toolkit, Context for low-frequency values).
- Avoid prop-drilling more than ~2 levels — lift to context or store.
- Derive values during render instead of storing duplicates in state.

## Navigation
- Next.js: use the App Router / `next/link`; keep route structure conventional.
- React Router: centralize route definitions; use `<Link>`, not manual history pushes scattered around.

## Polish
- Next.js: set `<title>`, favicon, and meta via the Metadata API (App Router) or `next/head`.
- Plain React (Vite/CRA): set them in `index.html` and update document title per route.

## Security specifics
- Public env vars: anything prefixed `NEXT_PUBLIC_` (Next.js) or `VITE_` (Vite) **ships to the browser** — never put secrets there. Server-only secrets stay unprefixed and are used only in server code (API routes, server components, server actions).
- Avoid `dangerouslySetInnerHTML`; if required, sanitize (e.g. DOMPurify) first.
- Next.js: keep secret-bearing logic in server components / route handlers / server actions, never in client components.
- Prefer httpOnly cookies for auth tokens over `localStorage`.

## Correctness gotchas
- Clean up effects: every subscription, event listener, timer, or observable opened in `useEffect` returns a cleanup function. Don't set state after unmount. Prevents memory leaks and "can't update unmounted component" bugs.
- Render defensively: guard against `null`/`undefined`/empty data before it loads — handle loading and error states, don't only write the happy path. Use optional chaining and sensible fallbacks.
- Stable keys in lists (not array index when the list reorders); correct, exhaustive effect dependencies.
