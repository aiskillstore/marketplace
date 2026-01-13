# SEO Reference

## Files
- **Sitemap**: `src/app/sitemap.ts`
- **Robots**: `src/app/robots.ts`
- **Metadata**: `layout.tsx` & `page.tsx`

## Snippets

### Generate Metadata
```typescript
import { Metadata } from "next";

export async function generateMetadata({ params }): Promise<Metadata> {
  const data = await fetchData(params.id);
  return {
    title: data.title,
    description: data.description,
    openGraph: {
      title: data.title,
      description: data.description,
      images: [data.image],
    },
  };
}
```

### JSON-LD (Next-SEO)
```tsx
import { ArticleJsonLd } from "next-seo";

<ArticleJsonLd
  useAppDir
  url="https://example.com/article"
  title="Article Title"
  images={["https://example.com/image.jpg"]}
  datePublished="2024-01-01"
  authorName="Author Name"
  description="Description..."
/>
```

### JSON-LD (Raw Script)
```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Product',
      name: 'Product Name'
    })
  }}
/>
```

### ISR Configuration
```typescript
// In page.tsx
export const revalidate = 60; // 60 seconds
export const dynamic = 'force-static'; // Optional: strict static
```

### Sitemap Item Interface
```typescript
{
  url: string;
  lastModified?: string | Date;
  changeFrequency?: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
  priority?: number; // 0.0 to 1.0
}
```
