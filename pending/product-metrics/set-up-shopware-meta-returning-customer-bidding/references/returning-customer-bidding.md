# Shopware returning customer bidding in Meta

Source: https://www.productmetrics.io/docs/bidding/returning-customers/shopware-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/returning-customers/shopware-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send repeat orders from Shopware to Meta as PMReturningCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion.

Each paid Shopware order reaches Product Metrics, which checks the customer's history and, for **every repeat order** (not once per customer), sends the custom events **`PMReturningCustomer`** (the order's revenue) and **`PMReturningCustomerProfit`** (its profit) to your pixel through the Meta Conversions API. Meta can only optimise on a custom event through a **custom conversion**, which you create once. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopware-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **Your Shopware sales channel connected**: Shopware 6.7 (this plugin build supports 6.7.14.0) with PHP 8.2+, an administrator who can upload extensions, Shopware's scheduled tasks and message workers running, and the channel's public HTTPS address under **Sales Channels → your channel → Domains**. You pair one sales channel with a one-time token; it reads **Active** before you link your property. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).
- **For the profit event**, your additional costs must be active and the order's costs complete.

## In the app

### 1. Connect Shopware and Meta

Install the Product Metrics plugin and pair one sales channel with a one-time token ([Shopware](https://www.productmetrics.io/docs/platforms/shopware)). Then add your **Pixel or Dataset ID** and a Conversions API access token under **Tracking → Meta Conversions API → Connect Meta** and send a test event ([Meta](https://www.productmetrics.io/docs/channels/meta)).

Connect your store, step by step:

Then add the Meta destination:

**You should see:** in Product Metrics, the store reads **Active** after **Verify connection**; Meta accepted the test event.

### 2. Check how Shopware decides returning customers

Product Metrics looks for an earlier paid order from the same customer **in the same sales channel**: by customer account, or by guest email. If it finds one, the customer is **returning**. If not, they are **new**.

- **Per sales channel.** One installation tracks one sales channel, and history is read within it. A customer who bought through another sales channel is new in this one.
- **Guests are matched by email.** A guest who orders twice with the same email is returning on the second order.
- **Paid only.** An order is sent once Shopware marks it paid, and only earlier paid orders count.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Shopware orders from new or returning customers?"

**You should see:** whether the order counts as new, returning or unknown.

### 3. Create the custom conversion

This step happens in Meta Events Manager.

1. Choose **Custom conversions → Create custom conversion** and select your pixel.
2. Choose the event **`PMReturningCustomer`** (or **`PMReturningCustomerProfit`** to optimise on profit).
3. Add the event parameter rule **`pm_purpose` equals `CUSTOMER_RETURNING`** (or `CUSTOMER_RETURNING_PROFIT`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

> **Warning:** Meta lists an event only after it has received it once. Custom events need **marketing and analytics consent**, so place a test order with both accepted in the banner you chose under **Choose your consent banner**.

Through the same sales channel, place a second paid order with the same customer account or guest email. Use a test event code to see it under **Test events**, then remove the code.

**You should see:** the custom conversion is listed under **Custom conversions** in Events Manager.

### 4. Optimise your campaign on it

In your retention campaign, choose the returning customer custom conversion as the conversion event and optimise on its value. Meta then gives buyers who look like your repeat customers higher priority.

**You should see:** the ad set's conversion event is your returning customer custom conversion.

### 5. Check it works

1. **Classification.** The order check from step 2 shows your test order as returning. Shopware syncs orders within a few minutes.
2. **Event.** In Events Manager, **`PMReturningCustomer`** arrives with `pm_purpose` = `CUSTOMER_RETURNING` and `customer_type` = `RETURNING`.
3. **Custom conversion.** It shows activity after the next repeat order.
4. **Delivery.** **Tracking → Meta Conversions API** says **Meta destination saved**, and **Sending** reads **On** without "Test mode".

## How it works on Shopware

| | On Shopware |
| --- | --- |
| **Where the history comes from** | Same sales channel, account or guest email |
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

### Does a customer of another sales channel count as returning?

No. One installation tracks one sales channel and history is read within it.

### Are Shopware guest repeat orders sent to Meta?

Yes. Guests are matched by email, so a second order with the same email is sent as `PMReturningCustomer`.

### Why can't I select PMReturningCustomer in Events Manager yet?

Meta lists `PMReturningCustomer` only after it has received it once, and custom events need **marketing and analytics consent**. Place a test order with both accepted in the banner you chose under **Choose your consent banner**.

### What does PMReturningCustomerProfit send for a loss?

0. A repeat order that makes a loss is sent with a profit of 0.
