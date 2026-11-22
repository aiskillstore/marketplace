# LTV bidding: bid on customer lifetime value in Google Ads, Meta and ChatGPT Ads

Source: https://www.productmetrics.io/docs/features/ltv-bidding (the same page as Markdown: https://www.productmetrics.io/docs/features/ltv-bidding.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send each customer's lifetime revenue and profit to Google Ads, Meta and ChatGPT Ads with every paid order, and bid on customers who come back.

**Lifetime value is what a customer has actually bought from you, added up from the paid orders Product Metrics has seen.** It is not a prediction.

Product Metrics sends it server-side with every paid order of a recognised customer: as **Product Metrics - Revenue LTV** and **Product Metrics - Profit LTV** conversion actions in Google Ads, as **`PMRevenueLTV`** and **`PMProfitLTV`** events in Meta, and as **`pm_revenue_ltv`** and **`pm_profit_ltv`** custom events in ChatGPT Ads. Smart bidding then gives higher priority to the clicks that bring customers who keep buying.

## Pick your platform

One guide per platform and channel.

| Store | Google Ads | Meta | ChatGPT Ads |
| --- | --- | --- | --- |
| Shopify | [Shopify + Google Ads](https://www.productmetrics.io/docs/bidding/ltv/shopify-google-ads) | [Shopify + Meta](https://www.productmetrics.io/docs/bidding/ltv/shopify-meta) | [Shopify + ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/shopify-openai) |
| WooCommerce | [WooCommerce + Google Ads](https://www.productmetrics.io/docs/bidding/ltv/woocommerce-google-ads) | [WooCommerce + Meta](https://www.productmetrics.io/docs/bidding/ltv/woocommerce-meta) | [WooCommerce + ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/woocommerce-openai) |
| Magento | [Magento + Google Ads](https://www.productmetrics.io/docs/bidding/ltv/magento-google-ads) | [Magento + Meta](https://www.productmetrics.io/docs/bidding/ltv/magento-meta) | [Magento + ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/magento-openai) |
| Lightspeed | [Lightspeed + Google Ads](https://www.productmetrics.io/docs/bidding/ltv/lightspeed-google-ads) | [Lightspeed + Meta](https://www.productmetrics.io/docs/bidding/ltv/lightspeed-meta) | [Lightspeed + ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/lightspeed-openai) |
| Shopware | [Shopware + Google Ads](https://www.productmetrics.io/docs/bidding/ltv/shopware-google-ads) | [Shopware + Meta](https://www.productmetrics.io/docs/bidding/ltv/shopware-meta) | [Shopware + ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/shopware-openai) |
| Any website (Cloudflare) | [Website + Google Ads](https://www.productmetrics.io/docs/bidding/ltv/cloudflare-google-ads) | [Website + Meta](https://www.productmetrics.io/docs/bidding/ltv/cloudflare-meta) | [Website + ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/cloudflare-openai) |

## In the app

### 1. Create the conversion actions

In **Tracking → Create Google Ads conversions**, select **Create 8 conversion actions**. They include **Product Metrics - Revenue LTV** and **Product Metrics - Profit LTV**, created as secondary actions. Details: [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions).

**You should see:** **Conversion actions** reads **Tracking ready**.

### 2. Make one LTV action primary

In Google Ads, make **Product Metrics - Revenue LTV** or **Product Metrics - Profit LTV** primary: [Make an action primary](https://www.productmetrics.io/docs/using/conversion-actions#3-make-an-action-primary). Profit LTV needs your [additional costs](https://www.productmetrics.io/docs/using/costs) active.

**You should see:** the LTV action you chose as primary under **Goals → Conversions**.

On Meta and ChatGPT Ads, you create the LTV conversion yourself: see [By channel](#by-channel).

## How lifetime value adds up

With each paid order, Product Metrics sends what that order adds to the customer's lifetime value; Meta also gets the running total.

```text
Order #1042  €108.00  first paid order Product Metrics saw from this customer
  → Meta       PMRevenueLTV  value 108.00  running total 108.00
  → Google Ads Product Metrics - Revenue LTV  value 108.00
Order #1077  €64.00   same customer, second paid order
  → Meta       PMRevenueLTV  value 64.00   running total 172.00
  → Google Ads Product Metrics - Revenue LTV  value 64.00
```

The values themselves are explained in [Conversion values](https://www.productmetrics.io/docs/concepts/conversion-values); who counts as a customer is in [New and returning customers](https://www.productmetrics.io/docs/concepts/new-and-returning-customers).

## Revenue LTV or Profit LTV

| | **Revenue LTV** | **Profit LTV** |
| --- | --- | --- |
| Adds up | Products and shipping of the customer's paid orders, minus refunds | Each order's profit: revenue excluding tax − product costs − additional costs |
| Needs | A recognised customer | A recognised customer and known costs on their orders |
| Use it when | Your costs aren't set up yet | You want bidding to steer on what customers earn you |

Profit is built the same way as for [POAS bidding](https://www.productmetrics.io/docs/features/poas-bidding): see [Profit](https://www.productmetrics.io/docs/concepts/profit).

## Rules

1. **A recognised customer.** By customer ID, else email address, else phone number, read from the store's order. An order without any of these gets no lifetime value.
2. **Paid orders only.** A cancelled order adds nothing. Revenue LTV counts products and shipping, and a refund lowers it.
3. **Observed, not imported.** Lifetime value starts from the orders Product Metrics has seen since you connected, and Meta's events are marked as observed.
4. **One store at a time.** Each connection is counted on its own: a Magento store view or a Shopware sales channel has its own customers.
5. **A guest who later orders with an account starts again**, because their customer ID replaces their email as the key.
6. **One currency for the total.** The running total is only sent when all of a customer's orders are in one currency.
7. **Consent.** The visitor must allow analytics and ad user data. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

## By channel

| | **[Google Ads](https://www.productmetrics.io/docs/channels/google-ads)** | **[Meta](https://www.productmetrics.io/docs/channels/meta)** | **[ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai)** |
| --- | --- | --- | --- |
| Sent as | Conversion actions **Product Metrics - Revenue LTV** and **Product Metrics - Profit LTV**, through Google's Data Manager | Custom events `PMRevenueLTV` and `PMProfitLTV`, through the Conversions API | Custom events `pm_revenue_ltv` and `pm_profit_ltv`, through the OpenAI Conversions API |
| Value | Per order: what this order adds, so the sum over a customer's orders is their lifetime value | Per order: what this order adds, with the running total alongside | Per order: what this order adds, so the sum over a customer's orders is their lifetime value |
| Setup | Created for you as secondary actions; you make one primary | You create a custom conversion per event in Events Manager | You create a conversion with the custom event name in Ads Manager → **Conversions** |
| Consent | Analytics and ad user data, plus an email, phone or address Google can match | Analytics and ad user data | Marketing consent (ad user data) |
| Profit LTV | Needs known costs on the customer's orders; a loss is sent as 0 | A loss is sent as 0, with the real profit alongside | Needs known costs on the customer's orders |

## By platform

| Platform | Customer recognised by | History |
| --- | --- | --- |
| [Shopify](https://www.productmetrics.io/docs/platforms/shopify) | Shopify customer ID, else email, else phone | Per store |
| [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce) | Customer account, else billing email | Per store; only statuses you marked as paid |
| [Magento](https://www.productmetrics.io/docs/platforms/magento) | Customer account, else guest email | Per store view; cancelled orders don't count |
| [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed) | Customer on the order, else email | Per shop; the API key needs Read on Customers |
| [Shopware](https://www.productmetrics.io/docs/platforms/shopware) | Customer account, else guest email | Per sales channel |
| [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare) | The email address your purchase page passes | From the first purchase Product Metrics receives; refunds count |

Profit LTV uses each order's profit, with product costs per platform as on [Profit](https://www.productmetrics.io/docs/concepts/profit#product-costs-per-platform).

## FAQ

### Is lifetime value a prediction of future spend?

No. It is what a customer has actually bought from you, added up from the paid orders Product Metrics has seen since you connected. Older orders aren't imported.

### Should I bid on Revenue LTV or Profit LTV?

Use Revenue LTV while your costs aren't set up yet. Use Profit LTV when you want bidding to steer on what customers earn you; it needs known costs on the customer's orders.

### How does LTV differ in Google Ads, Meta and ChatGPT Ads?

They don't differ in value: Google Ads, Meta and ChatGPT Ads each get a conversion with every paid order of a recognised customer, carrying what that order adds to their lifetime value. Meta also gets the running total.

### Why does a customer's lifetime value start again?

A guest who later orders with an account starts again, because their customer ID replaces their email as the key. Each store connection also counts its own customers, so a Magento store view or Shopware sales channel has its own.
