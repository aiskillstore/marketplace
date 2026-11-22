# Lightspeed new customer acquisition bidding in Google Ads

Source: https://www.productmetrics.io/docs/bidding/new-customers/lightspeed-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/new-customers/lightspeed-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send first orders from Lightspeed to Google Ads as Product Metrics - New Customer and bid on them with a target ROAS.

For a customer's first paid Lightspeed order, Product Metrics sends **Product Metrics - New Customer** (the order's revenue) and **Product Metrics - New Customer Profit** (its profit) to Google Ads, **once per customer**.

## Prerequisites

- **Your Lightspeed eCom (C-Series) shop connected**: a back-office administrator login (an API key can't sign in), the shop's cluster, hostname and numeric Shop ID, and an enabled API key with its secret that has Read on Content, Products, Customers and Orders, and Read and Write on Settings and Tracking. The shop can't already be connected to another workspace, and it reads **Active** with **Configuration is current** before you link your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).
- **Your shop domain on Cloudflare**, with its DNS record proxied (the orange cloud), and a workspace admin who signs in to Cloudflare once.
- **Google Ads connected and your additional costs active**, by a [workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role): [Google Ads](https://www.productmetrics.io/docs/channels/google-ads), [Costs](https://www.productmetrics.io/docs/using/costs).

## In the app

### 1. Check how Lightspeed decides new customers

Product Metrics uses **Lightspeed's new-customer flag** and the customer's order history in Lightspeed. When Lightspeed flags the order as a new customer's and it is the customer's only order, the customer is **new** straight away. Otherwise Product Metrics reads the customer's orders from Lightspeed: an earlier order makes them **returning**.

- **Matched by the Lightspeed customer.** An order without a Lightspeed customer to match is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.
- **Paid only.** An order is sent once Lightspeed marks it paid, so a pay-on-pickup order is sent when it is paid.
- **History is read in the background.** When Lightspeed's flag doesn't settle it, the order shows as unknown until the customer's orders are read.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Lightspeed orders from new or returning customers?"

**You should see:** each order counted as new, returning or unknown.

### 2. Create the conversion actions

Select **Tracking → Create Google Ads conversions → Create 8 conversion actions**: [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions). **Product Metrics - New Customer** and **Product Metrics - New Customer Profit** start as **secondary** goals, so nothing changes in your campaigns until you choose.

**You should see:** **Tracking → Conversion actions** shows **Tracking ready**.

### 3. Make one action primary

Pick the value to bid on:

| Bid on | Make primary |
| --- | --- |
| New customer revenue (ROAS) | **Product Metrics - New Customer** |
| New customer profit (POAS) | **Product Metrics - New Customer Profit** |

In Google Ads, make your chosen action primary and your old purchase action secondary ([how](https://www.productmetrics.io/docs/using/conversion-actions#3-make-an-action-primary)). To keep other campaigns on their current goal, set it as a campaign-specific goal instead.

**You should see:** in Google Ads, **Goals → Conversions** lists your chosen action as primary.

### 4. Bid with a target ROAS

Use **Maximise conversion value** with a **target ROAS**. Google Ads steers on the value you send, so the campaign values first orders and gives no value to the rest. Write the target as a percentage of that value: for example 300% on revenue, or 100% on profit to break even on first orders.

**Or use Google Ads' customer acquisition setting.** Performance Max and Shopping campaigns can bid for new customers only, or give new customers a higher value. Google needs to know your existing customers for that: Product Metrics fills the **All customers** list from your orders.

See [Customer list](https://www.productmetrics.io/docs/features/customer-list). In Standard Shopping, which has no customer acquisition setting, exclude that list instead.

**You should see:** the campaign on **Maximise conversion value** with your target ROAS. To confirm, ask your assistant: "Which bid strategy and target ROAS does my new customer campaign use, and which conversion goal does it bid on?"

### 5. Check it works

Place a test order: check out as a customer who has never ordered from your shop, and pay with your shop's test payment method.

**You should see:** the order check from step 1 shows it as new. A paid Lightspeed order shows up within a few minutes. **Product Metrics - New Customer** conversions grow in Google Ads as first orders come in. To compare with your store, ask your assistant: *"How many new and returning customers did we have in the last 30 days?"*

## How it works on Lightspeed

| | On Lightspeed |
| --- | --- |
| **Where the history comes from** | Lightspeed's new-customer flag, then the customer's orders |
| **Sent for** | The first paid order per customer |
| **Google Ads conversion action** | **Product Metrics - New Customer** (revenue), **Product Metrics - New Customer Profit** (profit) |
| **Value** | The order's revenue, or its profit after product and additional costs |
| **Refunds** | Product Metrics adjusts the conversion when the order is refunded or cancelled |
| **Consent** | Follows your consent platform: OneTrust, Cookiebot, Usercentrics or Osano; needs analytics and ad user data |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **The profit action gets no conversions** | Activate your additional costs under **Tracking → Add your additional costs**. Profit is only sent once they are active and the order's costs are complete. |
| **Orders count as neither new nor returning** | Product Metrics could not tell from the order history (step 1). Those orders still go to Google Ads as revenue and profit, just not as new or returning. |

## FAQ

### How does Lightspeed tell Product Metrics a customer is new?

With Lightspeed's new-customer flag. When the order is flagged and it is the customer's only order, it counts as new straight away; otherwise Product Metrics reads the customer's orders from Lightspeed.

### When is a pay-on-pickup order sent to Google Ads?

When Lightspeed marks it paid. Until then it isn't sent and doesn't count as history.

### Do Lightspeed orders from before I connected count?

They aren't sent to Google Ads, but they still count as history: a customer with an earlier Lightspeed order is returning, not new.

### What target ROAS should I set for new customers?

Write it as a percentage of the value you send. For example 300% on **Product Metrics - New Customer**, or 100% on **Product Metrics - New Customer Profit** to break even on first orders.
