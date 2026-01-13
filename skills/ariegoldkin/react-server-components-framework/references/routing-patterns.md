# Advanced Routing Patterns

## Parallel Routes

Render multiple pages simultaneously in the same layout.

### Folder Structure
```
app/
  @team/
    page.tsx
  @analytics/
    page.tsx
  layout.tsx
  page.tsx
```

### Implementation

```tsx
// app/layout.tsx
export default function Layout({
  children,
  team,
  analytics,
}: {
  children: React.ReactNode
  team: React.ReactNode
  analytics: React.ReactNode
}) {
  return (
    <div>
      <div>{children}</div>
      <div className="grid grid-cols-2 gap-4">
        <div>{team}</div>
        <div>{analytics}</div>
      </div>
    </div>
  )
}
```

---

## Intercepting Routes

Show a modal while keeping the URL, great for modals that deep-link.

### Folder Structure
```
app/
  photos/
    [id]/
      page.tsx
  (..)photos/
    [id]/
      page.tsx
  page.tsx
```

### Implementation

```tsx
// app/(..)photos/[id]/page.tsx (Intercepting route - shows modal)
import { Modal } from '@/components/Modal'
import { getPhoto } from '@/lib/photos'

export default async function PhotoModal({ params }: { params: { id: string } }) {
  const photo = await getPhoto(params.id)

  return (
    <Modal>
      <img src={photo.url} alt={photo.title} />
    </Modal>
  )
}

// app/photos/[id]/page.tsx (Direct route - shows full page)
import { getPhoto } from '@/lib/photos'

export default async function PhotoPage({ params }: { params: { id: string } }) {
  const photo = await getPhoto(params.id)

  return (
    <div>
      <h1>{photo.title}</h1>
      <img src={photo.url} alt={photo.title} />
    </div>
  )
}
```

---

## Partial Prerendering (PPR)

Combine static and dynamic content in the same route.

### Enable PPR

```js
// next.config.js
module.exports = {
  experimental: {
    ppr: true
  }
}
```

### Implementation

```tsx
// app/product/[id]/page.tsx
import { Suspense } from 'react'
import { getProduct } from '@/lib/products'
import { ReviewsList } from '@/components/ReviewsList'

export const experimental_ppr = true

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id)

  return (
    <div>
      {/* Static shell - prerendered */}
      <h1>{product.name}</h1>
      <p>{product.description}</p>

      {/* Dynamic content - streamed */}
      <Suspense fallback={<ReviewsSkeleton />}>
        <ReviewsList productId={params.id} />
      </Suspense>
    </div>
  )
}
```

---

## Route Groups

Organize routes without affecting URL structure.

### Folder Structure
```
app/
  (marketing)/
    about/page.tsx
    blog/page.tsx
    layout.tsx
  (shop)/
    products/page.tsx
    cart/page.tsx
    layout.tsx
```

Each group can have its own layout without affecting URLs:
- `/about` → uses (marketing) layout
- `/products` → uses (shop) layout

---

## Dynamic Routes

```tsx
// app/blog/[slug]/page.tsx
export default function BlogPost({ params }: { params: { slug: string } }) {
  return <h1>Post: {params.slug}</h1>
}

// app/shop/[...slug]/page.tsx (Catch-all)
export default function Product({ params }: { params: { slug: string[] } }) {
  return <h1>Category: {params.slug.join('/')}</h1>
}

// app/docs/[[...slug]]/page.tsx (Optional catch-all)
export default function Docs({ params }: { params: { slug?: string[] } }) {
  return <h1>Docs: {params.slug?.join('/') || 'Home'}</h1>
}
```
