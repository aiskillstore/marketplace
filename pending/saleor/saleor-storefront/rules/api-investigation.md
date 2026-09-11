# Saleor API Investigation

How to investigate Saleor API behavior when documentation is unclear or you need to understand exact data models, permission checks, or filtering logic.

## Step 1: Check the Generated Types (Schema)

If you're using `graphql-codegen` with API introspection (recommended), your generated types file contains the **full Saleor schema** as TypeScript types — all types, enums, inputs, not just the ones used in declared queries.

```bash
# Example: generated types file (path depends on your setup)
grep -A 20 "^export type Product " src/gql/graphql.ts
grep -A 10 "^export enum StockAvailability" src/gql/graphql.ts
grep -A 30 "^export type ProductFilterInput" src/gql/graphql.ts
```

This file is generated via API introspection, so it always matches your exact Saleor version. If the types confirm what you need, stop here.

## Step 2: Check Saleor Documentation

- [Saleor API Reference](https://docs.saleor.io/api-reference) — GraphQL schema with field descriptions
- [Saleor Developer Docs](https://docs.saleor.io/developer) — Guides and concepts

## Step 3: Check Saleor Source for Behavior

Types tell you *what* fields exist. For *how* they behave (permission checks, filtering logic, side effects), check the Saleor core source.

If the Saleor core repo is available locally (e.g. `../saleor/`), or clone it:

```bash
cd /tmp && git clone --depth 1 https://github.com/saleor/saleor.git saleor-core
```

For detailed directory structure and grep patterns, see the [saleor-key-directories](../references/saleor-key-directories.md) reference.

### Quick Investigation Patterns

```bash
# Find where a field is resolved
grep -r "def resolve_" saleor/graphql/product/

# Find permission checks
grep -r "has_perm" saleor/graphql/product/resolvers.py

# Find mutation logic
grep -r "def perform_mutation" saleor/graphql/checkout/
```

## Examples

### Does `product.attributes` filter by `visibleInStorefront`?

Check `saleor/graphql/product/resolvers.py`:

```python
def resolve_product_attributes(root, info, *, limit):
    if requestor_has_access_to_all_attributes(info.context):
        dataloader = AttributesByProductIdAndLimitLoader        # Admin: ALL
    else:
        dataloader = AttributesVisibleToCustomerByProductIdAndLimitLoader  # Customer: FILTERED
```

**Answer**: Yes. Storefront users only see `visibleInStorefront=True` attributes automatically.

### Token-Based Data Filtering

Saleor filters data based on authentication:

| Token                      | `product.attributes` returns    |
| -------------------------- | ------------------------------- |
| None (anonymous)           | Only `visibleInStorefront=True` |
| Customer JWT               | Only `visibleInStorefront=True` |
| App with `MANAGE_PRODUCTS` | ALL attributes                  |

This pattern applies across many entities in Saleor.

## Key Insights

### Storefront Auto-Filtering

When building storefront features, you typically don't need to:

- Fetch `visibleInStorefront` field
- Filter data client-side

The API already returns only what's meant to be shown based on your token.

### Product Types Control Variant Attributes

Which attributes appear on variants is configured at the **ProductType** level:

Dashboard → Configuration → Product Types → [Type] → Variant Attributes

If an attribute doesn't appear in `variant.attributes`, check the ProductType configuration — not the query.

## Anti-patterns

❌ **Don't guess API behavior** — Check the source  
❌ **Don't filter `visibleInStorefront` client-side** — API does it  
❌ **Don't assume attribute presence** — Check ProductType config in Dashboard
