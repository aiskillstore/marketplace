# React Server Components - Component Patterns

## Server vs Client Component Boundaries

### Component Boundary Rules

1. **Server Components** (default):
   - Can be `async` and use `await`
   - Can access backend resources directly (databases, file system, environment variables)
   - Cannot use hooks (`useState`, `useEffect`, `useContext`, etc.)
   - Cannot use browser-only APIs
   - Zero client JavaScript

2. **Client Components** (with `'use client'`):
   - Can use hooks and interactivity
   - Can access browser APIs
   - Cannot be `async`
   - Ships JavaScript to the client
   - Must be marked with `'use client'` directive at the top

3. **Composition Rules**:
   - Server Components can import and render Client Components
   - Client Components **cannot** directly import Server Components
   - Server Components can be passed to Client Components as `children` or props

---

## Server Component Patterns

### Basic Server Component

```tsx
// app/products/page.tsx
import { db } from '@/lib/database'

export default async function ProductsPage() {
  // Direct database access - runs on server only
  const products = await db.product.findMany({
    include: { category: true }
  })

  return (
    <div>
      <h1>Products</h1>
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
}
```

### Server Component with Environment Variables

```tsx
// app/dashboard/page.tsx
export default async function Dashboard() {
  // Safe - environment variables stay on server
  const apiKey = process.env.SECRET_API_KEY

  const data = await fetch(`https://api.example.com/data`, {
    headers: { Authorization: `Bearer ${apiKey}` }
  }).then(res => res.json())

  return <DashboardView data={data} />
}
```

---

## Client Component Patterns

### Basic Client Component

```tsx
// components/AddToCartButton.tsx
'use client' // Required for interactivity

import { useState } from 'react'

export function AddToCartButton({ productId }: { productId: string }) {
  const [count, setCount] = useState(1)
  const [isAdding, setIsAdding] = useState(false)

  const handleAdd = async () => {
    setIsAdding(true)
    await addToCart(productId, count)
    setIsAdding(false)
  }

  return (
    <div>
      <input
        type="number"
        value={count}
        onChange={(e) => setCount(parseInt(e.target.value))}
      />
      <button onClick={handleAdd} disabled={isAdding}>
        {isAdding ? 'Adding...' : 'Add to Cart'}
      </button>
    </div>
  )
}
```

### Client Component with Context

```tsx
// components/ThemeProvider.tsx
'use client'

import { createContext, useContext, useState } from 'react'

const ThemeContext = createContext<'light' | 'dark'>('light')

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
```

---

## Composition Patterns

### ✅ Good: Leaf Client Components

Keep Client Components at the edges (leaves) of the component tree:

```tsx
// app/products/page.tsx (Server Component)
import { db } from '@/lib/database'
import { FilterableProductList } from '@/components/FilterableProductList'

export default async function ProductsPage() {
  const products = await db.product.findMany()

  return (
    <div>
      <h1>Products</h1>
      {/* Server Component passes data to Client Component */}
      <FilterableProductList products={products} />
    </div>
  )
}

// components/FilterableProductList.tsx (Client Component)
'use client'

export function FilterableProductList({ products }: { products: Product[] }) {
  const [filter, setFilter] = useState('')
  const filtered = products.filter(p => p.name.includes(filter))

  return (
    <div>
      <input
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter products..."
      />
      <ProductList products={filtered} />
    </div>
  )
}
```

### ✅ Good: Server Component as Children

Pass Server Components to Client Components via `children` prop:

```tsx
// app/layout.tsx (Server Component)
import { ThemeProvider } from '@/components/ThemeProvider'
import { Header } from @/components/Header'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {/* Client Component wraps Server Components */}
        <ThemeProvider>
          <Header /> {/* This can be a Server Component */}
          {children} {/* These are Server Components */}
        </ThemeProvider>
      </body>
    </html>
  )
}

// components/ThemeProvider.tsx (Client Component)
'use client'

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  // Client-side logic
  return <div className="theme-wrapper">{children}</div>
}
```

### ❌ Bad: Large Client Components

Don't make entire pages Client Components:

```tsx
// ❌ Avoid this
'use client'

