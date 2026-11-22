# Server-side tracking and profit bidding on any website (Cloudflare)

Source: https://www.productmetrics.io/docs/platforms/cloudflare (the same page as Markdown: https://www.productmetrics.io/docs/platforms/cloudflare.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

No supported shop platform? Sign in to Cloudflare and Cloudflare Tracking sends your website's purchases server-side to Google Ads, Meta and ChatGPT Ads, so you can bid on profit.

**Cloudflare Tracking** is for any website that isn't on Shopify, WooCommerce, Magento, Lightspeed or Shopware 6. It reads each purchase from your **order confirmation page** and sends it server-side to each ad channel.

All you do is sign in: you log in to Cloudflare, approve Product Metrics and choose your domain, and Product Metrics adds the tracking to every page. No code, no Google tag.

- **Install:** sign in to Cloudflare. No code, no Google tag.
- **Product cost:** none on website orders: **Product cost fallback (%)**.
- **Consent banner:** OneTrust, Cookiebot, Usercentrics or Osano.

## Prerequisites

- A website whose domain uses Cloudflare DNS, with its DNS record proxied (the orange cloud).
- A Cloudflare login for that account that can approve access. Product Metrics never changes your DNS.
- A [workspace](https://www.productmetrics.io/docs/using/create-a-workspace), a property for the orders, and a workspace admin for the Cloudflare sign-in.

Running Shopify, WooCommerce, [Magento](https://www.productmetrics.io/docs/platforms/magento), [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed) or Shopware? Use that platform's page: it reads orders from the shop itself.

## In the app

### 1. Add your website

Go to **Ecommerce platforms → Connect Cloudflare Tracking** and enter the hostname your customers visit. One installation per hostname.

**You should see:** **Cloudflare Tracking** list your website under **Ecommerce platforms**.

### 2. Send its orders to a property

Under **Storefront scopes**, link the property that should receive the orders.

### 3. Sign in to Cloudflare

This is the whole setup on your side, in a browser. In **Tracking**, under **Complete your tracking setup**, open **Connect Cloudflare**. A workspace admin:

1. Selects **Connect Cloudflare**, signs in to Cloudflare and approves Product Metrics.
2. Chooses the **Cloudflare account** and the **Cloudflare zone** your domain is in.
3. Selects **Set up gateway** and keeps the page open until it finishes.

Product Metrics adds the tracking to every page of your domain. Nothing to paste or publish.

**You should see:** **Gateway setup complete**.

### 4. Finish tracking setup

- **Consent**: choose your banner (OneTrust, Cookiebot, Usercentrics or Osano). See [Consent](https://www.productmetrics.io/docs/using/consent).
- **Channels**: connect [Google Ads](https://www.productmetrics.io/docs/channels/google-ads) (with Data Manager access), [Meta](https://www.productmetrics.io/docs/channels/meta) and [ChatGPT Ads (OpenAI)](https://www.productmetrics.io/docs/channels/openai).
- **Google Ads conversion actions**: [create them](https://www.productmetrics.io/docs/using/conversion-actions).
- **Additional costs**: website orders carry no product costs, so set **Product cost fallback (%)** and add shipping, handling, returns and payment fees. See [Costs](https://www.productmetrics.io/docs/using/costs).

Step by step in **Tracking**:

**You should see:** the badge next to **Tracking** read **Tracking active**.

### 5. Check your purchases

Place a test order and finish it through to the order confirmation page. Then open **Check your purchases** in the app; your order shows within two minutes.

**You should see:** **Last purchase received** with the order's number and value. Under the Cloudflare gateway, **Live endpoints** lists the **Tracking SDK** and **Event collector** on your domain.

## How it works on a website

| | On a website |
| --- | --- |
| **Install** | Sign in to Cloudflare, approve Product Metrics, choose your domain |
| **Order source** | The purchase your order confirmation page reports |
| **Product cost** | None on website orders: **Product cost fallback (%)** plus your additional costs |
| **Consent** | OneTrust, Cookiebot, Usercentrics or Osano |
| **Value sent** | Exactly the order value the page reported |
| **Refunds and cancellations** | Tracked by Product Metrics. Google Ads conversions are adjusted; events already sent to Meta and ChatGPT Ads aren't revised |
| **Disconnect** | Product Metrics removes its Cloudflare resources, which takes tracking off your pages; the website stays set up |

## What you get with Cloudflare Tracking

Each feature, its channels and the Cloudflare Tracking guide for each:

**Features and guides with Cloudflare Tracking**

| Feature | Channels | On this platform |
| --- | --- | --- |
| [Server-side conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) | [Google Ads](https://www.productmetrics.io/docs/tracking/server-side/cloudflare-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/server-side/cloudflare-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/server-side/cloudflare-openai) | Purchases your confirmation page reports, served from your domain; the first report wins. |
| [Enhanced Conversions](https://www.productmetrics.io/docs/features/enhanced-conversions) | [Google Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/cloudflare-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/enhanced-conversions/cloudflare-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/cloudflare-openai) | Sent only with ad user data consent. |
| [Customer lists](https://www.productmetrics.io/docs/features/customer-list) | [Google Ads](https://www.productmetrics.io/docs/tracking/customer-lists/cloudflare-google-ads) | Customer Match lists from the purchases Product Metrics receives. |
| [POAS and ROAS bidding](https://www.productmetrics.io/docs/features/poas-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/poas/cloudflare-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/poas/cloudflare-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/poas/cloudflare-openai) | No product costs: profit uses **Product cost fallback (%)** plus your additional costs. |
| [New customer bidding](https://www.productmetrics.io/docs/features/new-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/cloudflare-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/new-customers/cloudflare-meta) | Only purchases Product Metrics has already seen; the page reports no history. |
| [Returning customer bidding](https://www.productmetrics.io/docs/features/returning-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/cloudflare-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/returning-customers/cloudflare-meta) | Same as new customers: purchases Product Metrics has already seen. |
| [LTV bidding](https://www.productmetrics.io/docs/features/ltv-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/ltv/cloudflare-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/ltv/cloudflare-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/cloudflare-openai) | Built from the purchases Product Metrics receives from the website. |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **"Proxy the storefront DNS record first"** | Turn on the orange cloud for your domain's DNS record in Cloudflare, then choose the zone again. |
| **"Update the storefront domain first"** | The zone doesn't contain your domain. Select **Change storefront domain**, enter the hostname customers use without `https://`, and choose the zone again. |
| **"Some permissions were not granted" or "Cloudflare did not authorize Product Metrics"** | Select **Connect Cloudflare** again and approve every permission. |

## FAQ

### Do I need a developer or any code for Cloudflare Tracking?

No. The setup is signing in to Cloudflare: you approve Product Metrics, choose your domain, and Product Metrics adds the tracking to every page. Nothing to paste or publish.

### Does Product Metrics change my DNS?

No. Your domain needs Cloudflare DNS with its record proxied (the orange cloud), but Product Metrics never changes your DNS.

### Can I bid on profit without product costs?

Yes. Website orders carry no product cost, so profit for POAS bidding uses your **Product cost fallback (%)** plus your additional costs. Set both in [Costs](https://www.productmetrics.io/docs/using/costs).

### Are refunds and cancellations tracked?

Yes. Product Metrics adjusts the Google Ads conversion when the order is refunded or cancelled, and counts the refund in profit and lifetime value. Meta and ChatGPT Ads don't accept revisions, so events already sent to them stay as they are.
