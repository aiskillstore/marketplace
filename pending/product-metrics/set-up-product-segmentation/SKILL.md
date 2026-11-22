---
name: set-up-product-segmentation
description: >-
  Set up and tune Product Segmentation in Product Metrics for Google Shopping and Performance Max:
  which Merchant Center custom label carries the segments and the category priority, the
  segmentation settings (date range, category column, excluded campaigns, margin or POAS, a target
  ROAS anchor, seasonality and competitor prices), product rules that set or lock a segment, and
  generating the supplemental feed. Use this skill when a merchant wants to segment products into
  custom labels, move the segments to another custom label, judge products on margin instead of
  revenue, keep a product line in Stars during a sale, or leave a campaign out of the segments. It
  previews every change and saves only the exact change the person confirmed. It works through Product Metrics, so use it even when Product
  Metrics is never mentioned. Not for connecting Merchant Center or Google Ads
  (connect-google-ads), reading the segments (check-product-segments), or building campaigns on
  them (check-campaign-structure).
license: MIT
metadata:
  author: Product Metrics
  version: "1.0.0"
  docs: https://www.productmetrics.io/docs/api/settings
---

# Set up and tune Product Segmentation

Product Metrics machine learning places every product in one of six segments on profitability, stock, product returns, potential and competitor prices, and writes the segment (and a category priority) to Merchant Center custom labels through a supplemental feed. Shopping and Performance Max campaigns filter on those labels. This skill changes what the segments are based on and where they go. Reference: https://www.productmetrics.io/docs/api/settings and https://www.productmetrics.io/docs/cli/commands#settings.

## Rules

- **The person confirms every change.** Read first, preview the change, show the person exactly what you will send and what the preview says it moves, and save only after their yes to that exact change. Never change settings, product rules or the feed on your own initiative, and never widen a change beyond what they approved.
- **All conversion actions by agents are secondary.** Product Metrics creates its actions as secondary and leaves existing ones as they are. What the account bids on is the person's choice: making an action primary (and the old purchase action secondary) in Google Ads (**Goals → Conversions**, or a campaign-specific goal), and picking the conversion a Meta ad set or ChatGPT Ads campaign optimises on, is their step by every route, also when they ask you to do it. Tell them exactly what to click, wait until they say it is done, then read it back. The bidding choice belongs to the advertiser, and one primary purchase action keeps bidding right and counts every purchase once.
- Use the `productmetrics` CLI with `--json`; otherwise the MCP `search` and `execute` tools with the operation ids in brackets. Add `--dry-run` to print a write without sending it. Ids come from earlier results, never from guesses.
- Saves need the `write` scope and an editor or admin; the feed needs a Product Segmentation subscription. Pass any `subscription_required` or `insufficient_scope` message on.
- Leave `--feed-scope` out for the property's default feed. Pass a feed id only when an earlier result gave one; previews refuse `all`.
- Explain segments on profitability and potential, never by clicks. Recommend changes as increasing or lowering priority.

## 1. Pick the store and check Merchant Center

```bash
productmetrics properties list --json
productmetrics merchant-center get-auto-setup-status --property-id <p> --json
```

If Merchant Center is not connected or its feed sources are not set up, use the `connect-google-ads` skill first.

## 2. Read the current state

| Read | Command (operation) |
| --- | --- |
| Settings and `settings_version` | `productmetrics settings get --property-id <p> --json` (`settings.get`) |
| Which custom labels the feed writes | `productmetrics feed-source-settings get --property-id <p> --json` (`feed_source_settings.get`) |
| Product rules, in the order they apply | `productmetrics product-rules list --property-id <p> --json` (`product_rules.list`) |
| What the rules move | `productmetrics product-rules get-impact --property-id <p> --json` (`product_rules.get_impact`) |

`preview: true` in the feed source settings means no Product Segmentation subscription: settings can be read, but no feed is generated.

## 3. Choose the custom labels

The segment and the category priority each go to one of `custom_label_0` to `custom_label_4`. To change that, after the person confirms the labels:

```bash
productmetrics feed-source-settings update \
  --property-id <p> \
  --product-segment '{"enabled":true,"target_custom_label":"custom_label_0"}' \
  --category-priority '{"enabled":true,"target_custom_label":"custom_label_1"}' \
  --if-match '"<settings_version>"' \
  --json
```

A label that already holds the store's own values is refused unless `force_override` is true. Overwriting it replaces those values for every product: ask about that explicitly. Campaigns that filter on the old label stop matching: check them with `check-campaign-structure` and tell the person what to change in Google Ads.

## 4. Tune the settings

| The person wants to | Change in `labelizer_settings` |
| --- | --- |
| Base segments on a longer or shorter period | `data_range`: `L7D`, `L14D`, `L30D`, `L45D`, `L60D`, `L75D`, `L90D`, `L180D` or `L365D` |
| Use another category column | `category_cols` (the first is used) and `category_col_source` (`auto` or `merchant`) |
| Leave a campaign's results out | `excluded_campaign_ids` (Google Ads campaign ids) |
| Judge products on margin (POAS) instead of revenue | `strategy_adjustments.margin_poas.enabled` |
| Anchor the segments on their target ROAS | `strategy_adjustments.target_anchor` with `enabled` and `target_roas` |
| Take seasonality or competitor prices into account | `strategy_adjustments.seasonality.enabled`, `strategy_adjustments.price_ratio.enabled` |
| Require more or less evidence before a product changes segment | `min_clicks`; `productmetrics settings recommend-min-clicks --property-id <p> --json` computes a recommended value (up to a minute; 429 means it is already running) |

Send every other field (`weights`, `auto_optimized`, `saved_at`, `saved_by_user_id`, the inventory adjustment) back as `settings get` returned it.

1. Save `data.labelizer_settings` from `settings get` to `draft.json` and change only the agreed fields.
2. Preview without saving:
   - `productmetrics settings preview --property-id <p> --body-file draft.json --json` (`settings.preview`): products and revenue per segment under the draft;
   - for `strategy_adjustments`, `productmetrics settings preview-strategy --property-id <p> --body-file draft.json --json` (`settings.preview_strategy`): how many products would move between segments compared with the published feed, and Stars that are out of stock.
3. Show the person the field changes and the segment moves side by side. Wait for their yes.
4. Save `{ "labelizer_settings": <draft> }` to `new-settings.json`, then:

```bash
productmetrics settings update \
  --property-id <p> \
  --body-file new-settings.json \
  --if-match '"<settings_version>"' \
  --json
```

A 409 `settings_conflict` means someone else saved in between: read again, reapply the agreed change, and ask again if the result differs.

## 5. Product rules

A rule sets the segment or category priority of the products its conditions match (`--action =` with `--action-value`, for example `stars`), or locks their current segment until a date (`--action keep` with `active_until`). Rules apply in order, after the existing ones.

1. Preview the conditions: `productmetrics product-rules preview --property-id <p> --when-cols custom_label_0 --when-ops == --when-vals Shoes --json` (`product_rules.preview`). For the moves the rule would cause, send `draft_rule` and `include_moves: true` in `--body`.
2. Show the matched products and moves; wait for the person's yes.
3. Create it (`product_rules.create`):

```bash
productmetrics product-rules create \
  --property-id <p> \
  --name 'Lock Stars during the winter sale' \
  --when-cols custom_label_0 --when-ops == --when-vals Shoes \
  --target-cols product_segment \
  --action = --action-value stars \
  --json
```

To test without a rule, `product-rules toggle` switches it off instead of deleting it. `product-rules update`, `reorder` and `delete` change existing rules; `delete` cannot be undone, so run it only when the person asks for that rule to go (`--yes`).

## 6. Push the change to the feed

Saved settings and rules reach the feed at the nightly run. If the person wants it now: `productmetrics feed generate --property-id <p> --json` (`feed.generate`; 429 means a run is already in progress).

## 7. Report back

Read the state back (`settings get`, `product-rules get-impact`) and tell the person: what changed, field by field; how many products moved between segments per the preview; which custom labels carry the segment and category priority; when the feed updates; and anything they still need to change in Google Ads campaigns.
