# Shopify returning customer bidding in Meta

Source: https://www.productmetrics.io/docs/bidding/returning-customers/shopify-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/returning-customers/shopify-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send repeat orders from Shopify to Meta as PMReturningCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion.

Each paid Shopify order reaches Product Metrics, which checks the customer's history and, for **every repeat order** (not once per customer), sends the custom events **`PMReturningCustomer`** (the order's revenue) and **`PMReturningCustomerProfit`** (its profit) to your pixel through the Meta Conversions API. Meta can only optimise on a custom event through a **custom conversion**, which you create once. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **Your Shopify store connected**: a Shopify login that can install apps and edit the theme, the Product Metrics app installed with its app embed on, the store linked to your property, and your subscription started in the app with **Create subscription** (billed through Shopify). See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).
- **For the profit event**, your additional costs must be active and the order's costs complete.

## In the app

### 1. Connect Shopify and Meta

Install the Product Metrics app and switch on its app embed ([Shopify](https://www.productmetrics.io/docs/platforms/shopify)). Then add your **Pixel or Dataset ID** and a Conversions API access token under **Tracking → Meta Conversions API → Connect Meta** and send a test event ([Meta](https://www.productmetrics.io/docs/channels/meta)).

Connect your store, step by step:

Then add the Meta destination:

**You should see:** the Shopify app says **You're set up**, with ticks for **Shopify permissions**, **App embed** and **Checkout pixel**; Meta accepted the test event.

### 2. Check how Shopify decides returning customers

Product Metrics reads the customer's orders from **Shopify**. If Shopify has another order from the same customer, processed before this one, the customer is **returning**. If not, they are **new**.

- **Matched by the Shopify customer** the order belongs to, so a buyer who checks out again with the same customer is recognised.
- **Long histories are read in full.** When the first page of a customer's orders shows no earlier order but there are more pages, the order waits as unknown until Product Metrics has read the rest. Then it counts as new or returning.
- **Paid only.** An order is sent once Shopify marks it paid.
- **No customer, no history.** An order Shopify links to no customer is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.
  

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Shopify orders from new or returning customers?"

**You should see:** whether the order counts as new, returning or unknown.

### 3. Create the custom conversion

This step happens in Meta Events Manager.

1. Choose **Custom conversions → Create custom conversion** and select your pixel.
2. Choose the event **`PMReturningCustomer`** (or **`PMReturningCustomerProfit`** to optimise on profit).
3. Add the event parameter rule **`pm_purpose` equals `CUSTOMER_RETURNING`** (or `CUSTOMER_RETURNING_PROFIT`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

> **Warning:** Meta lists an event only after it has received it once. Custom events need **marketing and analytics consent**, so place a test order with both accepted in **Shopify Customer Privacy**.

Check out again as a customer who already has a paid order in Shopify, and pay with your payment provider's test mode. Use a test event code to see it under **Test events**, then remove the code.

**You should see:** the custom conversion is listed under **Custom conversions** in Events Manager.

### 4. Optimise your campaign on it

In your retention campaign, choose the returning customer custom conversion as the conversion event and optimise on its value. Meta then gives buyers who look like your repeat customers higher priority.

**You should see:** the ad set's conversion event is your returning customer custom conversion.

### 5. Check it works

1. **Classification.** The order check from step 2 shows your test order as returning. A paid Shopify order shows up within a few minutes.
2. **Event.** In Events Manager, **`PMReturningCustomer`** arrives with `pm_purpose` = `CUSTOMER_RETURNING` and `customer_type` = `RETURNING`.
3. **Custom conversion.** It shows activity after the next repeat order.
4. **Delivery.** **Tracking → Meta Conversions API** says **Meta destination saved**, and **Sending** reads **On** without "Test mode".

## How it works on Shopify

| | On Shopify |
| --- | --- |
| **Where the history comes from** | Shopify customer, all earlier orders |
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

### Is PMReturningCustomer sent for every repeat order?

Yes, for every paid order after the first, not once per customer.

### Does a customer who ordered before I installed the app count?

Yes. Product Metrics reads the customer's earlier orders from Shopify, so an order from before you installed the app makes their next order returning.

### Why can't I select PMReturningCustomer in Events Manager yet?

Meta lists `PMReturningCustomer` only after it has received it once, and custom events need **marketing and analytics consent**. Place a test order with both accepted in **Shopify Customer Privacy**.

### Does a refund remove the PMReturningCustomer event?

No. A later refund doesn't change `PMReturningCustomer` or `PMReturningCustomerProfit` in Meta.
