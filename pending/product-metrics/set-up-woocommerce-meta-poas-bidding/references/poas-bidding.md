# WooCommerce POAS bidding: Meta Conversions API with profit

Source: https://www.productmetrics.io/docs/bidding/poas/woocommerce-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/poas/woocommerce-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send profit from WooCommerce orders to Meta through the Meta Conversions API with Advanced Matching, and optimise on it with a ROAS goal.

Every paid WooCommerce order goes to your Meta pixel through the Meta Conversions API, server-side, with its profit in the custom event [`PMOrderProfit`](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#meta-events). Optimise on a custom conversion on it and Meta steers on profit (POAS). Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/woocommerce-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).
- **Access to your pixel in Meta Events Manager**, to copy its ID and generate a Conversions API access token.

## In the app

### 1. Connect your WooCommerce store and Meta

Connect your store with [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce). Then, under **Tracking → Meta Conversions API → Connect Meta**, add your **Pixel or Dataset ID** and a Conversions API access token from Events Manager, and send a test event: [Meta](https://www.productmetrics.io/docs/channels/meta).

Connect your store, step by step:

Then add the Meta destination:

On WooCommerce, Product Metrics reads consent from the banner chosen under **Tracking → Configure consent** (OneTrust, Cookiebot, Usercentrics or Osano). Left on **Not configured**, consent counts as not given. The profit event also needs analytics consent. See [Consent](https://www.productmetrics.io/docs/using/consent).

**You should see:** the plugin says **Store connected successfully.** and **Webhooks: 2 of 2 active**; Events Manager shows the test event under **Test events**.

### 2. Activate your additional costs

Product costs come from the source you chose in the plugin under **Product cost**: **WooCommerce Core COGS** or a **Product meta key**. If you set **Payment cost** or **Actual shipping cost** to an **Order meta key**, those per-order costs are used instead of the estimates. Everything else comes from your **additional costs**.

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

## How it works on WooCommerce

| | On WooCommerce | Sent as |
| --- | --- | --- |
| **Revenue** | The order's revenue | `Purchase` (and `PMOrderRevenue`, `ORDER_REVENUE`) |
| **Product costs** | WooCommerce Core COGS, or the product meta key you chose in the plugin | Taken off profit |
| **Payment fees** | An order meta key you chose for **Payment cost**; otherwise your additional costs | Taken off profit |
| **Shipping, handling, returns** | Your additional costs | Taken off profit |
| **Profit** | Revenue ex tax − all costs | `PMOrderProfit` (`ORDER_PROFIT`); 0 for a loss, signed value in `pm_contribution_profit` |
| **Refunds** | Your store reports them | Not sent: Meta events aren't revised |

Meta rejects events older than 7 days, so past orders are not imported.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |
| **Events only show under Test events** | Remove the test event code from your Meta destination under **Tracking → Meta Conversions API**. |
| **Nothing reaches Meta** | Check that **Tracking → Configure consent** names the banner your store shows. Left on **Not configured**, Product Metrics can't read the visitor's choice and treats it as not given. |

## FAQ

### Which WooCommerce costs make up the profit Meta receives?

Product costs come from WooCommerce Core COGS or the product meta key you chose in the plugin. Payment fees come from an order meta key if you set one for **Payment cost**, otherwise from your additional costs, like shipping, handling and returns.

### Which consent banners work with WooCommerce?

OneTrust, Cookiebot, Usercentrics or Osano, chosen under **Tracking → Configure consent**. `PMOrderProfit` needs both marketing and analytics consent.

### Do I still need my Meta pixel?

You can keep it. `Purchase` uses the order transaction ID, so Meta counts it once when your pixel and the Meta Conversions API both send it within 48 hours. The server-side events also carry hashed customer data for Advanced Matching.

### Does Meta get past orders or refunds?

No. Meta rejects events older than 7 days, so past orders aren't imported, and a later refund doesn't revise the order's Meta events.
