---
name: bid-on-profit
description: >-
  Set up and check POAS (profit on ad spend) or ROAS bidding with Product Metrics in Google Ads and
  Meta: confirm the profit conversion actions exist, additional costs are active, the right action
  is primary, and the target ROAS fits the value sent. Use it when someone asks to "bid on profit",
  "switch to POAS", "use Product Metrics - Profit", "what target ROAS should I use", or why profit
  conversions are empty or zero. Uses the productmetrics CLI or the Product Metrics MCP server for the checks;
  making an action primary and setting a target ROAS are steps the person does in Google Ads or
  Meta.
---

# Bid on profit (POAS) or revenue (ROAS)

Product Metrics sends every paid order twice: with its **revenue** and with its **profit**. Google Ads and Meta only know "conversion value", so the bid strategy steers on whichever value is primary. Docs: https://www.productmetrics.io/docs/features/poas-bidding.

- **ROAS** = revenue ÷ ad spend, for example 4.2.
- **POAS** = profit ÷ ad spend. €300 profit on €200 spend is POAS 1.5.
- A **target ROAS** is a percentage: 420%. On the profit action, 100% is break-even and 150% means POAS 1.5.
- Recommend changes as increasing or lowering priority on products, segments or campaigns.

Use the `productmetrics` CLI with `--json` (`productmetrics status --json`), otherwise the MCP `search` and `execute` tools. Never invent ids.

**All conversion actions by agents are secondary.** Product Metrics creates its actions as secondary and leaves existing ones as they are. What the account bids on is the person's choice: making an action primary (and the old purchase action secondary) in Google Ads (**Goals → Conversions**, or a campaign-specific goal), and picking the conversion a Meta ad set or ChatGPT Ads campaign optimises on, is their step by every route, also when they ask you to do it. Tell them exactly what to click, wait until they say it is done, then read it back with `productmetrics google-ads get-conversion-actions --property-id <property_id> --json` (`goal_status`). The bidding choice belongs to the advertiser, and one primary purchase action keeps bidding right and counts every purchase once.

## 1. Pick the store

```bash
productmetrics whoami --json
```

Keep `company_id` and `property_id`.

## 2. Check the conversion actions

```bash
productmetrics google-ads get-conversion-actions --property-id <property_id> --json
```

You need **Product Metrics - Profit** (POAS) or **Product Metrics - Revenue** (ROAS) to exist and be linked. If they are missing, create them first (`set-up-tracking` skill, step 7). Product Metrics creates them as secondary, as all conversion actions by agents are.

## 3. Check additional costs (POAS only)

Profit is sent only once the additional costs are active and every cost of the order is known. Until then, orders go with revenue only. There is no API for costs: ask the person to open **Tracking** and check that the **Profit tracking** section says the additional costs are active. If not:

1. **Add your additional costs**: check shipping, handling, returns and payment fees.
2. Set **Product cost fallback (%)** for order lines without a cost price (required on Cloudflare Tracking, where website orders carry no product costs).
3. Select **Activate additional costs** (later changes: **Edit costs**, then **Activate margin policy**).

Docs: https://www.productmetrics.io/docs/using/costs.

## 4. Look at profit before switching (MCP)

When the Product Metrics MCP tools are connected, show what changes when bidding on profit:

- `get_poas_report` with `level: "campaign"`: POAS and profit after ads per campaign.
- `get_poas_report` with `level: "product"` and `only_unprofitable: true`: products that lose money after ads.

POAS for Search and Demand Gen campaigns uses the account's average margin and is marked estimated: say so.

## 5. Switch bidding (the person, in Google Ads)

This step is the person's: all conversion actions by agents are secondary. Tell the person:

1. In Google Ads, **Goals → Conversions**: make **Product Metrics - Profit** primary (or **Product Metrics - Revenue** for ROAS). Set the old purchase action to secondary so the same purchase isn't counted twice.
2. On the campaign, use **Maximise conversion value** with a **target ROAS**:
   - on profit: start near the campaign's current POAS × 100 (for example 150%); 100% is break-even;
   - on revenue: the ROAS target as a percentage (420% for 4.2).

Switching the value resets what Google Ads learned about conversion value. Suggest one campaign first. Wait until the person says it is done, then read it back with `get-conversion-actions` (step 2): `goal_status` shows which action is primary.

## 6. Meta

For ROAS, the standard `Purchase` event carries revenue. For POAS, the person creates a custom conversion in Events Manager: event `PMOrderProfit`, rule `pm_purpose` equals `ORDER_PROFIT`, category **Purchase**, value from the event, and selects it as the ad set's optimisation event themselves. Check the destination first:

```bash
productmetrics destinations list-meta --company-id <company_id> --json
```

Docs: https://www.productmetrics.io/docs/channels/meta.

## 7. After the switch

- Product Metrics Home shows **Collecting**, then compares the new actions with the old ones 14 days after the first order.
- Plan results after a campaign plan is applied: `productmetrics google-ads get-plan-results --property-id <property_id> --json`.

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| Profit action has no conversions | Additional costs not active, or an order cost unknown (no cost price and no fallback) |
| Profit is 0 on some orders | The order lost money: losses are sent as 0 |
| Conversions counted twice | Two purchase actions are primary |

## Report back

Say which value the store bids on now, whether costs are active, which action is primary (as far as the API shows: `get-conversion-actions` reports goal status), what POAS each main campaign runs at, and the exact steps left for the person.
