# WooCommerce POAS bidding: Google Ads conversion tracking with profit

Source: https://www.productmetrics.io/docs/bidding/poas/woocommerce-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/poas/woocommerce-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send profit from WooCommerce orders to Google Ads as a conversion action and bid on it with a target ROAS (POAS bidding).

Every paid WooCommerce order goes to Google Ads server-side with its profit (**Product Metrics - Profit**) and its revenue (**Product Metrics - Revenue**). The one you make primary is what your target ROAS bids on: [POAS and ROAS bidding](https://www.productmetrics.io/docs/features/poas-bidding).

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics, with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).
- **A Google login with access to the Google Ads client account** your campaigns run in.

## In the app

### 1. Connect your WooCommerce store and Google Ads

Connect your store with [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce), then connect the Google Ads client account that runs your campaigns with [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

Connect your store, step by step:

Then connect Google Ads:

**You should see:** the plugin says **Store connected successfully.** and **Webhooks: 2 of 2 active**; Product Metrics lists your Google Ads account under your store.

### 2. Create the conversion actions

First choose your consent banner: in **Tracking → Configure consent**, choose the banner your store shows: OneTrust, Cookiebot, Usercentrics or Osano. Clear your full-page cache after you change it. The profit conversion needs the visitor's analytics and ad user data consent. See [Consent](https://www.productmetrics.io/docs/using/consent).

Then select **Tracking → Create Google Ads conversions → Create 8 conversion actions**: [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions). This page uses **Product Metrics - Profit** and **Product Metrics - Revenue**.

**You should see:** every Product Metrics conversion action is created and linked.

### 3. Activate your additional costs

Product costs come from the source you chose in the plugin under **Product cost**: **WooCommerce Core COGS** or a **Product meta key**. If you set **Payment cost** or **Actual shipping cost** to an **Order meta key**, those per-order costs are used instead of the estimates. Everything else comes from your **additional costs**.

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

## How it works on WooCommerce

| | On WooCommerce | Sent as |
| --- | --- | --- |
| **Revenue** | The order's revenue | **Product Metrics - Revenue** |
| **Product costs** | WooCommerce Core COGS, or the product meta key you chose in the plugin | Taken off profit |
| **Payment fees** | An order meta key you chose for **Payment cost**; otherwise your additional costs | Taken off profit |
| **Shipping, handling, returns** | Your additional costs | Taken off profit |
| **Profit** | Revenue ex tax − all costs; 0 for a loss | **Product Metrics - Profit** |
| **Refunds** | Your store reports them | Product Metrics adjusts the conversion |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |

## FAQ

### What if a WooCommerce product has no cost price?

Product Metrics takes **WooCommerce Core COGS**, or the **Product meta key** you chose in the plugin first, then the cost of goods for the same SKU in your linked Merchant Center, then your **Product cost fallback (%)** of the line's revenue. With none of these, the order goes to Google Ads with revenue only.

### Can I use my own cost field instead of WooCommerce COGS?

Yes. In the plugin under **Product cost**, choose **Product meta key** instead of **WooCommerce Core COGS**. **Payment cost** and **Actual shipping cost** can also come from an **Order meta key**, which then replaces the estimate.

### Should I keep my old purchase conversion in Google Ads?

Keep it as secondary. Only one purchase action should be primary, or purchases are counted twice. Product Metrics always sends both revenue and profit; only the primary action steers bidding.

### What happens in Google Ads when an order is refunded?

When WooCommerce reports the refund, Product Metrics adjusts the order's conversion in Google Ads.
