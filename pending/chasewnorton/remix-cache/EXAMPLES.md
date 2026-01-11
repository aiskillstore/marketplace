# Real-World Examples

Comprehensive examples of using remix-cache in production scenarios.

## Table of Contents

- [E-Commerce Product Catalog](#e-commerce-product-catalog)
- [User Authentication & Sessions](#user-authentication--sessions)
- [API Response Caching](#api-response-caching)
- [Blog & Content Management](#blog--content-management)
- [Analytics Dashboard](#analytics-dashboard)
- [Multi-Tenant SaaS](#multi-tenant-saas)

---

## E-Commerce Product Catalog

Complete caching strategy for an e-commerce site.

### Cache Definitions

```typescript
// app/cache.server.ts
import { createCache } from 'remix-cache/server'

export const cache = createCache({
  redis: { host: process.env.REDIS_HOST!, port: 6379 },
  prefix: 'shop',
  local: { max: 500, ttl: 60 },
})

// Product detail cache
export const productCache = cache.define({
  name: 'product',
  key: (productId: string, locale: string = 'en') => `${productId}:${locale}`,
  fetch: async (productId: string, locale = 'en') => {
    return db.product.findUnique({
      where: { id: productId },
      include: {
        category: true,
        brand: true,
        images: true,
        variants: true,
        reviews: { take: 10, orderBy: { createdAt: 'desc' } },
      },
    })
  },
  ttl: 1800, // 30 minutes
  staleWhileRevalidate: 3600, // Serve stale for 1 hour
  tags: (productId, locale, product) => [
    'product',
    `product:${productId}`,
    `category:${product.categoryId}`,
    `brand:${product.brandId}`,
    `locale:${locale}`,
  ],
  invalidate: (productId, locale, product) => [
    // Also invalidate category page
    `category:${product.categoryId}:products:${locale}`,
    // And brand page
    `brand:${product.brandId}:products:${locale}`,
  ],
})

// Category listing cache
export const categoryProductsCache = cache.define({
  name: 'category-products',
  key: (categoryId: string, locale: string = 'en', page: number = 1) =>
    `${categoryId}:${locale}:${page}`,
  fetch: async (categoryId: string, locale = 'en', page = 1) => {
    return db.product.findMany({
      where: { categoryId },
      skip: (page - 1) * 20,
      take: 20,
      orderBy: { popularity: 'desc' },
    })
  },
  ttl: 600, // 10 minutes
  tags: (categoryId, locale, page) => [
    'product',
    `category:${categoryId}`,
    `category:${categoryId}:products`,
    `locale:${locale}`,
  ],
})

// Inventory cache (short TTL)
export const inventoryCache = cache.define({
  name: 'inventory',
  key: (productId: string, variantId?: string) =>
    variantId ? `${productId}:${variantId}` : productId,
  fetch: async (productId: string, variantId?: string) => {
    return db.inventory.findFirst({
      where: {
        productId,
        ...(variantId && { variantId }),
      },
    })
  },
  ttl: 60, // 1 minute (inventory changes frequently)
  tags: (productId, variantId) => [
    'inventory',
    `product:${productId}`,
    ...(variantId ? [`variant:${variantId}`] : []),
  ],
})

// Shopping cart cache (sliding window)
export const cartCache = cache.define({
  name: 'cart',
  key: (cartId: string) => cartId,
  fetch: async (cartId: string) => {
    return db.cart.findUnique({
      where: { id: cartId },
      include: { items: { include: { product: true } } },
    })
  },
  ttl: 3600, // 1 hour
  slidingWindow: true, // Extend session while active
  tags: (cartId, cart) => ['cart', `cart:${cartId}`, `user:${cart.userId}`],
})
```

### Routes

```typescript
// app/routes/products.$productId.tsx
import { json, type LoaderFunctionArgs, type ActionFunctionArgs } from '@remix-run/node'
import { useLoaderData } from '@remix-run/react'
import { useCache } from 'remix-cache/react'
import { productCache, inventoryCache } from '~/cache.server'

export async function loader({ params }: LoaderFunctionArgs) {
  const locale = getLocale(request) // Your locale detection

  const [product, inventory] = await Promise.all([
    productCache.get(params.productId, locale),
    inventoryCache.get(params.productId),
  ])

  if (!product) {
    throw new Response('Not Found', { status: 404 })
  }

  return json({ product, inventory })
}

export async function action({ request, params }: ActionFunctionArgs) {
  const formData = await request.formData()
  const intent = formData.get('intent')

  if (intent === 'update') {
    // Update product
    const product = await db.product.update({
      where: { id: params.productId },
      data: {
        name: formData.get('name'),
        price: parseFloat(formData.get('price')),
        description: formData.get('description'),
      },
    })

    // Invalidate product cache (triggers SSE event)
    await productCache.delete(params.productId, 'en')
    await productCache.delete(params.productId, 'es') // All locales

    return json({ product })
  }

  if (intent === 'update-inventory') {
    const inventory = await db.inventory.update({
      where: { productId: params.productId },
      data: { quantity: parseInt(formData.get('quantity')) },
    })

    // Invalidate inventory cache
    await inventoryCache.delete(params.productId)

    return json({ inventory })
  }

  return json({ error: 'Invalid intent' }, { status: 400 })
}

export default function ProductDetail() {
  const { product, inventory } = useLoaderData<typeof loader>()

  // Auto-revalidate when product or inventory changes
  useCache({
    tags: [`product:${product.id}`, 'inventory'],
    debounce: 200,
  })

  return (
    <div>
      <h1>{product.name}</h1>
      <p>${product.price}</p>
      <p>{product.description}</p>
      <p>In stock: {inventory.quantity}</p>

      {product.images.map(img => (
        <img key={img.id} src={img.url} alt={product.name} />
      ))}

      <Reviews reviews={product.reviews} />
    </div>
  )
}

// app/routes/categories.$categoryId.tsx
export async function loader({ params, request }: LoaderFunctionArgs) {
  const url = new URL(request.url)
  const page = parseInt(url.searchParams.get('page') || '1')
  const locale = getLocale(request)

  const products = await categoryProductsCache.get(
    params.categoryId,
    locale,
    page
  )

  return json({ products, page })
}

export default function CategoryPage() {
  const { products } = useLoaderData<typeof loader>()

  // Revalidate when any product in category changes
  useCache({ tags: ['product'], debounce: 300 })

  return (
    <ProductGrid products={products} />
  )
}
```

### Batch Inventory Updates

```typescript
// app/routes/admin.inventory.sync.tsx
export async function action({ request }: ActionFunctionArgs) {
  const updates = await request.json()

  // Batch update inventory
  const results = await Promise.all(
    updates.map(({ productId, quantity }) =>
      db.inventory.update({
        where: { productId },
        data: { quantity },
      })
    )
  )

  // Batch invalidate inventory caches
  await inventoryCache.deleteMany(
    updates.map(({ productId }) => [productId])
  )

  return json({ success: true, count: results.length })
}
```

---

## User Authentication & Sessions

Session management with sliding window and automatic revalidation.

### Cache Definitions

```typescript
// app/cache.server.ts

// Session cache with sliding window
export const sessionCache = cache.define({
  name: 'session',
  key: (sessionId: string) => sessionId,
  fetch: async (sessionId: string) => {
    return db.session.findUnique({
      where: { id: sessionId },
      include: { user: { include: { permissions: true } } },
    })
  },
  ttl: 1800, // 30 minutes
  slidingWindow: true, // Reset TTL on each access
  tags: (sessionId, session) => [
    'session',
    `session:${sessionId}`,
    `user:${session.userId}`,
  ],
})

// User profile cache
export const userCache = cache.define({
  name: 'user',
  key: (userId: string) => userId,
  fetch: async (userId: string) => {
    return db.user.findUnique({
      where: { id: userId },
      include: {
        profile: true,
        preferences: true,
        permissions: true,
      },
    })
  },
  ttl: 300, // 5 minutes
  tags: (userId, user) => [
    'user',
    `user:${userId}`,
    `org:${user.organizationId}`,
  ],
  invalidate: (userId, user) => [
    // Invalidate all sessions for this user
    `user:${userId}:sessions`,
  ],
})

// User permissions cache
export const permissionsCache = cache.define({
  name: 'permissions',
  key: (userId: string) => userId,
  fetch: async (userId: string) => {
    return db.permission.findMany({
      where: { userId },
    })
  },
  ttl: 600, // 10 minutes
  tags: (userId) => ['permission', `user:${userId}`],
})
```

### Auth Utilities

```typescript
// app/auth.server.ts
import { sessionCache, userCache } from '~/cache.server'

export async function requireUser(request: Request) {
  const sessionId = await getSessionId(request)

  if (!sessionId) {
    throw redirect('/login')
  }

  // Check session cache (sliding window resets TTL)
  const session = await sessionCache.get(sessionId)

  if (!session) {
    throw redirect('/login')
  }

  // Get user from cache
  const user = await userCache.get(session.userId)

  if (!user) {
    throw redirect('/login')
  }

  return user
}

export async function login(email: string, password: string) {
  const user = await db.user.findUnique({ where: { email } })

  if (!user || !(await verifyPassword(password, user.passwordHash))) {
    throw new Error('Invalid credentials')
  }

  // Create session
  const session = await db.session.create({
    data: {
      userId: user.id,
      expiresAt: new Date(Date.now() + 1800000), // 30 min
    },
  })

  // Cache session and user
  await sessionCache.set(session.id, session)
  await userCache.set(user.id, user)

  return session
}

export async function logout(sessionId: string) {
  // Delete session from DB
  await db.session.delete({ where: { id: sessionId } })

  // Invalidate session cache
  await sessionCache.delete(sessionId)
}

export async function updateUserProfile(userId: string, data: any) {
  const user = await db.user.update({
    where: { id: userId },
    data,
  })

  // Invalidate user cache (triggers SSE to all user's sessions)
  await userCache.delete(userId)

  return user
}
```

### Protected Routes

```typescript
// app/routes/dashboard.tsx
export async function loader({ request }: LoaderFunctionArgs) {
  const user = await requireUser(request)

  const [stats, notifications] = await Promise.all([
    fetchUserStats(user.id),
    fetchNotifications(user.id),
  ])

  return json({ user, stats, notifications })
}

export default function Dashboard() {
  const { user, stats, notifications } = useLoaderData<typeof loader>()

  // Revalidate when user data changes
  useCache({ tags: [`user:${user.id}`] })

  return (
    <div>
      <h1>Welcome, {user.profile.name}!</h1>
      <Stats data={stats} />
      <Notifications items={notifications} />
    </div>
  )
}
```

---

## API Response Caching

Cache external API responses with error handling and conditional TTL.

### Cache Definition

```typescript
// app/cache.server.ts

// API response cache with error handling
export const apiCache = cache.define({
  name: 'api',
  key: (endpoint: string, params?: Record<string, string>) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : ''
    return `${endpoint}${query}`
  },
  fetch: async (endpoint: string, params?: Record<string, string>) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : ''
    const url = `${process.env.API_BASE_URL}${endpoint}${query}`

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${process.env.API_KEY}`,
      },
    })

    if (!response.ok) {
      return {
        error: true,
        status: response.status,
        message: await response.text(),
      }
    }

    return {
      error: false,
      data: await response.json(),
    }
  },
  ttl: (endpoint, params, response) => {
    // Cache errors for shorter time
    if (response.error) return 60

    // Check if API provides cache headers
    if (response.data?.cache_control) {
      return response.data.cache_control.max_age
    }

    // Default: 5 minutes
    return 300
  },
  staleWhileRevalidate: 600, // Serve stale for 10 minutes
  tags: (endpoint) => ['api', `api:${endpoint}`],
})

