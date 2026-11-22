# Lightspeed returning customer bidding in Google Ads

Source: https://www.productmetrics.io/docs/bidding/returning-customers/lightspeed-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/returning-customers/lightspeed-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send repeat orders from Lightspeed to Google Ads as Product Metrics - Returning Customer and bid on them with a target ROAS.

Each paid Lightspeed order reaches Product Metrics, which checks the customer's history and, for **every repeat order** (not once per customer), sends **Product Metrics - Returning Customer** (the order's revenue) and **Product Metrics - Returning Customer Profit** (its profit) to Google Ads.

## Prerequisites

- **Your Lightspeed eCom (C-Series) shop connected**: a back-office administrator login (an API key can't sign in), the shop's cluster, hostname and numeric Shop ID, and an enabled API key with its secret that has Read on Content, Products, Customers and Orders, and Read and Write on Settings and Tracking. The shop can't already be connected to another workspace, and it reads **Active** with **Configuration is current** before you link your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).
- **Your shop domain on Cloudflare**, with its DNS record proxied (the orange cloud), and a workspace admin who signs in to Cloudflare once.
- **Google Ads connected and your additional costs active.** Follow [Google Ads](https://www.productmetrics.io/docs/channels/google-ads). Creating the conversion actions needs a workspace administrator. Profit is only sent once your additional costs are active and the order's costs are complete.

## In the app

### 1. Check how Lightspeed decides returning customers

Product Metrics uses **Lightspeed's new-customer flag** and the customer's order history in Lightspeed. When Lightspeed flags the order as a new customer's and it is the customer's only order, the customer is **new** straight away. Otherwise Product Metrics reads the customer's orders from Lightspeed: an earlier order makes them **returning**.

- **Matched by the Lightspeed customer.** An order without a Lightspeed customer to match is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.
- **Paid only.** An order is sent once Lightspeed marks it paid, so a pay-on-pickup order is sent when it is paid.
- **History is read in the background.** When Lightspeed's flag doesn't settle it, the order shows as unknown until the customer's orders are read.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Lightspeed orders from new or returning customers?"

**You should see:** whether the order counts as new, returning or unknown.

### 2. Create the conversion actions

In Product Metrics, select **Tracking** → **Create Google Ads conversions** → **Create 8 conversion actions**. All eight are **secondary** goals, so nothing changes in your campaigns until you choose, and Product Metrics never edits your existing conversion actions ([Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions)).

**You should see:** **Product Metrics - Returning Customer** and **Product Metrics - Returning Customer Profit** created and linked.

### 3. Bid on returning customers

Pick the value to bid on:

| Bid on | Make primary |
| --- | --- |
| Returning customer revenue (ROAS) | **Product Metrics - Returning Customer** |
| Returning customer profit (POAS) | **Product Metrics - Returning Customer Profit** |

1. In Google Ads, make your chosen action primary and your old purchase action secondary ([how](https://www.productmetrics.io/docs/using/conversion-actions#3-make-an-action-primary)). Usually you want this only in the campaign that serves returning customers, so set it as that campaign's own goal and keep your other campaigns on their current goal.
2. Use **Maximise conversion value** with a **target ROAS**, written as a percentage of the value you send: for example 500% on revenue, or 150% on profit. The campaign then values repeat orders and gives no value to the rest.

**A common split** is one campaign for returning customers on this action, and the others on new customers only with Google Ads' customer acquisition setting. Product Metrics keeps the customer lists that need: see [Customer list](https://www.productmetrics.io/docs/features/customer-list).

**You should see:** in Google Ads, **Goals → Conversions** lists your chosen action as primary.

### 4. Check it works

1. **Place a test order.** Check out again as the same Lightspeed customer, and pay with your shop's test payment method.
2. **Check its classification.** The order check from step 1 shows it as returning. A paid Lightspeed order shows up within a few minutes.
3. **Check the actions.** **Tracking → Conversion actions** shows **Tracking ready**, and in Google Ads your chosen action's conversions grow as repeat orders come in.
4. **Check the bid strategy.** Ask your assistant: *"Which bid strategy and target ROAS does my returning customer campaign use, and which conversion goal does it bid on?"*
5. **Compare with your store.** Ask your assistant: *"How many new and returning customers did we have in the last 30 days?"*

## How it works on Lightspeed

| | On Lightspeed |
| --- | --- |
| **Where the history comes from** | Lightspeed's new-customer flag, then the customer's orders |
| **Sent for** | Every paid order after the first |
| **Google Ads conversion action** | **Product Metrics - Returning Customer** (revenue), **Product Metrics - Returning Customer Profit** (profit) |
| **Value** | The order's revenue, or its profit after product and additional costs |
| **Refunds** | Product Metrics adjusts the conversion when the order is refunded or cancelled |
| **Consent** | Follows your consent platform: OneTrust, Cookiebot, Usercentrics or Osano; needs analytics and ad user data |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders count as neither new nor returning** | Product Metrics could not tell from the order history (step 1). Those orders still go to Google Ads as revenue and profit, just not as new or returning. |

## FAQ

### How does Lightspeed decide a customer is returning?

Product Metrics uses Lightspeed's new-customer flag and reads the customer's orders from Lightspeed. An earlier order makes them returning.

### Is the conversion sent for every repeat order?

Yes. **Product Metrics - Returning Customer** is sent for every paid order after the first, not once per customer.

### When is a pay-on-pickup repeat order sent?

When Lightspeed marks it paid.

### What target ROAS should I set for returning customers?

Write it as a percentage of the value you send. For example 500% on **Product Metrics - Returning Customer**, or 150% on **Product Metrics - Returning Customer Profit**.
