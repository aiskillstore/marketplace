---
name: nextjs-optimization
description: Optimize Next.js 15 applications for performance, Core Web Vitals, and production best practices using App Router patterns
version: 1.0.0
author: AI-Vibe-Prompts
tags: [nextjs, performance, optimization, react, app-router]
framework: nextjs
auto_invoke: true
---

# Next.js 15 Optimization Skill

## Objective

Optimize Next.js applications to achieve:
- Perfect Core Web Vitals scores (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- Fast page load times and optimal rendering strategies
- Efficient data fetching and caching
- Production-ready build configuration
- SEO and accessibility excellence

## When to Use This Skill

Auto-invoke when:
- Project uses Next.js (detected by `next` in dependencies)
- User mentions "optimize", "performance", "slow", or "Core Web Vitals"
- Before production deployment
- After adding new features or pages
- User requests Next.js-specific improvements

## Prerequisites Check

**Tools**: Read, Grep

1. **Verify Next.js version**:
   ```bash
   # Read package.json
   # Check for "next": "^15.0.0" or higher
   ```

2. **Detect App Router** (Next.js 13+):
   - Check for `app/` directory
   - Check for `layout.tsx`, `page.tsx` files

3. **Detect Pages Router** (Legacy):
   - Check for `pages/` directory
   - Suggest migration to App Router

## Optimization Categories

### 1. Rendering Strategy Optimization

**Goal**: Choose optimal rendering for each page/component

**Tools**: Read, Grep, Edit

#### 1.1 Server Components (Default in App Router)

**When to use**: 
- Data fetching from APIs/databases
- Heavy computation
- Access to backend resources

**Pattern**:
```typescript
// app/dashboard/page.tsx
export default async function DashboardPage() {
  const data = await fetchData(); // Runs on server
  return <Dashboard data={data} />;
}
```

**Check for violations**:
```bash
# Search for "use client" in components that don't need it
grep -r "use client" app/ | grep -v "onClick\|useState\|useEffect"
```

#### 1.2 Client Components

**When to use**:
- Interactive UI (onClick, forms)
- Browser APIs (window, localStorage)
- React hooks (useState, useEffect)

**Pattern**:
```typescript
// app/components/Counter.tsx
'use client';

export default function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

**Optimization**: Keep client components small and leaf nodes

#### 1.3 Static Generation (SSG)

**When to use**: 
- Content that rarely changes
- Marketing pages, blogs, documentation

**Pattern**:
```typescript
export const revalidate = 3600; // Revalidate every hour

export default async function BlogPost({ params }) {
  const post = await getPost(params.slug);
  return <Article post={post} />;
}
```

#### 1.4 Dynamic Rendering with ISR

**When to use**:
- Content that changes periodically
- E-commerce products, user profiles

**Pattern**:
```typescript
export const revalidate = 60; // Revalidate every minute

export async function generateStaticParams() {
  const products = await getProducts();
  return products.map((p) => ({ slug: p.slug }));
}
```

### 2. Image Optimization

**Goal**: Optimize images for performance and Core Web Vitals

**Tools**: Grep, Read, Edit

#### 2.1 Use Next.js Image Component

**Find unoptimized images**:
```bash
grep -rn "<img " app/ src/
```

**Replace with**:
```typescript
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  priority // For above-the-fold images
  placeholder="blur" // Optional blur-up effect
/>
```

#### 2.2 Configure Image Domains

**Read next.config.js**:
```javascript
module.exports = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'example.com',
      },
    ],
    formats: ['image/avif', 'image/webp'], // Modern formats
  },
};
```

#### 2.3 Lazy Loading Strategy

- **priority**: Above-the-fold images (LCP candidates)
- **loading="lazy"**: Below-the-fold images (default)

### 3. Font Optimization

**Goal**: Eliminate FOUT/FOIT and improve font loading

**Tools**: Read, Edit

#### 3.1 Use next/font

**Pattern**:
```typescript
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap', // Prevent FOIT
  variable: '--font-inter',
});

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
```

#### 3.2 Self-Hosted Fonts

```typescript
import localFont from 'next/font/local';