// Weather API cache (external service)
export const weatherCache = cache.define({
  name: 'weather',
  key: (city: string) => city.toLowerCase(),
  fetch: async (city: string) => {
    const response = await fetch(
      `https://api.weather.com/v1/current?city=${city}&apikey=${process.env.WEATHER_API_KEY}`
    )

    if (!response.ok) {
      throw new Error(`Weather API error: ${response.status}`)
    }

    return response.json()
  },
  ttl: 300, // 5 minutes (weather doesn't change often)
  staleWhileRevalidate: 900, // Serve stale for 15 minutes
})
```

### Usage

```typescript
// app/routes/api.proxy.$endpoint.tsx
export async function loader({ params, request }: LoaderFunctionArgs) {
  const url = new URL(request.url)
  const queryParams = Object.fromEntries(url.searchParams)

  const result = await apiCache.get(params.endpoint, queryParams)

  if (result.error) {
    throw new Response(result.message, { status: result.status })
  }

  return json(result.data)
}

// app/routes/weather.$city.tsx
export async function loader({ params }: LoaderFunctionArgs) {
  const weather = await weatherCache.get(params.city)
  return json({ weather })
}

export default function WeatherPage() {
  const { weather } = useLoaderData<typeof loader>()

  // Revalidate weather data
  useCache({ tags: ['api'], debounce: 500 })

  return (
    <div>
      <h1>Weather in {weather.city}</h1>
      <p>Temperature: {weather.temperature}°F</p>
      <p>Conditions: {weather.conditions}</p>
    </div>
  )
}
```

---

## Blog & Content Management

Content caching with cascading invalidation.

### Cache Definitions

```typescript
// app/cache.server.ts

