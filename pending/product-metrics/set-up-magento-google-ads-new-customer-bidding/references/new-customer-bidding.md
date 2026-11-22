# Magento new customer acquisition bidding in Google Ads

Source: https://www.productmetrics.io/docs/bidding/new-customers/magento-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/new-customers/magento-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send first orders from Magento to Google Ads as Product Metrics - New Customer and bid on them with a target ROAS.

For a customer's first paid Magento order, Product Metrics sends **Product Metrics - New Customer** (the order's revenue) and **Product Metrics - New Customer Profit** (its profit) to Google Ads, **once per customer**.

## Prerequisites

- **Your Magento store view connected**: Magento 2.4, 2.0 or 1.9 / OpenMage, Magento Admin access, the public HTTPS shop address and the **store-view ID**, and a **developer** with access to your server who installs the Product Metrics module (Composer or ZIP), adds the store view's private configuration file and keeps Magento cron running. The connection reads **Active** before you link your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).
- **Google Ads connected and your additional costs active**, by a [workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role): [Google Ads](https://www.productmetrics.io/docs/channels/google-ads), [Costs](https://www.productmetrics.io/docs/using/costs).

## In the app

### 1. Check how Magento decides new customers

The Product Metrics module looks for an earlier paid order from the same customer **in the same store view**: by customer account, or by guest email. If it finds one, the customer is **returning**. If not, they are **new**.

- **Per store view.** Each store view is connected on its own, and history is read per store view. A customer who bought in one store view is new in another.
- **History stops at the order.** Only orders placed before this order was created count.
- **Cancelled orders don't count** as earlier orders.
- **No account and no email: unknown.** An order with neither is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Magento orders from new or returning customers?"

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

Place a test order: in the connected store view, check out as a guest with an email that has never ordered there, and pay with your payment provider's test mode.

**You should see:** the order check from step 1 shows it as new. Magento sends orders through cron, so allow a few minutes after payment. **Product Metrics - New Customer** conversions grow in Google Ads as first orders come in. To compare with your store, ask your assistant: *"How many new and returning customers did we have in the last 30 days?"*

## How it works on Magento

| | On Magento |
| --- | --- |
| **Where the history comes from** | Same store view, account or guest email |
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

### Is a customer new in each Magento store view?

Yes. Each store view is connected on its own and history is read per store view, so a customer who bought in one store view is new in another.

### Are guest orders sent as new customers?

Yes, when the order has a guest email to match against earlier orders. An order with no account and no email is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.

### Does a cancelled earlier order make a customer returning?

No. Cancelled orders don't count as earlier orders, so the customer's first paid order is still sent as new.

### Do I need a developer for this on Magento?

Once. A developer installs the Product Metrics module and adds one configuration file per store view; the bidding steps on this page you do yourself.
