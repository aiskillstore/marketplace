# WooCommerce new customer bidding in Meta

Source: https://www.productmetrics.io/docs/bidding/new-customers/woocommerce-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/new-customers/woocommerce-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send first orders from WooCommerce to Meta as PMNewCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion.

For a customer's first paid WooCommerce order, Product Metrics sends the custom events **`PMNewCustomer`** (the order's revenue) and **`PMNewCustomerProfit`** (its profit) to your pixel through the Meta Conversions API, **once per customer**. Meta optimises on them through a **custom conversion**, which you create once. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/woocommerce-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).
- **Your additional costs active**, for the profit event: [Costs](https://www.productmetrics.io/docs/using/costs).

## In the app

### 1. Connect WooCommerce and Meta

Connect your store with [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce). Then, under **Tracking → Meta Conversions API → Connect Meta**, add your **Pixel or Dataset ID** and a Conversions API access token from Events Manager, and send a test event: [Meta](https://www.productmetrics.io/docs/channels/meta).

Connect your store, step by step:

Then add the Meta destination:

**You should see:** the plugin says **Store connected successfully.** and **Webhooks: 2 of 2 active**; Meta accepted the test event.

### 2. Check how WooCommerce decides new customers

Product Metrics looks for an earlier paid order from the same customer in **WooCommerce**: by customer account, or by **billing email** for guest orders. If it finds one, the customer is **returning**. If not, they are **new**.

- **Paid means the statuses you chose.** Only orders in the statuses selected under **Paid order statuses** (usually **Processing** and **Completed**) are sent, and only those count as earlier orders.
- **Guests are matched by billing email.** A guest who orders twice with the same billing email is returning on the second order.
- **Unpaid, failed and cancelled orders don't count**, as long as you left those statuses unselected.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 WooCommerce orders from new or returning customers?"

**You should see:** each order counted as new, returning or unknown.

### 3. Create the custom conversion

This step happens in Meta Events Manager.

1. Choose **Custom conversions → Create custom conversion** and select your pixel.
2. Choose the event **`PMNewCustomer`** (or **`PMNewCustomerProfit`** to optimise on profit).
3. Add the event parameter rule **`pm_purpose` equals `CUSTOMER_NEW`** (or `CUSTOMER_NEW_PROFIT`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

> **Warning:** Meta lists an event only after it has received it once. Custom events need **marketing and analytics consent**, so place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano (clear any full-page cache after changing it).

Check out as a guest with a billing email that has never ordered from your store, and pay so the order reaches one of your paid statuses. Use a test event code to see it under **Test events**, then remove the code.

**You should see:** the custom conversion is listed under **Custom conversions** in Events Manager.

### 4. Optimise your campaign on it

In your sales campaign, choose the new customer custom conversion as the conversion event and optimise on its value. Meta then gives buyers who look like first-time customers higher priority.

**You should see:** the ad set's conversion event is your new customer custom conversion.

### 5. Check it works

Open **Tracking → Meta Conversions API**, then Events Manager: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking#4-meta-and-chatgpt-ads).

**You should see:** **Meta destination saved**, and **Sending** reads **On** without "Test mode". The order check from step 2 shows your test order as new. With **Verify with next paid order** on, the plugin's **Live order delivery** reads **Verified** once the order arrives. In Events Manager, **`PMNewCustomer`** arrives with `pm_purpose` = `CUSTOMER_NEW` and `customer_type` = `NEW`, and the custom conversion shows activity after the next first order.

## How it works on WooCommerce

| | On WooCommerce |
| --- | --- |
| **Where the history comes from** | Account or guest billing email, paid statuses only |
| **Sent for** | The first paid order per customer |
| **Meta event (`pm_purpose`)** | `PMNewCustomer` (`CUSTOMER_NEW`), `PMNewCustomerProfit` (`CUSTOMER_NEW_PROFIT`) |
| **Value** | The order's revenue, or its profit; a loss is sent as 0 |
| **Refunds** | Later refunds don't change the event |
| **Past orders** | Not imported; Meta rejects events older than 7 days |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Meta says "The custom conversion for this event is not set up correctly"** | Check the event name and the `pm_purpose` rule of the custom conversion. |
| **Orders count as neither new nor returning** | Product Metrics could not tell from the order history (step 2). Those orders still go to Meta as revenue and profit, just not as new or returning. |

## FAQ

### Are WooCommerce guest orders sent as PMNewCustomer?

Yes, a guest's first paid order is. Guests are matched by billing email, so a second order with the same billing email is returning.

### Why can't I select PMNewCustomer in Events Manager yet?

Meta lists `PMNewCustomer` only after it has received it once, and custom events need **marketing and analytics consent**. Place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano, and clear any full-page cache after changing it.

### Which WooCommerce orders reach Meta?

Only orders in the statuses you selected under **Paid order statuses**, usually **Processing** and **Completed**.

### Does a refund remove the PMNewCustomer event?

No. A later refund doesn't change `PMNewCustomer` or `PMNewCustomerProfit` in Meta.
