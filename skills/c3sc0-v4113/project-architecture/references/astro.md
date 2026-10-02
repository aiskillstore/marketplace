# Astro boundaries

- `.astro` components render on the server and ship no JavaScript by default. Prefer them for static and data-display UI.
- Use a React island only when interaction requires it, and hydrate it with the least eager directive that works: `client:visible` or `client:idle` before `client:load`; `client:only` only when server rendering is impossible.
- Keep islands small; pass serializable props from the `.astro` parent.
- Read the current Astro documentation for the installed version before changing framework APIs, routing, or content collections.
- When `.agents/skills/` contains an Astro skill, load it for framework work.
