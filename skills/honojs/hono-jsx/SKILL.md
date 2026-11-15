---
name: hono-jsx
description: Use when building UI for a Hono app with hono/jsx — pages, layouts, forms, and interactive parts — server-rendered with jsxRenderer, developed and built with Vite, with client components via hono/jsx/dom. TRIGGER when tsconfig has jsxImportSource "hono/jsx", code imports 'hono/jsx', 'hono/jsx/dom', 'hono/jsx-renderer' or 'vite-ssr-components', or the user asks for a page, screen, layout, or form in a Hono project. Never reach for React.
---

# Hono JSX Skill

Build UI with `hono/jsx`: server-rendered HTML first, a small amount of client-side JSX only where the browser needs state. The `hono` skill covers the JSX syntax and `c.html()`; this skill covers how to structure the app. Cloudflare Workers with Vite is the default setup; see "Other runtimes" for the rest.

## No React

`hono/jsx` is the JSX runtime. Do not bring React in:

- Do not install `react`, `react-dom`, `@types/react`, or `@vitejs/plugin-react`. Do not import from `react`.
- `tsconfig.json` has `"jsx": "react-jsx"` and `"jsxImportSource": "hono/jsx"`. The `react-jsx` value is the transform name, not a React dependency.
- Server components are plain functions rendered once per request. No hooks, no state, no event handlers on the server. Need data: make the component `async` and `await`. Need interactivity: a client component with `hono/jsx/dom`, for that part only.
- Write `class`, not `className`.
- `vite-ssr-components` exports both flavors: import from `vite-ssr-components/hono`, never from `/react`.

## Project Layout (Cloudflare Workers + Vite)

Start from what `create-hono` generates with the `cloudflare-workers` template (`npm create hono@next`, or `npx hono init --template cloudflare-workers` in an existing directory): `src/index.ts` with a text response, `cloudflare.config.ts` for the `cf` CLI, and a `vite.config.ts` with only `cloudflare()`. It has no JSX setup; add the pieces below, and match this layout in existing projects instead of inventing a different structure. Verify routes with the Hono CLI from the `hono` skill (`npx hono request /`); it is a dev dependency of the template and runs the app through Vite, so `c.env` has the local bindings automatically.

```
src/
  index.tsx      # Hono app, routes (renamed from index.ts)
  renderer.tsx   # jsxRenderer layout: <html>, <head>, Vite assets
  client.ts      # optional: browser-side code
  style.css
public/          # static files served as-is
cloudflare.config.ts   # cf CLI: worker name, entrypoint, bindings
vite.config.ts
```

```jsonc
// package.json (scripts, from the template)
{
  "dev": "cf dev",
  "build": "cf build",
  "deploy": "cf deploy",
  "typecheck": "cf workers types && tsc"
}
```

On top of the template:

1. Rename `src/index.ts` to `src/index.tsx` and point the entrypoint import in `cloudflare.config.ts` at it:

   ```ts
   import * as entrypoint from './src/index.tsx' with { type: 'cf-worker' }
   ```

2. Install `vite-ssr-components` as a dev dependency and add its plugin:

   ```ts
   // vite.config.ts
   import { cloudflare } from '@cloudflare/vite-plugin'
   import { defineConfig } from 'vite'
   import ssrPlugin from 'vite-ssr-components/plugin'

   export default defineConfig({
     plugins: [cloudflare(), ssrPlugin()],
   })
   ```

3. Add `src/renderer.tsx`, `src/style.css`, and `public/`:

```tsx
// src/renderer.tsx
import { jsxRenderer } from 'hono/jsx-renderer'
import { Link, Script, ViteClient } from 'vite-ssr-components/hono'

export const renderer = jsxRenderer(({ children }) => {
  return (
    <html>
      <head>
        <ViteClient />
        <Link href="/src/style.css" rel="stylesheet" />
        <Script src="/src/client.ts" />
      </head>
      <body>{children}</body>
    </html>
  )
})
```

```tsx
// src/index.tsx
import { Hono } from 'hono'
import { renderer } from './renderer'

const app = new Hono<{ Bindings: Env }>()

app.use(renderer)

app.get('/', (c) => {
  return c.render(<h1>Hello!</h1>)
})

export default app
```

