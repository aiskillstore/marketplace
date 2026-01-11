# Data Fetching Patterns

## Extended fetch API

Next.js extends the native fetch API with caching and revalidation options.

### Caching Strategies

```tsx
// Static data - cached indefinitely (default)
const res = await fetch('https://api.example.com/posts', {
  cache: 'force-cache' // Default
})

// Revalidate every 60 seconds (ISR)
const res = await fetch('https://api.example.com/posts', {
  next: { revalidate: 60 }
})

// Always fresh - no caching
const res = await fetch('https://api.example.com/posts', {
  cache: 'no-store'
})

// Tag-based revalidation
const res = await fetch('https://api.example.com/posts', {
  next: { tags: ['posts'] }
})
```

### Revalidation Methods

```tsx
// app/actions.ts
'use server'

import { revalidatePath, revalidateTag } from 'next/cache'

export async function createPost(formData: FormData) {
  // ... create post logic

  // Revalidate specific path
  revalidatePath('/posts')

  // Revalidate all data with 'posts' tag
  revalidateTag('posts')
}
```

---

## Parallel Data Fetching

Fetch multiple resources simultaneously:

```tsx
export default async function UserPage({ params }: { params: { id: string } }) {
  // Fetch in parallel
  const [user, posts, comments] = await Promise.all([
    getUser(params.id),
    getUserPosts(params.id),
    getUserComments(params.id),
  ])

  return (
    <div>
      <UserProfile user={user} />
      <UserPosts posts={posts} />
      <UserComments comments={comments} />
    </div>
  )
}
```

---

## Sequential Data Fetching

When data depends on previous results:

```tsx
export default async function ArtistPage({ params }: { params: { id: string } }) {
  const artist = await getArtist(params.id)

  // This DEPENDS on artist data
  const albums = await getArtistAlbums(artist.id, artist.region)

  return (
    <div>
      <ArtistProfile artist={artist} />
      <AlbumList albums={albums} />
    </div>
  )
}
```

---

## Route Segment Config

Control caching and rendering behavior:

```tsx
// app/blog/[slug]/page.tsx

// Force static rendering (SSG)
export const dynamic = 'force-static'

// Force dynamic rendering (SSR)
export const dynamic = 'force-dynamic'

// Revalidate every hour
export const revalidate = 3600

// Generate static params at build time
export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.map((post) => ({
    slug: post.slug,
  }))
}
```

---

## Database Queries

Direct database access in Server Components:

```tsx
import { db } from '@/lib/prisma'

export default async function ProductsPage() {
  const products = await db.product.findMany({
    where: { published: true },
    include: {
      category: true,
      reviews: {
        take: 5,
        orderBy: { createdAt: 'desc' }
      }
    }
  })

  return <ProductList products={products} />
}
```

---

## Error Handling

Handle fetch errors in Server Components:

```tsx
export default async function PostsPage() {
  let posts

  try {
    posts = await fetch('https://api.example.com/posts').then(res => {
      if (!res.ok) throw new Error('Failed to fetch')
      return res.json()
    })
  } catch (error) {
    return <ErrorMessage message="Failed to load posts" />
  }

  return <PostList posts={posts} />
}
```
