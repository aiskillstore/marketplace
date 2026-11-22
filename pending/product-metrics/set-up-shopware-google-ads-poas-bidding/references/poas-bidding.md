# Shopware POAS bidding: Google Ads conversion tracking with profit

Source: https://www.productmetrics.io/docs/bidding/poas/shopware-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/poas/shopware-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send profit from Shopware orders to Google Ads as a conversion action and bid on it with a target ROAS (POAS bidding).

Every paid Shopware order goes to Google Ads server-side with its profit (**Product Metrics - Profit**) and its revenue (**Product Metrics - Revenue**). The one you make primary is what your target ROAS bids on: [POAS and ROAS bidding](https://www.productmetrics.io/docs/features/poas-bidding).

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics, with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your Shopware sales channel connected**: Shopware 6.7 (this plugin build supports 6.7.14.0) with PHP 8.2+, an administrator who can upload extensions, Shopware's scheduled tasks and message workers running, and the channel's public HTTPS address under **Sales Channels → your channel → Domains**. You pair one sales channel with a one-time token; it reads **Active** before you link your property. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).
- **A Google login with access to the Google Ads client account** your campaigns run in.

## In the app

### 1. Connect your Shopware store and Google Ads

Connect your store with [Shopware](https://www.productmetrics.io/docs/platforms/shopware), then connect the Google Ads client account that runs your campaigns with [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

Connect your store, step by step:

Then connect Google Ads:

**You should see:** in Product Metrics, the store reads **Active** after **Verify connection**; Product Metrics lists your Google Ads account under your store.

### 2. Create the conversion actions

First choose your consent banner: in **Tracking → Configure consent**, leave **Not configured** to use Shopware's own cookie manager, or choose OneTrust, Cookiebot, Usercentrics or Osano if your shop shows one of those. The profit conversion needs the visitor's analytics and ad user data consent. See [Consent](https://www.productmetrics.io/docs/using/consent).

Then select **Tracking → Create Google Ads conversions → Create 8 conversion actions**: [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions). This page uses **Product Metrics - Profit** and **Product Metrics - Revenue**.

**You should see:** every Product Metrics conversion action is created and linked.

### 3. Activate your additional costs

Product costs come from the purchase price on each Shopware order line, as it was when the order was placed. Everything else comes from your **additional costs**.

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

## How it works on Shopware

| | On Shopware | Sent as |
| --- | --- | --- |
| **Revenue** | The order's revenue | **Product Metrics - Revenue** |
| **Product costs** | The purchase price on each Shopware order line | Taken off profit |
| **Payment fees** | Your additional costs | Taken off profit |
| **Shipping, handling, returns** | Your additional costs | Taken off profit |
| **Profit** | Revenue ex tax − all costs; 0 for a loss | **Product Metrics - Profit** |
| **Refunds** | Your store reports them | Product Metrics adjusts the conversion |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |

## FAQ

### What if a Shopware product has no cost price?

Product Metrics takes the purchase price on each Shopware order line first, then the cost of goods for the same SKU in your linked Merchant Center, then your **Product cost fallback (%)** of the line's revenue. With none of these, the order goes to Google Ads with revenue only.

### Does a new purchase price change the profit of past orders?

No. Product Metrics uses the purchase price on each Shopware order line as it was when the order was placed, so a later change only affects new orders.

### Should I keep my old purchase conversion in Google Ads?

Keep it as secondary. Only one purchase action should be primary, or purchases are counted twice. Product Metrics always sends both revenue and profit; only the primary action steers bidding.

### What happens in Google Ads when an order is refunded?

When Shopware reports the refund, Product Metrics adjusts the order's conversion in Google Ads.