`vite-ssr-components` does the Vite plumbing: `<ViteClient />` injects the Vite client and SSR hot reload in dev and renders nothing in production; `<Script>` and `<Link>` point at source files and are rewritten to the hashed build output via the manifest. The plugin scans for them and adds each referenced file as a build entry, so there is no `rollupOptions.input` to maintain. Keep `<Script>` and `<Link>` as the component names, or configure the plugin's `components` option.

`npm run dev` (`cf dev`) is for humans; verify with the Hono CLI instead. Bindings are declared in `cloudflare.config.ts`, and their `Env` type comes from `npm run typecheck`; never hand-write it. In an existing wrangler project, keep wrangler, `npm run cf-typegen`, and `CloudflareBindings` as described in the `hono` skill.

## Layouts and Pages

`jsxRenderer` sets the layout; handlers call `c.render()` with the page content.

- **Per-page head content**: write `<title>`, `<meta>`, and `<link>` inside the page component. They are hoisted into `<head>`. Existing head elements stay, so keep the layout's `<title>` out if pages set their own.
- **Props to the layout** (a title, a current-nav key): extend `ContextRenderer` once, then pass the props as the second argument of `c.render()`.

```tsx
declare module 'hono' {
  interface ContextRenderer {
    (content: string | Promise<string>, props: { title: string }): Response
  }
}

export const renderer = jsxRenderer(({ children, title }) => (
  <html>
    <head>
      <title>{title}</title>
    </head>
    <body>{children}</body>
  </html>
))

app.get('/about', (c) => c.render(<About />, { title: 'About' }))
```

- **Nested layouts**: a sub-app can register its own `jsxRenderer` and receive the parent as `Layout`.

```tsx
const blog = new Hono()
blog.use(
  jsxRenderer(({ children, Layout }) => (
    <Layout>
      <nav>Blog</nav>
      {children}
    </Layout>
  ))
)
app.route('/blog', blog)
```

- **Request data inside components**: `useRequestContext()` from `hono/jsx-renderer` returns `c`, so a deep component can read `c.req`, `c.env`, or `c.var` without prop drilling. Prefer loading data in the handler and passing props when the data is only needed at one place.

```tsx
import { useRequestContext } from 'hono/jsx-renderer'

const UserMenu = async () => {
  const c = useRequestContext<{ Bindings: Env }>()
  const user = await c.env.KV.get('user')
  return <span>{user}</span>
}
```

- **Shared components**: put reusable pieces in `src/components/`. They are functions taking props; `FC<Props>` and `PropsWithChildren<Props>` from `hono/jsx` type them.

## Forms and Mutations

The default is an HTML form posting to a Hono route and a redirect. No client JavaScript is required, and it works before any script loads.

```tsx
app.get('/todos', async (c) => {
  const todos = await listTodos(c.env)
  return c.render(
    <>
      <form method="post" action="/todos">
        <input name="title" required />
        <button type="submit">Add</button>
      </form>
      <ul>{todos.map((t) => <li>{t.title}</li>)}</ul>
    </>
  )
})

app.post('/todos', async (c) => {
  const body = await c.req.parseBody()
  await addTodo(c.env, String(body.title))
  return c.redirect('/todos')
})
```

Validate with `validator('form', ...)` or a schema validator from the `hono` skill; on failure re-render the page with the error message rather than returning JSON.

## Client-Side Behavior

Most pages need no client JavaScript. When a part does, start with plain DOM code and reach for `hono/jsx/dom` only for UI that holds state and re-renders. Neither involves React.

**Plain script** — the default. Put it in `src/client.ts` and load it from the renderer with `<Script src="/src/client.ts" />`.

```ts
// src/client.ts
/// <reference lib="dom" />
document.querySelector('#menu-toggle')?.addEventListener('click', () => {
  document.querySelector('#menu')?.classList.toggle('open')
})
```

**`hono/jsx/dom`** — for a stateful part such as a counter, a live filter, or a multi-step form. The server renders an empty container; the client renders into it with `render()`. There is no hydration, so that part is empty until the script runs. Keep the page's actual content server-rendered.

```tsx
// src/client.tsx
/// <reference lib="dom" />
import { useState } from 'hono/jsx'
import { render } from 'hono/jsx/dom'

function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}

render(<Counter />, document.getElementById('counter')!)
```

