# Magento returning customer bidding in Google Ads

Source: https://www.productmetrics.io/docs/bidding/returning-customers/magento-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/returning-customers/magento-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send repeat orders from Magento to Google Ads as Product Metrics - Returning Customer and bid on them with a target ROAS.

Each paid Magento order reaches Product Metrics, which checks the customer's history and, for **every repeat order** (not once per customer), sends **Product Metrics - Returning Customer** (the order's revenue) and **Product Metrics - Returning Customer Profit** (its profit) to Google Ads.

## Prerequisites

- **Your Magento store view connected**: Magento 2.4, 2.0 or 1.9 / OpenMage, Magento Admin access, the public HTTPS shop address and the **store-view ID**, and a **developer** with access to your server who installs the Product Metrics module (Composer or ZIP), adds the store view's private configuration file and keeps Magento cron running. The connection reads **Active** before you link your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).
- **Google Ads connected and your additional costs active.** Follow [Google Ads](https://www.productmetrics.io/docs/channels/google-ads). Creating the conversion actions needs a workspace administrator. Profit is only sent once your additional costs are active and the order's costs are complete.

## In the app

### 1. Check how Magento decides returning customers

The Product Metrics module looks for an earlier paid order from the same customer **in the same store view**: by customer account, or by guest email. If it finds one, the customer is **returning**. If not, they are **new**.

- **Per store view.** Each store view is connected on its own, and history is read per store view. A customer who bought in one store view is new in another.
- **History stops at the order.** Only orders placed before this order was created count.
- **Cancelled orders don't count** as earlier orders.
- **No account and no email: unknown.** An order with neither is sent as **Product Metrics - Revenue** and **Product Metrics - Profit** only.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 Magento orders from new or returning customers?"

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

1. **Place a test order.** In the same store view, place a second paid order with the same customer account or guest email.
2. **Check its classification.** The order check from step 1 shows it as returning. Magento sends orders through cron, so allow a few minutes after payment.
3. **Check the actions.** **Tracking → Conversion actions** shows **Tracking ready**, and in Google Ads your chosen action's conversions grow as repeat orders come in.
4. **Check the bid strategy.** Ask your assistant: *"Which bid strategy and target ROAS does my returning customer campaign use, and which conversion goal does it bid on?"*
5. **Compare with your store.** Ask your assistant: *"How many new and returning customers did we have in the last 30 days?"*

## How it works on Magento

| | On Magento |
| --- | --- |
| **Where the history comes from** | Same store view, account or guest email |
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

### Is a customer from one Magento store view returning in another?

No. History is read per store view, so their first order in another store view counts as new.

### Does a cancelled earlier order make a customer returning?

No. Cancelled orders don't count as earlier orders.

### What target ROAS should I set for returning customers?

Write it as a percentage of the value you send. For example 500% on **Product Metrics - Returning Customer**, or 150% on **Product Metrics - Returning Customer Profit**.

### Should all my campaigns bid on returning customers?

Usually only the campaign that serves returning customers. Set the action as that campaign's own goal and keep your other campaigns on their current goal, for example on new customers with Google Ads' customer acquisition setting.
