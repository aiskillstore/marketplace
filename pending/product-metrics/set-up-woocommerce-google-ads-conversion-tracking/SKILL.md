---
name: set-up-woocommerce-google-ads-conversion-tracking
description: >-
  Server-side Google Ads conversion tracking for WooCommerce (WordPress). Use this skill when a
  WooCommerce merchant wants Google Ads to see all their purchases: setting up or fixing conversion
  tracking, moving it server-side, or Google Ads counting fewer conversions than the store has
  orders because of ad blockers and browser privacy. It sends every paid order to Google Ads from
  the server as conversion actions with revenue, profit, new and returning customer and lifetime
  value. It works through Product Metrics, so use it even when Product Metrics is never mentioned.
  Not for Enhanced Conversions, Customer Match or bidding: each has its own skill, as do other store
  platforms and ad channels.
license: MIT
metadata:
  author: Product Metrics
  version: "1.2.0"
  docs: https://www.productmetrics.io/docs/tracking/server-side/woocommerce-google-ads
---

# WooCommerce server-side tracking for Google Ads

Send every purchase from your WooCommerce store to Google Ads from the server, with the script served from your own domain. Server-side sending matters because a browser pixel misses the purchases that ad blockers and browser privacy rules block, and Google Ads can only optimise on the purchases it sees.

You run the Product Metrics steps through its CLI or MCP server; the person does the steps in WooCommerce and Google Ads. The rules below say how to work with both.

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
2. **Connect the store and Google Ads** if either is missing: `references/connect-woocommerce.md` and `references/connect-google-ads.md`.
3. **Follow `references/server-side-tracking.md`** step by step and confirm each **You should see** line before you move on: later steps depend on earlier ones (the consent banner decides what is sent for each order, and checks only pass once a test order has arrived).
4. **Report back** what is live now, what the person still has to do (with the exact labels from the reference), and how to check it again later.

## References

| Read | When | Docs page |
| --- | --- | --- |
| `references/server-side-tracking.md` | Server-side tracking: prerequisites, the steps, how it works on WooCommerce, troubleshooting and FAQ | https://www.productmetrics.io/docs/tracking/server-side/woocommerce-google-ads |
| `references/connect-woocommerce.md` | The WooCommerce store isn't connected yet, or its connection is broken | https://www.productmetrics.io/docs/platforms/woocommerce |
| `references/connect-google-ads.md` | Google Ads isn't connected yet, or you need the full list of what Product Metrics sends to it | https://www.productmetrics.io/docs/channels/google-ads |

If there is no `references/` folder next to this file (the skill was installed from the docs site), fetch the docs page in the last column instead, with `.md` appended for Markdown: it has the same steps.

## Related skills

- `set-up-woocommerce-google-ads-enhanced-conversions`: Enhanced Conversions for WooCommerce in Google Ads
- `set-up-woocommerce-google-ads-customer-match`: Customer Match lists for WooCommerce in Google Ads
- `set-up-woocommerce-google-ads-new-customer-bidding`: New customer bidding for WooCommerce in Google Ads
- `set-up-woocommerce-google-ads-returning-customer-bidding`: Returning customer bidding for WooCommerce in Google Ads
- `set-up-woocommerce-google-ads-poas-bidding`: POAS and ROAS bidding for WooCommerce in Google Ads
- `set-up-woocommerce-google-ads-ltv-bidding`: LTV bidding for WooCommerce in Google Ads
- `set-up-woocommerce-meta-conversions-api`: Server-side tracking for WooCommerce in Meta
- `set-up-woocommerce-chatgpt-ads-conversions-api`: Server-side tracking for WooCommerce in ChatGPT Ads
- `check-tracking`: check every part of tracking and find a test order
- `product-metrics`: picks the right skill for any store and channel

Install: `npx skills add product-metrics/skills --skill set-up-woocommerce-google-ads-conversion-tracking`. Every skill: https://www.productmetrics.io/docs/agent-skills/platform-skills.