export default function Dashboard() {
  const [filter, setFilter] = useState('')
  const products = await getProducts() // ERROR: Can't use async in Client Component

  return (
    <div>
      <input value={filter} onChange={(e) => setFilter(e.target.value)} />
      <ProductList products={products} filter={filter} />
    </div>
  )
}
```

---

## Props Passing Patterns

### Serializable Props Only

Only serializable data can be passed from Server to Client Components:

```tsx
// ✅ Good: Serializable props
<ClientComponent
  data={{ id: 1, name: 'Product' }}
  numbers={[1, 2, 3]}
  isActive={true}
/>

// ❌ Bad: Functions, classes, symbols
<ClientComponent
  onClick={() => {}} // ❌ Functions can't be serialized
  date={new Date()} // ❌ Dates lose precision
  component={SomeComponent} // ❌ Components can't be serialized
/>
```

### Passing Server Actions

Server Actions can be passed as props:

```tsx
// app/posts/page.tsx (Server Component)
import { deletePost } from '@/app/actions'

export default function PostsPage({ posts }: { posts: Post[] }) {
  return (
    <div>
      {posts.map(post => (
        <PostCard key={post.id} post={post} onDelete={deletePost} />
      ))}
    </div>
  )
}

// components/PostCard.tsx (Client Component)
'use client'

export function PostCard({ post, onDelete }: { post: Post; onDelete: (id: string) => Promise<void> }) {
  return (
    <div>
      <h2>{post.title}</h2>
      <button onClick={() => onDelete(post.id)}>Delete</button>
    </div>
  )
}
```

---

## Common Pitfalls

### Pitfall 1: Importing Server Component into Client Component

```tsx
// ❌ This will error
'use client'

import { ServerComponent } from './ServerComponent' // ERROR

export function ClientComponent() {
  return <ServerComponent /> // Won't work
}

// ✅ Use children prop instead
'use client'

export function ClientWrapper({ children }: { children: React.ReactNode }) {
  return <div className="wrapper">{children}</div>
}

// In parent Server Component:
<ClientWrapper>
  <ServerComponent /> {/* Works! */}
</ClientWrapper>
```

### Pitfall 2: Using Hooks in Server Components

```tsx
// ❌ This will error
export default async function Page() {
  const [state, setState] = useState(0) // ERROR: Can't use hooks

  return <div>{state}</div>
}

// ✅ Extract to Client Component
// page.tsx (Server Component)
export default function Page() {
  return <Counter />
}

// Counter.tsx (Client Component)
'use client'

export function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

### Pitfall 3: Async Client Components

```tsx
// ❌ This will error
'use client'

export default async function ClientComponent() { // ERROR: Client Components can't be async
  const data = await fetchData()
  return <div>{data}</div>
}

// ✅ Fetch in Server Component, pass as prop
// page.tsx (Server Component)
export default async function Page() {
  const data = await fetchData()
  return <ClientComponent data={data} />
}

// ClientComponent.tsx (Client Component)
'use client'

export function ClientComponent({ data }: { data: Data }) {
  const [state, setState] = useState(data)
  return <div>{state}</div>
}
```

---

## Advanced Patterns

### Conditional Client Components

Only load client-side code when needed:

```tsx
// app/product/[id]/page.tsx
import dynamic from 'next/dynamic'

const InteractiveReviews = dynamic(() => import('@/components/InteractiveReviews'), {
  ssr: false,
  loading: () => <ReviewsSkeleton />
})

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id)

  return (
    <div>
      <ProductDetails product={product} />

      {/* Only load interactive component on client */}
      <InteractiveReviews productId={params.id} />
    </div>
  )
}
```

### Shared State Between Server and Client

Use cookies or URL state for shared state:

```tsx
// app/settings/page.tsx (Server Component)
import { cookies } from 'next/headers'

export default function SettingsPage() {
  const theme = cookies().get('theme')?.value || 'light'

  return <ThemeToggle initialTheme={theme} />
}

// components/ThemeToggle.tsx (Client Component)
'use client'

export function ThemeToggle({ initialTheme }: { initialTheme: string }) {
  const [theme, setTheme] = useState(initialTheme)

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    document.cookie = `theme=${newTheme}; path=/`
  }

  return <button onClick={toggleTheme}>Toggle Theme</button>
}
```
