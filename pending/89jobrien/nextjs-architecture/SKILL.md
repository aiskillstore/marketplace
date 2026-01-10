---
name: nextjs-architecture
description: Next.js architecture specialist. Use when designing Next.js applications,
  migrating to App Router, implementing Server Components, or optimizing Next.js performance.
  Covers App Router, Server Components, and best practices.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Next.js Architecture

This skill provides Next.js architecture expertise including App Router, Server Components, performance optimization, and migration strategies.

## When to Use This Skill

- When designing Next.js application architecture
- When migrating from Pages Router to App Router
- When implementing Server Components
- When optimizing Next.js performance
- When making Next.js architecture decisions
- When building full-stack Next.js applications

## What This Skill Does

1. **Architecture Design**: Designs Next.js application structure
2. **App Router**: Implements App Router patterns and routing
3. **Server Components**: Uses Server Components effectively
4. **Performance**: Optimizes Next.js for production
5. **Migration**: Migrates from Pages Router to App Router
6. **Best Practices**: Applies Next.js best practices

## How to Use

### Design Architecture

```
Design the architecture for this Next.js application
```

```
Migrate this Pages Router app to App Router
```

### Specific Patterns

```
Implement Server Components for this feature
```

## Architecture Patterns

### App Router Structure

```
app/
├── (auth)/
│   ├── login/page.tsx
│   └── register/page.tsx
├── dashboard/
│   ├── layout.tsx
│   ├── page.tsx
│   └── analytics/page.tsx
├── api/
│   └── users/route.ts
└── layout.tsx
```

### Server Components

**Pattern:**

- Server Components by default
- Client Components with 'use client'
- Direct database access in Server Components
- Streaming with Suspense

### Performance

**Strategies:**

- Static generation for known content
- ISR for frequently changing content
- Streaming for slow queries
- Image optimization
- Code splitting

## Examples

### Example 1: App Router Migration

**Input**: Migrate Pages Router to App Router

**Output**:

```markdown
## Next.js Migration: Pages Router → App Router

### Migration Steps

**1. Convert Layout**
```typescript
// Before: pages/_app.tsx
export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />;
}

// After: app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

**2. Convert Pages**

```typescript
// Before: pages/users/[id].tsx
export default function UserPage({ user }) {
  return <UserProfile user={user} />;
}

// After: app/users/[id]/page.tsx
export default async function UserPage({ params }) {
  const user = await getUser(params.id);
  return <UserProfile user={user} />;
}
```

```

## Best Practices

### Next.js Architecture

1. **Server First**: Use Server Components by default
2. **Client When Needed**: Add 'use client' only when necessary
3. **Static When Possible**: Generate static pages when feasible
4. **Stream Slow Queries**: Use Suspense for slow data
5. **Optimize Images**: Use Next.js Image component

## Related Use Cases

- Next.js architecture design
- App Router migration
- Server Components implementation
- Next.js performance optimization
- Full-stack Next.js development
