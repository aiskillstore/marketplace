# WooCommerce ChatGPT Ads server-side tracking (OpenAI Conversions API)

Source: https://www.productmetrics.io/docs/tracking/server-side/woocommerce-openai (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/woocommerce-openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every paid WooCommerce order to your ChatGPT Ads pixel from the server, through the OpenAI Conversions API.

Every paid WooCommerce order is confirmed from your store's own order data and sent [from Product Metrics' server](https://www.productmetrics.io/docs/concepts/server-side-tracking) to your **ChatGPT Ads pixel** as `order_created`. This is [server-side, adblocker-proof conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking).

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Connect your WooCommerce store and ChatGPT Ads

**Store:** install the **Product Metrics for WooCommerce** plugin, then paste your one-time setup token under **WooCommerce → Product Metrics** and select **Connect store**. Then link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).

**ChatGPT Ads:** in Ads Manager → **Conversions**, copy your **Pixel ID** and create a Conversions API key, then add both under **Tracking → OpenAI Conversions API → Connect OpenAI**. See [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai).

**You should see:** the plugin says **Store connected successfully.** and **Webhooks: 2 of 2 active**; the app says **OpenAI accepted the test event**.

### 2. Set your consent banner

On WooCommerce, Product Metrics reads consent from the banner chosen under **Tracking → Configure consent** (OneTrust, Cookiebot, Usercentrics or Osano). Left on **Not configured**, consent counts as not given. ChatGPT Ads has no consent mode: an event is only sent with marketing consent (ad user data). Without ad personalisation consent, the event is sent marked as opted out. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Tracking → Configure consent** names the banner your store shows.

### 3. Check it works

In WordPress, under **WooCommerce → Product Metrics**, select **Verify with next paid order**, place and pay for a test order with marketing cookies accepted within ten minutes, then select **Refresh connection status**.

**You should see:** **Live order delivery** reads **Verified**. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## Events sent

| On WooCommerce | Sent to ChatGPT Ads as | Carries |
| --- | --- | --- |
| Paid order | `order_created` | Revenue, products, the transaction ID as `id` |
| Add to cart | `items_added` | Products, and the value when your storefront reports one |
| Checkout started | `checkout_started` | Products, and the value when your storefront reports one |
| Ad click from ChatGPT | `oppref` (from the `__oppref` cookie) | Needs ad storage consent |
| Browser | `obref` (from the `__obref` cookie), IP address, user agent | `obref` needs ad storage consent |

ChatGPT Ads accepts events up to 7 days old, so past orders are not imported, and later refunds don't revise sent events.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Nothing reaches ChatGPT Ads** | Check that **Tracking → Configure consent** names the banner your store shows. Left on **Not configured**, Product Metrics can't read the visitor's choice and treats it as not given. |

## FAQ

### When does a WooCommerce order reach ChatGPT Ads?

When it reaches a status you selected under **Paid order statuses**. OpenAI accepts events up to 7 days old, so an order paid more than a week after checkout isn't sent.

### Can I keep the OpenAI Pixel on WooCommerce?

Yes. OpenAI deduplicates on Pixel ID, event name and event ID, and keeps the first event it receives. `order_created` uses the order transaction ID, so it deduplicates on its own. `items_added` and `checkout_started` need your developer to pass Product Metrics' event ID to the pixel.

### Can I bid on profit in ChatGPT Ads?

Yes. POAS and LTV bidding work on ChatGPT Ads: see [POAS bidding on WooCommerce in ChatGPT Ads](https://www.productmetrics.io/docs/bidding/poas/woocommerce-openai).

### Does ChatGPT Ads get new and returning customers?

Not yet. ChatGPT Ads gets revenue, profit (POAS) and LTV through the OpenAI Conversions API; new and returning customer bidding runs in Google Ads and Meta.
