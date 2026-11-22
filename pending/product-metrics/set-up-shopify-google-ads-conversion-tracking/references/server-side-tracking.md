# Shopify server-side tracking for Google Ads

Source: https://www.productmetrics.io/docs/tracking/server-side/shopify-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/shopify-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your Shopify store to Google Ads from the server, with the script served from your own domain.

Each purchase is confirmed from **Shopify's order data** and sent to Google Ads [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through Google's **Data Manager**. Nothing in the browser talks to Google, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your Shopify store connected**: a Shopify login that can install apps and edit the theme, the Product Metrics app installed with its app embed on, the store linked to your property, and your subscription started in the app with **Create subscription** (billed through Shopify). See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).

## In the app

### 1. Connect Shopify and Google Ads

**Store:** install the Product Metrics app from the Shopify App Store, select **Link Shopify store** and turn on its app embed. See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).

**Google Ads:** connect it in onboarding (**Connect Google Ads and Merchant Center**) or on **Integrations**, pick the client account that runs your campaigns and grant Data Manager access. See [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

**You should see:** the Shopify app says **You're set up**, with ticks for **Shopify permissions**, **App embed** and **Checkout pixel**; your Google Ads account shows on **Integrations**.

### 2. Choose your consent banner

In Product Metrics, open **Tracking → Configure consent** and choose **Shopify Customer Privacy**. Choose OneTrust, Cookiebot, Usercentrics or Osano instead only if your store shows one of those banners. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Configure consent** names the banner your store actually shows.

### 3. Create the conversion actions

In Product Metrics, select **Tracking** → **Create Google Ads conversions** → **Create 8 conversion actions**. All eight are **secondary**, so nothing changes in your campaigns until you make one primary. See [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions).

Then [add your additional costs](https://www.productmetrics.io/docs/using/costs), so the profit actions carry profit.

**You should see:** the badge next to **Tracking** reads **Tracking active**.

### 4. Check it works

In the Shopify app, open **Tracking** in the app menu and select **Run tracking test**: each check shows **Passing**, **Needs attention** or **Listening**. Then **place and pay for a test order**; it is sent once Shopify marks it paid.

**You should see:** **Tracking is live on your store**, which means Product Metrics has seen your storefront. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on Shopify

| | On Shopify |
| --- | --- |
| **Script and collector served by** | Shopify's app proxy, under `/apps/` on your store domain: the **app embed** loads it on every page and the app's **checkout pixel** reports the purchase. No Cloudflare step, no script tag |
| **Purchase confirmed from** | Shopify's order data |
| **Sent** | When Shopify marks the order paid |
| **Delivered** | Server-side, through Google's Data Manager, to the eight **Product Metrics** conversion actions |
| **Refunds and cancellations** | Shopify reports cancellations and refunds; the Google Ads conversion is adjusted |
| **Consent read from** | Shopify Customer Privacy, or OneTrust, Cookiebot, Usercentrics or Osano |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in Google Ads** | Check that **Tracking → Configure consent** names the banner your store actually shows: Product Metrics sends an order only with the consent this page lists. See [Consent](https://www.productmetrics.io/docs/concepts/consent). |

## FAQ

### Do I need Google Tag Manager for this on Shopify?

No. The app embed loads the script through Shopify's app proxy under `/apps/` on your store domain, and the app's checkout pixel reports the purchase. There is no script tag to add.

### When is a Shopify order sent to Google Ads?

Once Shopify marks the order paid. That is why a test order only shows up after you pay for it.

### What happens in Google Ads when a Shopify order is refunded?

Shopify reports cancellations and refunds to Product Metrics, and the Google Ads conversion is adjusted.

### Will my existing purchase conversion be counted twice?

Not if only one is primary. The eight Product Metrics actions start as secondary; when you make one primary in Google Ads, set your old purchase action to secondary. See [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions).
