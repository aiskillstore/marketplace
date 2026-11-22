# ChatGPT Ads server-side tracking (OpenAI Conversions API) on any website with Cloudflare

Source: https://www.productmetrics.io/docs/tracking/server-side/cloudflare-openai (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/cloudflare-openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every paid website purchase to your ChatGPT Ads pixel from the server, through the OpenAI Conversions API.

Every paid website purchase is confirmed from your website's own order data and sent [from Product Metrics' server](https://www.productmetrics.io/docs/concepts/server-side-tracking) to your **ChatGPT Ads pixel** as `order_created`. This is [server-side, adblocker-proof conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking).

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Connect your website and ChatGPT Ads

**Website:** add your website in Product Metrics, then sign in to Cloudflare and link the website to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).

**ChatGPT Ads:** in Ads Manager → **Conversions**, copy your **Pixel ID** and create a Conversions API key, then add both under **Tracking → OpenAI Conversions API → Connect OpenAI**. See [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai).

**You should see:** the gateway card says **Gateway setup complete**; the app says **OpenAI accepted the test event**.

### 2. Set your consent banner

On Cloudflare Tracking, Product Metrics reads consent from the banner chosen under **Tracking → Configure consent** (OneTrust, Cookiebot, Usercentrics or Osano). ChatGPT Ads has no consent mode: an event is only sent with marketing consent (ad user data). Without ad personalisation consent, the event is sent marked as opted out. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Tracking → Configure consent** names the banner your website shows.

### 3. Check it works

**Place a test order** with marketing cookies accepted through to the order confirmation page.

**You should see:** **Tracking → Check your purchases** shows **Last purchase received** within two minutes, and **Live endpoints** lists the **Tracking SDK** and **Event collector** on your domain. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## Events sent

| On any website (Cloudflare) | Sent to ChatGPT Ads as | Carries |
| --- | --- | --- |
| Paid order | `order_created` | Revenue, products, the transaction ID as `id` |
| Add to cart | `items_added` | Products, and the value when your storefront reports one |
| Checkout started | `checkout_started` | Products, and the value when your storefront reports one |
| Ad click from ChatGPT | `oppref` (from the `__oppref` cookie) | Needs ad storage consent |
| Browser | `obref` (from the `__obref` cookie), IP address, user agent | `obref` needs ad storage consent |

ChatGPT Ads accepts events up to 7 days old, so past orders are not imported, and later refunds don't revise sent events. Product Metrics still tracks the refund in your profit and lifetime value.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in ChatGPT Ads** | Check that **Tracking → Configure consent** names the banner your website actually shows: Product Metrics sends an order only with the consent this page lists. See [Consent](https://www.productmetrics.io/docs/concepts/consent). |

## FAQ

### Do I need to change my website's code for ChatGPT Ads?

No. Setup is signing in to Cloudflare: a gateway on your zone serves the Tracking SDK and Event collector on your own domain.

### Can I keep the OpenAI Pixel on my website?

Yes. OpenAI deduplicates on Pixel ID, event name and event ID, and keeps the first event it receives. `order_created` uses the order transaction ID, so it deduplicates on its own.

### Can I bid on profit in ChatGPT Ads from my website?

Yes. POAS and LTV bidding work on ChatGPT Ads. Website orders carry no product costs, so set **Product cost fallback (%)** plus your additional costs under [Costs](https://www.productmetrics.io/docs/using/costs).

### Does ChatGPT Ads get new and returning customers?

Not yet. ChatGPT Ads gets revenue, profit (POAS) and LTV through the OpenAI Conversions API; new and returning customer bidding runs in Google Ads and Meta.
