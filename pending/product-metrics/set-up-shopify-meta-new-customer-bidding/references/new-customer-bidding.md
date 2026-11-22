# Shopify new customer bidding in Meta

Source: https://www.productmetrics.io/docs/bidding/new-customers/shopify-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/new-customers/shopify-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send first orders from Shopify to Meta as PMNewCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion.

For a customer's first paid Shopify order, Product Metrics sends the custom events **`PMNewCustomer`** (the order's revenue) and **`PMNewCustomerProfit`** (its profit) to your pixel through the Meta Conversions API, **once per customer**. Meta optimises on them through a **custom conversion**, which you create once. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **Your Shopify store connected**: a Shopify login that can install apps and edit the theme, the Product Metrics app installed with its app embed on, the store linked to your property, and your subscription started in the app with **Create subscription** (billed through Shopify). See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).
- **Your additional costs active**, for the profit event: [Costs](https://www.productmetrics.io/docs/using/costs).

## In the app

### 1. Connect Shopify and Meta

Connect your store with [Shopify](https://www.productmetrics.io/docs/platforms/shopify). Then, under **Tracking → Meta Conversions API → Connect Meta**, add your **Pixel or Dataset ID** and a Conversions API access token from Events Manager, and send a test event: [Meta](https://www.productmetrics.io/docs/channels/meta).

Connect your store, step by step:

Then add the Meta destination:

**You should see:** the Shopify app says **You're set up**, with ticks for **Shopify permissions**, **App embed** and **Checkout pixel**; Meta accepted the test event.

### 2. Check how Shopify decides new customers

Product Metrics reads the customer's orders from **Shopify**. If Shopify has another order from the same customer, processed before this one, the customer is **returning**. If not, they are **new**.

- **Matched by the Shopify customer** the order belongs to, so a buyer who checks out again with the same customer is recognised.
- **Long histories are read in full.** When the first page of a customer's orders shows no earlier order but there are more pages, the order waits as unknown until Product Metrics has read the rest. Then it counts as new or returning.
- **Paid only.** An order is sent once Shopify marks it paid.
- **No customer, no history.** An order Shopify links to no customer is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.
  

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Shopify orders from new or returning customers?"

**You should see:** each order counted as new, returning or unknown.

### 3. Create the custom conversion

This step happens in Meta Events Manager.

1. Choose **Custom conversions → Create custom conversion** and select your pixel.
2. Choose the event **`PMNewCustomer`** (or **`PMNewCustomerProfit`** to optimise on profit).
3. Add the event parameter rule **`pm_purpose` equals `CUSTOMER_NEW`** (or `CUSTOMER_NEW_PROFIT`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

> **Warning:** Meta lists an event only after it has received it once. Custom events need **marketing and analytics consent**, so place a test order with both accepted in **Shopify Customer Privacy**.

Check out with an email address that has never ordered from your store, and pay with your payment provider's test mode. Use a test event code to see it under **Test events**, then remove the code.

**You should see:** the custom conversion is listed under **Custom conversions** in Events Manager.

### 4. Optimise your campaign on it

In your sales campaign, choose the new customer custom conversion as the conversion event and optimise on its value. Meta then gives buyers who look like first-time customers higher priority.

**You should see:** the ad set's conversion event is your new customer custom conversion.

### 5. Check it works

Open **Tracking → Meta Conversions API**, then Events Manager: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking#4-meta-and-chatgpt-ads).

**You should see:** **Meta destination saved**, and **Sending** reads **On** without "Test mode". The order check from step 2 shows your test order as new. A paid Shopify order shows up within a few minutes. In Events Manager, **`PMNewCustomer`** arrives with `pm_purpose` = `CUSTOMER_NEW` and `customer_type` = `NEW`, and the custom conversion shows activity after the next first order.

## How it works on Shopify

| | On Shopify |
| --- | --- |
| **Where the history comes from** | Shopify customer, all earlier orders |
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

### Does Meta decide who is a new customer, or Shopify?

Product Metrics decides from the Shopify customer's earlier orders and sends `PMNewCustomer` once per customer. Meta optimises on the custom conversion you build on that event.

### Why can't I select PMNewCustomer in Events Manager yet?

Meta lists `PMNewCustomer` only after it has received it once, and custom events need **marketing and analytics consent**. Place a test order with both accepted in **Shopify Customer Privacy**.

### Are past Shopify orders sent to Meta?

No. Meta rejects events older than 7 days, so Product Metrics sends orders from the moment tracking is live.

### Does a refund remove the PMNewCustomer event?

No. A later refund doesn't change `PMNewCustomer` or `PMNewCustomerProfit` in Meta.
