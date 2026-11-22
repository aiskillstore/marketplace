# Returning customer bidding in Google Ads on any website with Cloudflare

Source: https://www.productmetrics.io/docs/bidding/returning-customers/cloudflare-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/returning-customers/cloudflare-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send repeat orders from your website to Google Ads as Product Metrics - Returning Customer and bid on them with a target ROAS.

Each purchase on your website reaches Product Metrics, which checks the customer's history and, for **every repeat order** (not once per customer), sends **Product Metrics - Returning Customer** (the order's revenue) and **Product Metrics - Returning Customer Profit** (its profit) to Google Ads.

## Prerequisites

- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).
- **Google Ads connected and your additional costs active.** Follow [Google Ads](https://www.productmetrics.io/docs/channels/google-ads). Creating the conversion actions needs a workspace administrator. Profit is only sent once your additional costs are active and the order's costs are complete.

## In the app

### 1. Check how your website decides returning customers

Cloudflare Tracking reads each purchase from your **order confirmation page**, not from a shop system, so it has no order history to look up. A buyer is **returning** when they are identified and Product Metrics has already seen them pay on your website. Product Metrics can't confirm that anyone is new.

- **No new customers.** Website orders are never sent as **Product Metrics - New Customer** or `PMNewCustomer`.
- **Returning from what Product Metrics has seen.** History starts when tracking went live: a customer who bought before that is not recognised as returning.
  
- **Everything else is unknown.** An order that isn't returning is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.
- **Want order history?** **Custom Store / Webhook Integration** lets a developer send every order from your backend, including the customer's order history. The website still needs Cloudflare Tracking to link visits to orders.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 website orders from new or returning customers?"

**You should see:** whether the order counts as returning or unknown.

### 2. Create the conversion actions

In Product Metrics, select **Tracking** → **Create Google Ads conversions** → **Create 8 conversion actions**. All eight are **secondary** goals, so nothing changes in your campaigns until you choose, and Product Metrics never edits your existing conversion actions ([Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions)).

**You should see:** **Product Metrics - Returning Customer** and **Product Metrics - Returning Customer Profit** created and linked.

### 3. Bid on returning customers

Pick the value to bid on:

| Bid on | Make primary |
| --- | --- |
| Returning customer revenue (ROAS) | **Product Metrics - Returning Customer** |
| Returning customer profit (POAS) | **Product Metrics - Returning Customer Profit** |

Website orders carry no product costs, so profit uses your **Product cost fallback (%)** plus your additional costs.

1. In Google Ads, make your chosen action primary and your old purchase action secondary ([how](https://www.productmetrics.io/docs/using/conversion-actions#3-make-an-action-primary)). Usually you want this only in the campaign that serves returning customers, so set it as that campaign's own goal and keep your other campaigns on their current goal.
2. Use **Maximise conversion value** with a **target ROAS**, written as a percentage of the value you send: for example 500% on revenue, or 150% on profit. The campaign then values repeat orders and gives no value to the rest.

**A common split** is one campaign for returning customers on this action, and the others on new customers only with Google Ads' customer acquisition setting. Product Metrics keeps the customer lists that need: see [Customer list](https://www.productmetrics.io/docs/features/customer-list).

**You should see:** in Google Ads, **Goals → Conversions** lists your chosen action as primary.

### 4. Check it works

1. **Place a test order.** Place two test orders on your website as the same identified customer, finishing each through to the order confirmation page.
2. **Check its classification.** The order check from step 1 shows it as returning. A test order shows up under **Check your purchases** within two minutes.
3. **Check the actions.** **Tracking → Conversion actions** shows **Tracking ready**, and in Google Ads your chosen action's conversions grow as repeat orders come in.
4. **Check the bid strategy.** Ask your assistant: *"Which bid strategy and target ROAS does my returning customer campaign use, and which conversion goal does it bid on?"*
5. **Compare with your store.** Ask your assistant: *"How many new and returning customers did we have in the last 30 days?"*

## How it works on a website

| | On a website |
| --- | --- |
| **Where the history comes from** | Purchases Product Metrics has seen on your website |
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

### How does Product Metrics know a website buyer is returning?

The buyer is identified and Product Metrics has already seen them pay on your website. Every other order is sent as revenue and profit only.

### Does a customer who bought before tracking went live count?

No. History starts when tracking went live, so earlier purchases on your website aren't known.

### Does profit bidding work without product costs on my website?

Yes. **Product Metrics - Returning Customer Profit** uses your **Product cost fallback (%)** plus your additional costs.

### What target ROAS should I set for returning customers?

Write it as a percentage of the value you send. For example 500% on **Product Metrics - Returning Customer**, or 150% on **Product Metrics - Returning Customer Profit**.
