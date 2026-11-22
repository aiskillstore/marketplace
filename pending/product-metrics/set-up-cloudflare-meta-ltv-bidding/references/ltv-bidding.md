# Lifetime value (LTV) bidding in Meta on any website with Cloudflare

Source: https://www.productmetrics.io/docs/bidding/ltv/cloudflare-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/ltv/cloudflare-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send each customer's lifetime revenue and profit from your website to Meta through the Meta Conversions API with Advanced Matching, and optimise on it.

With every purchase of a recognised customer, Product Metrics sends **`PMRevenueLTV`** and **`PMProfitLTV`** to your Meta pixel. Each carries **what this order adds** to the customer's lifetime value, with the running total as `pm_cumulative_ltv` ([Conversion values](https://www.productmetrics.io/docs/concepts/conversion-values)). Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/cloudflare-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).
- **Access to your pixel in Meta Events Manager**, to copy its ID and generate a Conversions API access token.

## In the app

### 1. Connect your website and Meta

Sign in to Cloudflare, set up the gateway and link the website to your property ([Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare)). Then add your **Pixel or Dataset ID** and a Conversions API access token under **Tracking → Meta Conversions API → Connect Meta** and send a test event ([Meta](https://www.productmetrics.io/docs/channels/meta)). From then on, Product Metrics sends `PMRevenueLTV` and `PMProfitLTV` on its own.

Connect your website, step by step:

Then add the Meta destination:

**You should see:** the gateway card says **Gateway setup complete**; Events Manager shows the test event under **Test events**.

### 2. Check your website recognises customers

Lifetime value needs to know who bought: on a website, the email address your purchase page passes to Product Metrics. Place a test order.

> **Note:** Want full customer history? **Custom Store / Webhook Integration** lets a developer send every order from your backend, including the customer's order history. The website keeps Cloudflare Tracking to link visits to orders.

**You should see:** your test order as the last purchase received.

### 3. Set consent and costs

In **Tracking → Configure consent**, choose the banner your website shows: OneTrust, Cookiebot, Usercentrics or Osano. Meta has no consent mode: the LTV events are only sent when the visitor allowed both **analytics** and **ad user data**. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

For Profit LTV: website orders carry no product costs, so profit uses your **Product cost fallback (%)** of each line's revenue, plus shipping, handling, returns and payment fees from your [additional costs](https://www.productmetrics.io/docs/using/costs). Set both under **Tracking → Add your additional costs**.

> **Note:** Revenue LTV needs no costs. Profit LTV is only sent while the order's costs are known, and the running total only while every earlier order's costs are known too.

**You should see:** **Configure consent** names the banner your website actually shows, and the **Profit tracking** section says your additional costs are active.

### 4. Create a custom conversion on PMRevenueLTV or PMProfitLTV

This step happens in Meta. An LTV event only appears in Meta's selector after Meta has received one, so first place a test order on your website with consent accepted (and your costs active, for `PMProfitLTV`).

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

## How it works on a website

| | On a website |
| --- | --- |
| **Customer** | The email address your purchase page passes to Product Metrics |
| **History** | The page reports no order history, so a customer's history starts with the first purchase Product Metrics receives from your website. Refunds and cancellations count. |
| **`PMRevenueLTV`** | This order's products and shipping; `pm_cumulative_ltv` is the running total |
| **`PMProfitLTV`** | This order's profit, 0 for a loss. Costs: your **Product cost fallback (%)**, plus your additional costs |
| **Consent** | OneTrust, Cookiebot, Usercentrics or Osano; needs analytics and ad user data |

Meta deduplicates on event name and order ID, so a resent order isn't counted twice. Events already sent aren't revised after a refund. Orders from before you connected aren't imported, so lifetime value starts from the orders Product Metrics has seen.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |

## FAQ

### What does Meta receive for a repeat order?

The events `PMRevenueLTV` and `PMProfitLTV`, sent through the Meta Conversions API. Each carries what this order adds to the customer's lifetime value, with the running total as `pm_cumulative_ltv`. Meta deduplicates on event name and order ID, so a resent order isn't counted twice.

### Are past website orders counted in lifetime value?

No. The page reports no order history, so a customer's history starts with the first purchase Product Metrics receives from your website. Refunds and cancellations after that do count. For full history, a developer can send every order from your backend with **Custom Store / Webhook Integration**.

### Does PMProfitLTV work without product costs on my website?

Yes. A website sends no product costs, so profit uses your **Product cost fallback (%)** of each line's revenue, plus your additional costs. Profit is only as accurate as that percentage. A loss-making order is sent as 0.

### Why is PMRevenueLTV missing from Meta's custom conversion selector?

An LTV event only appears there after Meta has received one. Place a test order with consent accepted first, and activate your costs if you want `PMProfitLTV`.
