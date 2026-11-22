# Lightspeed new customer bidding in Meta

Source: https://www.productmetrics.io/docs/bidding/new-customers/lightspeed-meta (the same page as Markdown: https://www.productmetrics.io/docs/bidding/new-customers/lightspeed-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send first orders from Lightspeed to Meta as PMNewCustomer through the Meta Conversions API with Advanced Matching, and optimise a campaign on a custom conversion.

For a customer's first paid Lightspeed order, Product Metrics sends the custom events **`PMNewCustomer`** (the order's revenue) and **`PMNewCustomerProfit`** (its profit) to your pixel through the Meta Conversions API, **once per customer**. Meta optimises on them through a **custom conversion**, which you create once. Each event carries hashed customer data for [Advanced Matching](https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-meta), so Meta can match it to the person who clicked.

## Prerequisites

- **Your Lightspeed eCom (C-Series) shop connected**: a back-office administrator login (an API key can't sign in), the shop's cluster, hostname and numeric Shop ID, and an enabled API key with its secret that has Read on Content, Products, Customers and Orders, and Read and Write on Settings and Tracking. The shop can't already be connected to another workspace, and it reads **Active** with **Configuration is current** before you link your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).
- **Your shop domain on Cloudflare**, with its DNS record proxied (the orange cloud), and a workspace admin who signs in to Cloudflare once.
- **Your additional costs active**, for the profit event: [Costs](https://www.productmetrics.io/docs/using/costs).

## In the app

### 1. Connect Lightspeed and Meta

Connect your store with [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed). Then, under **Tracking → Meta Conversions API → Connect Meta**, add your **Pixel or Dataset ID** and a Conversions API access token from Events Manager, and send a test event: [Meta](https://www.productmetrics.io/docs/channels/meta).

Connect your store, step by step:

Then add the Meta destination:

**You should see:** **Connection status**, **Credential status** and **Installation status** read **Active**, **Configured** and **Active**, publication reads **Configuration is current**, and the gateway says **Gateway setup complete**; Meta accepted the test event.

### 2. Check how Lightspeed decides new customers

Product Metrics uses **Lightspeed's new-customer flag** and the customer's order history in Lightspeed. When Lightspeed flags the order as a new customer's and it is the customer's only order, the customer is **new** straight away. Otherwise Product Metrics reads the customer's orders from Lightspeed: an earlier order makes them **returning**.

- **Matched by the Lightspeed customer.** An order without a Lightspeed customer to match is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.
- **Paid only.** An order is sent once Lightspeed marks it paid, so a pay-on-pickup order is sent when it is paid.
- **History is read in the background.** When Lightspeed's flag doesn't settle it, the order shows as unknown until the customer's orders are read.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Lightspeed orders from new or returning customers?"

**You should see:** each order counted as new, returning or unknown.

### 3. Create the custom conversion

This step happens in Meta Events Manager.

1. Choose **Custom conversions → Create custom conversion** and select your pixel.
2. Choose the event **`PMNewCustomer`** (or **`PMNewCustomerProfit`** to optimise on profit).
3. Add the event parameter rule **`pm_purpose` equals `CUSTOMER_NEW`** (or `CUSTOMER_NEW_PROFIT`).
4. Choose **Purchase** as the category. Use the event's value and currency; leave the fixed conversion value unset.

> **Warning:** Meta lists an event only after it has received it once. Custom events need **marketing and analytics consent**, so place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano.

Check out as a customer who has never ordered from your shop, and pay with your shop's test payment method. Use a test event code to see it under **Test events**, then remove the code.

**You should see:** the custom conversion is listed under **Custom conversions** in Events Manager.

### 4. Optimise your campaign on it

In your sales campaign, choose the new customer custom conversion as the conversion event and optimise on its value. Meta then gives buyers who look like first-time customers higher priority.

**You should see:** the ad set's conversion event is your new customer custom conversion.

### 5. Check it works

Open **Tracking → Meta Conversions API**, then Events Manager: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking#4-meta-and-chatgpt-ads).

**You should see:** **Meta destination saved**, and **Sending** reads **On** without "Test mode". The order check from step 2 shows your test order as new. A paid Lightspeed order shows up within a few minutes. In Events Manager, **`PMNewCustomer`** arrives with `pm_purpose` = `CUSTOMER_NEW` and `customer_type` = `NEW`, and the custom conversion shows activity after the next first order.

## How it works on Lightspeed

| | On Lightspeed |
| --- | --- |
| **Where the history comes from** | Lightspeed's new-customer flag, then the customer's orders |
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

### How does Lightspeed tell Product Metrics a customer is new?

With Lightspeed's new-customer flag. When the order is flagged and it is the customer's only order, `PMNewCustomer` is sent; otherwise Product Metrics first reads the customer's orders from Lightspeed.

### When is a pay-on-pickup order sent to Meta?

When Lightspeed marks it paid, not when it is placed.

### Why can't I select PMNewCustomer in Events Manager yet?

Meta lists `PMNewCustomer` only after it has received it once, and custom events need **marketing and analytics consent**. Place a test order with both accepted in OneTrust, Cookiebot, Usercentrics or Osano.

### Does a refund remove the PMNewCustomer event?

No. A later refund doesn't change `PMNewCustomer` or `PMNewCustomerProfit` in Meta.