// Blog post cache
export const postCache = cache.define({
  name: 'post',
  key: (slug: string) => slug,
  fetch: async (slug: string) => {
    return db.post.findUnique({
      where: { slug },
      include: {
        author: true,
        category: true,
        tags: true,
        comments: { take: 20, orderBy: { createdAt: 'desc' } },
      },
    })
  },
  ttl: 3600, // 1 hour
  staleWhileRevalidate: 7200, // Serve stale for 2 hours
  tags: (slug, post) => [
    'post',
    `post:${slug}`,
    `author:${post.authorId}`,
    `category:${post.categoryId}`,
    ...post.tags.map(t => `tag:${t.name}`),
  ],
  invalidate: (slug, post) => [
    // Invalidate author's post list
    `author:${post.authorId}:posts`,
    // Invalidate category page
    `category:${post.categoryId}:posts`,
    // Invalidate tag pages
    ...post.tags.map(t => `tag:${t.name}:posts`),
  ],
})

// Post listing cache
export const postListCache = cache.define({
  name: 'post-list',
  key: (page: number = 1, categoryId?: string) =>
    categoryId ? `${categoryId}:${page}` : `all:${page}`,
  fetch: async (page = 1, categoryId?: string) => {
    return db.post.findMany({
      where: categoryId ? { categoryId } : {},
      skip: (page - 1) * 10,
      take: 10,
      orderBy: { publishedAt: 'desc' },
      include: { author: true, category: true },
    })
  },
  ttl: 600, // 10 minutes
  tags: (page, categoryId) => [
    'post',
    'post-list',
    ...(categoryId ? [`category:${categoryId}`] : []),
  ],
})

