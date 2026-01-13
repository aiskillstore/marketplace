# React Server Components Implementation Checklist

Use this checklist when implementing features with React Server Components and Next.js 15 App Router.

## Component Architecture

### Server Components
- [ ] Default to Server Components (no `'use client'` directive)
- [ ] Make Server Components `async` when fetching data
- [ ] Access databases/APIs directly from Server Components
- [ ] Avoid using React hooks in Server Components
- [ ] Avoid browser APIs (window, document, localStorage) in Server Components
- [ ] Use environment variables safely (never expose secrets to client)

### Client Components
- [ ] Add `'use client'` directive at the top of file
- [ ] Keep Client Components small and focused
- [ ] Push `'use client'` boundary as low as possible in component tree
- [ ] Use Client Components only for interactivity (forms, animations, event handlers)
- [ ] Verify all imports in Client Components are client-safe
- [ ] Avoid heavy dependencies that increase bundle size

### Component Composition
- [ ] Server Components can import and render Client Components
- [ ] Client Components receive Server Components via `children` prop (not direct import)
- [ ] Pass serializable props between Server and Client Components
- [ ] Avoid passing functions, dates, or complex objects as props

## Data Fetching

### fetch API Configuration
- [ ] Use `cache: 'force-cache'` for static data (default)
- [ ] Use `cache: 'no-store'` for dynamic/real-time data
- [ ] Use `next: { revalidate: <seconds> }` for Incremental Static Regeneration (ISR)
- [ ] Use `next: { tags: ['tag'] }` for tag-based revalidation
- [ ] Fetch data in parallel with `Promise.all()` when possible
- [ ] Fetch data sequentially only when dependent on previous results

### Database Access
- [ ] Use ORM/database client directly in Server Components
- [ ] Close database connections properly
- [ ] Use connection pooling for production
- [ ] Implement proper error handling with try-catch
- [ ] Add indexes for frequently queried fields
- [ ] Select only required fields (avoid `SELECT *`)

### Performance
- [ ] Avoid waterfalls - fetch data in parallel
- [ ] Use Suspense boundaries for independent data sources
- [ ] Implement loading states with `loading.tsx`
- [ ] Consider route segment config (`revalidate`, `dynamic`)
- [ ] Use `generateStaticParams()` for static generation
- [ ] Implement proper caching strategy (static, dynamic, ISR)

## Server Actions

### Setup & Security
- [ ] Add `'use server'` directive to Server Actions file
- [ ] Validate all input data (use Zod, Yup, or similar)
- [ ] Check user authorization before mutations
- [ ] Use try-catch for error handling
- [ ] Sanitize user input to prevent injection attacks
- [ ] Rate limit sensitive actions

### Implementation
- [ ] Return structured responses `{ success, data?, error? }`
- [ ] Use `revalidatePath()` after mutations
- [ ] Use `revalidateTag()` for tag-based revalidation
- [ ] Use `redirect()` only after successful mutations
- [ ] Handle FormData properly (get, set, append)
- [ ] Support both form actions and programmatic calls

### Progressive Enhancement
- [ ] Forms work without JavaScript enabled
- [ ] Provide loading states during submission
- [ ] Show validation errors inline
- [ ] Clear form after successful submission
- [ ] Prevent double submissions

### Client Integration
- [ ] Use `useFormState()` for form state management
- [ ] Use `useFormStatus()` for loading states
- [ ] Use `useOptimistic()` for optimistic UI updates
- [ ] Handle errors gracefully with user feedback

## Routing

### File Structure
- [ ] Use `page.tsx` for route pages
- [ ] Use `layout.tsx` for shared layouts
- [ ] Use `loading.tsx` for loading states
- [ ] Use `error.tsx` for error boundaries
- [ ] Use `not-found.tsx` for 404 pages
- [ ] Use `route.ts` for API routes

### Dynamic Routes
- [ ] Use `[param]` for dynamic segments
- [ ] Use `[...slug]` for catch-all segments
- [ ] Use `[[...slug]]` for optional catch-all
- [ ] Implement `generateStaticParams()` for SSG
- [ ] Handle `notFound()` for missing resources

### Advanced Routing
- [ ] Use parallel routes `@folder` for multi-panel layouts
- [ ] Use intercepting routes `(..)` for modals
- [ ] Understand route group `(folder)` behavior
- [ ] Use `useRouter()` from `next/navigation` in Client Components
- [ ] Use `redirect()` from `next/navigation` in Server Components

## Streaming & Suspense

### Suspense Boundaries
- [ ] Wrap slow components in `<Suspense>`
- [ ] Provide meaningful fallback UI
- [ ] Create independent Suspense boundaries for parallel loading
- [ ] Avoid wrapping entire page in single Suspense
- [ ] Use Suspense for data-fetching components only

### Loading States
- [ ] Implement skeleton screens for better UX
- [ ] Match skeleton layout to actual content
- [ ] Show progress indicators for long operations
- [ ] Use `loading.tsx` for route-level loading
- [ ] Provide instant feedback for user actions

