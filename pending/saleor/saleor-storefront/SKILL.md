---
name: saleor-storefront
description: >
  Saleor e-commerce API patterns for building storefronts. Use when working with
  Saleor's GraphQL API, products, variants, checkout, channels, permissions, or
  debugging API behavior. Framework-agnostic — applies to any Saleor storefront.
license: MIT
metadata:
  author: saleor
  version: "1.0.0"
---

# Saleor Storefront

Universal guide for building storefronts on the Saleor e-commerce platform. Covers
the Saleor GraphQL API data model, permission system, checkout lifecycle, channel
architecture, and product/variant patterns. Framework-agnostic — these rules apply
whether you're using Next.js, Remix, Nuxt, or a custom setup.

## When to Apply

Reference these guidelines when:

- Querying Saleor's GraphQL API for products, categories, or collections
- Building product detail pages with variant selection
- Implementing checkout and payment flows
- Working with multi-channel and multi-currency setups
- Debugging "product not purchasable" or permission errors
- Working with Saleor 3.23+ stock availability modes (`useLegacyShippingZoneStockAvailability`)
- Investigating Saleor API behavior via source code

## Rule Categories

| Priority | Category  | Impact   | Prefix       |
| -------- | --------- | -------- | ------------ |
| 1        | API       | CRITICAL | `api-`       |
| 2        | Products  | HIGH     | `products-`  |
| 3        | Checkout  | HIGH     | `checkout-`  |
| 4        | Channels  | MEDIUM   | `channels-`  |

## Quick Reference

### 1. API (CRITICAL)

- `api-data-model` — Nullable fields, pricing structure, automatic storefront filtering
- `api-permissions` — Token types, permission errors, two-tier query pattern
- `api-graphql-patterns` — Channel-scoped queries, variant attributes, filtering, codegen
- `api-investigation` — How to investigate Saleor API behavior via types and source

### 2. Products (HIGH)

- `products-variants` — Variant model, selection vs non-selection attributes, pricing, UX patterns

### 3. Checkout (HIGH)

- `checkout-lifecycle` — Session lifecycle, common errors, debugging payment issues

### 4. Channels (MEDIUM)

- `channels-purchasability` — Stock availability modes (legacy vs direct, 3.23+), purchasability vs shippability, fulfillment triangle, mode-aware checklists, channel-scoped queries, stock webhooks

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/api-data-model.md
rules/products-variants.md
```

Each rule file contains:

- Brief explanation of why it matters
- Code examples (correct and incorrect patterns)
- Anti-patterns to avoid

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`