// Comment cache
export const commentCache = cache.define({
  name: 'comment',
  key: (postSlug: string) => postSlug,
  fetch: async (postSlug: string) => {
    const post = await db.post.findUnique({ where: { slug: postSlug } })
    if (!post) return []

    return db.comment.findMany({
      where: { postId: post.id },
      orderBy: { createdAt: 'desc' },
      include: { author: true },
    })
  },
  ttl: 300, // 5 minutes (comments change frequently)
  tags: (postSlug, comments) => ['comment', `post:${postSlug}:comments`],
})
```

### Routes

```typescript
// app/routes/blog.$slug.tsx
export async function loader({ params }: LoaderFunctionArgs) {
  const [post, comments] = await Promise.all([
    postCache.get(params.slug),
    commentCache.get(params.slug),
  ])

  if (!post) {
    throw new Response('Not Found', { status: 404 })
  }

  return json({ post, comments })
}

export async function action({ request, params }: ActionFunctionArgs) {
  const formData = await request.formData()
  const intent = formData.get('intent')

  if (intent === 'update-post') {
    const post = await db.post.update({
      where: { slug: params.slug },
      data: {
        title: formData.get('title'),
        content: formData.get('content'),
      },
    })

    // Invalidate post and cascading caches
    await postCache.delete(params.slug)

    return json({ post })
  }

  if (intent === 'add-comment') {
    const post = await db.post.findUnique({ where: { slug: params.slug } })

    const comment = await db.comment.create({
      data: {
        postId: post.id,
        authorId: formData.get('authorId'),
        content: formData.get('content'),
      },
    })

    // Invalidate comments cache
    await commentCache.delete(params.slug)

    return json({ comment })
  }

  return json({ error: 'Invalid intent' }, { status: 400 })
}

export default function BlogPost() {
  const { post, comments } = useLoaderData<typeof loader>()

  // Revalidate post and comments
  useCache({
    tags: [`post:${post.slug}`, 'comment'],
    debounce: 200,
  })

  return (
    <article>
      <h1>{post.title}</h1>
      <p>By {post.author.name} in {post.category.name}</p>
      <div dangerouslySetInnerHTML={{ __html: post.content }} />

      <Comments comments={comments} postSlug={post.slug} />
    </article>
  )
}
```

---

## Analytics Dashboard

Real-time analytics with aggressive caching.

### Cache Definitions

```typescript
// app/cache.server.ts

