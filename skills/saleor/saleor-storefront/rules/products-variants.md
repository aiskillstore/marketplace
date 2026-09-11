# Saleor Products & Variants

Understanding Saleor's product-variant model is essential for building product detail pages, cart operations, and filtering.

> **Source**: [Saleor Docs - Products](https://docs.saleor.io/developer/products)

## Core Concept: You Add Variants to Cart, Not Products

Each variant is a specific attribute combination:

| Product | Attributes     | Variant ID |
| ------- | -------------- | ---------- |
| T-Shirt | Black + Medium | `abc123`   |
| T-Shirt | Black + Large  | `def456`   |
| T-Shirt | White + Medium | `ghi789`   |

The `checkoutLinesAdd` mutation requires a specific `variantId`. Without selecting ALL required attributes, there's no variant to add.

## Two Types of Variant Attributes

Saleor distinguishes between two types via the ProductType configuration:

| Type              | GraphQL Filter              | Purpose                              | UI Pattern          |
| ----------------- | --------------------------- | ------------------------------------ | ------------------- |
| **Selection**     | `VARIANT_SELECTION`         | Identify which variant (color, size) | Interactive picker  |
| **Non-Selection** | `NOT_VARIANT_SELECTION`     | Describe the variant (material)      | Display-only badges |

```graphql
product {
	selectionAttributes: attributes(variantSelection: VARIANT_SELECTION) {
		attribute { name slug }
		values { name slug }
	}
	nonSelectionAttributes: attributes(variantSelection: NOT_VARIANT_SELECTION) {
		attribute { name slug }
		values { name slug }
	}
}
```

**Key insight**: Neither type is "passed" to checkout. You only pass the `variantId`. All attributes are already stored on the variant in Saleor.

## Variant Pricing

Each variant has per-channel pricing:

```graphql
variant {
	pricing {
		price { gross { amount currency } }              # Current price (after discounts)
		priceUndiscounted { gross { amount currency } }  # Original price
	}
}
```

A variant has a discount when `priceUndiscounted > price`.

## Variant Availability

Availability depends on stock:

```graphql
variant {
	quantityAvailable  # Stock count (may require permission)
}
```

For storefront use, check `product.isAvailable` or variant-level stock. Remember the [fulfillment triangle](channels-purchasability.md) — stock exists in warehouses, not channels.

## Variant Media

Variants can have their own images, separate from the product's main gallery:

```graphql
variant {
	media { url alt }  # Variant-specific images
}
product {
	media { url alt }  # Product-level images (fallback)
}
```

Common pattern: show variant images when selected, fall back to product images.

## Product Types Control Everything

Which attributes appear on variants is configured at the **ProductType** level in Saleor Dashboard:

**Dashboard → Configuration → Product Types → [Type] → Variant Attributes**

If an attribute doesn't appear in `variant.attributes`, check the ProductType configuration — it's not a query issue.

## Variant Selection UX Pattern

The recommended pattern for variant selection on storefronts:

1. **URL is source of truth** — `?color=black&size=m&variant=abc123`
2. **"Add to Cart" disabled** until ALL selection attributes are chosen
3. **Incompatible options are clickable** — they clear conflicting selections (don't block)
4. **Out-of-stock options are visible** but not clickable (strikethrough)
5. **Auto-adjustment** — selecting an incompatible option clears other selections rather than blocking

This ensures users can always explore all options without getting "stuck."

## Anti-patterns

❌ **Don't enable "Add to Cart" without full variant selection** — Needs a specific variant ID  
❌ **Don't block incompatible options** — Let users click, clear conflicting selections  
❌ **Don't assume single attribute** — Products can have multiple selection attributes  
❌ **Don't make non-selection attributes interactive** — They're display-only  
❌ **Don't use `0` in boolean checks for prices** — `0` is a valid price, use `typeof === "number"`
