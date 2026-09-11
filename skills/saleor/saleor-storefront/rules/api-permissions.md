# Saleor API Permissions

Understanding how Saleor's permission model works prevents "Permission denied" errors and ensures your storefront queries only request data they're authorized to access.

> **Source**: [Saleor Docs - Permissions](https://docs.saleor.io/developer/permissions)

## Token Types

| Token Type            | How to Get                    | Typical Use              |
| --------------------- | ----------------------------- | ------------------------ |
| **Anonymous**         | No token                      | Product browsing         |
| **Customer JWT**      | `tokenCreate` mutation        | User account, checkout   |
| **App token**         | Saleor Dashboard → Extensions | Server-side operations   |
| **Staff JWT**         | Dashboard login               | Admin operations (never use in storefront) |

## Permission Error

When you see:

```
"To access this path, you need one of the following permissions: MANAGE_..."
```

The field requires admin permissions and isn't available to anonymous/customer tokens. Your options:

1. **Remove the field** from the storefront query (most common fix)
2. **Fetch server-side** with an app token that has the required permission

## Common Permission Boundaries

### Public (no token needed)

- Product details, listings, search
- Categories, collections
- Menu/navigation structure
- Page content

### Customer JWT required

- `me` query (current user)
- `checkoutLinesAdd`, `checkoutComplete`
- Order history (`me.orders`)
- Address book (`me.addresses`)

### App token required

- `channels` query (requires `AUTHENTICATED_APP`)
- Any field annotated with `MANAGE_*` permissions

## Channel Listing

The `channels` query requires an authenticated app token. No specific permission beyond `AUTHENTICATED_APP` is needed to list channels:

1. Create an app in **Saleor Dashboard → Extensions → Add extension**
2. No special permissions required for channel listing
3. Use the token server-side only via `SALEOR_APP_TOKEN` env var

**Never use a staff token in a storefront.** App tokens are the correct approach for server-side data that requires authentication.

## Two-Tier Query Pattern

Most Saleor storefronts use two query helpers:

```typescript
// Public queries — no auth, only publicly visible data
// Safe for caching, SSG, ISR
const products = await publicQuery(ProductListDocument, { variables });

// Authenticated queries — requires user session or app token
// NOT safe for caching (user-specific)
const checkout = await authenticatedQuery(CheckoutDocument, { variables });
```

This separation ensures:
- Only publicly visible products are fetched on display pages
- No user cookies leak into cached responses
- No "Signature has expired" errors on public pages

## Anti-patterns

❌ **Don't request `MANAGE_*` fields in storefront queries** — They'll fail for customers  
❌ **Don't use staff tokens in production storefronts** — Use app tokens instead  
❌ **Don't cache authenticated queries** — User-specific data must be fresh  
❌ **Don't mix public and authenticated data in a single cached response**
