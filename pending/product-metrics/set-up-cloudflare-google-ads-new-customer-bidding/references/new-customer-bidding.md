# New customer acquisition bidding in Google Ads on any website with Cloudflare

Source: https://www.productmetrics.io/docs/bidding/new-customers/cloudflare-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/new-customers/cloudflare-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Why website orders tracked with Cloudflare aren't sent to Google Ads as new customers, and what to bid on instead.

Cloudflare Tracking reads each purchase from your **order confirmation page**. The page tells Product Metrics what was bought, not whether this customer ever bought before, so Product Metrics can't confirm a first order. **Product Metrics - New Customer** and **Product Metrics - New Customer Profit** are **never sent** for website orders. Everything else works: revenue, profit (with **Product cost fallback (%)**) and returning customers.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics. Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).
- **Google Ads connected.** Follow [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

## In the app

### 1. Check how your website decides new customers

A buyer is **returning** when they are identified and Product Metrics has already seen them pay on your website. Product Metrics can't confirm that anyone is new.

- **Returning from what Product Metrics has seen.** History starts when tracking went live: a customer who bought before that is not recognised as returning.
  
- **Everything else is unknown.** An order that isn't returning is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.

Ask your assistant: "Were my last 20 website orders from new or returning customers?"

**You should see:** first purchases counted as unknown, and returning only for identified buyers Product Metrics has already seen pay.

### 2. Bid on something else

- **Bid on returning customers** with **Product Metrics - Returning Customer**: [Returning customer bidding on any website with Cloudflare in Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/cloudflare-google-ads).
- **Bid on all orders by profit** with **Product Metrics - Profit**: [POAS bidding](https://www.productmetrics.io/docs/features/poas-bidding).

### 3. Or send orders from your backend

With **Custom Store / Webhook Integration**, a developer sends every order from your backend, signed, when it is paid, refunded or cancelled, **including the customer's order history**. With that history Product Metrics can tell new customers apart.

The website still needs Cloudflare Tracking to link visits to orders.

### 4. Check it works

Place a test order on your website and finish it through to the order confirmation page.

**You should see:** your test order's transaction ID, value and currency. In the app, **Check your purchases** shows **Last purchase received**.

## How it works on a website

| | On a website |
| --- | --- |
| **Where the history comes from** | Purchases Product Metrics has seen on your website |
| **New customers** | Never sent: no order history to confirm a first order |
| **Returning customers** | Sent for identified buyers seen paying before |
| **Every order** | Sent as revenue and profit |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **No new customer conversions arrive** | Website orders are never sent as new customers. Bid on returning customers or on all orders by profit instead (step 2). |

## FAQ

### Are first-time website buyers still sent to Google Ads?

Yes, as **Product Metrics - Revenue** and **Product Metrics - Profit**. They aren't sent as **Product Metrics - New Customer**.

### Why can a Shopify store send new customers but my website can't?

A store platform gives Product Metrics the customer's order history. Cloudflare Tracking reads the order confirmation page, which shows what was bought, not whether the buyer bought before.

### Does profit bidding work without product costs on my website?

Yes. Profit uses your **Product cost fallback (%)** plus your additional costs, so you can bid on **Product Metrics - Profit**.

### Is a buyer from before tracking went live seen as returning?

No. History starts when tracking went live, so only purchases Product Metrics has seen on your website count.
