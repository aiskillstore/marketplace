# Setup troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Components render, but with no colours, borders or spacing | Tailwind never scanned the classes inside `@wunderui/react/dist` | The `@source` path in the CSS entry is relative to the CSS file. Re-run `setup.mjs styles`, or fix the path by hand. |
| Colours are the project's, not WunderUI's (or the other way round) | Both define `--primary`, `--background` … and the later block wins | Put the project's `:root` overrides after `@import "@wunderui/react/styles.css"` to keep them; remove them to use WunderUI's. |
| `@import "@wunderui/react/styles.css"` fails to resolve | The package is not installed, or it was installed from a checkout that was never built | `npm run build` in the checkout, then reinstall it. |
| Dark mode does nothing | WunderUI's dark theme is the `.dark` class on `<html>`, not the media query | Use `ThemeProvider` from `@wunderui/react` (Next.js), or toggle the class yourself. |
| Error about hooks or `createContext` in a Server Component | The component is used where only server code runs | The package ships a `"use client"` banner; import it in a client component or a page that renders on the client. |
| `cn` is not exported | It never was | `npm install cn` and import it from `cn`. |
| MCP tools do not show up | Servers load when the agent starts | Restart Claude Code / the editor. With a local checkout, run `npm install` in it once. |
| Tailwind v3 project | WunderUI needs v4 (`@theme`, `@utility`) | `npx @tailwindcss/upgrade`, then run setup again. |
