# Next.js 15 Metadata API - Complete Guide

Complete reference for SEO, metadata, and Open Graph in Next.js 15.

**Official Docs:** https://nextjs.org/docs/app/building-your-application/optimizing/metadata

---

## Table of Contents

- [Static Metadata](#static-metadata)
- [Dynamic Metadata](#dynamic-metadata)
- [File-Based Metadata](#file-based-metadata)
- [Open Graph](#open-graph)
- [Twitter Cards](#twitter-cards)
- [JSON-LD](#json-ld)
- [Viewport and Icons](#viewport-and-icons)
- [Robots and Sitemap](#robots-and-sitemap)

---

## Static Metadata

Define metadata with exported object.

### Example 1: Basic Page Metadata

```typescript
// app/about/page.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'About Quetrex',
  description: 'Voice-first AI assistant for developers',
}

export default function AboutPage() {
  return <div>About page</div>
}
```

### Example 2: Complete Metadata Object

```typescript
// app/page.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Quetrex - AI Development Platform',
  description: 'Build faster with voice-first AI assistance',
  keywords: ['AI', 'development', 'voice assistant', 'Next.js'],
  authors: [{ name: 'Quetrex Team' }],
  creator: 'Quetrex',
  publisher: 'Quetrex Inc',
  metadataBase: new URL('https://quetrex.dev'),
  alternates: {
    canonical: '/',
  },
}

export default function HomePage() {
  return <div>Home</div>
}
```

### Example 3: Layout Metadata

```typescript
// app/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: {
    template: '%s | Quetrex',
    default: 'Quetrex - AI Development Platform',
  },
  description: 'Voice-first AI assistant for developers',
  metadataBase: new URL('https://quetrex.dev'),
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

---

## Dynamic Metadata

Generate metadata based on route parameters.

### Example 4: Dynamic generateMetadata

```typescript
// app/projects/[id]/page.tsx
import type { Metadata } from 'next'

interface PageProps {
  params: Promise<{ id: string }>
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { id } = await params
  const project = await fetchProject(id)

  return {
    title: project.name,
    description: project.description,
  }
}

export default async function ProjectPage({ params }: PageProps) {
  const { id } = await params
  const project = await fetchProject(id)

  return <ProjectView project={project} />
}
```

### Example 5: Metadata with Parent Data

```typescript
// app/blog/[slug]/page.tsx
import type { Metadata, ResolvingMetadata } from 'next'

export async function generateMetadata(
  { params }: { params: Promise<{ slug: string }> },
  parent: ResolvingMetadata
): Promise<Metadata> {
  const { slug } = await params
  const post = await fetchPost(slug)

  // Access parent metadata
  const previousImages = (await parent).openGraph?.images || []

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      images: [post.coverImage, ...previousImages],
    },
  }
}

export default async function BlogPost({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await fetchPost(slug)

  return <Article post={post} />
}
```

### Example 6: Conditional Metadata

```typescript
// app/projects/[id]/page.tsx
export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id } = await params
  const project = await fetchProject(id)

  const metadata: Metadata = {
    title: project.name,
    description: project.description,
  }

  // Add robots meta for private projects
  if (project.visibility === 'private') {
    metadata.robots = {
      index: false,
      follow: false,
    }
  }

  return metadata
}
```

---

## File-Based Metadata

Use special files for metadata.

### Example 7: favicon.ico

```
app/
├── favicon.ico           # Favicon (16x16, 32x32, or 48x48)
└── page.tsx
```

### Example 8: icon.png/jpg

```
app/
├── icon.png              # App icon (any size)
├── apple-icon.png        # Apple touch icon
└── page.tsx
```

### Example 9: Dynamic Icon Generation

```typescript
// app/icon.tsx
import { ImageResponse } from 'next/og'

export const size = {
  width: 32,
  height: 32,
}

export const contentType = 'image/png'

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 24,
          background: 'black',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
        }}
      >
        S
      </div>
    ),
    {
      ...size,
    }
  )
}
```

### Example 10: opengraph-image.png

```
app/
├── opengraph-image.png   # OG image (1200x630)
└── page.tsx
```

### Example 11: Dynamic OG Image

```typescript
// app/blog/[slug]/opengraph-image.tsx
import { ImageResponse } from 'next/og'

