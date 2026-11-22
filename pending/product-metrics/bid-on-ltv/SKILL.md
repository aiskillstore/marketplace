---
name: bid-on-ltv
description: >-
  Set up LTV bidding: send each customer's lifetime revenue and profit to Google Ads, Meta and
  ChatGPT Ads with every paid order, and bid on customer lifetime value instead of the first order.
  Uses Product Metrics, which builds lifetime value from the store's own order history (Shopify,
  WooCommerce, Lightspeed, Magento, Shopware or any website on Cloudflare). Use this skill whenever
  someone asks about LTV bidding, customer lifetime value or CLV bidding, value-based bidding on
  long-term value, or optimising for repeat buyers' total spend, even if they never name Product
  Metrics.
license: MIT
metadata:
  author: Product Metrics
  version: "1.2.0"
  docs: https://www.productmetrics.io/docs/features/ltv-bidding
---

# LTV bidding: bid on customer lifetime value in Google Ads, Meta and ChatGPT Ads

Send each customer's lifetime revenue and profit to Google Ads, Meta and ChatGPT Ads with every paid order, and bid on customers who come back.

You run the Product Metrics steps through its CLI or MCP server; the person does the steps in the ad platform. The rules below say how to work with both.

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

1. **Explain how it works** from `references/ltv-bidding.md`: what counts, what is sent, and the rules. Read it before you answer questions about it.
2. **Find the store platform and channel** with `productmetrics setup get-status --json` (MCP: `setup.get_status`).
3. **Follow the steps for that store and channel**: the matching skill below if it is installed, otherwise its docs page (append `.md` for Markdown). The steps differ per store (where the order history comes from) and per channel (conversion action or event).
4. **Hand the switch to the person.** Making the action primary in Google Ads (and the old purchase action secondary), or selecting the conversion a Meta ad set or ChatGPT Ads campaign optimises on, is their step: give them the exact clicks, wait until they say it is done, then read it back.
5. **Report back** which value the campaign bids on now and the exact steps left for the person.

## Steps for each store and channel

| Store | Skill and docs page |
| --- | --- |
| Shopify | `set-up-shopify-google-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/shopify-google-ads)<br>`set-up-shopify-meta-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/shopify-meta)<br>`set-up-shopify-chatgpt-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/shopify-openai) |
| WooCommerce | `set-up-woocommerce-google-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/woocommerce-google-ads)<br>`set-up-woocommerce-meta-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/woocommerce-meta)<br>`set-up-woocommerce-chatgpt-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/woocommerce-openai) |
| Lightspeed | `set-up-lightspeed-google-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/lightspeed-google-ads)<br>`set-up-lightspeed-meta-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/lightspeed-meta)<br>`set-up-lightspeed-chatgpt-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/lightspeed-openai) |
| Magento | `set-up-magento-google-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/magento-google-ads)<br>`set-up-magento-meta-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/magento-meta)<br>`set-up-magento-chatgpt-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/magento-openai) |
| Shopware | `set-up-shopware-google-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/shopware-google-ads)<br>`set-up-shopware-meta-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/shopware-meta)<br>`set-up-shopware-chatgpt-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/shopware-openai) |
| Cloudflare | `set-up-cloudflare-google-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/cloudflare-google-ads)<br>`set-up-cloudflare-meta-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/cloudflare-meta)<br>`set-up-cloudflare-chatgpt-ads-ltv-bidding` (https://www.productmetrics.io/docs/bidding/ltv/cloudflare-openai) |

## References

| Read | When | Docs page |
| --- | --- | --- |
| `references/ltv-bidding.md` | How it works, the rules per channel and platform, and the FAQ | https://www.productmetrics.io/docs/features/ltv-bidding |

If there is no `references/` folder next to this file (the skill was installed from the docs site), fetch the docs page in the last column instead, with `.md` appended for Markdown: it has the same steps.

Install: `npx skills add product-metrics/skills --skill bid-on-ltv`. Every skill: https://www.productmetrics.io/docs/agent-skills/platform-skills.