## Metadata & SEO

### Static Metadata
- [ ] Export metadata object from `page.tsx`
- [ ] Include title, description, and keywords
- [ ] Add Open Graph tags for social sharing
- [ ] Add Twitter Card tags
- [ ] Configure viewport and icons

### Dynamic Metadata
- [ ] Implement `generateMetadata()` function
- [ ] Fetch data required for metadata
- [ ] Return proper `Metadata` type
- [ ] Handle cases where data is not found
- [ ] Cache metadata generation appropriately

## Error Handling

### Error Boundaries
- [ ] Create `error.tsx` for route-level errors
- [ ] Make `error.tsx` a Client Component
- [ ] Provide error message and reset button
- [ ] Log errors for monitoring
- [ ] Handle different error types appropriately

### Not Found Handling
- [ ] Create `not-found.tsx` for 404 errors
- [ ] Call `notFound()` when resource doesn't exist
- [ ] Provide helpful navigation back to app
- [ ] Include search functionality if appropriate

### Validation Errors
- [ ] Validate on both client and server
- [ ] Show field-level errors
- [ ] Prevent form submission if invalid
- [ ] Use `useFormState()` for server-side errors
- [ ] Clear errors when user corrects input

## Performance Optimization

### Bundle Size
- [ ] Verify Client Component boundaries are minimal
- [ ] Use dynamic imports for heavy components
- [ ] Analyze bundle with `@next/bundle-analyzer`
- [ ] Remove unused dependencies
- [ ] Use tree-shaking friendly imports

### Rendering Strategy
- [ ] Choose appropriate rendering mode (static, dynamic, ISR)
- [ ] Use `generateStaticParams()` for known routes
- [ ] Configure `revalidate` for ISR
- [ ] Use `dynamic = 'force-static'` for static pages
- [ ] Use `dynamic = 'force-dynamic'` for always-fresh pages

### Caching
- [ ] Configure appropriate cache headers
- [ ] Use `fetch` cache options correctly
- [ ] Implement tag-based revalidation
- [ ] Clear cache after mutations
- [ ] Understand Next.js caching behavior

### Images & Assets
- [ ] Use `next/image` for optimized images
- [ ] Specify width and height for images
- [ ] Use appropriate image formats (WebP, AVIF)
- [ ] Lazy load offscreen images
- [ ] Optimize fonts with `next/font`

## Testing

### Component Testing
- [ ] Test Server Components with React Testing Library
- [ ] Test Client Components with user interactions
- [ ] Test Server Actions independently
- [ ] Mock database calls in tests
- [ ] Test error states and edge cases

### Integration Testing
- [ ] Test data fetching and rendering
- [ ] Test form submissions end-to-end
- [ ] Test navigation between routes
- [ ] Test Suspense boundaries
- [ ] Test error boundaries

### Performance Testing
- [ ] Measure Time to First Byte (TTFB)
- [ ] Measure First Contentful Paint (FCP)
- [ ] Measure Largest Contentful Paint (LCP)
- [ ] Measure Cumulative Layout Shift (CLS)
- [ ] Test with slow network conditions

## Deployment

### Pre-Deployment
- [ ] Run `npm run build` successfully
- [ ] Fix all TypeScript errors
- [ ] Fix all ESLint warnings
- [ ] Test production build locally
- [ ] Verify environment variables are set

### Configuration
- [ ] Configure `next.config.js` appropriately
- [ ] Set up proper domain and URLs
- [ ] Configure caching headers
- [ ] Set up CDN for static assets
- [ ] Enable compression

### Monitoring
- [ ] Set up error tracking (Sentry, LogRocket)
- [ ] Monitor Core Web Vitals
- [ ] Track Server Action errors
- [ ] Monitor database query performance
- [ ] Set up alerts for critical errors

## Common Pitfalls to Avoid

- [ ] ❌ Don't use `useState` in Server Components
- [ ] ❌ Don't use `useEffect` in Server Components
- [ ] ❌ Don't access browser APIs in Server Components
- [ ] ❌ Don't import Server Components into Client Components directly
- [ ] ❌ Don't pass non-serializable props (functions, dates, class instances)
- [ ] ❌ Don't forget `'use client'` directive for interactive components
- [ ] ❌ Don't forget `'use server'` directive for Server Actions
- [ ] ❌ Don't skip input validation in Server Actions
- [ ] ❌ Don't expose secrets to Client Components
- [ ] ❌ Don't create large Client Component boundaries

## Migration Checklist (Pages → App Router)

- [ ] Keep `pages/` directory initially (both routers work together)
- [ ] Create `app/` directory
- [ ] Move routes incrementally to `app/`
- [ ] Convert `getServerSideProps()` to `async` Server Components
- [ ] Convert `getStaticProps()` to `fetch` with cache
- [ ] Convert API routes to Route Handlers or Server Actions
- [ ] Update `next/link` usage (remove `<a>` child)
- [ ] Update `next/router` to `next/navigation`
- [ ] Test each migrated route thoroughly
- [ ] Remove `pages/` when fully migrated