export const alt = 'Blog Post'
export const size = {
  width: 1200,
  height: 630,
}
export const contentType = 'image/png'

export default async function Image({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await fetchPost(slug)

  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 64,
          background: 'linear-gradient(to right, #667eea 0%, #764ba2 100%)',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          padding: '80px',
        }}
      >
        {post.title}
      </div>
    ),
    {
      ...size,
    }
  )
}
```

---

## Open Graph

Configure Open Graph metadata for social sharing.

### Example 12: Basic Open Graph

```typescript
// app/page.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Quetrex - AI Development Platform',
  description: 'Voice-first AI assistant',
  openGraph: {
    title: 'Quetrex - AI Development Platform',
    description: 'Voice-first AI assistant for developers',
    url: 'https://quetrex.dev',
    siteName: 'Quetrex',
    locale: 'en_US',
    type: 'website',
  },
}
```

### Example 13: Open Graph with Images

```typescript
// app/projects/[id]/page.tsx
export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id } = await params
  const project = await fetchProject(id)

  return {
    title: project.name,
    description: project.description,
    openGraph: {
      title: project.name,
      description: project.description,
      url: `https://quetrex.dev/projects/${id}`,
      siteName: 'Quetrex',
      images: [
        {
          url: project.coverImage,
          width: 1200,
          height: 630,
          alt: project.name,
        },
      ],
      locale: 'en_US',
      type: 'article',
      publishedTime: project.createdAt.toISOString(),
      authors: [project.owner.name],
    },
  }
}
```

### Example 14: Article Open Graph

```typescript
// app/blog/[slug]/page.tsx
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const post = await fetchPost(slug)

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      url: `https://quetrex.dev/blog/${slug}`,
      siteName: 'Quetrex Blog',
      images: [
        {
          url: post.coverImage,
          width: 1200,
          height: 630,
        },
      ],
      type: 'article',
      publishedTime: post.publishedAt.toISOString(),
      modifiedTime: post.updatedAt.toISOString(),
      authors: [post.author.name],
      section: post.category,
      tags: post.tags,
    },
  }
}
```

---

## Twitter Cards

Configure Twitter Card metadata.

### Example 15: Summary Card

```typescript
// app/page.tsx
export const metadata: Metadata = {
  title: 'Quetrex',
  description: 'Voice-first AI assistant',
  twitter: {
    card: 'summary',
    title: 'Quetrex - AI Development Platform',
    description: 'Voice-first AI assistant for developers',
    creator: '@quetrex',
    images: ['https://quetrex.dev/og-image.png'],
  },
}
```

### Example 16: Summary Large Image Card

```typescript
// app/blog/[slug]/page.tsx
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const post = await fetchPost(slug)

  return {
    title: post.title,
    description: post.excerpt,
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
      creator: '@quetrex',
      images: [post.coverImage],
    },
  }
}
```

### Example 17: Combined Open Graph and Twitter

```typescript
// app/projects/[id]/page.tsx
export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id } = await params
  const project = await fetchProject(id)

  return {
    title: project.name,
    description: project.description,
    openGraph: {
      title: project.name,
      description: project.description,
      url: `https://quetrex.dev/projects/${id}`,
      images: [
        {
          url: project.coverImage,
          width: 1200,
          height: 630,
        },
      ],
      type: 'article',
    },
    twitter: {
      card: 'summary_large_image',
      title: project.name,
      description: project.description,
      images: [project.coverImage],
      creator: `@${project.owner.username}`,
    },
  }
}
```

---

## JSON-LD

Structured data for search engines.

### Example 18: Organization Schema

```typescript
// app/page.tsx
export const metadata: Metadata = {
  title: 'Quetrex',
  other: {
    'application/ld+json': JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: 'Quetrex',
      url: 'https://quetrex.dev',
      logo: 'https://quetrex.dev/logo.png',
      sameAs: [
        'https://twitter.com/quetrex',
        'https://github.com/quetrex',
      ],
    }),
  },
}
```

### Example 19: Article Schema

```typescript
// app/blog/[slug]/page.tsx
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const post = await fetchPost(slug)

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    description: post.excerpt,
    image: post.coverImage,
    datePublished: post.publishedAt.toISOString(),
    dateModified: post.updatedAt.toISOString(),
    author: {
      '@type': 'Person',
      name: post.author.name,
    },
  }

  return {
    title: post.title,
    description: post.excerpt,
    other: {
      'application/ld+json': JSON.stringify(jsonLd),
    },
  }
}
```

### Example 20: Product Schema

```typescript
// app/products/[id]/page.tsx
export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id } = await params
  const product = await fetchProduct(id)

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description,
    image: product.images,
    offers: {
      '@type': 'Offer',
      price: product.price,
      priceCurrency: 'USD',
      availability: product.inStock
        ? 'https://schema.org/InStock'
        : 'https://schema.org/OutOfStock',
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: product.rating,
      reviewCount: product.reviewCount,
    },
  }

  return {
    title: product.name,
    description: product.description,
    other: {
      'application/ld+json': JSON.stringify(jsonLd),
    },
  }
}
```

---

## Viewport and Icons

Configure viewport and app icons.

### Example 21: Viewport Configuration

```typescript
// app/layout.tsx
import type { Viewport } from 'next'

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#000000' },
  ],
}
```

### Example 22: PWA Manifest

```typescript
// app/manifest.ts
import type { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Quetrex - AI Development Platform',
    short_name: 'Quetrex',
    description: 'Voice-first AI assistant for developers',
    start_url: '/',
    display: 'standalone',
    background_color: '#000000',
    theme_color: '#000000',
    icons: [
      {
        src: '/icon-192.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/icon-512.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  }
}
```

### Example 23: Apple Web App

```typescript
// app/layout.tsx
export const metadata: Metadata = {
  title: 'Quetrex',
  description: 'AI Development Platform',
  appleWebApp: {
    capable: true,
    title: 'Quetrex',
    statusBarStyle: 'black-translucent',
  },
}
```

---

## Robots and Sitemap

Control search engine crawling.

### Example 24: Robots.txt

```typescript
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/admin/', '/api/'],
      },
    ],
    sitemap: 'https://quetrex.dev/sitemap.xml',
  }
}
```

### Example 25: Dynamic Sitemap

```typescript
// app/sitemap.ts
import type { MetadataRoute } from 'next'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await fetchAllPosts()

  const postEntries: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `https://quetrex.dev/blog/${post.slug}`,
    lastModified: post.updatedAt,
    changeFrequency: 'weekly',
    priority: 0.8,
  }))

  return [
    {
      url: 'https://quetrex.dev',
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
    {
      url: 'https://quetrex.dev/about',
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.5,
    },
    ...postEntries,
  ]
}
```

### Example 26: Robots Meta Tag

```typescript
// app/admin/page.tsx
export const metadata: Metadata = {
  title: 'Admin Dashboard',
  robots: {
    index: false,
    follow: false,
    nocache: true,
    googleBot: {
      index: false,
      follow: false,
    },
  },
}
```

---

## Summary

**Metadata Types:**
- Static: Exported `metadata` object
- Dynamic: `generateMetadata()` function
- File-based: Special files (icon.png, opengraph-image.png)

**Key Files:**
- `metadata` - Static metadata export
- `generateMetadata()` - Dynamic metadata function
- `manifest.ts` - PWA manifest
- `robots.ts` - Robots.txt
- `sitemap.ts` - XML sitemap
- `icon.png` - App icon
- `opengraph-image.png` - OG image

**Best Practices:**
1. Use title templates in root layout
2. Set metadataBase for absolute URLs
3. Generate dynamic OG images
4. Include JSON-LD for rich results
5. Configure viewport properly
6. Use proper Open Graph types
7. Add Twitter Card metadata
8. Create dynamic sitemaps
9. Control robots correctly
10. Test with social media debuggers

**Official Docs:**
- Metadata API: https://nextjs.org/docs/app/api-reference/functions/generate-metadata
- File-based Metadata: https://nextjs.org/docs/app/api-reference/file-conventions/metadata
- Manifest: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/manifest
