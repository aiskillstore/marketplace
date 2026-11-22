# Magento returning customer bidding in Meta

Source: https://www.productmetrics.io/docs/bidding/returning-customers/magento-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/returning-customers/magento-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send repeat orders from Magento to Meta as PMReturningCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion.

Each paid Magento order reaches Product Metrics, which checks the customer's history and, for **every repeat order** (not once per customer), sends the custom events **`PMReturningCustomer`** (the order's revenue) and **`PMReturningCustomerProfit`** (its profit) to your pixel through the Meta Conversions API. Meta can only optimise on a custom event through a **custom conversion**, which you create once. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/magento-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **Your Magento store view connected**: Magento 2.4, 2.0 or 1.9 / OpenMage, Magento Admin access, the public HTTPS shop address and the **store-view ID**, and a **developer** with access to your server who installs the Product Metrics module (Composer or ZIP), adds the store view's private configuration file and keeps Magento cron running. The connection reads **Active** before you link your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).
- **For the profit event**, your additional costs must be active and the order's costs complete.

## In the app

### 1. Connect Magento and Meta

Your developer installs the module and adds one configuration file per store view ([Magento](https://www.productmetrics.io/docs/platforms/magento)). Then add your **Pixel or Dataset ID** and a Conversions API access token under **Tracking → Meta Conversions API → Connect Meta** and send a test event ([Meta](https://www.productmetrics.io/docs/channels/meta)).

Connect your store, step by step:

Then add the Meta destination:

**You should see:** under **Manage Magento**, the connection is **Active** and your property is linked; Meta accepted the test event.

### 2. Check how Magento decides returning customers

The Product Metrics module looks for an earlier paid order from the same customer **in the same store view**: by customer account, or by guest email. If it finds one, the customer is **returning**. If not, they are **new**.

- **Per store view.** Each store view is connected on its own, and history is read per store view. A customer who bought in one store view is new in another.
- **History stops at the order.** Only orders placed before this order was created count.
- **Cancelled orders don't count** as earlier orders.
- **No account and no email: unknown.** An order with neither is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Magento orders from new or returning customers?"

**You should see:** whether the order counts as new, returning or unknown.

### 3. Create the custom conversion

This step happens in Meta Events Manager.

1. Choose **Custom conversions → Create custom conversion** and select your pixel.
2. Choose the event **`PMReturningCustomer`** (or **`PMReturningCustomerProfit`** to optimise on profit).
3. Add the event parameter rule **`pm_purpose` equals `CUSTOMER_RETURNING`** (or `CUSTOMER_RETURNING_PROFIT`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

> **Warning:** Meta lists an event only after it has received it once. Custom events need **marketing and analytics consent**, so place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano.

In the same store view, place a second paid order with the same customer account or guest email. Use a test event code to see it under **Test events**, then remove the code.

**You should see:** the custom conversion is listed under **Custom conversions** in Events Manager.

### 4. Optimise your campaign on it

In your retention campaign, choose the returning customer custom conversion as the conversion event and optimise on its value. Meta then gives buyers who look like your repeat customers higher priority.

**You should see:** the ad set's conversion event is your returning customer custom conversion.

### 5. Check it works

1. **Classification.** The order check from step 2 shows your test order as returning. Magento sends orders through cron, so allow a few minutes after payment.
2. **Event.** In Events Manager, **`PMReturningCustomer`** arrives with `pm_purpose` = `CUSTOMER_RETURNING` and `customer_type` = `RETURNING`.
3. **Custom conversion.** It shows activity after the next repeat order.
4. **Delivery.** **Tracking → Meta Conversions API** says **Meta destination saved**, and **Sending** reads **On** without "Test mode".

## How it works on Magento

| | On Magento |
| --- | --- |
| **Where the history comes from** | Same store view, account or guest email |
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

### Is a customer from one Magento store view returning in another?

No. History is read per store view, so their first order in another store view isn't sent as `PMReturningCustomer`.

### Does a cancelled earlier order make a customer returning?

No. Cancelled orders don't count as earlier orders.

### Why can't I select PMReturningCustomer in Events Manager yet?

Meta lists `PMReturningCustomer` only after it has received it once, and custom events need **marketing and analytics consent**. Place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano.

### Does a refund remove the PMReturningCustomer event?

No. A later refund doesn't change `PMReturningCustomer` or `PMReturningCustomerProfit` in Meta.