const customFont = localFont({
  src: './fonts/CustomFont.woff2',
  display: 'swap',
  variable: '--font-custom',
});
```

### 4. Data Fetching Optimization

**Goal**: Minimize waterfalls and optimize cache

**Tools**: Read, Grep, Edit

#### 4.1 Parallel Data Fetching

**Anti-pattern** (Sequential):
```typescript
const user = await getUser();
const posts = await getPosts(user.id); // Waits for user
```

**Optimized** (Parallel):
```typescript
const [user, posts] = await Promise.all([
  getUser(),
  getPosts(),
]);
```

#### 4.2 Streaming with Suspense

**Pattern**:
```typescript
import { Suspense } from 'react';

export default function Page() {
  return (
    <>
      <Header />
      <Suspense fallback={<Skeleton />}>
        <SlowComponent />
      </Suspense>
      <Footer />
    </>
  );
}
```

#### 4.3 Cache Configuration

```typescript
// Aggressive caching
fetch('https://api.example.com/data', {
  next: { revalidate: 3600 }, // Cache for 1 hour
});

// No caching
fetch('https://api.example.com/data', {
  cache: 'no-store', // Always fresh
});

// Opt out of caching
export const dynamic = 'force-dynamic';
```

### 5. Bundle Optimization

**Goal**: Reduce JavaScript bundle size

**Tools**: Bash, Read, Edit

#### 5.1 Analyze Bundle

```bash
# Add to package.json scripts
npm run build
npx @next/bundle-analyzer
```

#### 5.2 Dynamic Imports

**Find large components**:
```bash
find app -name "*.tsx" -exec wc -l {} \; | sort -rn | head -10
```

**Split with dynamic imports**:
```typescript
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Skeleton />,
  ssr: false, // Skip SSR if not needed
});
```

#### 5.3 Tree Shaking

**Check for barrel exports**:
```bash
grep -rn "export \* from" app/
```

**Replace with specific imports**:
```typescript
// Anti-pattern
import { Button, Card, Modal } from '@/components';

// Optimized
import { Button } from '@/components/Button';
```

### 6. Metadata & SEO

**Goal**: Perfect SEO and social sharing

**Tools**: Read, Edit

#### 6.1 Static Metadata

```typescript
// app/layout.tsx
export const metadata = {
  title: {
    default: 'My App',
    template: '%s | My App',
  },
  description: 'Description for SEO',
  openGraph: {
    title: 'My App',
    description: 'Description for social sharing',
    images: ['/og-image.jpg'],
  },
  twitter: {
    card: 'summary_large_image',
  },
};
```

#### 6.2 Dynamic Metadata

```typescript
export async function generateMetadata({ params }) {
  const post = await getPost(params.slug);
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      images: [post.ogImage],
    },
  };
}
```

### 7. Production Configuration

**Goal**: Optimize next.config.js for production

**Tools**: Read, Edit

#### 7.1 Essential Config

```javascript
// next.config.js
module.exports = {
  reactStrictMode: true,
  poweredByHeader: false, // Security
  compress: true, // Gzip compression
  
  // Compiler optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // Image optimization
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
  },
  
  // React Compiler (Next.js 15)
  experimental: {
    reactCompiler: true,
  },
};
```

#### 7.2 Turbopack (Development)

```json
// package.json
{
  "scripts": {
    "dev": "next dev --turbo"
  }
}
```

### 8. Core Web Vitals Optimization

**Goal**: Achieve perfect Lighthouse scores

**Tools**: Bash, Grep, Edit

#### 8.1 LCP (Largest Contentful Paint) < 2.5s

**Optimize**:
- Use `priority` on hero images
- Preload critical resources
- Server-side render above-the-fold content

```typescript
// Preload critical resources
<link rel="preload" href="/hero.jpg" as="image" />
```

#### 8.2 FID (First Input Delay) < 100ms

**Optimize**:
- Minimize JavaScript execution
- Use dynamic imports for non-critical code
- Defer third-party scripts

```typescript
import Script from 'next/script';

<Script
  src="https://analytics.example.com"
  strategy="lazyOnload" // Load after page interactive
