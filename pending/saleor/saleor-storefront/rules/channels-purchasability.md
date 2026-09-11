# Saleor Channels & Purchasability

Understanding Saleor's channel model and how product availability is computed is essential for debugging why products appear unavailable or can't be purchased. **As of Saleor 3.23 there are two availability modes** — the rules are not what they used to be, and storefront code needs to handle both.

> **Source**: [Saleor Docs - Stock Overview](https://docs.saleor.io/developer/stock/overview)

## How Channels Work

A Saleor channel represents a sales storefront with its own:

- **Currency** (one currency per channel)
- **Product visibility** (published/unpublished per channel)
- **Pricing** (variant prices set per channel)
- **Countries** served (and a default country for forms)
- **Tax settings** (e.g. whether displayed prices are net or gross)

Channels are identified by a **slug** (e.g. `default-channel`, `us-store`, `eu-store`). The slug is what you pass to the API to scope a query:

```graphql
query ($slug: String!, $channel: String!) {
	product(slug: $slug, channel: $channel) { ... }
}
```

How the storefront *picks* which slug to send is a routing concern, not a Saleor concern. Common patterns:

- Path segment: `/us/products/...` → `us-store`
- Subdomain: `uk.example.com` → `uk-store`
- Cookie, geo-IP, or user preference → resolved server-side

Saleor doesn't enforce any of these — pick what fits your framework and infrastructure. Note that one channel can span many countries (an `eu-store` channel typically covers all Eurozone countries), so don't assume a 1:1 channel-to-country mapping.

## Two Availability Modes (Saleor 3.23+)

Saleor 3.23 introduced a per-shop boolean **`Shop.useLegacyShippingZoneStockAvailability`** that switches the entire stock-availability computation between two semantically different modes.

### Purchasability vs Shippability

The single most important insight is that 3.23 splits one entangled concept into two orthogonal ones:

| Concern | Meaning | Driven by |
|---|---|---|
| **Purchasability** | Can a customer add this variant to cart? | Channel publication, channel listing, variant pricing, warehouse-channel link, stock quantity |
| **Shippability** | Can a customer complete checkout for a shippable order? | Shipping zones, shipping methods, destination |

In **legacy mode** (pre-3.23 behavior, still the default for upgraded shops) the two are entangled: a missing shipping zone hides the product entirely, so shippability problems cause purchasability problems.

In **direct mode** (default for new installations) the two are independent: a product can be purchasable but unshippable. The customer adds to cart; checkout fails when no shipping methods are available.

**Storefront UX implication**: In direct mode `isAvailable: true` does **not** guarantee the customer can complete checkout. Build the "in cart, but no shipping methods cover the address" branch explicitly — don't assume `isAvailable` implies a successful checkout.

### Defaults

- **New installations**: direct mode (`useLegacyShippingZoneStockAvailability = false`)
- **Existing/upgraded installations**: legacy mode (`true`), preserved by migration

Admins must opt into direct mode explicitly. Both modes are supported in 3.23 — storefront code should handle both until Saleor announces otherwise.

### Detecting which mode the shop is in

Query the flag from `Shop`:

```graphql
query StockAvailabilityMode {
	shop {
		id
		useLegacyShippingZoneStockAvailability
	}
}
```

The `id` is required for Apollo cache normalization. The flag is shop-wide and rarely changes, so fetch it wherever fits your architecture — typically alongside other layout-level shop config (default country, tax display) so it's cached once per session. Avoid re-querying it per product / per page when one upstream fetch will do.

The literal toggle label in the Saleor admin is **"Use legacy shipping zone stock availability"** — quote it exactly when telling users where to flip the switch.

## Legacy Mode: The Fulfillment Triangle

In legacy mode (`useLegacyShippingZoneStockAvailability = true`), product purchasability depends on three connected entities:

```
        CHANNEL                 SHIPPING ZONE              WAREHOUSE
     (sales storefront)       (delivery region)         (inventory location)
            │                        │                        │
            ├────── assigned to ─────┤                        │
            │                        ├──── fulfills from ─────┤
            ├──────────── assigned to ────────────────────────┤
```

**All three connections must exist for a product to be purchasable.**

### Legacy mode 7-point purchasability checklist

When debugging why a product can't be purchased in a legacy-mode channel, verify all conditions:

1. Product is **published** in the channel
2. Product is **available for purchase** in the channel
3. At least one variant has a **price** in the channel
4. Channel has at least one active **shipping zone**
5. That shipping zone has at least one **warehouse**
6. That warehouse has **stock** for the variant
7. That warehouse is also **assigned to the channel**

### Unreachable stock (legacy mode)

A warehouse assigned to a channel but **not** to any shipping zone for that channel results in "unreachable" stock — it exists in the system but customers cannot buy it. This is the most common cause of confusing `isAvailable: false` in legacy mode.

## Direct Mode: Decoupled Visibility

In direct mode (`useLegacyShippingZoneStockAvailability = false`), shipping zones do **not** gate visibility. A `Stock` row counts toward customer-visible availability iff:

1. The stock's warehouse is assigned to the channel.

That's it. Shipping zones are still required for shipping methods at checkout, but they no longer affect `isAvailable` or `quantityAvailable`.

### Direct mode 5-point purchasability checklist

1. Product is **published** in the channel
2. Product is **available for purchase** in the channel
3. At least one variant has a **price** in the channel
4. At least one **warehouse is assigned to the channel** with stock for the variant
5. (For checkout success) at least one shipping zone covers the customer's destination — but this no longer affects `isAvailable`

### `quantityAvailable` is destination-independent in direct mode

In legacy mode, `quantityAvailable` depended on the destination address (because shipping-zone coverage was part of the computation). In direct mode it's well-defined without an address — it's just summed stock across warehouses linked to the channel.

If your storefront previously passed an address to `quantityAvailable` to get accurate numbers, you can simplify in direct mode. But code that handles both modes should keep the address-aware path.

## Channel-Scoped Queries

Always pass the `channel` argument to get correct pricing and availability:

```graphql
query ProductDetails($slug: String!, $channel: String!) {
	product(slug: $slug, channel: $channel) {
		name
		isAvailable
		pricing {
			priceRange { start { gross { amount currency } } }
		}
	}
}
```

Without `channel`, pricing and availability fields return null. The semantics of `isAvailable` differ by mode (see above), but the query shape is the same.

## Why Products Differ Across Channels

The same product can be purchasable in one channel and not another because:

- **Different warehouses** are assigned to each channel
- **Stock levels** vary per warehouse
- **Pricing** may only be set in certain channels
- **Shipping zones** cover different countries (in legacy mode this gates visibility; in direct mode it only gates checkout completion)

## Stock Webhooks Relevant to Storefronts with Side Services

If your storefront includes a backend service that subscribes to Saleor webhooks (e.g. for cache invalidation, search reindexing, "back in stock" notifications), four channel-scoped events were added in 3.23:

```
PRODUCT_VARIANT_BACK_IN_STOCK_FOR_CLICK_AND_COLLECT
PRODUCT_VARIANT_BACK_IN_STOCK_IN_CHANNEL
PRODUCT_VARIANT_OUT_OF_STOCK_FOR_CLICK_AND_COLLECT
PRODUCT_VARIANT_OUT_OF_STOCK_IN_CHANNEL
```

**Footgun**: these fire **only when `useLegacyShippingZoneStockAvailability = false`**. A shop in legacy mode can subscribe with no error and receive nothing. If your subscription seems silent, verify the shop is in direct mode before debugging payload shape or webhook plumbing.

The pre-3.23 events `PRODUCT_VARIANT_BACK_IN_STOCK` / `PRODUCT_VARIANT_OUT_OF_STOCK` are warehouse-level (not channel-scoped) and continue to fire in both modes.

## Listing Channels

The `channels` query requires an authenticated app token:

```graphql
query {
	channels {
		id
		slug
		name
		currencyCode
	}
}
```

Create an app in **Saleor Dashboard → Extensions → Add extension**. No special permissions beyond `AUTHENTICATED_APP` are needed to list channels. Use the token server-side only.

## Anti-patterns

❌ **Don't assume the fulfillment triangle still applies** — It only applies in legacy mode. Direct mode (default for new shops) decouples shipping zones from visibility  
❌ **Don't conflate "listed" with "purchasable"** — A channel listing existing is necessary, not sufficient. Counting listings is not counting purchasability  
❌ **Don't trust `isAvailable: true` to imply checkout will succeed** — In direct mode, shipping methods may still be empty for the destination  
❌ **Don't assume stock means purchasable** — In legacy mode the warehouse must be in both the channel AND a covering shipping zone  
❌ **Don't debug availability client-side only** — Verify in Saleor Dashboard, and check which mode the shop is in first  
❌ **Don't forget the `channel` argument** — Pricing and availability require it  
❌ **Don't hardcode channel slugs** — Fetch from API or use a configuration fallback  
❌ **Don't use the words "available" / "in stock" / "purchasable" in copy without specifying the sense** — They're mode-conditional terms now
