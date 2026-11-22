# Lightspeed returning customer bidding in Meta

Source: https://www.productmetrics.io/docs/bidding/returning-customers/lightspeed-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/returning-customers/lightspeed-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send repeat orders from Lightspeed to Meta as PMReturningCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion.

Each paid Lightspeed order reaches Product Metrics, which checks the customer's history and, for **every repeat order** (not once per customer), sends the custom events **`PMReturningCustomer`** (the order's revenue) and **`PMReturningCustomerProfit`** (its profit) to your pixel through the Meta Conversions API. Meta can only optimise on a custom event through a **custom conversion**, which you create once. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **Your Lightspeed eCom (C-Series) shop connected**: a back-office administrator login (an API key can't sign in), the shop's cluster, hostname and numeric Shop ID, and an enabled API key with its secret that has Read on Content, Products, Customers and Orders, and Read and Write on Settings and Tracking. The shop can't already be connected to another workspace, and it reads **Active** with **Configuration is current** before you link your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).
- **Your shop domain on Cloudflare**, with its DNS record proxied (the orange cloud), and a workspace admin who signs in to Cloudflare once.
- **For the profit event**, your additional costs must be active and the order's costs complete.

## In the app

### 1. Connect Lightspeed and Meta

Create a Lightspeed API key and connect it in Product Metrics ([Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed)). Then add your **Pixel or Dataset ID** and a Conversions API access token under **Tracking → Meta Conversions API → Connect Meta** and send a test event ([Meta](https://www.productmetrics.io/docs/channels/meta)).

Connect your store, step by step:

Then add the Meta destination:

**You should see:** **Connection status**, **Credential status** and **Installation status** read **Active**, **Configured** and **Active**, publication reads **Configuration is current**, and the gateway says **Gateway setup complete**; Meta accepted the test event.

### 2. Check how Lightspeed decides returning customers

Product Metrics uses **Lightspeed's new-customer flag** and the customer's order history in Lightspeed. When Lightspeed flags the order as a new customer's and it is the customer's only order, the customer is **new** straight away. Otherwise Product Metrics reads the customer's orders from Lightspeed: an earlier order makes them **returning**.

- **Matched by the Lightspeed customer.** An order without a Lightspeed customer to match is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.
- **Paid only.** An order is sent once Lightspeed marks it paid, so a pay-on-pickup order is sent when it is paid.
- **History is read in the background.** When Lightspeed's flag doesn't settle it, the order shows as unknown until the customer's orders are read.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Lightspeed orders from new or returning customers?"

**You should see:** whether the order counts as new, returning or unknown.

### 3. Create the custom conversion

This step happens in Meta Events Manager.

1. Choose **Custom conversions → Create custom conversion** and select your pixel.
2. Choose the event **`PMReturningCustomer`** (or **`PMReturningCustomerProfit`** to optimise on profit).
3. Add the event parameter rule **`pm_purpose` equals `CUSTOMER_RETURNING`** (or `CUSTOMER_RETURNING_PROFIT`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

> **Warning:** Meta lists an event only after it has received it once. Custom events need **marketing and analytics consent**, so place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano.

Check out again as the same Lightspeed customer, and pay with your shop's test payment method. Use a test event code to see it under **Test events**, then remove the code.

**You should see:** the custom conversion is listed under **Custom conversions** in Events Manager.

### 4. Optimise your campaign on it

In your retention campaign, choose the returning customer custom conversion as the conversion event and optimise on its value. Meta then gives buyers who look like your repeat customers higher priority.

**You should see:** the ad set's conversion event is your returning customer custom conversion.

### 5. Check it works

1. **Classification.** The order check from step 2 shows your test order as returning. A paid Lightspeed order shows up within a few minutes.
2. **Event.** In Events Manager, **`PMReturningCustomer`** arrives with `pm_purpose` = `CUSTOMER_RETURNING` and `customer_type` = `RETURNING`.
3. **Custom conversion.** It shows activity after the next repeat order.
4. **Delivery.** **Tracking → Meta Conversions API** says **Meta destination saved**, and **Sending** reads **On** without "Test mode".

## How it works on Lightspeed

| | On Lightspeed |
| --- | --- |
| **Where the history comes from** | Lightspeed's new-customer flag, then the customer's orders |
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

### How does Lightspeed decide a customer is returning?

Product Metrics uses Lightspeed's new-customer flag and reads the customer's orders from Lightspeed. An earlier order makes them returning.

### When is a pay-on-pickup repeat order sent to Meta?

When Lightspeed marks it paid.

### Why can't I select PMReturningCustomer in Events Manager yet?

Meta lists `PMReturningCustomer` only after it has received it once, and custom events need **marketing and analytics consent**. Place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano.

### Are past Lightspeed orders sent to Meta?

No. Meta rejects events older than 7 days, so Product Metrics sends orders from the moment tracking is live.