/>
```

#### 8.3 CLS (Cumulative Layout Shift) < 0.1

**Optimize**:
- Always specify image dimensions
- Reserve space for dynamic content
- Use `font-display: swap`

```css
/* Reserve space for ads/banners */
.ad-container {
  min-height: 250px;
}
```

### 9. Caching Strategy

**Goal**: Maximize cache hits and minimize server load

**Tools**: Read, Edit

#### 9.1 Route Segment Config

```typescript
// app/dashboard/page.tsx
export const revalidate = 3600; // ISR every hour
export const dynamic = 'auto'; // Automatic optimization
export const fetchCache = 'force-cache'; // Aggressive caching
```

#### 9.2 Data Cache

```typescript
// Deduplicated and cached automatically
const user = await fetch('https://api.example.com/user');

// Revalidate tag-based
export const revalidate = 60;
export const tags = ['user', 'profile'];
```

### 10. Monitoring & Measurement

**Goal**: Track performance over time

**Tools**: Bash, WebSearch

#### 10.1 Add Web Vitals Reporting

```typescript
// app/layout.tsx
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <SpeedInsights />
      </body>
    </html>
  );
}
```

#### 10.2 Lighthouse CI

```bash
# Run Lighthouse
npx lighthouse http://localhost:3000 --view

# Check Core Web Vitals
npm run build
npm run start
npx lighthouse http://localhost:3000 --only-categories=performance
```

## Optimization Checklist

**Run through this checklist**:

- [ ] All images use `next/image` with proper dimensions
- [ ] Fonts use `next/font` with `display: swap`
- [ ] Server Components used by default (no unnecessary 'use client')
- [ ] Client Components are leaf nodes and minimal
- [ ] Data fetching uses parallel requests where possible
- [ ] Slow components wrapped in `<Suspense>`
- [ ] Large components use dynamic imports
- [ ] Metadata configured for all pages
- [ ] `next.config.js` has production optimizations
- [ ] React Compiler enabled (Next.js 15)
- [ ] Bundle analyzed and optimized
- [ ] Core Web Vitals meet targets (test with Lighthouse)

## Output Format

```markdown
# Next.js Optimization Report

## Current Status
- **Next.js Version**: 15.0.3
- **Rendering**: App Router
- **React Version**: 19.0.0

## Issues Found

### 🔴 Critical (3)
1. **Unoptimized Images**: 12 `<img>` tags found
   - Files: `app/page.tsx`, `app/about/page.tsx`
   - Fix: Replace with `next/image`

2. **Large Client Bundle**: 342 KB (target: < 200 KB)
   - Cause: Heavy chart library loaded synchronously
   - Fix: Use dynamic import for `Chart` component

3. **Missing Font Optimization**: Using Google Fonts via <link>
   - Fix: Migrate to `next/font/google`

### 🟡 Warnings (2)
1. **Sequential Data Fetching**: Waterfall detected in `app/dashboard/page.tsx`
2. **No Metadata**: Missing OpenGraph tags on 5 pages

## Optimizations Applied

✅ Enabled React Compiler in next.config.js
✅ Added image optimization config
✅ Configured proper cache headers
✅ Added Suspense boundaries to slow routes

## Performance Impact (Estimated)

- **Load Time**: 3.2s → 1.8s (-44%)
- **Bundle Size**: 342 KB → 198 KB (-42%)
- **LCP**: 3.1s → 2.3s (✅ Good)
- **FID**: 85ms → 45ms (✅ Good)
- **CLS**: 0.15 → 0.05 (✅ Good)

## Next Steps

1. Replace 12 `<img>` tags with `next/image`
2. Split Chart component with dynamic import
3. Add metadata to 5 pages
4. Run Lighthouse to verify improvements
```

## Best Practices

1. **Server-First Mindset**: Default to Server Components
2. **Progressive Enhancement**: Build for slow networks first
3. **Measure, Don't Guess**: Use Lighthouse and Web Vitals
4. **Cache Aggressively**: But revalidate appropriately
5. **Optimize Incrementally**: Fix critical issues first

## Integration with Other Skills

- `codebase-analysis` - Detect Next.js project and version
- `quality-gates` - Run build and verify no regressions
- `react-patterns` - Ensure React 19 best practices
- `testing-strategy` - Add performance tests

## Common Anti-Patterns to Avoid

❌ Using 'use client' at the top level
❌ Not specifying image dimensions
❌ Synchronous data fetching
❌ Loading entire component libraries
❌ No Suspense boundaries
❌ Ignoring Core Web Vitals

## Version History

- **1.0.0** (2025-01-03): Initial skill for Next.js 15 with App Router focus
