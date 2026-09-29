---
name: next
description: Next.js renderer for json-render that turns JSON specs into full Next.js applications with routes, layouts, SSR, and metadata. Use when working with @json-render/next, building Next.js apps from JSON specs, or creating AI-generated multi-page applications.
---

# @json-render/next

Next.js renderer that converts JSON specs into full Next.js applications with routes, pages, layouts, metadata, and SSR support.

## Quick Start

```bash
npm install @json-render/core @json-render/react @json-render/next
```

### 1. Define Your Spec

```typescript
// lib/spec.ts
import type { NextAppSpec } from "@json-render/next";

export const spec: NextAppSpec = {
  metadata: {
    title: { default: "My App", template: "%s | My App" },
    description: "A json-render Next.js application",
  },
  layouts: {
    main: {
      root: "shell",
      elements: {
        shell: { type: "Container", props: {}, children: ["nav", "slot"] },
        nav: { type: "NavBar", props: { links: [
          { href: "/", label: "Home" },
          { href: "/about", label: "About" },
        ]}, children: [] },
        slot: { type: "Slot", props: {}, children: [] },
      },
    },
  },
  routes: {
    "/": {
      layout: "main",
      metadata: { title: "Home" },
      page: {
        root: "hero",
        elements: {
          hero: { type: "Card", props: { title: "Welcome" }, children: [] },
        },
      },
    },
    "/about": {
      layout: "main",
      metadata: { title: "About" },
      page: {
        root: "content",
        elements: {
          content: { type: "Card", props: { title: "About Us" }, children: [] },
        },
      },
    },
  },
};
```

### 2. Create the App

```typescript
// lib/app.ts
import { createNextApp } from "@json-render/next/server";
import { spec } from "./spec";

export const { Page, generateMetadata, generateStaticParams } = createNextApp({
  spec,
  loaders: {
    // Server-side data loaders (optional)
    loadPost: async ({ slug }) => {
      const post = await getPost(slug as string);
      return { post };
    },
  },
});
```

### 3. Wire Up Route Files

```tsx
// app/[[...slug]]/page.tsx
export { Page as default, generateMetadata, generateStaticParams } from "@/lib/app";
```

```tsx
// app/[[...slug]]/layout.tsx
import { NextAppProvider } from "@json-render/next";
import { registry, handlers } from "@/lib/registry";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <NextAppProvider registry={registry} handlers={handlers}>
          {children}
        </NextAppProvider>
      </body>
    </html>
  );
}
```

## Key Concepts

### NextAppSpec

The top-level spec defines an entire Next.js application:

- **metadata**: Root-level SEO metadata (title template, description, OpenGraph)
- **layouts**: Reusable layout element trees (each must include a `Slot` component)
- **routes**: Route definitions keyed by URL pattern
- **state**: Global initial state shared across all routes

### Route Patterns

Routes use Next.js URL conventions:

- `"/"` -- home page
- `"/about"` -- static route
- `"/blog/[slug]"` -- dynamic segment
- `"/docs/[...path]"` -- catch-all segment
- `"/settings/[[...path]]"` -- optional catch-all segment

### Layouts

Layouts wrap page content. Every layout MUST include a `Slot` component where page content will be rendered. Layouts are defined once in `spec.layouts` and referenced by routes via the `layout` field.

### Built-in Components

- **Slot**: Placeholder in layouts where page content is rendered
- **Link**: Client-side navigation link (wraps `next/link`)

### Built-in Actions

- **setState**: Update state value. Params: `{ statePath, value }`
- **pushState**: Append to array. Params: `{ statePath, value, clearStatePath? }`
- **removeState**: Remove from array by index. Params: `{ statePath, index }`
- **navigate**: Client-side navigation. Params: `{ href }`

### Data Loaders

Server-side async functions that run in the Server Component before rendering. Results are merged into the page's initial state.

```typescript
createNextApp({
  spec,
  loaders: {
    loadPost: async ({ slug }) => {
      const post = await db.post.findUnique({ where: { slug } });
      return { post };
    },
  },
});
```

### SSR

Pages are server-rendered automatically. The `createNextApp` `Page` component is an async Server Component that:

1. Matches the route from the spec
2. Runs server-side data loaders
3. Generates metadata
4. Passes the resolved spec to the client renderer for hydration

### Entry Points

- `@json-render/next` -- Client components (NextAppProvider, PageRenderer, Link)
- `@json-render/next/server` -- Server utilities (createNextApp, matchRoute, schema)

## API Reference

### Server Exports (`@json-render/next/server`)

- `createNextApp(options)` -- Create Page, generateMetadata, generateStaticParams
- `schema` -- Custom schema for Next.js apps (for AI catalog generation)
- `matchRoute(spec, pathname)` -- Match a URL to a route spec
- `resolveMetadata(spec, route)` -- Resolve metadata for a route
- `slugToPath(slug)` -- Convert catch-all slug array to pathname
- `collectStaticParams(spec)` -- Collect static params for all routes

### Client Exports (`@json-render/next`)

- `NextAppProvider` -- Context provider for registry and handlers
- `PageRenderer` -- Renders a page spec with optional layout
- `NextErrorBoundary` -- Error boundary component
- `NextLoading` -- Loading state component
- `NextNotFound` -- Not-found component
- `Link` -- Built-in navigation component (wraps next/link)
