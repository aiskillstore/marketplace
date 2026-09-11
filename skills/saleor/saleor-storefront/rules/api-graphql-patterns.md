# Saleor GraphQL Patterns

Common patterns and gotchas when writing GraphQL queries against the Saleor API.

> **Source**: [Saleor API Reference](https://docs.saleor.io/api-reference)

## Channel-Scoped Queries

Most storefront queries require a `channel` argument:

```graphql
query ProductDetails($slug: String!, $channel: String!) {
	product(slug: $slug, channel: $channel) {
		id
		name
		pricing { priceRange { start { gross { amount currency } } } }
	}
}
```

Without `channel`, pricing and availability data won't be returned.

## Variant Attribute Queries

Saleor distinguishes between two types of variant attributes via the `variantSelection` filter:

```graphql
product {
	# Attributes that IDENTIFY which variant (color, size) — interactive pickers
	selectionAttributes: attributes(variantSelection: VARIANT_SELECTION) {
		attribute { name slug }
		values { name slug }
	}

	# Attributes that DESCRIBE the variant (material, brand) — display only
	nonSelectionAttributes: attributes(variantSelection: NOT_VARIANT_SELECTION) {
		attribute { name slug }
		values { name slug }
	}
}
```

| Type              | `variantSelection` value    | Purpose                              | UI Pattern          |
| ----------------- | --------------------------- | ------------------------------------ | ------------------- |
| **Selection**     | `VARIANT_SELECTION`         | Identify which variant (color, size) | Interactive picker  |
| **Non-Selection** | `NOT_VARIANT_SELECTION`     | Describe the variant (material)      | Display-only badges |

**Key insight**: Neither type is "passed" to checkout. You only pass the `variantId`. All attributes are already stored on the variant in Saleor.

## Product Filtering

Use `ProductFilterInput` for server-side filtering:

```graphql
query Products($channel: String!, $filter: ProductFilterInput) {
	products(channel: $channel, filter: $filter, first: 20) {
		edges {
			node { id name slug }
		}
	}
}
```

Common filter fields:

| Filter             | Type            | Notes                                        |
| ------------------ | --------------- | -------------------------------------------- |
| `categories`       | `[ID!]`         | Requires category IDs (not slugs)            |
| `collections`      | `[ID!]`         | Requires collection IDs                      |
| `price`            | `PriceRangeInput` | `{ gte: 10, lte: 50 }`                    |
| `search`           | `String`        | Full-text search                             |
| `stockAvailability`| `StockAvailability` | `IN_STOCK` or `OUT_OF_STOCK`           |
| `attributes`       | `[AttributeInput!]` | Filter by attribute values              |

**Gotcha**: Categories and collections require **IDs**, not slugs. You need a slug-to-ID resolution step if your URLs use slugs.

## Pagination

Saleor uses cursor-based pagination:

```graphql
products(first: 20, after: $cursor) {
	edges { node { id name } cursor }
	pageInfo { hasNextPage endCursor }
}
```

## GraphQL Codegen

Most Saleor storefronts use `graphql-codegen` with API introspection:

```typescript
// .graphqlrc.ts or codegen.ts
const config = {
	schema: process.env.NEXT_PUBLIC_SALEOR_API_URL,
	documents: "src/graphql/*.graphql",
	generates: {
		"src/gql/": { preset: "client" },
	},
};
```

**Critical**: Always regenerate types after changing `.graphql` files. The generated files contain the full schema and typed document nodes.

## Anti-patterns

❌ **Don't forget the `channel` argument** — Most queries require it for pricing/availability  
❌ **Don't use category slugs in filters** — Resolve to IDs first  
❌ **Don't edit generated type files** — Regenerate instead  
❌ **Don't make `variantSelection` attributes interactive** when they're `NOT_VARIANT_SELECTION` — They're display-only
