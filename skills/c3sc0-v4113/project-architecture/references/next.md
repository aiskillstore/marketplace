# Next.js boundaries

- Components are Server Components by default. Add `'use client'` only to the smallest leaf that needs state, effects, event handlers, or browser APIs.
- Fetch data in Server Components or route handlers, not in client effects, unless the data is user-interactive.
- Pass serializable props across the server/client boundary; never pass functions or class instances.
- Read the docs bundled with the installed version in `node_modules/next/dist/docs/` before using or changing framework APIs; they match the version the project actually runs.
- When `.agents/skills/` contains Next.js workflow skills (for example Cache Components or dev-loop skills), load them for that work.
- Provide `loading.tsx`, `error.tsx`, and `not-found.tsx` where a route segment needs those states.
