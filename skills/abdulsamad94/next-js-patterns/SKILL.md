---
name: next-js-patterns
description: Best practices and patterns for Next.js App Router, Server Actions, and Routing in this project.
---

# Next.js Patterns

## App Router
We use the Next.js 15 App Router located in `app/`.

### Pages
- **Location**: `app/[route]/page.tsx`
- **Component**: Default export function.
- **Client vs Server**: Use `"use client"` directive at the top for components requiring state (`useState`, `useEffect`) or browser APIs. otherwise default to Server Components.

### Layouts
- **Location**: `app/layout.tsx` (Root), `app/[route]/layout.tsx` (Nested).
- **Purpose**: Wrappers for pages, holding navigation, fonts, and metadata.

## Navigation
- Use `Link` from `next/link` for internal navigation.
- Use `useRouter` from `next/navigation` for programmatic navigation (inside Client Components).

```tsx
import Link from "next/link";
import { useRouter } from "next/navigation";

// Link
<Link href="/dashboard">Dashboard</Link>

// Router
const router = useRouter();
router.push('/login');
```

## Data Fetching
- **Server Components**: Fetch directly using `await fetch()` or DB calls.
- **Client Components**: Use `useEffect` or SWR/TanStack Query (if added later). Currently using standard `fetch` in `useEffect`.

## Font Optimization
- We use `next/font/google` (e.g., Poppins) in `app/layout.tsx`.
- Variable fonts are passed to `body` className.

## Metadata
- Define `export const metadata: Metadata = { ... }` in `page.tsx` or `layout.tsx` for SEO.
