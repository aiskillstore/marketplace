# Shopware lifetime value (LTV) bidding in Google Ads

Source: https://www.productmetrics.io/docs/bidding/ltv/shopware-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/ltv/shopware-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send each customer's lifetime revenue and profit from Shopware to Google Ads and bid on it with a target ROAS.

Product Metrics adds up each customer's paid Shopware orders into a **lifetime value**: what they have actually spent with you, not a prediction. Google Ads receives it as **Product Metrics - Revenue LTV** and **Product Metrics - Profit LTV**, with **every paid order** of a recognised customer: each conversion carries **what this order adds** to their lifetime value, so a customer's conversions add up to their lifetime value ([Conversion values](https://www.productmetrics.io/docs/concepts/conversion-values)).

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics, with Pro (Full Signal Tracking).
- **Your Shopware sales channel connected**: Shopware 6.7 (this plugin build supports 6.7.14.0) with PHP 8.2+, an administrator who can upload extensions, Shopware's scheduled tasks and message workers running, and the channel's public HTTPS address under **Sales Channels → your channel → Domains**. You pair one sales channel with a one-time token; it reads **Active** before you link your property. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).
- **Google Ads connected** to your property, with Data Manager access granted, and [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected. See [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

## In the app

### 1. Check your Shopware sales channel recognises customers

Ask your assistant: "Are my last five Shopware orders from new or returning customers?" A guest who later orders with an account starts again under their account.

**You should see:** whether your test order's customer was recognised, as new or returning.

### 2. Set consent

In **Tracking → Configure consent**, leave **Not configured** to use Shopware's own cookie manager, or choose OneTrust, Cookiebot, Usercentrics or Osano if your shop shows one of those. With Shopware's cookie manager, the visitor's choice for **Product Metrics advertising attribution** decides what goes with the order.

Google Ads gets a customer's LTV conversion only when the visitor allowed both **analytics** and **ad user data**, and the order carries an email address, phone number or full address Google can match. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Configure consent** names the banner your Shopware sales channel actually shows.

### 3. Create the LTV conversion actions

In Product Metrics, select **Tracking** → **Create Google Ads conversions** → **Create 8 conversion actions**. All eight are **secondary**, so nothing changes in your campaigns yet ([Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions)).

**You should see:** both LTV conversion actions are created and linked.

### 4. Add your costs (for Profit LTV)

Product costs come from the purchase price Shopware stores on each order line, as it was when the order was placed. Payment fees, returns, shipping and handling come from your [additional costs](https://www.productmetrics.io/docs/using/costs): activate them under **Tracking → Add your additional costs**.

> **Note:** Revenue LTV needs no costs. Profit LTV is only sent while the order's costs are known, and the running total only while every earlier order's costs are known too.

**You should see:** the **Profit tracking** section says your additional costs are active.

### 5. Bid on lifetime value

1. In Google Ads, make **Product Metrics - Revenue LTV** or **Product Metrics - Profit LTV** primary and your old purchase action secondary ([how](https://www.productmetrics.io/docs/using/conversion-actions#3-make-an-action-primary)). Both need a recognised customer; Profit LTV also needs known costs.
2. Set the campaign to **Maximise conversion value** with a **target ROAS**, written as a percentage.

> **Warning:** An LTV conversion carries what each order adds to a customer's lifetime value, and only recognised customers' orders count. Don't copy the target ROAS of your purchase action without thinking: set it on what a customer is worth to you over time.

**You should see:** in Google Ads, **Goals → Conversions** lists the LTV action you chose as primary.

### 6. Check it works

Open **Tracking → Conversion actions**. Then place a test order with consent accepted and ask your assistant: "I just placed a test order. Did Product Metrics get it?" See [Check tracking](https://www.productmetrics.io/docs/using/check-tracking).

**You should see:** **Tracking ready**, and the test order with its revenue, profit and customer. In the conversion action report, the LTV action gets conversions from recognised customers.

## How it works on Shopware

| | On Shopware |
| --- | --- |
| **Customer** | The Shopware **customer account**, else the guest email, else the phone number |
| **History** | One installation tracks one sales channel, so a customer is counted within the paired sales channel. |
| **Revenue LTV** | Products and shipping of every paid order Product Metrics has seen from the customer |
| **Profit LTV** | The same orders' profit. Costs: purchase price on each Shopware order line, plus your additional costs |
| **Sent as** | **Product Metrics - Revenue LTV** and **Product Metrics - Profit LTV**: one conversion with every paid order, worth what that order adds (a loss-making order's Profit LTV is sent as 0) |
| **Consent** | Shopware's own cookie manager (**Product Metrics advertising attribution**), or OneTrust, Cookiebot, Usercentrics or Osano; needs analytics and ad user data |

Orders from before you connected aren't imported, so lifetime value starts from the orders Product Metrics has seen.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |

## FAQ

### How does Product Metrics recognise a returning Shopware customer?

By the Shopware customer account, else the guest email, else the phone number. One installation tracks one sales channel, so a customer is counted within the paired sales channel.

### Does Google Ads get an LTV conversion for every repeat order?

Yes. Google Ads gets one with every paid order of a recognised customer, worth what that order adds, so a customer's LTV conversions add up to their lifetime value.

### What target ROAS should I set for LTV bidding?

Set it on what a customer is worth to you over time, written as a percentage. Don't copy the target ROAS of your purchase action without thinking: each LTV conversion carries what an order adds to a recognised customer's lifetime value, and orders from customers Product Metrics can't recognise send none.

### What does Google Ads need to match an LTV conversion?

The visitor must allow both analytics and ad user data, and the order must carry an email address, phone number or full address Google can match through Enhanced Conversions. On Shopware, consent comes from Shopware's own cookie manager (**Product Metrics advertising attribution**), or OneTrust, Cookiebot, Usercentrics or Osano.
