# WooCommerce server-side tracking with the Meta Conversions API

Source: https://www.productmetrics.io/docs/tracking/server-side/woocommerce-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/woocommerce-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your WooCommerce store to Meta from the server through the Meta Conversions API, with Advanced Matching and the script served from your own domain.

Each purchase is confirmed from **your WooCommerce orders** and sent to your Meta pixel [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through the **Meta Conversions API**. Nothing in the browser talks to Meta, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/woocommerce-meta).

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking).
- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).
- **Access to your pixel in Meta Events Manager**, to copy its ID and generate a Conversions API access token.

## In the app

### 1. Connect WooCommerce and Meta

**Store:** install the **Product Metrics for WooCommerce** plugin, then paste your one-time setup token under **WooCommerce → Product Metrics** and select **Connect store**. Then link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).

**Meta:** in Events Manager, copy your **Pixel or Dataset ID** and generate a Conversions API access token, then add both under **Tracking → Meta Conversions API → Connect Meta** and send a test event. See [Meta](https://www.productmetrics.io/docs/channels/meta).

**You should see:** the plugin says **Store connected successfully.** and **Webhooks: 2 of 2 active**; Events Manager shows the test event under **Test events**.

### 2. Choose your consent banner

In Product Metrics, open **Tracking → Configure consent** and choose the banner your store shows: OneTrust, Cookiebot, Usercentrics or Osano.

After you change it, clear your full-page cache so every page loads the new setting. Left on **Not configured**, Product Metrics can't read the visitor's choice and treats it as not given. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

> **Warning:** Meta has no consent mode. Product Metrics sends an event only when the visitor allowed ad user data; the custom events also need analytics consent. A wrong banner here means nothing reaches Meta.

**You should see:** **Configure consent** names the banner your store actually shows.

### 3. Create custom conversions

In Events Manager, create a custom conversion for each Product Metrics value you want to bid on, with the rule `pm_purpose` equals the purpose: `PMOrderRevenue` (`ORDER_REVENUE`) for revenue, `PMOrderProfit` (`ORDER_PROFIT`) for profit, every other event in [Meta events](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#meta-events). Follow [Create custom conversions in Meta](https://www.productmetrics.io/docs/using/conversion-actions#custom-conversions-in-meta) once a test order has reached Meta.

**You should see:** your custom conversions show in Events Manager.

### 4. Check it works

In WordPress, under **WooCommerce → Product Metrics**, select **Verify with next paid order**, place and pay for a test order within ten minutes, then select **Refresh connection status**.

**You should see:** **Live order delivery** reads **Verified**; in Events Manager, the order shows as `Purchase`, plus the Product Metrics custom events your visitor's consent allows. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on WooCommerce

| | On WooCommerce |
| --- | --- |
| **Script and collector served by** | The plugin, from your WordPress site: its collector is a WordPress REST route on your domain (`/wp-json/<namespace>/c/<key>`, with a namespace generated for your store). No Cloudflare step, no DNS change, no script tag |
| **Purchase confirmed from** | Your WooCommerce orders |
| **Sent** | When the order reaches a status you selected under **Paid order statuses** |
| **Delivered** | Server-side, through the Meta Conversions API: `Purchase` plus the Product Metrics custom events |
| **Refunds and cancellations** | Sent events aren't revised. Meta refuses events more than 7 days old |
| **Consent read from** | OneTrust, Cookiebot, Usercentrics or Osano |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **The event isn't in Meta's custom conversion selector** | Meta lists an event only after it received it. Place a test order with all cookies accepted, then create the custom conversion. |

## FAQ

### Can I keep the Meta pixel on WooCommerce?

Yes. Meta counts an event once when the pixel and the Meta Conversions API send the same event name and event ID within 48 hours. `Purchase` uses the order transaction ID, so it deduplicates on its own. `AddToCart` and `InitiateCheckout` need your developer to pass Product Metrics' event ID to the pixel.

### When does a WooCommerce order reach Meta?

When it reaches a status you selected under **Paid order statuses**. Make sure that happens within 7 days of the order: Meta refuses older events.

### What customer data does Advanced Matching send to Meta?

With marketing consent, each event carries the hashed email, name, postal code and country, plus IP address and browser, through the Meta Conversions API. See [Meta Conversions API on WooCommerce](https://www.productmetrics.io/docs/tracking/enhanced-conversions/woocommerce-meta).

### Why do custom events show fewer orders than Purchase?

`Purchase` needs ad user data consent, while the Product Metrics custom events such as `PMOrderProfit` also need analytics consent. Visitors who allowed only ad user data count in `Purchase` alone.
