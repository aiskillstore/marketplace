# Shopify POAS bidding: Meta Conversions API with profit

Source: https://www.productmetrics.io/docs/bidding/poas/shopify-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/poas/shopify-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send profit from Shopify orders to Meta through the Meta Conversions API with Advanced Matching, and optimise on it with a ROAS goal.

Every paid Shopify order goes to your Meta pixel through the Meta Conversions API, server-side, with its profit in the custom event [`PMOrderProfit`](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#meta-events). Optimise on a custom conversion on it and Meta steers on profit (POAS). Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics.
- **Your Shopify store connected**: a Shopify login that can install apps and edit the theme, the Product Metrics app installed with its app embed on, the store linked to your property, and your subscription started in the app with **Create subscription** (billed through Shopify). See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).
- **Access to your pixel in Meta Events Manager**, to copy its ID and generate a Conversions API access token.

## In the app

### 1. Connect your Shopify store and Meta

Connect your store with [Shopify](https://www.productmetrics.io/docs/platforms/shopify). Then, under **Tracking → Meta Conversions API → Connect Meta**, add your **Pixel or Dataset ID** and a Conversions API access token from Events Manager, and send a test event: [Meta](https://www.productmetrics.io/docs/channels/meta).

Connect your store, step by step:

Then add the Meta destination:

On Shopify, Product Metrics reads consent from **Shopify Customer Privacy** (choose it under **Tracking → Configure consent**). The profit event also needs analytics consent. See [Consent](https://www.productmetrics.io/docs/using/consent).

**You should see:** the Shopify app says **You're set up**, with ticks for **Shopify permissions**, **App embed** and **Checkout pixel**; Events Manager shows the test event under **Test events**.

### 2. Activate your additional costs

Product costs come from each variant's **cost per item** in Shopify. Payment fees are the actual Shopify Payments fees where Shopify reports them; other gateways use **External payment fixed cost** and **External payment (%)**. Everything else comes from your **additional costs**.

Then, under **Tracking → Add your additional costs**, check the defaults for your country, set **Product cost fallback (%)** and select **Activate additional costs**: [Costs](https://www.productmetrics.io/docs/using/costs).

**You should see:** the **Profit tracking** section says your additional costs are active.

### 3. Create a custom conversion on PMOrderProfit

This step happens in Meta. `PMOrderProfit` only appears in Meta's selector after Meta has received one, so first place a test order with consent accepted and your costs active.

1. In Events Manager, choose **Custom conversions → Create custom conversion**.
2. Select your pixel and the event `PMOrderProfit`.
3. Add the event parameter rule `pm_purpose` equals `ORDER_PROFIT`.
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

For ROAS, skip this: the standard `Purchase` event already carries revenue.

Once your test order arrived, remove the test event code, or events keep landing under **Test events** only.

**You should see:** the custom conversion shows in Events Manager.

### 4. Optimise on profit

In your sales campaign, choose the `PMOrderProfit` custom conversion as the conversion event, optimise for value and set a ROAS goal as a percentage: 100% is break-even, 150% keeps €0.50 profit per €1 of ad spend. For revenue (ROAS), use `Purchase` with your revenue target, for example 420% for a ROAS of 4.2.

> **Warning:** Moving a campaign from revenue to profit? Lower the goal: [POAS and ROAS bidding](https://www.productmetrics.io/docs/features/poas-bidding).

**You should see:** the ad set's conversion event is your `PMOrderProfit` custom conversion.

### 5. Check it works

Open **Tracking → Meta Conversions API**: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking#4-meta-and-chatgpt-ads).

**You should see:** **Access token: Saved**, **Sending: On** with test mode off, and the delivery counts; recent orders arrive with a known profit.

## How it works on Shopify

| | On Shopify | Sent as |
| --- | --- | --- |
| **Revenue** | The order's revenue | `Purchase` (and `PMOrderRevenue`, `ORDER_REVENUE`) |
| **Product costs** | Each variant's cost per item in Shopify | Taken off profit |
| **Payment fees** | Actual Shopify Payments fees; otherwise your additional costs | Taken off profit |
| **Shipping, handling, returns** | Your additional costs | Taken off profit |
| **Profit** | Revenue ex tax − all costs | `PMOrderProfit` (`ORDER_PROFIT`); 0 for a loss, signed value in `pm_contribution_profit` |
| **Refunds** | Your store reports them | Not sent: Meta events aren't revised |

Meta rejects events older than 7 days, so past orders are not imported.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |
| **Events only show under Test events** | Remove the test event code from your Meta destination under **Tracking → Meta Conversions API**. |

## FAQ

### Which Shopify costs make up the profit Meta receives?

Product costs come from each variant's **cost per item** in Shopify, and payment fees are the actual Shopify Payments fees where Shopify reports them. Shipping, handling, returns and other payment fees come from your additional costs.

### Which consent does the profit event need on Shopify?

Product Metrics reads consent from **Shopify Customer Privacy**. `PMOrderProfit` needs both marketing and analytics consent.

### Do I still need my Meta pixel?

You can keep it. `Purchase` uses the order transaction ID, so Meta counts it once when your pixel and the Meta Conversions API both send it within 48 hours. The server-side events also carry hashed customer data for Advanced Matching.

### Does Meta get past orders or refunds?

No. Meta rejects events older than 7 days, so past orders aren't imported, and a later refund doesn't revise the order's Meta events.
