# Returning customer bidding in Google Ads and Meta

Source: https://www.productmetrics.io/docs/features/returning-customer-bidding (the same page as Markdown: https://www.productmetrics.io/docs/features/returning-customer-bidding.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every paid repeat order to Google Ads and Meta as a returning customer conversion, and bid on repeat buyers' revenue or profit.

Product Metrics reads every paid order from your store, checks the customer's history in that store and, for a **repeat order**, sends **Product Metrics - Returning Customer** (revenue) and **Product Metrics - Returning Customer Profit** (profit) to Google Ads, and the `PMReturningCustomer` and `PMReturningCustomerProfit` events to Meta. Make one of them the goal of the campaign that serves repeat buyers.

## Pick your platform

One page per platform and channel: how that platform decides, which conversion carries it, the steps to bid on it and how to check it works.

| Store | Google Ads | Meta |
| --- | --- | --- |
| Shopify | [Shopify + Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/shopify-google-ads) | [Shopify + Meta](https://www.productmetrics.io/docs/bidding/returning-customers/shopify-meta) |
| WooCommerce | [WooCommerce + Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/woocommerce-google-ads) | [WooCommerce + Meta](https://www.productmetrics.io/docs/bidding/returning-customers/woocommerce-meta) |
| Magento | [Magento + Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/magento-google-ads) | [Magento + Meta](https://www.productmetrics.io/docs/bidding/returning-customers/magento-meta) |
| Lightspeed | [Lightspeed + Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/lightspeed-google-ads) | [Lightspeed + Meta](https://www.productmetrics.io/docs/bidding/returning-customers/lightspeed-meta) |
| Shopware | [Shopware + Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/shopware-google-ads) | [Shopware + Meta](https://www.productmetrics.io/docs/bidding/returning-customers/shopware-meta) |
| Any website (Cloudflare) | [Website + Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/cloudflare-google-ads) | [Website + Meta](https://www.productmetrics.io/docs/bidding/returning-customers/cloudflare-meta) |

## In the app

### 1. Create the conversion actions

In **Tracking → Create Google Ads conversions**, select **Create 8 conversion actions**. They include **Product Metrics - Returning Customer** and **Product Metrics - Returning Customer Profit**, created as secondary actions. Details: [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions).

**You should see:** **Conversion actions** reads **Tracking ready**.

### 2. Make it the goal of your returning customer campaign

In Google Ads, make **Product Metrics - Returning Customer** or **Product Metrics - Returning Customer Profit** the goal of the campaign that serves repeat buyers, and bid with a target ROAS (for example 500%): [Make an action primary](https://www.productmetrics.io/docs/using/conversion-actions#3-make-an-action-primary).

**You should see:** the action you chose as that campaign's goal. To check, ask your assistant: *"How many of my last 20 orders came from returning customers?"*

On Meta, you create the custom conversion yourself: see [By channel](#by-channel).

## How Product Metrics decides a customer is returning

A customer is **returning** when Product Metrics finds an earlier paid order from them in your store before this one. Without one, the customer is **new**.

1. **Only paid orders count.** An order is sent once your platform marks it paid, and only earlier paid orders count as history.
2. **Every repeat order.** Unlike the new customer conversion, which is sent once per customer, the returning customer conversion is sent for every repeat order.
3. **Unknown stays out.** When Product Metrics can't tell, for example a guest order it can't match to earlier orders, the order is still sent as **Product Metrics - Revenue** and **Product Metrics - Profit**, but not as new or returning.
4. **The store's own records decide.** History comes from your store platform: the customer account, or the guest email where the platform supports it.

```text
Order #1042  first paid order for anna@example.com     → NEW        → New Customer + Revenue
Order #1077  anna@example.com again                    → RETURNING  → Returning Customer + Revenue
Order #1103  anna@example.com a third time             → RETURNING  → Returning Customer + Revenue
```

The concept in full: [New and returning customers](https://www.productmetrics.io/docs/concepts/new-and-returning-customers).

## What each conversion carries

| Conversion | Google Ads conversion action | Meta event (`pm_purpose`) | Value |
| --- | --- | --- | --- |
| Returning customer revenue | Product Metrics - Returning Customer | `PMReturningCustomer` (`CUSTOMER_RETURNING`) | The order's revenue |
| Returning customer profit | Product Metrics - Returning Customer Profit | `PMReturningCustomerProfit` (`CUSTOMER_RETURNING_PROFIT`) | The order's profit, after product and additional costs |

The profit version is only sent once your additional costs are active and the order's costs are complete. How profit is worked out is on [Profit](https://www.productmetrics.io/docs/concepts/profit). Returning customer conversions carry each repeat order's own value; to value a customer by what the order adds to their lifetime value, see [LTV bidding](https://www.productmetrics.io/docs/features/ltv-bidding).

See also [Conversion values](https://www.productmetrics.io/docs/concepts/conversion-values) and [Conversion actions and events](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events).

## By channel

| | [Google Ads](https://www.productmetrics.io/docs/channels/google-ads) | [Meta](https://www.productmetrics.io/docs/channels/meta) |
| --- | --- | --- |
| Conversion | **Product Metrics - Returning Customer** and **Product Metrics - Returning Customer Profit** | `PMReturningCustomer` and `PMReturningCustomerProfit` events |
| Value | The repeat order's revenue, or its profit | The repeat order's revenue, or its profit; a loss is sent as 0 |
| Setup | Product Metrics creates the actions as secondary; you make one the goal of your returning customer campaign and bid with a target ROAS (for example 500%) | You create a custom conversion with the `pm_purpose` rule |
| Consent | Needs marketing (ad user data) and analytics consent | Needs marketing and analytics consent |
| Refunds | Product Metrics adjusts the conversion when the order is refunded or cancelled | Later refunds don't change the event |
| Past orders | Sent from the moment tracking is live | Not imported; Meta rejects events older than 7 days |

On [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai), Product Metrics sends `pm_returning_customer` and `pm_returning_customer_profit` as custom events: create a conversion on one in **Ads Manager → Conversions** and select it as the campaign's conversion.

A common Google Ads split is one campaign for returning customers on this action and the others on new customers only, with the customer acquisition setting. Product Metrics keeps the customer lists that need. See [Customer list](https://www.productmetrics.io/docs/features/customer-list) and [New customer bidding](https://www.productmetrics.io/docs/features/new-customer-bidding).

## By platform

| Platform | Where customer history comes from |
| --- | --- |
| [Shopify](https://www.productmetrics.io/docs/platforms/shopify) | The customer's earlier orders in Shopify. |
| [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce) | Earlier paid orders by customer account, or by billing email for guest orders. Only the order statuses you marked as paid count. |
| [Magento](https://www.productmetrics.io/docs/platforms/magento) | Earlier paid orders in the same store view, by customer account or guest email. An order with neither isn't sent as new or returning. |
| [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed) | Lightspeed's new-customer flag and the customer's order history. |
| [Shopware](https://www.productmetrics.io/docs/platforms/shopware) | Earlier paid orders in the same sales channel, by customer account or guest email. |
| [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare) | Product Metrics only sees purchases on the page, not your order history. A buyer is sent as returning when they're identified and Product Metrics has already seen them pay; otherwise the order is sent as revenue and profit only. |

## FAQ

### Is the returning customer conversion sent for every repeat order?

Yes. Unlike the new customer conversion, which is sent once per customer, it is sent for every paid order after the first.

### How is this different from LTV bidding?

A returning customer conversion carries the repeat order's own value. [LTV bidding](https://www.productmetrics.io/docs/features/ltv-bidding) values the order by what it adds to the customer's lifetime value.

### Does returning customer bidding work on a Cloudflare website?

Yes. A buyer is sent as returning when they are identified and Product Metrics has already seen them pay on your website; other orders are sent as revenue and profit only.

### Should returning customers have their own Google Ads campaign?

That is the common split: one campaign bids on returning customers, the others on new customers only with the customer acquisition setting.
