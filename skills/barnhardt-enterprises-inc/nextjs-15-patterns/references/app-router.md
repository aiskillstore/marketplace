# App Router Reference

## File Conventions

| File | Purpose |
|------|---------|
| `page.tsx` | Route UI |
| `layout.tsx` | Shared layout |
| `loading.tsx` | Loading UI |
| `error.tsx` | Error UI |
| `not-found.tsx` | 404 UI |
| `route.ts` | API endpoint |
| `template.tsx` | Re-rendered layout |
| `default.tsx` | Parallel route fallback |

## Route Groups

```
app/
├── (marketing)/
│   ├── about/page.tsx      # /about
│   └── contact/page.tsx    # /contact
├── (shop)/
│   ├── products/page.tsx   # /products
│   └── cart/page.tsx       # /cart
└── layout.tsx
```

## Dynamic Routes

```
app/
├── users/
│   ├── [id]/page.tsx           # /users/123
│   ├── [...slug]/page.tsx      # /users/a/b/c
│   └── [[...slug]]/page.tsx    # /users or /users/a/b
```

## Intercepting Routes

```
app/
├── feed/
│   └── (..)photo/[id]/page.tsx  # Intercept from parent
├── photo/[id]/page.tsx          # Direct access
```

Conventions:
- `(.)` - Same level
- `(..)` - One level up
- `(..)(..)` - Two levels up
- `(...)` - Root level
