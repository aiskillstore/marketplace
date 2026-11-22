# Cloudflare POAS bidding: Google Ads conversion tracking with profit

Source: https://www.productmetrics.io/docs/bidding/poas/cloudflare-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/poas/cloudflare-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send profit from your website's orders to Google Ads as a conversion action and bid on it with a target ROAS (POAS bidding).

Every website purchase goes to Google Ads server-side with its profit (**Product Metrics - Profit**) and its revenue (**Product Metrics - Revenue**). The one you make primary is what your target ROAS bids on: [POAS and ROAS bidding](https://www.productmetrics.io/docs/features/poas-bidding).

Revenue is the value your purchase page reports.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics, with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).
- **A Google login with access to the Google Ads client account** your campaigns run in.

## In the app

### 1. Connect your website and Google Ads

Connect your website with [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare), then connect the Google Ads client account that runs your campaigns with [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

Connect your website, step by step:

Then connect Google Ads:

**You should see:** the gateway card says **Gateway setup complete**; Product Metrics lists your Google Ads account under your store.

### 2. Create the conversion actions

First choose your consent banner: in **Tracking → Configure consent**, choose the banner your website shows: OneTrust, Cookiebot, Usercentrics or Osano. The profit conversion needs the visitor's analytics and ad user data consent. See [Consent](https://www.productmetrics.io/docs/using/consent).

Then select **Tracking → Create Google Ads conversions → Create 8 conversion actions**: [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions). This page uses **Product Metrics - Profit** and **Product Metrics - Revenue**.

**You should see:** every Product Metrics conversion action is created and linked.

### 3. Activate your additional costs

A website sends no product costs, so profit uses your **Product cost fallback (%)** of each line's revenue. Set it to what your products cost you as a share of their price; profit is only as accurate as this number. Shipping, payment fees and the rest come from your **additional costs**.

Then, under **Tracking → Add your additional costs**, check the defaults for your country, set **Product cost fallback (%)** and select **Activate additional costs**: [Costs](https://www.productmetrics.io/docs/using/costs).

**You should see:** the **Profit tracking** section says your additional costs are active.

### 4. Bid on profit

1. In Google Ads, make **Product Metrics - Profit** primary and your old purchase action secondary ([how](https://www.productmetrics.io/docs/using/conversion-actions#3-make-an-action-primary)).
2. Set the campaign to **Maximise conversion value** with a **target ROAS**, written as a percentage: 100% is break-even; 150% keeps €0.50 profit per €1 of ad spend.

> **Warning:** Moving a campaign from revenue to profit? Lower the target: [when to switch to POAS](https://www.productmetrics.io/docs/features/poas-bidding#when-to-switch-to-poas).

**You should see:** in Google Ads, **Goals → Conversions** lists **Product Metrics - Profit** as primary.

### 5. Check it works

Place a test order, then open **Tracking** in Product Metrics: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

**You should see:** the badge next to **Tracking** reads **Tracking active**, and the test order arrives with its revenue and profit. **Home** shows **Collecting** until it compares the new actions with your current ones, 14 days after the first order.

## How it works on a website

| | On a website | Sent as |
| --- | --- | --- |
| **Revenue** | The order's revenue | **Product Metrics - Revenue** |
| **Product costs** | None sent: your **Product cost fallback (%)** of each line's revenue | Taken off profit |
| **Payment fees** | Your additional costs | Taken off profit |
| **Shipping, handling, returns** | Your additional costs | Taken off profit |
| **Profit** | Revenue ex tax − all costs; 0 for a loss | **Product Metrics - Profit** |
| **Refunds and cancellations** | Tracked by Product Metrics | The conversion is adjusted after a refund or cancellation |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |

## FAQ

### Can I bid on profit when my website has no cost prices?

Yes. A website sends no product costs, so profit uses your **Product cost fallback (%)** of each line's revenue, minus your additional costs. Set the fallback to what your products cost you as a share of their price.

### Do I need a developer to set up tracking on my website?

No. Cloudflare Tracking is set up by signing in to Cloudflare, with your website's domain on Cloudflare. For Google Ads, also connect Merchant Center in Product Metrics.

### Should I keep my old purchase conversion in Google Ads?

Keep it as secondary. Only one purchase action should be primary, or purchases are counted twice. Product Metrics always sends both revenue and profit; only the primary action steers bidding.

### Is an order sold at a loss sent to Google Ads?

Yes, with a profit of 0, because Google Ads accepts no negative value. Its revenue still goes to **Product Metrics - Revenue**.
