# Magento server-side tracking with the Meta Conversions API

Source: https://www.productmetrics.io/docs/tracking/server-side/magento-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/magento-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your Magento store view to Meta from the server through the Meta Conversions API, with Advanced Matching and the script served from your own domain.

Each purchase is confirmed from **your Magento orders** and sent to your Meta pixel [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through the **Meta Conversions API**. Nothing in the browser talks to Meta, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/magento-meta).

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking).
- **Your Magento store view connected**: Magento 2.4, 2.0 or 1.9 / OpenMage, Magento Admin access, the public HTTPS shop address and the **store-view ID**, and a **developer** with access to your server who installs the Product Metrics module (Composer or ZIP), adds the store view's private configuration file and keeps Magento cron running. The connection reads **Active** before you link your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).
- **Access to your pixel in Meta Events Manager**, to copy its ID and generate a Conversions API access token.

## In the app

### 1. Connect Magento and Meta

**Store:** create the module configuration under **Ecommerce platforms → Connect Magento**, have your developer install the module, then verify the store view and link it to your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).

**Meta:** in Events Manager, copy your **Pixel or Dataset ID** and generate a Conversions API access token, then add both under **Tracking → Meta Conversions API → Connect Meta** and send a test event. See [Meta](https://www.productmetrics.io/docs/channels/meta).

**You should see:** under **Manage Magento**, the connection is **Active** and your property is linked; Events Manager shows the test event under **Test events**.

### 2. Choose your consent banner

In Product Metrics, open **Tracking → Configure consent** and choose the banner your shop shows: OneTrust, Cookiebot, Usercentrics or Osano. **Magento's own cookie restriction notice does not grant consent.** With any other banner, your developer passes the visitor's choices to Product Metrics; anything not set stays denied. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

> **Warning:** Meta has no consent mode. Product Metrics sends an event only when the visitor allowed ad user data; the custom events also need analytics consent. A wrong banner here means nothing reaches Meta.

**You should see:** **Configure consent** names the banner your store view actually shows.

### 3. Create custom conversions

In Events Manager, create a custom conversion for each Product Metrics value you want to bid on, with the rule `pm_purpose` equals the purpose: `PMOrderRevenue` (`ORDER_REVENUE`) for revenue, `PMOrderProfit` (`ORDER_PROFIT`) for profit, every other event in [Meta events](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#meta-events). Follow [Create custom conversions in Meta](https://www.productmetrics.io/docs/using/conversion-actions#custom-conversions-in-meta) once a test order has reached Meta.

**You should see:** your custom conversions show in Events Manager.

### 4. Check it works

**Place a paid test order** in the connected store view with your payment provider's test mode, and allow a few minutes for cron.

**You should see:** under **Manage Magento**, the desired and active revision numbers are the same, and the order appears for the linked property; in Events Manager, the order shows as `Purchase`, plus the Product Metrics custom events your visitor's consent allows. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on Magento

| | On Magento |
| --- | --- |
| **Script and collector served by** | The Product Metrics module, on its own paths of your store domain, set for each store view by the module's configuration file. Nothing loads from another domain and there is no script tag |
| **Purchase confirmed from** | Your Magento orders |
| **Sent** | When the order is paid; the module sends changes every two minutes through cron |
| **Delivered** | Server-side, through the Meta Conversions API: `Purchase` plus the Product Metrics custom events |
| **Refunds and cancellations** | Sent events aren't revised. Meta refuses events more than 7 days old |
| **Consent read from** | OneTrust, Cookiebot, Usercentrics or Osano, or your own banner, passed on by your developer |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **The event isn't in Meta's custom conversion selector** | Meta lists an event only after it received it. Place a test order with all cookies accepted, then create the custom conversion. |

## FAQ

### Do I need a developer to send Magento orders to Meta?

Once, to install the Product Metrics module and make sure Magento cron runs. Connecting Meta and creating custom conversions happen in Product Metrics and Events Manager.

### How quickly does a paid Magento order reach Meta?

The module sends order changes every two minutes through Magento cron. Mark orders paid within 7 days: Meta refuses older events.

### Does Magento's cookie notice give consent for Meta?

No. Magento's cookie restriction notice does not grant consent, and Meta has no consent mode. Without a supported banner, or your developer passing your banner's choices, nothing reaches Meta.

### Are Magento refunds sent to Meta?

No. Sent Meta events aren't revised, so a refund or cancellation in Magento doesn't change them.
