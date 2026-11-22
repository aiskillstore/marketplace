# Magento new customer bidding in Meta

Source: https://www.productmetrics.io/docs/bidding/new-customers/magento-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/new-customers/magento-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send first orders from Magento to Meta as PMNewCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion.

For a customer's first paid Magento order, Product Metrics sends the custom events **`PMNewCustomer`** (the order's revenue) and **`PMNewCustomerProfit`** (its profit) to your pixel through the Meta Conversions API, **once per customer**. Meta optimises on them through a **custom conversion**, which you create once. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/magento-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **Your Magento store view connected**: Magento 2.4, 2.0 or 1.9 / OpenMage, Magento Admin access, the public HTTPS shop address and the **store-view ID**, and a **developer** with access to your server who installs the Product Metrics module (Composer or ZIP), adds the store view's private configuration file and keeps Magento cron running. The connection reads **Active** before you link your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).
- **Your additional costs active**, for the profit event: [Costs](https://www.productmetrics.io/docs/using/costs).

## In the app

### 1. Connect Magento and Meta

Connect your store with [Magento](https://www.productmetrics.io/docs/platforms/magento). Then, under **Tracking → Meta Conversions API → Connect Meta**, add your **Pixel or Dataset ID** and a Conversions API access token from Events Manager, and send a test event: [Meta](https://www.productmetrics.io/docs/channels/meta).

Connect your store, step by step:

Then add the Meta destination:

**You should see:** under **Manage Magento**, the connection is **Active** and your property is linked; Meta accepted the test event.

### 2. Check how Magento decides new customers

The Product Metrics module looks for an earlier paid order from the same customer **in the same store view**: by customer account, or by guest email. If it finds one, the customer is **returning**. If not, they are **new**.

- **Per store view.** Each store view is connected on its own, and history is read per store view. A customer who bought in one store view is new in another.
- **History stops at the order.** Only orders placed before this order was created count.
- **Cancelled orders don't count** as earlier orders.
- **No account and no email: unknown.** An order with neither is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Magento orders from new or returning customers?"

**You should see:** each order counted as new, returning or unknown.

### 3. Create the custom conversion

This step happens in Meta Events Manager.

1. Choose **Custom conversions → Create custom conversion** and select your pixel.
2. Choose the event **`PMNewCustomer`** (or **`PMNewCustomerProfit`** to optimise on profit).
3. Add the event parameter rule **`pm_purpose` equals `CUSTOMER_NEW`** (or `CUSTOMER_NEW_PROFIT`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

> **Warning:** Meta lists an event only after it has received it once. Custom events need **marketing and analytics consent**, so place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano.

In the connected store view, check out as a guest with an email that has never ordered there, and pay with your payment provider's test mode. Allow a few minutes for Magento cron to run. Use a test event code to see it under **Test events**, then remove the code.

**You should see:** the custom conversion is listed under **Custom conversions** in Events Manager.

### 4. Optimise your campaign on it

In your sales campaign, choose the new customer custom conversion as the conversion event and optimise on its value. Meta then gives buyers who look like first-time customers higher priority.

**You should see:** the ad set's conversion event is your new customer custom conversion.

### 5. Check it works

Open **Tracking → Meta Conversions API**, then Events Manager: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking#4-meta-and-chatgpt-ads).

**You should see:** **Meta destination saved**, and **Sending** reads **On** without "Test mode". The order check from step 2 shows your test order as new. Magento sends orders through cron, so allow a few minutes after payment. In Events Manager, **`PMNewCustomer`** arrives with `pm_purpose` = `CUSTOMER_NEW` and `customer_type` = `NEW`, and the custom conversion shows activity after the next first order.

## How it works on Magento

| | On Magento |
| --- | --- |
| **Where the history comes from** | Same store view, account or guest email |
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

### Is a customer new in each Magento store view?

Yes. History is read per store view, so a customer who bought in one store view sends `PMNewCustomer` again on their first order in another.

### Why can't I select PMNewCustomer in Events Manager yet?

Meta lists `PMNewCustomer` only after it has received it once, and custom events need **marketing and analytics consent**. Place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano.

### Are past Magento orders sent to Meta?

No. Meta rejects events older than 7 days, so Product Metrics sends orders from the moment tracking is live.

### What does PMNewCustomerProfit send for a loss-making order?

0. A first order that makes a loss is sent with a profit of 0.
