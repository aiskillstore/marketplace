# WooCommerce returning customer bidding in Meta

Source: https://www.productmetrics.io/docs/bidding/returning-customers/woocommerce-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/returning-customers/woocommerce-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send repeat orders from WooCommerce to Meta as PMReturningCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion.

Each paid WooCommerce order reaches Product Metrics, which checks the customer's history and, for **every repeat order** (not once per customer), sends the custom events **`PMReturningCustomer`** (the order's revenue) and **`PMReturningCustomerProfit`** (its profit) to your pixel through the Meta Conversions API. Meta can only optimise on a custom event through a **custom conversion**, which you create once. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/woocommerce-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).
- **For the profit event**, your additional costs must be active and the order's costs complete.

## In the app

### 1. Connect WooCommerce and Meta

Install the Product Metrics plugin, paste the one-time token and choose your paid statuses ([WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce)). Then add your **Pixel or Dataset ID** and a Conversions API access token under **Tracking → Meta Conversions API → Connect Meta** and send a test event ([Meta](https://www.productmetrics.io/docs/channels/meta)).

Connect your store, step by step:

Then add the Meta destination:

**You should see:** the plugin says **Store connected successfully.** and **Webhooks: 2 of 2 active**; Meta accepted the test event.

### 2. Check how WooCommerce decides returning customers

Product Metrics looks for an earlier paid order from the same customer in **WooCommerce**: by customer account, or by **billing email** for guest orders. If it finds one, the customer is **returning**. If not, they are **new**.

- **Paid means the statuses you chose.** Only orders in the statuses selected under **Paid order statuses** (usually **Processing** and **Completed**) are sent, and only those count as earlier orders.
- **Guests are matched by billing email.** A guest who orders twice with the same billing email is returning on the second order.
- **Unpaid, failed and cancelled orders don't count**, as long as you left those statuses unselected.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 WooCommerce orders from new or returning customers?"

**You should see:** whether the order counts as new, returning or unknown.

### 3. Create the custom conversion

This step happens in Meta Events Manager.

1. Choose **Custom conversions → Create custom conversion** and select your pixel.
2. Choose the event **`PMReturningCustomer`** (or **`PMReturningCustomerProfit`** to optimise on profit).
3. Add the event parameter rule **`pm_purpose` equals `CUSTOMER_RETURNING`** (or `CUSTOMER_RETURNING_PROFIT`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

> **Warning:** Meta lists an event only after it has received it once. Custom events need **marketing and analytics consent**, so place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano (clear any full-page cache after changing it).

Place a second order with the same customer account or billing email, and pay so it reaches one of your paid statuses. Use a test event code to see it under **Test events**, then remove the code.

**You should see:** the custom conversion is listed under **Custom conversions** in Events Manager.

### 4. Optimise your campaign on it

In your retention campaign, choose the returning customer custom conversion as the conversion event and optimise on its value. Meta then gives buyers who look like your repeat customers higher priority.

**You should see:** the ad set's conversion event is your returning customer custom conversion.

### 5. Check it works

1. **Classification.** The order check from step 2 shows your test order as returning. With **Verify with next paid order** on, the plugin's **Live order delivery** reads **Verified** once the order arrives.
2. **Event.** In Events Manager, **`PMReturningCustomer`** arrives with `pm_purpose` = `CUSTOMER_RETURNING` and `customer_type` = `RETURNING`.
3. **Custom conversion.** It shows activity after the next repeat order.
4. **Delivery.** **Tracking → Meta Conversions API** says **Meta destination saved**, and **Sending** reads **On** without "Test mode".

## How it works on WooCommerce

| | On WooCommerce |
| --- | --- |
| **Where the history comes from** | Account or guest billing email, paid statuses only |
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

### Is a WooCommerce guest's repeat order sent to Meta?

Yes. Guests are matched by billing email, so a second order with the same billing email is sent as `PMReturningCustomer`.

### Why can't I select PMReturningCustomer in Events Manager yet?

Meta lists `PMReturningCustomer` only after it has received it once, and custom events need **marketing and analytics consent**. Place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano, and clear any full-page cache after changing it.

### Are past WooCommerce orders sent to Meta?

No. Meta rejects events older than 7 days, so Product Metrics sends orders from the moment tracking is live.

### What does PMReturningCustomerProfit send for a loss?

0. A repeat order that makes a loss is sent with a profit of 0.
