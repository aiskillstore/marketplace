# New customer bidding in Google Ads and Meta

Source: https://www.productmetrics.io/docs/features/new-customer-bidding (the same page as Markdown: https://www.productmetrics.io/docs/features/new-customer-bidding.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send each customer's first paid order to Google Ads and Meta as a new customer conversion, and bid on new customer acquisition.

Product Metrics reads every paid order from your store, checks the customer's history in that store and, for a **first paid order**, sends **Product Metrics - New Customer** (revenue) and **Product Metrics - New Customer Profit** (profit) to Google Ads, and the `PMNewCustomer` and `PMNewCustomerProfit` events to Meta.

Make one of them your campaign's goal and the campaign gives first orders higher priority than repeat orders.

## Pick your platform

One page per platform and channel: how that platform decides, which conversion carries it, the steps to bid on it and how to check it works.

| Store | Google Ads | Meta |
| --- | --- | --- |
| Shopify | [Shopify + Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/shopify-google-ads) | [Shopify + Meta](https://www.productmetrics.io/docs/bidding/new-customers/shopify-meta) |
| WooCommerce | [WooCommerce + Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/woocommerce-google-ads) | [WooCommerce + Meta](https://www.productmetrics.io/docs/bidding/new-customers/woocommerce-meta) |
| Magento | [Magento + Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/magento-google-ads) | [Magento + Meta](https://www.productmetrics.io/docs/bidding/new-customers/magento-meta) |
| Lightspeed | [Lightspeed + Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/lightspeed-google-ads) | [Lightspeed + Meta](https://www.productmetrics.io/docs/bidding/new-customers/lightspeed-meta) |
| Shopware | [Shopware + Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/shopware-google-ads) | [Shopware + Meta](https://www.productmetrics.io/docs/bidding/new-customers/shopware-meta) |
| Any website (Cloudflare) | [Website + Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/cloudflare-google-ads) | [Website + Meta](https://www.productmetrics.io/docs/bidding/new-customers/cloudflare-meta) |

On **Any website (Cloudflare)** the guides explain why new customer conversions aren't sent and what to bid on instead.

## In the app

### 1. Create the conversion actions

In **Tracking → Create Google Ads conversions**, select **Create 8 conversion actions**. They include **Product Metrics - New Customer** and **Product Metrics - New Customer Profit**, created as secondary actions. Details: [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions).

**You should see:** **Conversion actions** reads **Tracking ready**.

### 2. Make one new customer action primary

In Google Ads, make **Product Metrics - New Customer** or **Product Metrics - New Customer Profit** primary and your old purchase action secondary, then bid with a target ROAS (for example 300%): [Make an action primary](https://www.productmetrics.io/docs/using/conversion-actions#3-make-an-action-primary).

**You should see:** the action you chose as primary under **Goals → Conversions**. To check, ask your assistant: *"How many of my last 20 orders were new customers?"*

On Meta, you create the custom conversion yourself: see [By channel](#by-channel).

## How Product Metrics decides a customer is new

A customer is **new** when Product Metrics finds no earlier paid order from them in your store before this one. It is **returning** when it finds one.

1. **Only paid orders count.** An order is sent once your platform marks it paid. Pending orders aren't sent and don't count as history.
2. **Once per customer.** The new customer conversion is sent for a customer's first order only. A later order from the same customer never sends it again, to Google Ads or to Meta.
3. **Unknown stays out.** When Product Metrics can't tell, for example a guest order it can't match to earlier orders, the order is still sent as **Product Metrics - Revenue** and **Product Metrics - Profit**, but not as new or returning.
4. **The store's own records decide.** History comes from your store platform: the customer account, or the guest email where the platform supports it.

```text
Order #1042  first paid order for anna@example.com     → NEW        → New Customer + Revenue
Order #1077  anna@example.com again                    → RETURNING  → Returning Customer + Revenue
Order #1080  guest, no account or email to match       → UNKNOWN    → Revenue only
```

The concept in full: [New and returning customers](https://www.productmetrics.io/docs/concepts/new-and-returning-customers).

## What each conversion carries

| Conversion | Google Ads conversion action | Meta event (`pm_purpose`) | Value |
| --- | --- | --- | --- |
| New customer revenue | Product Metrics - New Customer | `PMNewCustomer` (`CUSTOMER_NEW`) | The order's revenue |
| New customer profit | Product Metrics - New Customer Profit | `PMNewCustomerProfit` (`CUSTOMER_NEW_PROFIT`) | The order's profit, after product and additional costs |

The profit version is only sent once your additional costs are active and the order's costs are complete. How profit is worked out is on [Profit](https://www.productmetrics.io/docs/concepts/profit). See also [Conversion values](https://www.productmetrics.io/docs/concepts/conversion-values) and [Conversion actions and events](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events).

## By channel

| | [Google Ads](https://www.productmetrics.io/docs/channels/google-ads) | [Meta](https://www.productmetrics.io/docs/channels/meta) |
| --- | --- | --- |
| Conversion | **Product Metrics - New Customer** and **Product Metrics - New Customer Profit** | `PMNewCustomer` and `PMNewCustomerProfit` events |
| Value | First order's revenue, or its profit | First order's revenue, or its profit; a loss is sent as 0 |
| Setup | Product Metrics creates the actions as secondary; you make one primary and bid with a target ROAS (for example 300%) | You create a custom conversion with the `pm_purpose` rule |
| Consent | Needs marketing (ad user data) and analytics consent | Needs marketing and analytics consent |
| Refunds | Product Metrics adjusts the conversion when the order is refunded or cancelled | Later refunds don't change the event |
| Past orders | Sent from the moment tracking is live | Not imported; Meta rejects events older than 7 days |

On [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai), Product Metrics sends `pm_new_customer` and `pm_new_customer_profit` as custom events: create a conversion on one in **Ads Manager → Conversions** and select it as the campaign's conversion.

In Google Ads you can also use the customer acquisition setting in Performance Max and Shopping: Product Metrics fills the **All customers** list it needs. See [Customer list](https://www.productmetrics.io/docs/features/customer-list).

## By platform

| Platform | Where customer history comes from |
| --- | --- |
| [Shopify](https://www.productmetrics.io/docs/platforms/shopify) | The customer's earlier orders in Shopify. |
| [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce) | Earlier paid orders by customer account, or by billing email for guest orders. Only the order statuses you marked as paid count. |
| [Magento](https://www.productmetrics.io/docs/platforms/magento) | Earlier paid orders in the same store view, by customer account or guest email. An order with neither isn't sent as new or returning. |
| [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed) | Lightspeed's new-customer flag and the customer's order history. |
| [Shopware](https://www.productmetrics.io/docs/platforms/shopware) | Earlier paid orders in the same sales channel, by customer account or guest email. |
| [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare) | Product Metrics only sees the purchase on the page, not your order history, so it can't confirm a first order: website orders aren't sent as new customers. |

## FAQ

### Is the new customer conversion sent more than once per customer?

No. It is sent for a customer's first paid order only, to Google Ads and to Meta. Later orders are sent as returning customers.

### Are guest orders counted as new customers?

Yes, where the platform matches guests by email: WooCommerce, Magento and Shopware. A guest order Product Metrics can't match is sent as revenue and profit only.

### Can I bid on new customers on a website tracked with Cloudflare?

No. Product Metrics only sees the purchase on the page, not your order history, so it can't confirm a first order. Bid on returning customers or on profit instead.

### What happens when a first order is refunded?

In Google Ads, Product Metrics adjusts the conversion. In Meta, a later refund doesn't change the event.