// Analytics cache with conditional TTL
export const analyticsCache = cache.define({
  name: 'analytics',
  key: (metric: string, startDate: string, endDate: string, userId?: string) =>
    userId
      ? `${metric}:${startDate}:${endDate}:${userId}`
      : `${metric}:${startDate}:${endDate}`,
  fetch: async (metric: string, startDate: string, endDate: string, userId?: string) => {
    return db.analyticsEvent.aggregate({
      where: {
        metric,
        userId,
        timestamp: {
          gte: new Date(startDate),
          lte: new Date(endDate),
        },
      },
      _count: true,
      _sum: { value: true },
      _avg: { value: true },
    })
  },
  ttl: (metric, startDate, endDate, userId, data) => {
    const end = new Date(endDate)
    const now = new Date()

    // Historical data: cache for 24 hours
    if (end < now) return 86400

    // Current day: cache for 5 minutes
    return 300
  },
  tags: (metric, startDate, endDate, userId) => [
    'analytics',
    `metric:${metric}`,
    ...(userId ? [`user:${userId}`] : []),
  ],
})
```

### Usage

```typescript
// app/routes/dashboard.analytics.tsx
export async function loader({ request }: LoaderFunctionArgs) {
  const user = await requireUser(request)
  const url = new URL(request.url)

  const startDate = url.searchParams.get('start') || getYesterday()
  const endDate = url.searchParams.get('end') || getToday()

  const [pageViews, uniqueVisitors, conversions] = await Promise.all([
    analyticsCache.get('pageviews', startDate, endDate),
    analyticsCache.get('visitors', startDate, endDate),
    analyticsCache.get('conversions', startDate, endDate, user.id),
  ])

  return json({ pageViews, uniqueVisitors, conversions, startDate, endDate })
}

export default function AnalyticsDashboard() {
  const data = useLoaderData<typeof loader>()

  // Revalidate analytics data
  useCache({ tags: ['analytics'], debounce: 5000 })

  return (
    <div>
      <h1>Analytics Dashboard</h1>
      <MetricCard title="Page Views" value={data.pageViews._count} />
      <MetricCard title="Unique Visitors" value={data.uniqueVisitors._count} />
      <MetricCard title="Conversions" value={data.conversions._count} />
    </div>
  )
}
```

---

## Multi-Tenant SaaS

Organization-scoped caching for SaaS applications.

### Cache Definitions

```typescript
// app/cache.server.ts

// Org-scoped data cache
export const orgDataCache = cache.define({
  name: 'org-data',
  key: (orgId: string, dataType: string) => `${orgId}:${dataType}`,
  fetch: async (orgId: string, dataType: string) => {
    return db[dataType].findMany({
      where: { organizationId: orgId },
    })
  },
  ttl: 600, // 10 minutes
  tags: (orgId, dataType) => [
    `org:${orgId}`,
    `org:${orgId}:${dataType}`,
  ],
})

// Org settings cache (long TTL)
export const orgSettingsCache = cache.define({
  name: 'org-settings',
  key: (orgId: string) => orgId,
  fetch: async (orgId: string) => {
    return db.organizationSettings.findUnique({
      where: { organizationId: orgId },
    })
  },
  ttl: 3600, // 1 hour (settings rarely change)
  tags: (orgId) => [`org:${orgId}`, `org:${orgId}:settings`],
})
```

### Usage with Tenant Isolation

```typescript
// app/routes/app.$orgId.projects.tsx
export async function loader({ params, request }: LoaderFunctionArgs) {
  const user = await requireUser(request)

  // Verify user belongs to org
  if (!user.organizations.some(o => o.id === params.orgId)) {
    throw new Response('Forbidden', { status: 403 })
  }

  const [projects, settings] = await Promise.all([
    orgDataCache.get(params.orgId, 'projects'),
    orgSettingsCache.get(params.orgId),
  ])

  return json({ projects, settings })
}

export async function action({ params, request }: ActionFunctionArgs) {
  const user = await requireUser(request)
  const formData = await request.formData()

  // Update project
  const project = await db.project.update({
    where: { id: formData.get('projectId') },
    data: { name: formData.get('name') },
  })

  // Invalidate org's project cache
  await cache.invalidateByTag(`org:${params.orgId}:projects`)

  return json({ project })
}

export default function OrgProjects() {
  const { projects, settings } = useLoaderData<typeof loader>()
  const params = useParams()

  // Revalidate when org data changes
  useCache({ tags: [`org:${params.orgId}`], debounce: 300 })

  return <ProjectList projects={projects} settings={settings} />
}
```

This examples file provides comprehensive, production-ready patterns for common use cases!
