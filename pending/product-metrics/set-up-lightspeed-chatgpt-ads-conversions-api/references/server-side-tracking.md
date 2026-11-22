# Lightspeed ChatGPT Ads server-side tracking (OpenAI Conversions API)

Source: https://www.productmetrics.io/docs/tracking/server-side/lightspeed-openai (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/lightspeed-openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every paid Lightspeed order to your ChatGPT Ads pixel from the server, through the OpenAI Conversions API.

Every paid Lightspeed order is confirmed from your shop's own order data and sent [from Product Metrics' server](https://www.productmetrics.io/docs/concepts/server-side-tracking) to your **ChatGPT Ads pixel** as `order_created`. This is [server-side, adblocker-proof conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking).

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your Lightspeed eCom (C-Series) shop connected**: a back-office administrator login (an API key can't sign in), the shop's cluster, hostname and numeric Shop ID, and an enabled API key with its secret that has Read on Content, Products, Customers and Orders, and Read and Write on Settings and Tracking. The shop can't already be connected to another workspace, and it reads **Active** with **Configuration is current** before you link your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).
- **Your shop domain on Cloudflare**, with its DNS record proxied (the orange cloud), and a workspace admin who signs in to Cloudflare once.
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Connect your Lightspeed shop and ChatGPT Ads

**Store:** add a Lightspeed API key in Product Metrics and sign in to Cloudflare for the gateway, then link the shop to your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).

**ChatGPT Ads:** in Ads Manager → **Conversions**, copy your **Pixel ID** and create a Conversions API key, then add both under **Tracking → OpenAI Conversions API → Connect OpenAI**. See [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai).

**You should see:** **Connection status**, **Credential status** and **Installation status** read **Active**, **Configured** and **Active**, publication reads **Configuration is current**, and the gateway says **Gateway setup complete**; the app says **OpenAI accepted the test event**.

### 2. Set your consent banner

On Lightspeed, Product Metrics reads consent from the banner chosen under **Tracking → Configure consent** (OneTrust, Cookiebot, Usercentrics or Osano). ChatGPT Ads has no consent mode: an event is only sent with marketing consent (ad user data). Without ad personalisation consent, the event is sent marked as opted out. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Tracking → Configure consent** names the banner your shop shows.

### 3. Check it works

In **Tracking**, open the **Tracking SDK** link under the Cloudflare gateway's **Live endpoints**: it returns JavaScript (the collector only accepts POST requests). Then **place and pay for a test order** with marketing cookies accepted.

**You should see:** **Live endpoints** lists the **Tracking SDK** and **Event collector** on your shop domain, and the order appears for the linked property. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## Events sent

| On Lightspeed | Sent to ChatGPT Ads as | Carries |
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

### When is a pay-on-pickup order sent to ChatGPT Ads?

When Lightspeed marks it paid. OpenAI accepts events up to 7 days old, so an order paid more than a week after checkout isn't sent.

### Can I keep the OpenAI Pixel on my Lightspeed shop?

Yes. OpenAI deduplicates on Pixel ID, event name and event ID, and keeps the first event it receives. `order_created` uses the order transaction ID, so it deduplicates on its own.

### Can I bid on profit in ChatGPT Ads?

Yes. POAS and LTV bidding work on ChatGPT Ads: see [POAS bidding on Lightspeed in ChatGPT Ads](https://www.productmetrics.io/docs/bidding/poas/lightspeed-openai).

### Does ChatGPT Ads get new and returning customers?

Not yet. ChatGPT Ads gets revenue, profit (POAS) and LTV through the OpenAI Conversions API; new and returning customer bidding runs in Google Ads and Meta.
