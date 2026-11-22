# Lifetime value (LTV) bidding in Google Ads on any website with Cloudflare

Source: https://www.productmetrics.io/docs/bidding/ltv/cloudflare-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/ltv/cloudflare-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send each customer's lifetime revenue and profit from your website to Google Ads and bid on it with a target ROAS.

Product Metrics adds up each customer's website purchases into a **lifetime value**: what they have actually spent with you, not a prediction. Google Ads receives it as **Product Metrics - Revenue LTV** and **Product Metrics - Profit LTV**, with **every paid order** of a recognised customer: each conversion carries **what this order adds** to their lifetime value, so a customer's conversions add up to their lifetime value ([Conversion values](https://www.productmetrics.io/docs/concepts/conversion-values)).

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics, with Pro (Full Signal Tracking).
- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).
- **Google Ads connected** to your property, with Data Manager access granted, and [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected. See [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

## In the app

### 1. Check your website recognises customers

Lifetime value needs to know who bought: on a website, the email address your purchase page passes to Product Metrics. Place a test order.

> **Note:** Want full customer history? **Custom Store / Webhook Integration** lets a developer send every order from your backend, including the customer's order history. The website keeps Cloudflare Tracking to link visits to orders.

**You should see:** your test order as the last purchase received.

### 2. Set consent

In **Tracking → Configure consent**, choose the banner your website shows: OneTrust, Cookiebot, Usercentrics or Osano. Google Ads gets a customer's LTV conversion only when the visitor allowed both **analytics** and **ad user data**, and the order carries an email address, phone number or full address Google can match. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Configure consent** names the banner your website actually shows.

### 3. Create the LTV conversion actions

In Product Metrics, select **Tracking** → **Create Google Ads conversions** → **Create 8 conversion actions**. All eight are **secondary**, so nothing changes in your campaigns yet ([Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions)).

**You should see:** both LTV conversion actions are created and linked.

### 4. Add your costs (for Profit LTV)

Website orders carry no product costs, so profit uses your **Product cost fallback (%)** of each line's revenue, plus shipping, handling, returns and payment fees from your [additional costs](https://www.productmetrics.io/docs/using/costs): set both under **Tracking → Add your additional costs**.

> **Note:** Revenue LTV needs no costs. Profit LTV is only sent while the order's costs are known, and the running total only while every earlier order's costs are known too.

**You should see:** the **Profit tracking** section says your additional costs are active.

### 5. Bid on lifetime value

1. In Google Ads, make **Product Metrics - Revenue LTV** or **Product Metrics - Profit LTV** primary and your old purchase action secondary ([how](https://www.productmetrics.io/docs/using/conversion-actions#3-make-an-action-primary)). Both need a recognised customer; Profit LTV also needs known costs.
2. Set the campaign to **Maximise conversion value** with a **target ROAS**, written as a percentage.

> **Warning:** An LTV conversion carries what each order adds to a customer's lifetime value, and only recognised customers' orders count. Don't copy the target ROAS of your purchase action without thinking: set it on what a customer is worth to you over time.

**You should see:** in Google Ads, **Goals → Conversions** lists the LTV action you chose as primary.

### 6. Check it works

Open **Tracking → Conversion actions**. Then ask your assistant about your test order: "I just placed a test order. Did Product Metrics get it?" See [Check tracking](https://www.productmetrics.io/docs/using/check-tracking).

**You should see:** **Tracking ready**, and the test order with its revenue, profit and customer. In the conversion action report, the LTV action gets conversions from recognised customers.

## How it works on a website

| | On a website |
| --- | --- |
| **Customer** | The email address your purchase page passes to Product Metrics |
| **History** | The page reports no order history, so a customer's history starts with the first purchase Product Metrics receives from your website. Refunds and cancellations count. |
| **Revenue LTV** | Products and shipping of every purchase Product Metrics has seen from the customer |
| **Profit LTV** | The same orders' profit. Costs: your **Product cost fallback (%)**, plus your additional costs |
| **Sent as** | **Product Metrics - Revenue LTV** and **Product Metrics - Profit LTV**: one conversion with every paid order, worth what that order adds (a loss-making order's Profit LTV is sent as 0) |
| **Consent** | OneTrust, Cookiebot, Usercentrics or Osano; needs analytics and ad user data |

Orders from before you connected aren't imported, so lifetime value starts from the orders Product Metrics has seen.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |

## FAQ

### Are past website orders counted in lifetime value?

No. The page reports no order history, so a customer's history starts with the first purchase Product Metrics receives from your website. Refunds and cancellations after that do count. For full history, a developer can send every order from your backend with **Custom Store / Webhook Integration**.

### Does Profit LTV work without product costs on my website?

Yes. A website sends no product costs, so profit uses your **Product cost fallback (%)** of each line's revenue, plus your additional costs. Profit is only as accurate as that percentage.

### Does Google Ads get an LTV conversion for every repeat order?

Yes. Google Ads gets one with every paid order of a recognised customer, worth what that order adds, so a customer's LTV conversions add up to their lifetime value.

### What target ROAS should I set for LTV bidding?

Set it on what a customer is worth to you over time, written as a percentage. Don't copy the target ROAS of your purchase action without thinking: each LTV conversion carries what an order adds to a recognised customer's lifetime value, and orders from customers Product Metrics can't recognise send none.
