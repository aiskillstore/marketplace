---
name: set-up-cloudflare-chatgpt-ads-conversions-api
description: >-
  ChatGPT Ads conversion tracking for any website on Cloudflare (Cloudflare Tracking, no store
  plugin) through the OpenAI Conversions API. Use this skill when a merchant with a website on
  Cloudflare advertising on ChatGPT wants their purchases tracked: connecting the OpenAI Conversions
  API or the ChatGPT Ads pixel. It sends every paid order to ChatGPT Ads from the server, with
  revenue, profit, new and returning customer and lifetime value events. It works through Product
  Metrics, so use it even when Product Metrics is never mentioned. Not for customer data matching or
  bidding: each has its own skill, as do other store platforms and ad channels.
license: MIT
metadata:
  author: Product Metrics
  version: "1.2.0"
  docs: https://www.productmetrics.io/docs/tracking/server-side/cloudflare-openai
---

# ChatGPT Ads server-side tracking (OpenAI Conversions API) on any website with Cloudflare

Send every paid website purchase to your ChatGPT Ads pixel from the server, through the OpenAI Conversions API. Server-side sending matters because a browser pixel misses the purchases that ad blockers and browser privacy rules block, and ChatGPT Ads can only optimise on the purchases it sees.

You run the Product Metrics steps through its CLI or MCP server; the person does the steps in Cloudflare and ChatGPT Ads. The rules below say how to work with both.

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
2. **Connect the store and ChatGPT Ads** if either is missing: `references/connect-cloudflare.md` and `references/connect-chatgpt-ads.md`.
3. **Follow `references/server-side-tracking.md`** step by step and confirm each **You should see** line before you move on: later steps depend on earlier ones (the consent banner decides what is sent for each order, and checks only pass once a test order has arrived).
4. **Report back** what is live now, what the person still has to do (with the exact labels from the reference), and how to check it again later.

## References

| Read | When | Docs page |
| --- | --- | --- |
| `references/server-side-tracking.md` | Server-side tracking: prerequisites, the steps, how it works on any website on Cloudflare, troubleshooting and FAQ | https://www.productmetrics.io/docs/tracking/server-side/cloudflare-openai |
| `references/connect-cloudflare.md` | The website isn't connected yet, or its connection is broken | https://www.productmetrics.io/docs/platforms/cloudflare |
| `references/connect-chatgpt-ads.md` | ChatGPT Ads isn't connected yet, or you need the full list of what Product Metrics sends to it | https://www.productmetrics.io/docs/channels/openai |

If there is no `references/` folder next to this file (the skill was installed from the docs site), fetch the docs page in the last column instead, with `.md` appended for Markdown: it has the same steps.

## Related skills

- `set-up-cloudflare-chatgpt-ads-customer-matching`: Customer data matching for any website on Cloudflare in ChatGPT Ads
- `set-up-cloudflare-chatgpt-ads-poas-bidding`: POAS and ROAS bidding for any website on Cloudflare in ChatGPT Ads
- `set-up-cloudflare-chatgpt-ads-ltv-bidding`: LTV bidding for any website on Cloudflare in ChatGPT Ads
- `set-up-cloudflare-google-ads-conversion-tracking`: Server-side tracking for any website on Cloudflare in Google Ads
- `set-up-cloudflare-meta-conversions-api`: Server-side tracking for any website on Cloudflare in Meta
- `check-tracking`: check every part of tracking and find a test order
- `product-metrics`: picks the right skill for any store and channel

Install: `npx skills add product-metrics/skills --skill set-up-cloudflare-chatgpt-ads-conversions-api`. Every skill: https://www.productmetrics.io/docs/agent-skills/platform-skills.
