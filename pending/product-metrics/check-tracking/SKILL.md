---
name: check-tracking
description: >-
  Check that Product Metrics conversion tracking works for a store, with the productmetrics CLI or the Product
  Metrics MCP server: store connection active, store linked to the property, Google Ads conversion
  actions present, Enhanced Conversions accepted, Meta Conversions API destination connected, and the latest
  purchase received. Use it when someone asks "is my tracking working?", "why are conversions
  missing in Google Ads?", "did my test order arrive?", after finishing setup, or when Google Ads
  conversions drop while the store's own sales do not. Reads only; it changes nothing.
---

# Check Product Metrics tracking

You read the tracking setup of one store and tell the person, in plain language, whether purchases reach Google Ads and Meta, and what to fix if not. Every operation here only reads. Docs: https://www.productmetrics.io/docs/using/check-tracking.

Use the `productmetrics` CLI with `--json` when it is installed (`productmetrics status --json`), otherwise the MCP `search` and `execute` tools (operation id `tracking.get_configuration` is `productmetrics tracking get-configuration`). Never invent an id: take it from an earlier result.

**All conversion actions by agents are secondary.** Product Metrics creates its actions as secondary and leaves existing ones as they are. What the account bids on is the person's choice: making an action primary (and the old purchase action secondary) in Google Ads (**Goals → Conversions**, or a campaign-specific goal), and picking the conversion a Meta ad set or ChatGPT Ads campaign optimises on, is their step by every route, also when they ask you to do it. Tell them exactly what to click, wait until they say it is done, then run the checks again. The bidding choice belongs to the advertiser, and one primary purchase action keeps bidding right and counts every purchase once. This skill only reads: if the wrong action is primary, or two purchase actions are, tell the person what to change in Google Ads.

## 1. Pick the store

```bash
productmetrics whoami --json
```

One property: use it. Several, and the person named none: ask which store. Keep `company_id` and `property_id`.

## 2. Run the checks

Run these in order and keep the answers:

| Check | Command | Good when |
| --- | --- | --- |
| Setup overview | `productmetrics setup get-status --company-id <c> --property-id <p> --json` | `hub.property.next_action` is null, `company.store.status` is `active` |
| Store connection | `productmetrics tracking get-commerce-configuration --company-id <c> --json` | The store is `active` and feeds this property |
| Tracking configuration | `productmetrics tracking get-configuration --company-id <c> --property-id <p> --json` | Installation active, storefront scope assigned to the property, purchases sent to the Google Ads purchase action, delivery healthy |
| Conversion actions | `productmetrics google-ads get-conversion-actions --property-id <p> --json` | Every purpose exists and is linked |
| Enhanced conversions | `productmetrics tracking get-enhanced-conversions --company-id <c> --property-id <p> --json` | Customer data terms accepted, Data Manager accepted |
| Meta (if used) | `productmetrics destinations list-meta --company-id <c> --json` | Destination enabled, status `connected`, no recent delivery errors |
| Shopware only | `productmetrics tracking get-shopware6-status --company-id <c> --installation-id <i> --json` | Not `setup_required`; no quarantined jobs |

`installation_id` and the storefront scope id come from `tracking get-configuration`.

## 3. Check a real purchase

Ask the person for a recent paid order, or to place and pay for a test order.

- **Website through Cloudflare Tracking:**
  ```bash
  productmetrics tracking get-last-purchase \
    --company-id <c> \
    --installation-id <i> \
    --json
  ```
  `lastPurchase` shows the transaction id, value (in micros: divide by 1,000,000), currency and time. `null` means none arrived yet. It answers 409 for a store connection: use orders instead.
- **Store platforms (Shopify, WooCommerce, Shopware, Lightspeed, Magento):**
  ```bash
  productmetrics orders list \
    --company-id <c> \
    --storefront-scope-id <scope_id> \
    --limit 10 \
    --json
  ```
  Find the order by number. Then `productmetrics orders get --company-id <c> --order-id <order_id> --storefront-scope-id <scope_id> --json` for its margin and new or returning customer.

Only paid orders are sent. An unpaid test order not showing up is expected.

## 4. Compare with sales (MCP)

When the Product Metrics MCP tools are connected and conversions in Google Ads look low, compare:

- `get_store_overview` for the store's own revenue,
- `get_google_ads_report` with `level: "conversion_action"` for what Google Ads recorded.

A drop in Google Ads that the store's revenue doesn't show usually points to tracking, not lost sales.

## 5. Common causes

| You see | Tell the person |
| --- | --- |
| Store not `active` | Finish the platform step: https://www.productmetrics.io/docs/platforms/shopify (or woocommerce, magento, lightspeed, shopware, cloudflare) |
| Scope not assigned to the property | Link the store to the property under **Ecommerce platforms** (or `productmetrics tracking assign-property`) |
| Conversion actions missing | **Tracking → Create Google Ads conversions** |
| Customer data terms not accepted | In Google Ads, **Goals → Settings → Customer data use**, accept the terms, then **Re-check** in Product Metrics |
| Enhanced conversions **Setting up** | Normal for about 15 minutes after creating the actions |
| Profit actions empty | Additional costs not active: **Tracking → Profit tracking → Activate margin policy** |
| Few matched conversions | **Configure consent** names a banner the store doesn't show |
| Meta status `error` | The access token expired or lost permission: the person creates a new one in Events Manager |

## Report back

1. One line verdict: **Tracking works**, or **Tracking needs attention: <the one thing>**.
2. Each check with its result, in the order above.
3. The test order, if you checked one: number, value with currency, when it arrived.
4. What to fix, with the exact app labels.

Quote any error message and request id. If a check could not be read, say so; don't assume it passed.
