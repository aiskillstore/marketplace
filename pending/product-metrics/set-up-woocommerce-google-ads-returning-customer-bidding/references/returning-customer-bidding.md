# WooCommerce returning customer bidding in Google Ads

Source: https://www.productmetrics.io/docs/bidding/returning-customers/woocommerce-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/returning-customers/woocommerce-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send repeat orders from WooCommerce to Google Ads as Product Metrics - Returning Customer and bid on them with a target ROAS.

Each paid WooCommerce order reaches Product Metrics, which checks the customer's history and, for **every repeat order** (not once per customer), sends **Product Metrics - Returning Customer** (the order's revenue) and **Product Metrics - Returning Customer Profit** (its profit) to Google Ads.

## Prerequisites

- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).
- **Google Ads connected and your additional costs active.** Follow [Google Ads](https://www.productmetrics.io/docs/channels/google-ads). Creating the conversion actions needs a workspace administrator. Profit is only sent once your additional costs are active and the order's costs are complete.

## In the app

### 1. Check how WooCommerce decides returning customers

Product Metrics looks for an earlier paid order from the same customer in **WooCommerce**: by customer account, or by **billing email** for guest orders. If it finds one, the customer is **returning**. If not, they are **new**.

- **Paid means the statuses you chose.** Only orders in the statuses selected under **Paid order statuses** (usually **Processing** and **Completed**) are sent, and only those count as earlier orders.
- **Guests are matched by billing email.** A guest who orders twice with the same billing email is returning on the second order.
- **Unpaid, failed and cancelled orders don't count**, as long as you left those statuses unselected.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 WooCommerce orders from new or returning customers?"

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

1. **Place a test order.** Place a second order with the same customer account or billing email, and pay so it reaches one of your paid statuses.
2. **Check its classification.** The order check from step 1 shows it as returning. With **Verify with next paid order** on, the plugin's **Live order delivery** reads **Verified** once the order arrives.
3. **Check the actions.** **Tracking → Conversion actions** shows **Tracking ready**, and in Google Ads your chosen action's conversions grow as repeat orders come in.
4. **Check the bid strategy.** Ask your assistant: *"Which bid strategy and target ROAS does my returning customer campaign use, and which conversion goal does it bid on?"*
5. **Compare with your store.** Ask your assistant: *"How many new and returning customers did we have in the last 30 days?"*

## How it works on WooCommerce

| | On WooCommerce |
| --- | --- |
| **Where the history comes from** | Account or guest billing email, paid statuses only |
| **Sent for** | Every paid order after the first |
| **Google Ads conversion action** | **Product Metrics - Returning Customer** (revenue), **Product Metrics - Returning Customer Profit** (profit) |
| **Value** | The order's revenue, or its profit after product and additional costs |
| **Refunds** | Product Metrics adjusts the conversion when the order is refunded or cancelled |
| **Consent** | Follows your consent platform: OneTrust, Cookiebot, Usercentrics or Osano (clear any full-page cache after changing it); needs analytics and ad user data |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders count as neither new nor returning** | Product Metrics could not tell from the order history (step 1). Those orders still go to Google Ads as revenue and profit, just not as new or returning. |

## FAQ

### Is a guest who orders again counted as returning?

Yes. Guests are matched by billing email, so a second order with the same billing email is returning.

### Do pending or failed orders count as earlier orders?

No. Only orders in the statuses you selected under **Paid order statuses** count, usually **Processing** and **Completed**.

### What target ROAS should I set for returning customers?

Write it as a percentage of the value you send. For example 500% on **Product Metrics - Returning Customer**, or 150% on **Product Metrics - Returning Customer Profit**.

### What happens when a repeat order is refunded?

Product Metrics adjusts the conversion in Google Ads when the order is refunded or cancelled.
