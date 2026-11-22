# Shopify server-side tracking with the Meta Conversions API

Source: https://www.productmetrics.io/docs/tracking/server-side/shopify-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/shopify-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your Shopify store to Meta from the server through the Meta Conversions API, with Advanced Matching and the script served from your own domain.

Each purchase is confirmed from **Shopify's order data** and sent to your Meta pixel [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through the **Meta Conversions API**. Nothing in the browser talks to Meta, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-meta).

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps).
- **Your Shopify store connected**: a Shopify login that can install apps and edit the theme, the Product Metrics app installed with its app embed on, the store linked to your property, and your subscription started in the app with **Create subscription** (billed through Shopify). See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).
- **Access to your pixel in Meta Events Manager**, to copy its ID and generate a Conversions API access token.

## In the app

### 1. Connect Shopify and Meta

**Store:** install the Product Metrics app from the Shopify App Store, select **Link Shopify store** and turn on its app embed and link it to your property. See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).

**Meta:** in Events Manager, copy your **Pixel or Dataset ID** and generate a Conversions API access token, then add both under **Tracking → Meta Conversions API → Connect Meta** and send a test event. See [Meta](https://www.productmetrics.io/docs/channels/meta).

**You should see:** the Shopify app says **You're set up**, with ticks for **Shopify permissions**, **App embed** and **Checkout pixel**; Events Manager shows the test event under **Test events**.

### 2. Choose your consent banner

In Product Metrics, open **Tracking → Configure consent** and choose **Shopify Customer Privacy**. Choose OneTrust, Cookiebot, Usercentrics or Osano instead only if your store shows one of those banners. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

> **Warning:** Meta has no consent mode. Product Metrics sends an event only when the visitor allowed ad user data; the custom events also need analytics consent. A wrong banner here means nothing reaches Meta.

**You should see:** **Configure consent** names the banner your store actually shows.

### 3. Create custom conversions

In Events Manager, create a custom conversion for each Product Metrics value you want to bid on, with the rule `pm_purpose` equals the purpose: `PMOrderRevenue` (`ORDER_REVENUE`) for revenue, `PMOrderProfit` (`ORDER_PROFIT`) for profit, every other event in [Meta events](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#meta-events). Follow [Create custom conversions in Meta](https://www.productmetrics.io/docs/using/conversion-actions#custom-conversions-in-meta) once a test order has reached Meta.

**You should see:** your custom conversions show in Events Manager.

### 4. Check it works

In the Shopify app, open **Tracking** in the app menu and select **Run tracking test**: each check shows **Passing**, **Needs attention** or **Listening**. Then **place and pay for a test order**; it is sent once Shopify marks it paid.

**You should see:** **Tracking is live on your store**, which means Product Metrics has seen your storefront; in Events Manager, the order shows as `Purchase`, plus the Product Metrics custom events your visitor's consent allows. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on Shopify

| | On Shopify |
| --- | --- |
| **Script and collector served by** | Shopify's app proxy, under `/apps/` on your store domain: the **app embed** loads it on every page and the app's **checkout pixel** reports the purchase. No Cloudflare step, no script tag |
| **Purchase confirmed from** | Shopify's order data |
| **Sent** | When Shopify marks the order paid |
| **Delivered** | Server-side, through the Meta Conversions API: `Purchase` plus the Product Metrics custom events |
| **Refunds and cancellations** | Sent events aren't revised. Meta refuses events more than 7 days old |
| **Consent read from** | Shopify Customer Privacy, or OneTrust, Cookiebot, Usercentrics or Osano |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **The event isn't in Meta's custom conversion selector** | Meta lists an event only after it received it. Place a test order with all cookies accepted, then create the custom conversion. |

## FAQ

### Does this replace my Meta pixel on Shopify?

No, you can keep it. Meta counts an event once when the pixel and the Meta Conversions API send the same event name and event ID within 48 hours. `Purchase` uses the order transaction ID, so it deduplicates on its own.

### Are past Shopify orders sent to Meta?

No. Meta refuses events more than 7 days old, so orders are sent from the moment tracking is live, once Shopify marks them paid.

### What customer data does Advanced Matching send to Meta?

With marketing consent, each event carries the hashed email, name, postal code and country, plus IP address and browser, through the Meta Conversions API. See [Meta Conversions API on Shopify](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-meta).

### Does a Shopify refund change the Meta event?

No. Sent Meta events aren't revised, so a refund or cancellation in Shopify leaves the original `Purchase` in place.
