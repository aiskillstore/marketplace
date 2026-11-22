# WooCommerce new customer acquisition bidding in Google Ads

Source: https://www.productmetrics.io/docs/bidding/new-customers/woocommerce-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/bidding/new-customers/woocommerce-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send first orders from WooCommerce to Google Ads as Product Metrics - New Customer and bid on them with a target ROAS.

For a customer's first paid WooCommerce order, Product Metrics sends **Product Metrics - New Customer** (the order's revenue) and **Product Metrics - New Customer Profit** (its profit) to Google Ads, **once per customer**.

## Prerequisites

- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).
- **Google Ads connected and your additional costs active**, by a [workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role): [Google Ads](https://www.productmetrics.io/docs/channels/google-ads), [Costs](https://www.productmetrics.io/docs/using/costs).

## In the app

### 1. Check how WooCommerce decides new customers

Product Metrics looks for an earlier paid order from the same customer in **WooCommerce**: by customer account, or by **billing email** for guest orders. If it finds one, the customer is **returning**. If not, they are **new**.

- **Paid means the statuses you chose.** Only orders in the statuses selected under **Paid order statuses** (usually **Processing** and **Completed**) are sent, and only those count as earlier orders.
- **Guests are matched by billing email.** A guest who orders twice with the same billing email is returning on the second order.
- **Unpaid, failed and cancelled orders don't count**, as long as you left those statuses unselected.

Check a few recent orders before you bid on them. Ask your assistant: "Were my last 20 WooCommerce orders from new or returning customers?"

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

Place a test order: check out as a guest with a billing email that has never ordered from your store, and pay so the order reaches one of your paid statuses.

**You should see:** the order check from step 1 shows it as new. With **Verify with next paid order** on, the plugin's **Live order delivery** reads **Verified** once the order arrives. **Product Metrics - New Customer** conversions grow in Google Ads as first orders come in. To compare with your store, ask your assistant: *"How many new and returning customers did we have in the last 30 days?"*

## How it works on WooCommerce

| | On WooCommerce |
| --- | --- |
| **Where the history comes from** | Account or guest billing email, paid statuses only |
| **Sent for** | The first paid order per customer |
| **Google Ads conversion action** | **Product Metrics - New Customer** (revenue), **Product Metrics - New Customer Profit** (profit) |
| **Value** | The order's revenue, or its profit after product and additional costs |
| **Refunds** | Product Metrics adjusts the conversion when the order is refunded or cancelled |
| **Consent** | Follows your consent platform: OneTrust, Cookiebot, Usercentrics or Osano (clear any full-page cache after changing it); needs analytics and ad user data |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **The profit action gets no conversions** | Activate your additional costs under **Tracking → Add your additional costs**. Profit is only sent once they are active and the order's costs are complete. |
| **Orders count as neither new nor returning** | Product Metrics could not tell from the order history (step 1). Those orders still go to Google Ads as revenue and profit, just not as new or returning. |

## FAQ

### Which WooCommerce orders count as paid?

Only orders in the statuses you selected under **Paid order statuses**, usually **Processing** and **Completed**. Pending, failed and cancelled orders don't count as long as those statuses stay unselected.

### Are guest checkouts recognised as repeat buyers?

Yes. Guests are matched by billing email, so a guest who orders again with the same billing email is returning and isn't sent as new a second time.

### What target ROAS should I set for new customers?

Write it as a percentage of the value you send. For example 300% on **Product Metrics - New Customer**, or 100% on **Product Metrics - New Customer Profit** to break even on first orders.

### What happens when a first order is refunded?

Product Metrics adjusts the conversion in Google Ads when the order is refunded or cancelled.
