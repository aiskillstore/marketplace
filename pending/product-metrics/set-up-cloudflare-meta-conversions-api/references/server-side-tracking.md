# Server-side tracking with the Meta Conversions API on any website with Cloudflare

Source: https://www.productmetrics.io/docs/tracking/server-side/cloudflare-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/cloudflare-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your website to Meta from the server through the Meta Conversions API, with Advanced Matching and the script served from your own domain.

Each purchase is confirmed from **the purchase your order confirmation page reports** and sent to your Meta pixel [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through the **Meta Conversions API**. Nothing in the browser talks to Meta, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/cloudflare-meta).

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking).
- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).
- **Access to your pixel in Meta Events Manager**, to copy its ID and generate a Conversions API access token.

## In the app

### 1. Connect your website and Meta

**Website:** add your website in Product Metrics, then sign in to Cloudflare and link the website to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).

**Meta:** in Events Manager, copy your **Pixel or Dataset ID** and generate a Conversions API access token, then add both under **Tracking → Meta Conversions API → Connect Meta** and send a test event. See [Meta](https://www.productmetrics.io/docs/channels/meta).

**You should see:** the gateway card says **Gateway setup complete**; Events Manager shows the test event under **Test events**.

### 2. Choose your consent banner

In Product Metrics, open **Tracking → Configure consent** and choose the banner your website shows: OneTrust, Cookiebot, Usercentrics or Osano. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

> **Warning:** Meta has no consent mode. Product Metrics sends an event only when the visitor allowed ad user data; the custom events also need analytics consent. A wrong banner here means nothing reaches Meta.

**You should see:** **Configure consent** names the banner your website actually shows.

### 3. Create custom conversions

In Events Manager, create a custom conversion for each Product Metrics value you want to bid on, with the rule `pm_purpose` equals the purpose: `PMOrderRevenue` (`ORDER_REVENUE`) for revenue, `PMOrderProfit` (`ORDER_PROFIT`) for profit, every other event in [Meta events](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#meta-events). Follow [Create custom conversions in Meta](https://www.productmetrics.io/docs/using/conversion-actions#custom-conversions-in-meta) once a test order has reached Meta.

**You should see:** your custom conversions show in Events Manager.

### 4. Check it works

**Place a test order** through to the order confirmation page.

**You should see:** **Tracking → Check your purchases** shows **Last purchase received** within two minutes, and **Live endpoints** lists the **Tracking SDK** and **Event collector** on your domain; in Events Manager, the order shows as `Purchase`, plus the Product Metrics custom events your visitor's consent allows. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on a website

| | On a website |
| --- | --- |
| **Script and collector served by** | A Cloudflare gateway (a Worker on your website's Cloudflare zone) that serves the **Tracking SDK** and **Event collector** on your own domain. Setup is only signing in to Cloudflare: no code, and Product Metrics never changes your DNS |
| **Purchase confirmed from** | The purchase your order confirmation page reports |
| **Sent** | When your order confirmation page reports the purchase; if it reports the same order twice, the first report wins |
| **Delivered** | Server-side, through the Meta Conversions API: `Purchase` plus the Product Metrics custom events |
| **Refunds and cancellations** | Tracked by Product Metrics; sent events aren't revised. Meta refuses events more than 7 days old |
| **Consent read from** | OneTrust, Cookiebot, Usercentrics or Osano |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **The event isn't in Meta's custom conversion selector** | Meta lists an event only after it received it. Place a test order with all cookies accepted, then create the custom conversion. |

## FAQ

### Do I need to change my website's code for Meta?

No. Setup is signing in to Cloudflare: a gateway on your zone serves the Tracking SDK and Event collector on your own domain, and the order goes to Meta through the Meta Conversions API.

### Can I keep my Meta pixel?

Yes. Meta counts an event once when the pixel and the Meta Conversions API send the same event name and event ID within 48 hours. `Purchase` uses the order transaction ID, so it deduplicates on its own.

### How does Meta get profit from my website orders?

Website orders carry no product costs, so set **Product cost fallback (%)** plus your additional costs under [Costs](https://www.productmetrics.io/docs/using/costs). `PMOrderProfit` then carries profit; a loss-making order is sent with value 0, as Meta accepts no negative value.

### Are refunds on my website sent to Meta?

No. Product Metrics tracks the refund in your profit and lifetime value, but sent Meta events aren't revised.
