# Shopify POAS bidding: Google Ads conversion tracking with profit

Source: https://www.productmetrics.io/docs/bidding/poas/shopify-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/poas/shopify-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send profit from Shopify orders to Google Ads as a conversion action and bid on it with a target ROAS (POAS bidding).

Every paid Shopify order goes to Google Ads server-side with its profit (**Product Metrics - Profit**) and its revenue (**Product Metrics - Revenue**). The one you make primary is what your target ROAS bids on: [POAS and ROAS bidding](https://www.productmetrics.io/docs/features/poas-bidding).

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics. Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your Shopify store connected**: a Shopify login that can install apps and edit the theme, the Product Metrics app installed with its app embed on, the store linked to your property, and your subscription started in the app with **Create subscription** (billed through Shopify). See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).
- **A Google login with access to the Google Ads client account** your campaigns run in.

## In the app

### 1. Connect your Shopify store and Google Ads

Connect your store with [Shopify](https://www.productmetrics.io/docs/platforms/shopify), then connect the Google Ads client account that runs your campaigns with [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

Connect your store, step by step:

Then connect Google Ads:

**You should see:** the Shopify app says **You're set up**, with ticks for **Shopify permissions**, **App embed** and **Checkout pixel**; Product Metrics lists your Google Ads account under your store.

### 2. Create the conversion actions

First choose your consent banner: in **Tracking → Configure consent**, choose **Shopify Customer Privacy**, unless your store shows OneTrust, Cookiebot, Usercentrics or Osano instead. The profit conversion needs the visitor's analytics and ad user data consent. See [Consent](https://www.productmetrics.io/docs/using/consent).

Then select **Tracking → Create Google Ads conversions → Create 8 conversion actions**: [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions). This page uses **Product Metrics - Profit** and **Product Metrics - Revenue**.

**You should see:** every Product Metrics conversion action is created and linked.

### 3. Activate your additional costs

Product costs come from each variant's **cost per item** in Shopify. Payment fees are the actual Shopify Payments fees where Shopify reports them; other gateways use **External payment fixed cost** and **External payment (%)**. Everything else comes from your **additional costs**.

Then, under **Tracking → Add your additional costs**, check the defaults for your country, set **Product cost fallback (%)** and select **Activate additional costs**: [Costs](https://www.productmetrics.io/docs/using/costs).

**You should see:** the **Profit tracking** section says your additional costs are active.

### 4. Bid on profit

1. In Google Ads, make **Product Metrics - Profit** primary and your old purchase action secondary ([how](https://www.productmetrics.io/docs/using/conversion-actions#3-make-an-action-primary)).
2. Set the campaign to **Maximise conversion value** with a **target ROAS**, written as a percentage: 100% is break-even; 150% keeps €0.50 profit per €1 of ad spend.

> **Warning:** Moving a campaign from revenue to profit? Lower the target: [when to switch to POAS](https://www.productmetrics.io/docs/features/poas-bidding#when-to-switch-to-poas).

**You should see:** in Google Ads, **Goals → Conversions** lists **Product Metrics - Profit** as primary.

### 5. Check it works

Place a test order, then select **Tracking → Run tracking test** in the Shopify app: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

**You should see:** each check shows **Passing**, and the test order arrives with its revenue and profit. **Home** shows **Collecting** until it compares the new actions with your current ones, 14 days after the first order.

## How it works on Shopify

| | On Shopify | Sent as |
| --- | --- | --- |
| **Revenue** | The order's revenue | **Product Metrics - Revenue** |
| **Product costs** | Each variant's cost per item in Shopify | Taken off profit |
| **Payment fees** | Actual Shopify Payments fees; otherwise your additional costs | Taken off profit |
| **Shipping, handling, returns** | Your additional costs | Taken off profit |
| **Profit** | Revenue ex tax − all costs; 0 for a loss | **Product Metrics - Profit** |
| **Refunds** | Your store reports them | Product Metrics adjusts the conversion |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |

## FAQ

### What if a Shopify product has no cost price?

Product Metrics takes each variant's **cost per item** in Shopify first, then the cost of goods for the same SKU in your linked Merchant Center, then your **Product cost fallback (%)** of the line's revenue. With none of these, the order goes to Google Ads with revenue only.

### Are Shopify Payments fees taken off profit?

Yes. Product Metrics uses the actual Shopify Payments fee where Shopify reports it. Orders paid through other gateways use your **External payment fixed cost** and **External payment (%)**.

### Should I keep my old purchase conversion in Google Ads?

Keep it as secondary. Only one purchase action should be primary, or purchases are counted twice. Product Metrics always sends both revenue and profit; only the primary action steers bidding.

### What happens in Google Ads when an order is refunded?

When Shopify reports the refund, Product Metrics adjusts the order's conversion in Google Ads.
