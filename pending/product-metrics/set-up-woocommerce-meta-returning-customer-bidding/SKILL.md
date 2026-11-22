---
name: set-up-woocommerce-meta-returning-customer-bidding
description: >-
  Returning customer bidding for WooCommerce (WordPress) in Meta. Use this skill when a WooCommerce
  merchant wants retention or win-back campaigns in Meta that value repeat orders. It sends every
  paid repeat order as a returning customer conversion, with its revenue or profit, to bid on. It
  works through Product Metrics, so use it even when Product Metrics is never mentioned. Not for new
  customer, POAS or LTV bidding: each has its own skill, as do other store platforms and ad
  channels.
license: MIT
metadata:
  author: Product Metrics
  version: "1.2.0"
  docs: https://www.productmetrics.io/docs/bidding/returning-customers/woocommerce-meta
---

# WooCommerce returning customer bidding in Meta

Send repeat orders from WooCommerce to Meta as PMReturningCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion. It matters because a retention campaign should value repeat orders, and only those.

You run the Product Metrics steps through its CLI or MCP server; the person does the steps in WooCommerce and Meta. The rules below say how to work with both.

## Rules

- **All conversion actions by agents are secondary**, the status Product Metrics creates its actions with. Choosing what a campaign bids or optimises on (making an action primary, or picking the Meta or ChatGPT Ads conversion) is the person's step, by every route and also when they ask: give them the exact clicks, wait until they say it is done, then read it back.
- **Pick the interface in this order:** the `productmetrics` CLI (check with `productmetrics status --json`, pass `--json` to every command, and run `productmetrics <group> <command> --help --json` before one you have not used); then the Product Metrics MCP server (`https://www.productmetrics.io/mcp`: `search` the API spec, then `execute`; never guess a path or body); otherwise the app steps in https://app.productmetrics.io.
- **Read where setup stands first:** `productmetrics setup get-status --json` (MCP: `setup.get_status`). Read `journey_stage` and the `next_action` fields, read it again with `--company-id` and `--property-id` once you know them, skip every step that is done and tell the person which ones are.
- **Discover ids, never invent them.** `company_id`, `property_id`, installation and scope ids come from earlier results.
- **Writes:** pass `--auto-idempotency-key` (MCP: `idempotencyKey: crypto.randomUUID()`) where the command's `--help` lists it, and retry a failed write with the key the error hint names. Other writes take no key: read the state before you retry.
- **Browser steps:** exit code 4 or `next_action: { "type": "browser", "url": … }` means the person opens the URL. Say what they will see, wait until they say they are done, then read the state again. A WooCommerce or Shopware 6 store returns `"type": "store_plugin"` instead: the person pastes the setup token into the Product Metrics plugin in their store admin before it expires.
- **Steps in the store admin or ad platform are the person's:** give them the exact labels from the reference or docs page.
- **Secrets:** never ask for, print or store passwords, tokens or API keys, except a credential the API needs from the person (the Lightspeed API key and secret, the Meta Conversions API access token, the OpenAI Conversions API key). Pass it straight to the command and never repeat it, log it or put it in a summary.
- **Deletes** only when the person explicitly asks.
- **"Ask your assistant" steps are yours.** Answer them with `productmetrics orders list --company-id <company_id> --storefront-scope-id <scope_id> --json` (MCP: `orders.list`, newest first) and `productmetrics orders get --company-id <company_id> --order-id <order_id> --storefront-scope-id <scope_id> --json` (MCP: `orders.get`), which shows an order's margin and whether its customer was new or returning.
- **Talk to a store owner, not a developer:** short sentences, what you did, what they need to do, what comes next. ROAS is a plain number (4.2); a target ROAS is a percentage (420%). Recommend increasing or lowering priority, never "raise or cut bids".
- The long form of these rules: https://www.productmetrics.io/docs/cli/for-agents.

## Workflow

1. **Read where setup stands** with `productmetrics setup get-status --json` (MCP: `setup.get_status`), and skip every step that is done.
2. **Make sure server-side tracking to Meta is live.** If it isn't, set it up first with `set-up-woocommerce-meta-conversions-api` (or `references/connect-woocommerce.md` and `references/connect-meta.md`).
3. **Follow `references/returning-customer-bidding.md`** step by step and confirm each **You should see** line before you move on: later steps depend on earlier ones (the consent banner decides what is sent for each order, and checks only pass once a test order has arrived).
4. **Hand the switch to the person.** They create the custom conversion in Meta Events Manager and select it as the ad set's optimisation event, with the labels from the reference. This step is theirs. Wait until they say it is done.
5. **Agree the target** with the facts below, and suggest one campaign first.
6. **Report back** what is live now, what the person still has to do (with the exact labels from the reference), and how to check it again later.

## Target ROAS facts

- A target ROAS is a percentage of the value sent. On a profit value, 100% is break-even and 150% keeps €0.50 profit per €1 of ad spend.
- An order with an unknown cost goes with revenue only; a loss-making order's profit is sent as 0.
- Usually only the campaign that serves returning customers bids on this value; the others keep their current goal.
- In Meta, the person optimises on a custom conversion built on the Product Metrics event for this goal (for profit: `PMOrderProfit` with the rule `pm_purpose` equals `ORDER_PROFIT`), which they select themselves. An event only appears in Meta's selector after Meta has received one, so a test order comes first.

## References

| Read | When | Docs page |
| --- | --- | --- |
| `references/returning-customer-bidding.md` | Returning customer bidding: prerequisites, the steps, how it works on WooCommerce, troubleshooting and FAQ | https://www.productmetrics.io/docs/bidding/returning-customers/woocommerce-meta |
| `references/connect-woocommerce.md` | The WooCommerce store isn't connected yet, or its connection is broken | https://www.productmetrics.io/docs/platforms/woocommerce |
| `references/connect-meta.md` | Meta isn't connected yet, or you need the full list of what Product Metrics sends to it | https://www.productmetrics.io/docs/channels/meta |

If there is no `references/` folder next to this file (the skill was installed from the docs site), fetch the docs page in the last column instead, with `.md` appended for Markdown: it has the same steps.

## Related skills

- `set-up-woocommerce-meta-conversions-api`: Server-side tracking for WooCommerce in Meta
- `set-up-woocommerce-meta-advanced-matching`: Advanced Matching for WooCommerce in Meta
- `set-up-woocommerce-meta-new-customer-bidding`: New customer bidding for WooCommerce in Meta
- `set-up-woocommerce-meta-poas-bidding`: POAS and ROAS bidding for WooCommerce in Meta
- `set-up-woocommerce-meta-ltv-bidding`: LTV bidding for WooCommerce in Meta
- `set-up-woocommerce-google-ads-returning-customer-bidding`: Returning customer bidding for WooCommerce in Google Ads
- `bid-on-profit`: check POAS or ROAS bidding on any store
- `product-metrics`: picks the right skill for any store and channel

Install: `npx skills add product-metrics/skills --skill set-up-woocommerce-meta-returning-customer-bidding`. Every skill: https://www.productmetrics.io/docs/agent-skills/platform-skills.
