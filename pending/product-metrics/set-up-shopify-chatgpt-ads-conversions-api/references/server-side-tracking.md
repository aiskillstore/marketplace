# Shopify ChatGPT Ads server-side tracking (OpenAI Conversions API)

Source: https://www.productmetrics.io/docs/tracking/server-side/shopify-openai (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/shopify-openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every paid Shopify order to your ChatGPT Ads pixel from the server, through the OpenAI Conversions API.

Every paid Shopify order is confirmed from your store's own order data and sent [from Product Metrics' server](https://www.productmetrics.io/docs/concepts/server-side-tracking) to your **ChatGPT Ads pixel** as `order_created`. This is [server-side, adblocker-proof conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking).

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics.
- **Your Shopify store connected**: a Shopify login that can install apps and edit the theme, the Product Metrics app installed with its app embed on, the store linked to your property, and your subscription started in the app with **Create subscription** (billed through Shopify). See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Connect your Shopify store and ChatGPT Ads

**Store:** install the Product Metrics app from the Shopify App Store, select **Link Shopify store** and turn on its app embed and link it to your property. See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).

**ChatGPT Ads:** in Ads Manager → **Conversions**, copy your **Pixel ID** and create a Conversions API key, then add both under **Tracking → OpenAI Conversions API → Connect OpenAI**. See [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai).

**You should see:** the Shopify app says **You're set up**, with ticks for **Shopify permissions**, **App embed** and **Checkout pixel**; the app says **OpenAI accepted the test event**.

### 2. Set your consent banner

On Shopify, Product Metrics reads consent from **Shopify Customer Privacy** (choose it under **Tracking → Configure consent**). ChatGPT Ads has no consent mode: an event is only sent with marketing consent (ad user data). Without ad personalisation consent, the event is sent marked as opted out. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Tracking → Configure consent** names the banner your store shows.

### 3. Check it works

In the Shopify app, open **Tracking** in the app menu and select **Run tracking test**: each check shows **Passing**, **Needs attention** or **Listening**. Then **place and pay for a test order** with marketing cookies accepted; it is sent once Shopify marks it paid.

**You should see:** **Tracking is live on your store**, which means Product Metrics has seen your storefront. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## Events sent

| On Shopify | Sent to ChatGPT Ads as | Carries |
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
| **Orders are missing in ChatGPT Ads** | Check that **Tracking → Configure consent** names the banner your store actually shows: Product Metrics sends an order only with the consent this page lists. See [Consent](https://www.productmetrics.io/docs/concepts/consent). |

## FAQ

### Do I need a script tag for ChatGPT Ads on Shopify?

No. The app embed loads the script through Shopify's app proxy under `/apps/` on your store domain, and the app's checkout pixel reports the purchase.

### Can I keep the OpenAI Pixel on my Shopify store?

Yes. OpenAI deduplicates on Pixel ID, event name and event ID, and keeps the first event it receives. `order_created` uses the order transaction ID, so it deduplicates on its own.

### Can I bid on profit in ChatGPT Ads?

Yes. POAS and LTV bidding work on ChatGPT Ads: see [POAS bidding on Shopify in ChatGPT Ads](https://www.productmetrics.io/docs/bidding/poas/shopify-openai).

### Does ChatGPT Ads get new and returning customers?

Not yet. ChatGPT Ads gets revenue, profit (POAS) and LTV through the OpenAI Conversions API; new and returning customer bidding runs in Google Ads and Meta.
