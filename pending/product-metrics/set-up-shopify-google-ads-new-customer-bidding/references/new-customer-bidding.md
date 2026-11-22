# Shopify new customer acquisition bidding in Google Ads

Source: https://www.productmetrics.io/docs/bidding/new-customers/shopify-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/new-customers/shopify-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send first orders from Shopify to Google Ads as Product Metrics - New Customer and bid on them with a target ROAS.

For a customer's first paid Shopify order, Product Metrics sends **Product Metrics - New Customer** (the order's revenue) and **Product Metrics - New Customer Profit** (its profit) to Google Ads, **once per customer**.

## Prerequisites

- **Your Shopify store connected**: a Shopify login that can install apps and edit the theme, the Product Metrics app installed with its app embed on, the store linked to your property, and your subscription started in the app with **Create subscription** (billed through Shopify). See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).
- **Google Ads connected and your additional costs active**, by a [workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role): [Google Ads](https://www.productmetrics.io/docs/channels/google-ads), [Costs](https://www.productmetrics.io/docs/using/costs).

## In the app

### 1. Check how Shopify decides new customers

Product Metrics reads the customer's orders from **Shopify**. If Shopify has another order from the same customer, processed before this one, the customer is **returning**. If not, they are **new**.

- **Matched by the Shopify customer** the order belongs to, so a buyer who checks out again with the same customer is recognised.
- **Long histories are read in full.** When the first page of a customer's orders shows no earlier order but there are more pages, the order waits as unknown until Product Metrics has read the rest. Then it counts as new or returning.
- **Paid only.** An order is sent once Shopify marks it paid.
- **No customer, no history.** An order Shopify links to no customer is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.
  

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Shopify orders from new or returning customers?"

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

Place a test order: check out with an email address that has never ordered from your store, and pay with your payment provider's test mode.

**You should see:** the order check from step 1 shows it as new. A paid Shopify order shows up within a few minutes. **Product Metrics - New Customer** conversions grow in Google Ads as first orders come in. To compare with your store, ask your assistant: *"How many new and returning customers did we have in the last 30 days?"*

## How it works on Shopify

| | On Shopify |
| --- | --- |
| **Where the history comes from** | Shopify customer, all earlier orders |
| **Sent for** | The first paid order per customer |
| **Google Ads conversion action** | **Product Metrics - New Customer** (revenue), **Product Metrics - New Customer Profit** (profit) |
| **Value** | The order's revenue, or its profit after product and additional costs |
| **Refunds** | Product Metrics adjusts the conversion when the order is refunded or cancelled |
| **Consent** | Follows your consent platform: **Shopify Customer Privacy**; needs analytics and ad user data |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **The profit action gets no conversions** | Activate your additional costs under **Tracking → Add your additional costs**. Profit is only sent once they are active and the order's costs are complete. |
| **Orders count as neither new nor returning** | Product Metrics could not tell from the order history (step 1). Those orders still go to Google Ads as revenue and profit, just not as new or returning. |

## FAQ

### Is a customer who ordered before I installed the app new?

No. Product Metrics reads the customer's earlier orders from Shopify, so an order placed before you installed the app still makes them returning.

### What if a customer has a long order history in Shopify?

Product Metrics reads all of it. Until it has, the order waits as unknown, then it counts as new or returning.

### What target ROAS should I set for new customers?

Write it as a percentage of the value you send. For example 300% on **Product Metrics - New Customer**, or 100% on **Product Metrics - New Customer Profit** to break even on first orders.

### Can I use Google Ads' new customer acquisition setting instead?

Yes. Performance Max and Shopping campaigns can bid for new customers only, and Product Metrics fills the **All customers** list Google Ads needs for that from your orders. See [Customer list](https://www.productmetrics.io/docs/features/customer-list).