Hooks (`useState`, `useEffect`, `useRef`, ...) have React-compatible signatures and are imported from `hono/jsx`. Calling the server from the client is a `fetch` to a JSON route; `hc` from `hono/client` adds typed calls once there is an API surface worth typing.

**Type-checking client files.** The template's `tsconfig.json` has `lib: ["ESNext"]` and no `DOM`, so `document` fails `tsc`. Put a lib reference at the top of each client file instead of editing `tsconfig.json`:

```ts
/// <reference lib="dom" />
```

Vite does not read `lib`, so this only matters for `tsc`.

## Styling

- A stylesheet at `src/style.css` linked with `<Link href="/src/style.css" rel="stylesheet" />` in the renderer. Vite processes it, so CSS imports and PostCSS work.
- `hono/css` for component-scoped styles: `css` returns a class name, `<Style />` in `<head>` emits the collected rules.

```tsx
import { css, Style } from 'hono/css'

const card = css`
  padding: 1rem;
  &:hover { background: #eee; }
`
// <head><Style /></head> ... <div class={card}>...</div>
```

## Streaming

For a page where one part is slow, keep the shell instant: enable `stream: true` on the renderer and wrap the slow async component in `Suspense`.

```tsx
import { Suspense } from 'hono/jsx/streaming'

export const renderer = jsxRenderer(({ children }) => <html><body>{children}</body></html>, { stream: true })

app.get('/', (c) =>
  c.render(
    <Suspense fallback={<p>Loading...</p>}>
      <SlowList />
    </Suspense>
  )
)
```

`Suspense` and `ErrorBoundary` are marked experimental in the docs. Use them for genuinely slow data, not by default.

## Escaping and Raw HTML

JSX escapes interpolated strings. To insert trusted HTML, use `dangerouslySetInnerHTML={{ __html }}` or `raw()` from `hono/html`. Never pass user input through either.

## Other Runtimes

Without the Cloudflare Vite plugin, use `@hono/vite-dev-server` for dev and `@hono/vite-build/<runtime>` for the build. Client assets are then built in a separate Vite mode and referenced by fixed paths:

```ts
// vite.config.ts
import build from '@hono/vite-build/node' // or /bun, /cloudflare-workers
import devServer from '@hono/vite-dev-server'
import { defineConfig } from 'vite'

export default defineConfig(({ mode }) => {
  if (mode === 'client') {
    return {
      build: { rollupOptions: { input: './src/client.tsx', output: { entryFileNames: 'static/client.js' } } },
    }
  }
  return {
    plugins: [
      // staticRoot is a Node adapter option: it serves dist/static from the built server
      build({ entry: 'src/index.tsx', staticRoot: './dist' }),
      devServer({ entry: 'src/index.tsx' }),
    ],
  }
})
```

```tsx
// renderer: pick the script path by mode
{import.meta.env.PROD ? (
  <script type="module" src="/static/client.js" />
) : (
  <script type="module" src="/src/client.tsx" />
)}
```

Build with `vite build --mode client && vite build`, then run `node dist/index.js` (the Node build bundles `@hono/node-server`, install it as a dependency). `@hono/vite-dev-server` also has adapters (`/cloudflare`, `/node`, `/bun`) when bindings or runtime APIs are needed in dev.

## Documentation

Fetch with `Accept: text/markdown` (see the `hono` skill):

- https://hono.dev/docs/guides/jsx
- https://hono.dev/docs/guides/jsx-dom
- https://hono.dev/docs/middleware/builtin/jsx-renderer
- https://hono.dev/docs/helpers/css
- https://hono.dev/docs/helpers/html
- https://github.com/yusukebe/vite-ssr-components
- https://github.com/honojs/vite-plugins (dev-server, build)

## Checklist

- No React packages; `jsxImportSource` is `hono/jsx`; `class` attributes.
- Layout in `jsxRenderer`, pages via `c.render()`, per-page `<title>` inside the page.
- Forms post to routes and redirect; client JavaScript only where needed, plain DOM first.
- Vite assets go through `vite-ssr-components` (`ViteClient`, `Script`, `Link`), not hand-written `<script>` tags, on Cloudflare.
- Bindings types generated, never hand-written: `Env` from `npm run typecheck` (`cf`), `CloudflareBindings` from `npm run cf-typegen` (wrangler).
