# Shopware server-side tracking with the Meta Conversions API

Source: https://www.productmetrics.io/docs/tracking/server-side/shopware-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/shopware-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your Shopware sales channel to Meta from the server through the Meta Conversions API, with Advanced Matching and the script served from your own domain.

Each purchase is confirmed from **your Shopware orders** and sent to your Meta pixel [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through the **Meta Conversions API**. Nothing in the browser talks to Meta, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopware-meta).

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking).
- **Your Shopware sales channel connected**: Shopware 6.7 (this plugin build supports 6.7.14.0) with PHP 8.2+, an administrator who can upload extensions, Shopware's scheduled tasks and message workers running, and the channel's public HTTPS address under **Sales Channels → your channel → Domains**. You pair one sales channel with a one-time token; it reads **Active** before you link your property. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).
- **Access to your pixel in Meta Events Manager**, to copy its ID and generate a Conversions API access token.

## In the app

### 1. Connect Shopware and Meta

**Store:** install the Product Metrics plugin and pair your sales channel with a one-time token and link it to your property. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).

**Meta:** in Events Manager, copy your **Pixel or Dataset ID** and generate a Conversions API access token, then add both under **Tracking → Meta Conversions API → Connect Meta** and send a test event. See [Meta](https://www.productmetrics.io/docs/channels/meta).

**You should see:** in Product Metrics, the store reads **Active** after **Verify connection**; Events Manager shows the test event under **Test events**.

### 2. Choose your consent banner

Using Shopware's own cookie manager? Leave **Tracking → Configure consent** on **Not configured**: the extension adds a **Product Metrics measurement** group with **Product Metrics analytics** and **Product Metrics advertising attribution**. Choose OneTrust, Cookiebot, Usercentrics or Osano only if your shop shows one of those banners instead. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

> **Warning:** Meta has no consent mode. Product Metrics sends an event only when the visitor allowed ad user data; the custom events also need analytics consent. A wrong banner here means nothing reaches Meta.

**You should see:** **Configure consent** names the banner your sales channel actually shows.

### 3. Create custom conversions

In Events Manager, create a custom conversion for each Product Metrics value you want to bid on, with the rule `pm_purpose` equals the purpose: `PMOrderRevenue` (`ORDER_REVENUE`) for revenue, `PMOrderProfit` (`ORDER_PROFIT`) for profit, every other event in [Meta events](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#meta-events). Follow [Create custom conversions in Meta](https://www.productmetrics.io/docs/using/conversion-actions#custom-conversions-in-meta) once a test order has reached Meta.

**You should see:** your custom conversions show in Events Manager.

### 4. Check it works

**Place a paid test order** through the paired sales channel with your payment provider's test mode, and give Shopware a few minutes to sync it.

**You should see:** your cookie banner lists **Product Metrics measurement** (with Shopware's own cookie manager); in Events Manager, the order shows as `Purchase`, plus the Product Metrics custom events your visitor's consent allows. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on Shopware

| | On Shopware |
| --- | --- |
| **Script and collector served by** | The Shopware extension, on a path generated for your sales channel (`/<random>/c/<token>`). No Cloudflare step, no script tag; one installation tracks one sales channel |
| **Purchase confirmed from** | Your Shopware orders |
| **Sent** | When the order from the paired sales channel is paid |
| **Delivered** | Server-side, through the Meta Conversions API: `Purchase` plus the Product Metrics custom events |
| **Refunds and cancellations** | Sent events aren't revised. Meta refuses events more than 7 days old |
| **Consent read from** | Shopware's own cookie manager, or OneTrust, Cookiebot, Usercentrics or Osano |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **The event isn't in Meta's custom conversion selector** | Meta lists an event only after it received it. Place a test order with all cookies accepted, then create the custom conversion. |
| **Nothing reaches Meta** | Check that **Tracking → Configure consent** names the banner your store shows, or reads **Not configured** if it uses Shopware's own cookie manager. |

## FAQ

### Can I keep the Meta pixel on Shopware?

Yes. Meta counts an event once when the pixel and the Meta Conversions API send the same event name and event ID within 48 hours. `Purchase` uses the order transaction ID, so it deduplicates on its own.

### Which Shopware sales channel is sent to Meta?

Only the one paired with the extension: one installation tracks one sales channel, and its paid orders go to Meta.

### Are past Shopware orders sent to Meta?

No. Meta refuses events more than 7 days old, so only orders paid after tracking is live are sent.

### What customer data does Advanced Matching send to Meta?

With marketing consent, each event carries the hashed email, name, postal code and country, plus IP address and browser, through the Meta Conversions API. See [Meta Conversions API on Shopware](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopware-meta).
