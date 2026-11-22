---
name: set-up-shopware-google-ads-new-customer-bidding
description: >-
  New customer bidding (new customer acquisition) for Shopware in Google Ads. Use this skill when a
  Shopware merchant wants Google Ads to win new buyers instead of people who would buy anyway: new
  customer acquisition, or campaigns that keep spending on existing customers. It sends each
  customer's first paid order as a separate new customer conversion, with its revenue or profit, to
  bid on. It works through Product Metrics, so use it even when Product Metrics is never mentioned.
  Not for POAS, returning customer or LTV bidding: each has its own skill, as do other store
  platforms and ad channels.
license: MIT
metadata:
  author: Product Metrics
  version: "1.2.0"
  docs: https://www.productmetrics.io/docs/bidding/new-customers/shopware-google-ads
---

# Shopware new customer acquisition bidding in Google Ads

Send first orders from Shopware to Google Ads as Product Metrics - New Customer and bid on them with a target ROAS. It matters because a purchase conversion values a repeat buyer the same as a new one, so Google Ads keeps spending on people who would buy anyway.

You run the Product Metrics steps through its CLI or MCP server; the person does the steps in Shopware and Google Ads. The rules below say how to work with both.

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
2. **Make sure server-side tracking to Google Ads is live.** If it isn't, set it up first with `set-up-shopware-google-ads-conversion-tracking` (or `references/connect-shopware.md` and `references/connect-google-ads.md`).
3. **Follow `references/new-customer-bidding.md`** step by step and confirm each **You should see** line before you move on: later steps depend on earlier ones (the consent banner decides what is sent for each order, and checks only pass once a test order has arrived).
4. **Hand the switch to the person.** They make the action they bid on primary and the old purchase action secondary in Google Ads (**Goals → Conversions**, or a campaign-specific goal), with the labels from the reference. This step is theirs. Wait until they say it is done, then read it back with `productmetrics google-ads get-conversion-actions --property-id <property_id> --json` (`goal_status`).
5. **Agree the target** with the facts below, and suggest one campaign first: switching the value resets what Google Ads learned about conversion value.
6. **Report back** what is live now, what the person still has to do (with the exact labels from the reference), and how to check it again later.

## Target ROAS facts

- A target ROAS is a percentage of the value sent. On a profit value, 100% is break-even and 150% keeps €0.50 profit per €1 of ad spend.
- An order with an unknown cost goes with revenue only; a loss-making order's profit is sent as 0.
- On the new customer profit value, 100% breaks even on the first order; the customer's later orders come on top.
- In Google Ads, the person keeps **one** purchase action primary: the Product Metrics action they bid on. They set the old purchase action to secondary (or use a campaign-specific goal), so every purchase is counted once. Product Metrics creates its actions as secondary, as every conversion action by an agent is.

## References

| Read | When | Docs page |
| --- | --- | --- |
| `references/new-customer-bidding.md` | New customer bidding: prerequisites, the steps, how it works on Shopware, troubleshooting and FAQ | https://www.productmetrics.io/docs/bidding/new-customers/shopware-google-ads |
| `references/connect-shopware.md` | The Shopware store isn't connected yet, or its connection is broken | https://www.productmetrics.io/docs/platforms/shopware |
| `references/connect-google-ads.md` | Google Ads isn't connected yet, or you need the full list of what Product Metrics sends to it | https://www.productmetrics.io/docs/channels/google-ads |

If there is no `references/` folder next to this file (the skill was installed from the docs site), fetch the docs page in the last column instead, with `.md` appended for Markdown: it has the same steps.

## Related skills

- `set-up-shopware-google-ads-conversion-tracking`: Server-side tracking for Shopware in Google Ads
- `set-up-shopware-google-ads-enhanced-conversions`: Enhanced Conversions for Shopware in Google Ads
- `set-up-shopware-google-ads-customer-match`: Customer Match lists for Shopware in Google Ads
- `set-up-shopware-google-ads-returning-customer-bidding`: Returning customer bidding for Shopware in Google Ads
- `set-up-shopware-google-ads-poas-bidding`: POAS and ROAS bidding for Shopware in Google Ads
- `set-up-shopware-google-ads-ltv-bidding`: LTV bidding for Shopware in Google Ads
- `set-up-shopware-meta-new-customer-bidding`: New customer bidding for Shopware in Meta
- `bid-on-profit`: check POAS or ROAS bidding on any store
- `product-metrics`: picks the right skill for any store and channel

Install: `npx skills add product-metrics/skills --skill set-up-shopware-google-ads-new-customer-bidding`. Every skill: https://www.productmetrics.io/docs/agent-skills/platform-skills.
