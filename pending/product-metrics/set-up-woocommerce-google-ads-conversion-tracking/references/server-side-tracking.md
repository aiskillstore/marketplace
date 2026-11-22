# WooCommerce server-side tracking for Google Ads

Source: https://www.productmetrics.io/docs/tracking/server-side/woocommerce-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/woocommerce-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your WooCommerce store to Google Ads from the server, with the script served from your own domain.

Each purchase is confirmed from **your WooCommerce orders** and sent to Google Ads [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through Google's **Data Manager**. Nothing in the browser talks to Google, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).

## In the app

### 1. Connect WooCommerce and Google Ads

**Store:** install the **Product Metrics for WooCommerce** plugin, then paste your one-time setup token under **WooCommerce → Product Metrics** and select **Connect store**. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).

**Google Ads:** under **Ecommerce platforms**, select your store → **Connect Google Ads** → **Continue with Google**, pick the client account that runs your campaigns and grant Data Manager access. See [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

**You should see:** the plugin says **Store connected successfully.** and **Webhooks: 2 of 2 active**; Product Metrics lists your Google Ads account under your store.

### 2. Choose your consent banner

In Product Metrics, open **Tracking → Configure consent** and choose the banner your store shows: OneTrust, Cookiebot, Usercentrics or Osano.

After you change it, clear your full-page cache so every page loads the new setting. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Configure consent** names the banner your store actually shows.

### 3. Create the conversion actions

In Product Metrics, select **Tracking** → **Create Google Ads conversions** → **Create 8 conversion actions**. All eight are **secondary**, so nothing changes in your campaigns until you make one primary. See [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions).

Then [add your additional costs](https://www.productmetrics.io/docs/using/costs), so the profit actions carry profit.

**You should see:** the badge next to **Tracking** reads **Tracking active**.

### 4. Check it works

In WordPress, under **WooCommerce → Product Metrics**, select **Verify with next paid order**, place and pay for a test order within ten minutes, then select **Refresh connection status**.

**You should see:** **Live order delivery** reads **Verified**. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on WooCommerce

| | On WooCommerce |
| --- | --- |
| **Script and collector served by** | The plugin, from your WordPress site: its collector is a WordPress REST route on your domain (`/wp-json/<namespace>/c/<key>`, with a namespace generated for your store). No Cloudflare step, no DNS change, no script tag |
| **Purchase confirmed from** | Your WooCommerce orders |
| **Sent** | When the order reaches a status you selected under **Paid order statuses** |
| **Delivered** | Server-side, through Google's Data Manager, to the eight **Product Metrics** conversion actions |
| **Refunds and cancellations** | WooCommerce order updates are read again, including refunds; the Google Ads conversion is adjusted |
| **Consent read from** | OneTrust, Cookiebot, Usercentrics or Osano |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Nothing reaches Google Ads** | Check that **Tracking → Configure consent** names the banner your store shows. Left on **Not configured**, Product Metrics can't read the visitor's choice and treats it as not given. |

## FAQ

### Do I need Google Tag Manager on WooCommerce?

No. The Product Metrics for WooCommerce plugin serves the script from your WordPress site, with its collector as a REST route on your own domain. No script tag, no DNS change and no Cloudflare step.

### Which WooCommerce order status sends the conversion?

The statuses you select under **Paid order statuses**. An order is sent to Google Ads when it reaches one of them.

### Are WooCommerce refunds passed on to Google Ads?

Yes. Product Metrics reads WooCommerce order updates again, including refunds, and adjusts the Google Ads conversion.

### Which action should I make primary to bid on profit?

**Product Metrics - Profit**, made primary in Google Ads, with your old purchase action set to secondary so the same purchase isn't counted twice. For ROAS, use **Product Metrics - Revenue** instead.
