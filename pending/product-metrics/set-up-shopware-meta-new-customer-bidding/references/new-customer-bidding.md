# Shopware new customer bidding in Meta

Source: https://www.productmetrics.io/docs/bidding/new-customers/shopware-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/new-customers/shopware-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send first orders from Shopware to Meta as PMNewCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion.

For a customer's first paid Shopware order, Product Metrics sends the custom events **`PMNewCustomer`** (the order's revenue) and **`PMNewCustomerProfit`** (its profit) to your pixel through the Meta Conversions API, **once per customer**. Meta optimises on them through a **custom conversion**, which you create once. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopware-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **Your Shopware sales channel connected**: Shopware 6.7 (this plugin build supports 6.7.14.0) with PHP 8.2+, an administrator who can upload extensions, Shopware's scheduled tasks and message workers running, and the channel's public HTTPS address under **Sales Channels → your channel → Domains**. You pair one sales channel with a one-time token; it reads **Active** before you link your property. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).
- **Your additional costs active**, for the profit event: [Costs](https://www.productmetrics.io/docs/using/costs).

## In the app

### 1. Connect Shopware and Meta

Connect your store with [Shopware](https://www.productmetrics.io/docs/platforms/shopware). Then, under **Tracking → Meta Conversions API → Connect Meta**, add your **Pixel or Dataset ID** and a Conversions API access token from Events Manager, and send a test event: [Meta](https://www.productmetrics.io/docs/channels/meta).

Connect your store, step by step:

Then add the Meta destination:

**You should see:** in Product Metrics, the store reads **Active** after **Verify connection**; Meta accepted the test event.

### 2. Check how Shopware decides new customers

Product Metrics looks for an earlier paid order from the same customer **in the same sales channel**: by customer account, or by guest email. If it finds one, the customer is **returning**. If not, they are **new**.

- **Per sales channel.** One installation tracks one sales channel, and history is read within it. A customer who bought through another sales channel is new in this one.
- **Guests are matched by email.** A guest who orders twice with the same email is returning on the second order.
- **Paid only.** An order is sent once Shopware marks it paid, and only earlier paid orders count.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Shopware orders from new or returning customers?"

**You should see:** each order counted as new, returning or unknown.

### 3. Create the custom conversion

This step happens in Meta Events Manager.

1. Choose **Custom conversions → Create custom conversion** and select your pixel.
2. Choose the event **`PMNewCustomer`** (or **`PMNewCustomerProfit`** to optimise on profit).
3. Add the event parameter rule **`pm_purpose` equals `CUSTOMER_NEW`** (or `CUSTOMER_NEW_PROFIT`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

> **Warning:** Meta lists an event only after it has received it once. Custom events need **marketing and analytics consent**, so place a test order with both accepted in the banner you chose under **Choose your consent banner**.

Through the sales channel you paired, check out as a guest with an email that has never ordered there, and pay with your payment provider's test mode. Give Shopware a few minutes to sync it. Use a test event code to see it under **Test events**, then remove the code.

**You should see:** the custom conversion is listed under **Custom conversions** in Events Manager.

### 4. Optimise your campaign on it

In your sales campaign, choose the new customer custom conversion as the conversion event and optimise on its value. Meta then gives buyers who look like first-time customers higher priority.

**You should see:** the ad set's conversion event is your new customer custom conversion.

### 5. Check it works

Open **Tracking → Meta Conversions API**, then Events Manager: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking#4-meta-and-chatgpt-ads).

**You should see:** **Meta destination saved**, and **Sending** reads **On** without "Test mode". The order check from step 2 shows your test order as new. Shopware syncs orders within a few minutes. In Events Manager, **`PMNewCustomer`** arrives with `pm_purpose` = `CUSTOMER_NEW` and `customer_type` = `NEW`, and the custom conversion shows activity after the next first order.

## How it works on Shopware

| | On Shopware |
| --- | --- |
| **Where the history comes from** | Same sales channel, account or guest email |
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

### Is customer history shared across Shopware sales channels?

No. One installation tracks one sales channel, so a customer who bought through another sales channel is new in this one.

### Why can't I select PMNewCustomer in Events Manager yet?

Meta lists `PMNewCustomer` only after it has received it once, and custom events need **marketing and analytics consent**. Place a test order with both accepted in the banner you chose under **Choose your consent banner**.

### Are past Shopware orders sent to Meta?

No. Meta rejects events older than 7 days, so Product Metrics sends orders from the moment tracking is live.

### What does PMNewCustomerProfit send for a loss-making order?

0. A first order that makes a loss is sent with a profit of 0.
