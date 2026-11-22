# Lightspeed server-side tracking with the Meta Conversions API

Source: https://www.productmetrics.io/docs/tracking/server-side/lightspeed-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/lightspeed-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your Lightspeed shop to Meta from the server through the Meta Conversions API, with Advanced Matching and the script served from your own domain.

Each purchase is confirmed from **your Lightspeed eCom orders** and sent to your Meta pixel [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through the **Meta Conversions API**. Nothing in the browser talks to Meta, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-meta).

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking).
- **Your Lightspeed eCom (C-Series) shop connected**: a back-office administrator login (an API key can't sign in), the shop's cluster, hostname and numeric Shop ID, and an enabled API key with its secret that has Read on Content, Products, Customers and Orders, and Read and Write on Settings and Tracking. The shop can't already be connected to another workspace, and it reads **Active** with **Configuration is current** before you link your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).
- **Your shop domain on Cloudflare**, with its DNS record proxied (the orange cloud), and a workspace admin who signs in to Cloudflare once.
- **Access to your pixel in Meta Events Manager**, to copy its ID and generate a Conversions API access token.

## In the app

### 1. Connect Lightspeed and Meta

**Store:** add a Lightspeed API key in Product Metrics and sign in to Cloudflare for the gateway, then link the shop to your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).

**Meta:** in Events Manager, copy your **Pixel or Dataset ID** and generate a Conversions API access token, then add both under **Tracking → Meta Conversions API → Connect Meta** and send a test event. See [Meta](https://www.productmetrics.io/docs/channels/meta).

**You should see:** **Connection status**, **Credential status** and **Installation status** read **Active**, **Configured** and **Active**, publication reads **Configuration is current**, and the gateway says **Gateway setup complete**; Events Manager shows the test event under **Test events**.

### 2. Choose your consent banner

In Product Metrics, open **Tracking → Configure consent** and choose the banner your shop shows: OneTrust, Cookiebot, Usercentrics or Osano. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

> **Warning:** Meta has no consent mode. Product Metrics sends an event only when the visitor allowed ad user data; the custom events also need analytics consent. A wrong banner here means nothing reaches Meta.

**You should see:** **Configure consent** names the banner your shop actually shows.

### 3. Create custom conversions

In Events Manager, create a custom conversion for each Product Metrics value you want to bid on, with the rule `pm_purpose` equals the purpose: `PMOrderRevenue` (`ORDER_REVENUE`) for revenue, `PMOrderProfit` (`ORDER_PROFIT`) for profit, every other event in [Meta events](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#meta-events). Follow [Create custom conversions in Meta](https://www.productmetrics.io/docs/using/conversion-actions#custom-conversions-in-meta) once a test order has reached Meta.

**You should see:** your custom conversions show in Events Manager.

### 4. Check it works

In **Tracking**, open the **Tracking SDK** link under the Cloudflare gateway's **Live endpoints**: it returns JavaScript (the collector only accepts POST requests). Then **place and pay for a test order**.

**You should see:** **Live endpoints** lists the **Tracking SDK** and **Event collector** on your shop domain, and the order appears for the linked property; in Events Manager, the order shows as `Purchase`, plus the Product Metrics custom events your visitor's consent allows. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on Lightspeed

| | On Lightspeed |
| --- | --- |
| **Script and collector served by** | A Cloudflare gateway (a Worker on your shop's Cloudflare zone), as Lightspeed eCom has no app proxy. Product Metrics never changes your DNS |
| **Purchase confirmed from** | Your Lightspeed eCom orders |
| **Sent** | When Lightspeed marks the order paid (a pay-on-pickup order when it is paid) |
| **Delivered** | Server-side, through the Meta Conversions API: `Purchase` plus the Product Metrics custom events |
| **Refunds and cancellations** | Sent events aren't revised. Meta refuses events more than 7 days old |
| **Consent read from** | OneTrust, Cookiebot, Usercentrics or Osano |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **The event isn't in Meta's custom conversion selector** | Meta lists an event only after it received it. Place a test order with all cookies accepted, then create the custom conversion. |

## FAQ

### Why does Lightspeed tracking for Meta use Cloudflare?

Lightspeed eCom has no app proxy, so a Cloudflare gateway on your shop's zone serves the script and collector on your shop domain. Product Metrics never changes your DNS.

### When is a pay-on-pickup order sent to Meta?

When Lightspeed marks it paid. Meta refuses events more than 7 days old, so an order paid later than that doesn't reach Meta.

### Can I keep the Meta pixel on my Lightspeed shop?

Yes. Meta counts an event once when the pixel and the Meta Conversions API send the same event name and event ID within 48 hours. `Purchase` uses the order transaction ID, so it deduplicates on its own.

### Do Lightspeed credit notes change the Meta event?

No. Sent Meta events aren't revised. Credit notes adjust the Google Ads conversion only.
