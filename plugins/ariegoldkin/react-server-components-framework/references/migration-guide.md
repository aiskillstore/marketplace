# Migration Guide

## Pages Router → App Router

### Incremental Adoption

1. Keep existing `pages/` directory
2. Add new routes in `app/` directory
3. Both routers work simultaneously
4. Migrate route by route

---

## Data Fetching Migration

### Before (Pages Router with getServerSideProps)

```tsx
// pages/posts.tsx
export async function getServerSideProps() {
  const posts = await getPosts()
  return { props: { posts } }
}

export default function Posts({ posts }) {
  return <PostList posts={posts} />
}
```

### After (App Router)

```tsx
// app/posts/page.tsx
export default async function Posts() {
  const posts = await getPosts()
  return <PostList posts={posts} />
}
```

---

## Client-Side Rendering → RSC

### Before (CSR with useEffect)

```tsx
'use client'

export default function Posts() {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/posts')
      .then(res => res.json())
      .then(data => {
        setPosts(data)
        setLoading(false)
      })
  }, [])

  if (loading) return <Loading />
  return <PostList posts={posts} />
}
```

### After (RSC)

```tsx
// Server Component - no hooks, just async/await
export default async function Posts() {
  const posts = await fetch('/api/posts').then(res => res.json())
  return <PostList posts={posts} />
}
```

---

## API Routes → Server Actions

### Before (API Route)

```tsx
// pages/api/posts.ts
export default async function handler(req, res) {
  if (req.method === 'POST') {
    const post = await db.post.create({ data: req.body })
    res.json(post)
  }
}

// Client-side call
const response = await fetch('/api/posts', {
  method: 'POST',
  body: JSON.stringify({ title, content })
})
```

### After (Server Action)

```tsx
// app/actions.ts
'use server'

export async function createPost(data: { title: string; content: string }) {
  const post = await db.post.create({ data })
  revalidatePath('/posts')
  return post
}

// Direct call (no fetch needed)
const post = await createPost({ title, content })
```

---

## Layout Migration

### Before (Pages Router)

```tsx
// pages/_app.tsx
export default function App({ Component, pageProps }) {
  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  )
}
```

### After (App Router)

```tsx
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <Layout>{children}</Layout>
      </body>
    </html>
  )
}
```

---

## Metadata Migration

### Before (Pages Router)

```tsx
import Head from 'next/head'

export default function Post({ post }) {
  return (
    <>
      <Head>
        <title>{post.title}</title>
        <meta name="description" content={post.excerpt} />
      </Head>
      <Article post={post} />
    </>
  )
}
```

### After (App Router)

```tsx
import type { Metadata } from 'next'

export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug)

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage],
    },
  }
}
```

---

## Common Migration Pitfalls

1. **Forgetting 'use client'** for interactive components
2. **Trying to use hooks** in Server Components
3. **Not awaiting** async Server Components
4. **Importing Server Components** into Client Components
5. **Missing revalidation** after mutations
