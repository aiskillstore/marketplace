# Next.js 16 Migration Playbook

Source: `NEXTJS_16_COMPLETE_GUIDE.md` (sections 3-4, 7)

## 1. Old vs New Snapshot

| Area | v15 Behavior | v16 Behavior |
|------|--------------|--------------|
| Routing | `pages/*`, `_app.tsx`, `middleware.ts` | `app/*`, nested `layout.tsx`, `proxy.ts` |
| Data Fetching | `getServerSideProps`, implicit cache | Async Server Components, explicit caching via `'use cache'`, `cacheLife`, `cacheTag` |
| Bundler | Webpack default, Turbopack opt-in | Turbopack default, opt-out `--webpack` |
| Caching API | `revalidateTag('tag')` | `cacheLife()`, `cacheTag()`, `revalidateTag('tag','profile')`, `updateTag('tag')` |
| Async APIs | Sync `params`, `searchParams`, `cookies()` | All request APIs return Promises and must be awaited |

## 2. Critical Migration Steps

1. **Adopt Turbopack**
   - Remove custom webpack config or opt-out with `next build --webpack`.
   - For custom aliases/plugins, configure `turbopack.resolveAlias` in `next.config.ts`.
2. **Await Request APIs**
   - Change all components to `export default async function Page({ params })` and destructure via `const { slug } = await params`.
   - Run `npx @next/codemod@canary async-request-api` for automated updates.
3. **Rename Middleware**
   - Rename `middleware.ts` → `proxy.ts`, export `proxy`, and keep `config.matcher` for scoped interception.
   - Remember `proxy.ts` runs on Node runtime only.
4. **Enable Cache Components**
   - Replace `experimental.ppr`/`experimental.dynamicIO` with `cacheComponents: true`.
   - Wrap dynamic fetches inside `<Suspense>` or use `'use cache'` blocks with `cacheLife()`/`cacheTag()`.
5. **Handle Image Query Strings**
   - Configure `images.localPatterns` for local assets using `?v=` or other search parameters.
6. **Metadata Image Routes**
   - Await `params` and `id` inside `opengraph-image.tsx` and `twitter-image.tsx` handlers.
7. **Clean Deprecated APIs**
   - Remove `serverRuntimeConfig`, `publicRuntimeConfig`, `next lint`, `next/legacy/image`, tilde Sass imports.

## 3. Pitfalls & Solutions

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Missing `<Suspense>` | Error: "Uncached data accessed outside of <Suspense>" | Wrap dynamic content inside `<Suspense>` when `cacheComponents` enabled |
| `'use cache'` with runtime data | Cookies/headers unavailable | Read request data first, pass as props into cached component |
| `revalidateTag` without profile | No cache refresh | Call `revalidateTag('tag', 'max')` or `updateTag('tag')` |
| Webpack config detected | Turbopack build fails | Remove plugin or opt-out to Webpack |
| Tilde Sass imports | Import error | Use bare module imports or set `turbopack.resolveAlias['~*'] = '*'` |

## 4. Migration Checklists

### Core Steps
- [ ] Upgrade Node.js to 20.9+
- [ ] Run `npx @next/codemod@canary upgrade latest`
- [ ] Move to App Router structure (`app/`)
- [ ] Rename `middleware.ts` → `proxy.ts`
- [ ] Await `params`, `searchParams`, `cookies()`, `headers()`
- [ ] Enable `cacheComponents: true` & `reactCompiler: true` as needed
- [ ] Replace `next lint` scripts with direct `eslint`
- [ ] Configure `images.localPatterns` when using query strings
- [ ] Remove deprecated runtime configs and tilde imports

### Cache Components Rollout
- [ ] Identify cacheable sections (blog list, product catalog)
- [ ] Add `'use cache'` and `cacheLife()` directives
- [ ] Tag data with `cacheTag()` and call `updateTag()` after mutations
- [ ] Wrap dynamic subsections with `<Suspense>` fallbacks
- [ ] Ensure runtime data (cookies/headers) handled outside cached scope

### Turbopack Validation
- [ ] Run `next dev` and `next build` with Turbopack
- [ ] Measure build/startup vs prior versions
- [ ] Enable `turbopackFileSystemCacheForDev` (beta) for large repos
- [ ] Verify third-party integrations (Sass, SVGR, etc.)

## 5. Reference Commands

```bash
# Upgrade entire project
npx @next/codemod@canary upgrade latest

# Fix async params
npx @next/codemod@canary async-request-api

# Opt-out to webpack when necessary
next build --webpack

# Rename middleware
mv middleware.ts proxy.ts
```

Use this playbook during audits or migrations to Next.js 16 to ensure coverage of breaking changes and performance upgrades.
