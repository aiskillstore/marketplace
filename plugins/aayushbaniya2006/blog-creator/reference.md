# Blog Creator Reference

## Frontmatter Schema
```typescript
interface BlogFrontmatter {
  title: string;        // H1 and Meta Title
  tags: string[];       // For related posts logic
  featuredImage?: string; // Path starting with /
  createdDate: string;  // YYYY-MM-DD
  description?: string; // Meta description
}
```

## Key Paths
- **Content**: `src/content/blog/`
- **Listing Page**: `src/app/(website-layout)/blog/page.tsx`
- **Detail Page**: `src/app/(website-layout)/blog/[slug]/page.tsx`
- **Logic**: `src/lib/mdx/blogs.ts`

## Snippet: New Post
```markdown
---
title: Post Title
tags: ["news", "update"]
featuredImage: '/assets/images/og.png'
createdDate: '2024-11-26'
description: 'Short description for SEO.'
---

# Header
Content here.
```

