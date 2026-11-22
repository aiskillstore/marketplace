# Returning customer bidding in Meta on any website with Cloudflare

Source: https://www.productmetrics.io/docs/bidding/returning-customers/cloudflare-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/returning-customers/cloudflare-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send repeat orders from your website to Meta as PMReturningCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion.

Each purchase on your website reaches Product Metrics, which checks the customer's history and, for **every repeat order** (not once per customer), sends the custom events **`PMReturningCustomer`** (the order's revenue) and **`PMReturningCustomerProfit`** (its profit) to your pixel through the Meta Conversions API. Meta can only optimise on a custom event through a **custom conversion**, which you create once. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/cloudflare-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).
- **For the profit event**, your additional costs must be active and the order's costs complete.

## In the app

### 1. Connect your website and Meta

Sign in to Cloudflare and choose your domain ([Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare)). Then add your **Pixel or Dataset ID** and a Conversions API access token under **Tracking → Meta Conversions API → Connect Meta** and send a test event ([Meta](https://www.productmetrics.io/docs/channels/meta)).

Connect your website, step by step:

Then add the Meta destination:

**You should see:** the gateway card says **Gateway setup complete**; Meta accepted the test event.

### 2. Check how your website decides returning customers

Cloudflare Tracking reads each purchase from your **order confirmation page**, not from a shop system, so it has no order history to look up. A buyer is **returning** when they are identified and Product Metrics has already seen them pay on your website. Product Metrics can't confirm that anyone is new.

- **No new customers.** Website orders are never sent as **Product Metrics - New Customer** or `PMNewCustomer`.
- **Returning from what Product Metrics has seen.** History starts when tracking went live: a customer who bought before that is not recognised as returning.
  
- **Everything else is unknown.** An order that isn't returning is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.
- **Want order history?** **Custom Store / Webhook Integration** lets a developer send every order from your backend, including the customer's order history. The website still needs Cloudflare Tracking to link visits to orders.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 website orders from new or returning customers?"

**You should see:** whether the order counts as returning or unknown.

### 3. Create the custom conversion

This step happens in Meta Events Manager.

1. Choose **Custom conversions → Create custom conversion** and select your pixel.
2. Choose the event **`PMReturningCustomer`** (or **`PMReturningCustomerProfit`** to optimise on profit).
3. Add the event parameter rule **`pm_purpose` equals `CUSTOMER_RETURNING`** (or `CUSTOMER_RETURNING_PROFIT`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

> **Warning:** Meta lists an event only after it has received it once. Custom events need **marketing and analytics consent**, so place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano.

Place two test orders on your website as the same identified customer, finishing each through to the order confirmation page. Use a test event code to see it under **Test events**, then remove the code.

**You should see:** the custom conversion is listed under **Custom conversions** in Events Manager.

### 4. Optimise your campaign on it

In your retention campaign, choose the returning customer custom conversion as the conversion event and optimise on its value. Meta then gives buyers who look like your repeat customers higher priority.

**You should see:** the ad set's conversion event is your returning customer custom conversion.

### 5. Check it works

1. **Classification.** The order check from step 2 shows your test order as returning. A test order shows up under **Check your purchases** within two minutes.
2. **Event.** In Events Manager, **`PMReturningCustomer`** arrives with `pm_purpose` = `CUSTOMER_RETURNING` and `customer_type` = `RETURNING`.
3. **Custom conversion.** It shows activity after the next repeat order.
4. **Delivery.** **Tracking → Meta Conversions API** says **Meta destination saved**, and **Sending** reads **On** without "Test mode".

## How it works on a website

| | On a website |
| --- | --- |
| **Where the history comes from** | Purchases Product Metrics has seen on your website |
| **Sent for** | Every paid order after the first |
| **Meta event (`pm_purpose`)** | `PMReturningCustomer` (`CUSTOMER_RETURNING`), `PMReturningCustomerProfit` (`CUSTOMER_RETURNING_PROFIT`) |
| **Value** | The order's revenue, or its profit; a loss is sent as 0 |
| **Refunds** | Later refunds don't change the event |
| **Past orders** | Not imported; Meta rejects events older than 7 days |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders count as neither new nor returning** | Product Metrics could not tell from the order history (step 2). Those orders still go to Meta as revenue and profit, just not as new or returning. |

## FAQ

### How does Product Metrics know a website buyer is returning?

The buyer is identified and Product Metrics has already seen them pay on your website. Every other order is sent as revenue and profit only.

### Does a customer who bought before tracking went live count?

No. History starts when tracking went live, so earlier purchases on your website aren't known.

### Does PMReturningCustomerProfit work without product costs?

Yes. Profit uses your **Product cost fallback (%)** plus your additional costs.

### Why can't I select PMReturningCustomer in Events Manager yet?

Meta lists `PMReturningCustomer` only after it has received it once, and custom events need **marketing and analytics consent**. Place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano.
