---
name: check-stock-and-returns
description: >-
  Check stock and product returns against advertising with Product Metrics: products advertised
  while out of stock or about to run out, reorder dates and suggested quantities, slow movers with
  too much stock, Stars that will run out, and return rates per category. Use this skill when a
  merchant asks whether they advertise products they cannot deliver, which products to reorder
  before a sale, which slow movers to clear, how returns differ by category, or wants to set lead
  times and safety buffers for the stock planner. It reads stock, cover and returns next to the
  products' ad results and profit, and saves a lead time or safety buffer only after the person
  confirms the exact value; it never orders stock or pauses anything. It works through Product
  Metrics, so use it even when Product Metrics is never mentioned. Not for products that lose money
  after ads (find-unprofitable-products), segment questions (check-product-segments), or
  segmentation settings (set-up-product-segmentation).
license: MIT
metadata:
  author: Product Metrics
  version: "1.0.0"
  docs: https://www.productmetrics.io/docs/mcp/tools
---

# Check stock and returns

Product Metrics reads stock from the connected shop (on hand, weekly sales, weeks of cover, stockout and reorder dates, suggested reorder quantity) and sets it next to the products' ad results and margin. Stock and product returns are also signals in the segments. Tool reference: https://www.productmetrics.io/docs/mcp/tools.

## Rules

- **The person confirms every change.** The only write here is an inventory planning setting (lead time and safety buffer), saved only after the person confirms the exact shop, scope and values.
- **All conversion actions by agents are secondary.** Product Metrics creates its actions as secondary and leaves existing ones as they are. What the account bids on is the person's choice: making an action primary (and the old purchase action secondary) in Google Ads (**Goals → Conversions**, or a campaign-specific goal), and picking the conversion a Meta ad set or ChatGPT Ads campaign optimises on, is their step by every route, also when they ask you to do it. Tell them exactly what to click, wait until they say it is done, then read it back. The bidding choice belongs to the advertiser, and one primary purchase action keeps bidding right and counts every purchase once.
- Reorder dates and quantities are the planner's: report them, never order stock or pause a product or campaign.
- Insight cards describe what happened together, never a cause.
- Recommend changes as increasing or lowering priority on products, segments or campaigns.
- Stock, orders and inventory need Pro: pass a 402 `subscription_required` message on.

## 1. Connect and pick the store

MCP: `list_properties`, then pass `property_id` to every tool. CLI: `productmetrics properties list --json`. If neither is connected, send the person to https://www.productmetrics.io/docs/mcp/connect.

## 2. Pick the check for the question

| The person asks | MCP | CLI |
| --- | --- | --- |
| Are we advertising what we cannot deliver? | `get_poas_report` with `stock: "at_risk"` (or `out_of_stock`, `low_cover`) | `productmetrics inventory get-state --property-id <p> --filter reorder_due --json` |
| Which products spend while out of stock? | `list_products_to_investigate` with `signal_kinds: ["spend_while_out_of_stock", "stock_risk"]` | |
| Which Stars are about to run out? | `get_insights` with `spots: ["dashboard_run_out"]` | `productmetrics insights get --property-id <p> --spot dashboard_run_out --json` |
| What to reorder, and how much? | `get_inventory_state` with `filter: "reorder_due"` (or `item_ids`) | `productmetrics inventory get-state --property-id <p> --filter reorder_due --json` |
| Which slow movers hold too much stock? | `get_inventory_state` with `filter: "slow_movers"`; `get_poas_report` with `stock: "slow_movers"` | `productmetrics inventory get-state --property-id <p> --filter slow_movers --json` |
| Low-stock products the next settings save would put in Stars | `get_insights` with `spots: ["save_settings_stock"]` | `productmetrics insights get --property-id <p> --spot save_settings_stock --json` |
| How do returns differ by category? | `get_insights` with `spots: ["category_returns"]` | `productmetrics insights get --property-id <p> --spot category_returns --category-col <column> --json` |
| Stock and margin for one product | `get_product_context` with `detail: "detailed"` | `productmetrics store list-health-products --property-id <p> --window-days 30 --search <name> --json` |

`category_returns` needs the category column: take it from `productmetrics settings get --property-id <p> --json` (`category_cols`). Inventory list rows carry the shop's product id, variant id and SKU; `search_products` with the SKU finds the `item_id`.

## 3. Set lead times and safety buffers

The planner's reorder dates depend on the lead time (days between ordering and having stock) and the safety buffer (extra days of stock), per shop as a default, per brand or per product.

1. Read: `productmetrics inventory-settings get --property-id <p> --json`. The shop id is `effective.productSpineStoreId`.
2. Agree the exact row with the person: scope (`default`, `brand` or `product`), the brand name or platform product id, and both values.
3. After their yes:

```bash
productmetrics inventory-settings update \
  --property-id <p> \
  --store-id <productSpineStoreId> \
  --scope-kind brand --scope-value 'Acme' \
  --lead-time-days 21 --safety-buffer-days 7 \
  --json
```

It answers the saved rows and the values now in use; read them back to the person. It needs an editor or admin.

## 4. Read the results correctly

- **Low cover** means fewer weeks of cover than the lead time, or a stockout before the next delivery. **At risk** is out of stock or running out before restock.
- Insight cards have a state: `ready`, `below_threshold` (too little at stake to show) or `not_applicable` (a source is missing: say which). Quote their `dataAsOf` and footnote.
- Money in the account currency (€1,240.50).

## 5. Report back

1. **The answer**: how many advertised products are out of stock or at risk, and the ad results on them in the period.
2. **Products to act on**: name, stock on hand, weeks of cover, stockout and reorder date, suggested quantity.
3. **Returns**: the categories with the highest return rate, with the period.
4. **Options**: lower priority on products that will run out, increase priority on slow movers the person wants to clear, reorder what the planner suggests. The person decides and acts.
