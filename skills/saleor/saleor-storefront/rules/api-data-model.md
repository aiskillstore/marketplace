# Saleor API Data Model

Understanding Saleor's data model quirks — nullable fields, pricing structure, and automatic storefront filtering — prevents bugs and wasted debugging time.

> **Source**: [Saleor API Reference](https://docs.saleor.io/api-reference)

## Nullable Fields

Saleor's GraphQL schema has many nullable fields. Handle nulls intentionally — use optional chaining with a fallback for display values, but guard or throw when null signals a real problem:

```typescript
// Display value with fallback
const name = product.category?.name ?? "Uncategorized";

// Guard when null means something is wrong
if (!product.defaultVariant) {
	throw new Error(`Product ${product.slug} has no default variant`);
}
```

Common nullable fields that catch people off guard:

| Field                    | Nullable? | Why                                  |
| ------------------------ | --------- | ------------------------------------ |
| `product.category`       | Yes       | Products can be uncategorized        |
| `product.defaultVariant` | Yes       | Products might have no variants      |
| `variant.pricing`        | Yes       | No price set for the channel         |
| `product.thumbnail`      | Yes       | No images uploaded                   |
| `product.description`    | Yes       | Rich text JSON, can be empty or null |
| `checkout.shippingPrice` | Yes       | No shipping method selected yet      |

## Pricing Structure

Every priced entity in Saleor uses the `TaxedMoney` pattern:

```graphql
type TaxedMoney {
	gross: Money!   # Price including tax
	net: Money!     # Price excluding tax
	tax: Money!     # Tax amount
	currency: String!
}
```

Pricing is always **per-channel**. A product variant can have different prices in different channels.

### Variant Pricing

```graphql
variant {
	pricing {
		price { gross { amount currency } }          # Current price (after discounts)
		priceUndiscounted { gross { amount currency } } # Original price
	}
}
```

A variant has a discount when `priceUndiscounted.gross.amount > price.gross.amount`.

### Discount Percentage

```typescript
const discount = Math.round(
	((undiscounted - price) / undiscounted) * 100
);
```

## Automatic Storefront Filtering

Saleor automatically filters data based on authentication token. You typically do NOT need to:

- Fetch the `visibleInStorefront` field
- Filter data client-side by visibility

The API already returns only what's meant to be shown:

| Token Type              | What's Returned                         |
| ----------------------- | --------------------------------------- |
| None (anonymous)        | Only public, `visibleInStorefront` data |
| Customer JWT            | Same as anonymous + user's own data     |
| App with specific perms | Based on granted permissions            |
| App with `MANAGE_*`     | ALL data for that domain                |

This applies to attributes, products, collections, and other entities with "visible in storefront" flags.

## Anti-patterns

❌ **Don't assume fields are non-null** — Check the schema and handle nulls explicitly  
❌ **Don't blindly use `?.` everywhere** — When null means something is broken, throw or guard  
❌ **Don't filter `visibleInStorefront` client-side** — The API already does it based on your token  
❌ **Don't mix up `gross` and `net`** — Storefronts typically display `gross` (tax-inclusive)
