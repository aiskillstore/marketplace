# WooCommerce lifetime value (LTV) bidding in Meta

Source: https://www.productmetrics.io/docs/bidding/ltv/woocommerce-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/ltv/woocommerce-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send each customer's lifetime revenue and profit from WooCommerce to Meta through the Meta Conversions API with Advanced Matching, and optimise on it.

With every paid order of a recognised WooCommerce customer, Product Metrics sends **`PMRevenueLTV`** and **`PMProfitLTV`** to your Meta pixel. Each carries **what this order adds** to the customer's lifetime value, with the running total as `pm_cumulative_ltv` ([Conversion values](https://www.productmetrics.io/docs/concepts/conversion-values)). Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/woocommerce-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).
- **Access to your pixel in Meta Events Manager**, to copy its ID and generate a Conversions API access token.

## In the app

### 1. Connect your WooCommerce store and Meta

Connect your WooCommerce store with the Product Metrics plugin and link it to your property ([WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce)). Then add your **Pixel or Dataset ID** and a Conversions API access token under **Tracking → Meta Conversions API → Connect Meta** and send a test event ([Meta](https://www.productmetrics.io/docs/channels/meta)). From then on, Product Metrics sends `PMRevenueLTV` and `PMProfitLTV` on its own.

Connect your store, step by step:

Then add the Meta destination:

**You should see:** the plugin says **Store connected successfully.** and **Webhooks: 2 of 2 active**; Events Manager shows the test event under **Test events**.

### 2. Check your WooCommerce store recognises customers

Ask your assistant: "Are my last five WooCommerce orders from new or returning customers?" A guest who later orders with an account starts again under their account. Only the order statuses you marked as paid under **Orders & product data** count: if you leave out a status your store really uses, those orders add nothing to lifetime value.

**You should see:** whether your test order's customer was recognised, as new or returning.

### 3. Set consent and costs

In **Tracking → Configure consent**, choose the banner your store shows: OneTrust, Cookiebot, Usercentrics or Osano. Clear your full-page cache after you change it. With any other banner, or left on **Not configured**, Product Metrics can't read the visitor's choice and treats it as not given: those customers get no lifetime value. Meta has no consent mode: the LTV events are only sent when the visitor allowed both **analytics** and **ad user data**. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

For Profit LTV, product costs come from **WooCommerce Core COGS** or the product meta key you chose in the plugin. Payment and actual shipping costs can come from order meta keys; everything else comes from your [additional costs](https://www.productmetrics.io/docs/using/costs): activate them under **Tracking → Add your additional costs**.

> **Note:** Revenue LTV needs no costs. Profit LTV is only sent while the order's costs are known, and the running total only while every earlier order's costs are known too.

**You should see:** **Configure consent** names the banner your WooCommerce store actually shows, and the **Profit tracking** section says your additional costs are active.

### 4. Create a custom conversion on PMRevenueLTV or PMProfitLTV

This step happens in Meta. An LTV event only appears in Meta's selector after Meta has received one, so first place a test order with consent accepted (and your costs active, for `PMProfitLTV`).

1. In Events Manager, choose **Custom conversions → Create custom conversion**.
2. Select your pixel and the event `PMRevenueLTV` (or `PMProfitLTV`).
3. Add the event parameter rule `pm_purpose` equals `CUSTOMER_REVENUE_LTV` (or `CUSTOMER_PROFIT_LTV`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

Once your test order arrived, remove the test event code, or events keep landing under **Test events** only.

**You should see:** the custom conversion shows in Events Manager.

### 5. Optimise on lifetime value

In your sales campaign, choose the LTV custom conversion as the conversion event, optimise for value and set a ROAS goal as a percentage: `PMRevenueLTV` (`CUSTOMER_REVENUE_LTV`) for lifetime revenue, `PMProfitLTV` (`CUSTOMER_PROFIT_LTV`) for lifetime profit. Every event and its purpose: [Meta events](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#meta-events).

**You should see:** the ad set's conversion event is your LTV custom conversion.

### 6. Check it works

Open **Tracking → Meta Conversions API** ([Check tracking](https://www.productmetrics.io/docs/using/check-tracking)).

**You should see:** **Access token: Saved**, **Sending: On** and the delivery counts, and `PMRevenueLTV` arriving in Events Manager from the Conversions API.

## How it works on WooCommerce

| | On WooCommerce |
| --- | --- |
| **Customer** | The WooCommerce **customer account**, else the billing email for guest orders, else the phone number |
| **History** | Each connected WooCommerce store is counted on its own. |
| **`PMRevenueLTV`** | This order's products and shipping; `pm_cumulative_ltv` is the running total |
| **`PMProfitLTV`** | This order's profit, 0 for a loss. Costs: WooCommerce Core COGS or your product meta key, plus your additional costs |
| **Consent** | OneTrust, Cookiebot, Usercentrics or Osano; needs analytics and ad user data |

Meta deduplicates on event name and order ID, so a resent order isn't counted twice. Events already sent aren't revised after a refund. Orders from before you connected aren't imported, so lifetime value starts from the orders Product Metrics has seen.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |

## FAQ

### What does Meta receive for a repeat order?

The events `PMRevenueLTV` and `PMProfitLTV`, sent through the Meta Conversions API. Each carries what this order adds to the customer's lifetime value, with the running total as `pm_cumulative_ltv`. Meta deduplicates on event name and order ID, so a resent order isn't counted twice.

### How is a WooCommerce customer recognised for Meta?

By the WooCommerce customer account, else the billing email for guest orders, else the phone number. Only orders with a status you marked as paid under **Orders & product data** count. Each event also carries hashed customer data for Advanced Matching, so Meta can match it to the person who clicked.

### Why is PMRevenueLTV missing from Meta's custom conversion selector?

An LTV event only appears there after Meta has received one. Place a test order with consent accepted first, and activate your costs if you want `PMProfitLTV`.

### Where does Profit LTV get its costs on WooCommerce?

Product costs come from WooCommerce Core COGS or your product meta key, chosen in the plugin. Everything else comes from your additional costs. A loss-making order is sent as 0.
