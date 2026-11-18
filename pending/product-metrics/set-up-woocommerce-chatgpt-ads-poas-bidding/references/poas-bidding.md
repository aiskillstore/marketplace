# WooCommerce POAS bidding: ChatGPT Ads tracking with profit

Source: https://www.productmetrics.io/docs/bidding/poas/woocommerce-openai (the same page as Markdown: https://www.productmetrics.io/docs/bidding/poas/woocommerce-openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send profit from WooCommerce orders to ChatGPT Ads through the OpenAI Conversions API and bid on it (POAS).

Every paid WooCommerce order goes to your ChatGPT Ads pixel through the OpenAI Conversions API, server-side, with its profit in the custom event [`pm_order_profit`](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#chatgpt-ads-events). Optimise for it and ChatGPT Ads bids on profit (POAS).

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Connect your WooCommerce store and ChatGPT Ads

Connect your store with [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce). Then, under **Tracking → OpenAI Conversions API → Connect OpenAI**, add your **Pixel ID** and a Conversions API key from Ads Manager → **Conversions**: [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai).

Connect your store, step by step:

Then add the ChatGPT Ads destination:

On WooCommerce, Product Metrics reads consent from the banner chosen under **Tracking → Configure consent** (OneTrust, Cookiebot, Usercentrics or Osano). Left on **Not configured**, consent counts as not given. `pm_order_profit` also needs analytics consent.

Without ad personalisation consent, the event is sent marked as opted out. See [Consent](https://www.productmetrics.io/docs/using/consent).

**You should see:** the plugin says **Store connected successfully.** and **Webhooks: 2 of 2 active**; the app says **OpenAI accepted the test event**.

### 2. Activate your additional costs

Product costs come from the source you chose in the plugin under **Product cost**: **WooCommerce Core COGS** or a **Product meta key**. If you set **Payment cost** or **Actual shipping cost** to an **Order meta key**, those per-order costs are used instead of the estimates. Everything else comes from your **additional costs**.

Then, under **Tracking → Add your additional costs**, check the defaults for your country, set **Product cost fallback (%)** and select **Activate additional costs**: [Costs](https://www.productmetrics.io/docs/using/costs).

**You should see:** the **Profit tracking** section says your additional costs are active.

### 3. Add a conversion for pm_order_profit

This step happens in ChatGPT Ads. Place a test order first, with consent accepted and your costs active, so ChatGPT Ads has received `pm_order_profit`.

1. In ChatGPT Ads Manager, open **Conversions**.
2. Create a conversion with the custom event name `pm_order_profit`.

For revenue, `order_created` needs no extra step.

**You should see:** the conversion shows in Ads Manager.

### 4. Bid on profit in ChatGPT Ads

In your ChatGPT Ads campaign, choose the `pm_order_profit` conversion as the conversion to optimise for, and optimise for its value: break-even is 100%, €1 of profit per €1 of ad spend. For revenue (ROAS), use `order_created`; your margin decides break-even, for example 286% at a 35% margin.

**You should see:** the campaign's conversion is `pm_order_profit`, and its conversions show next to the campaign's spend in Ads Manager.

### 5. Check it works

Open **Tracking → OpenAI Conversions API**: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking#4-meta-and-chatgpt-ads).

**You should see:** **Sending: On** and the delivery counts; recent orders arrive with a known profit.

## How it works on WooCommerce

| | On WooCommerce | Sent as |
| --- | --- | --- |
| **Revenue** | The order's revenue | `order_created` (and `pm_order_revenue`) |
| **Product costs** | WooCommerce Core COGS, or the product meta key you chose in the plugin | Taken off profit |
| **Payment fees** | An order meta key you chose for **Payment cost**; otherwise your additional costs | Taken off profit |
| **Shipping, handling, returns** | Your additional costs | Taken off profit |
| **Profit** | Revenue ex tax − all costs | `pm_order_profit`; 0 for a loss |
| **Refunds** | Your store reports them | Not sent: ChatGPT Ads events aren't revised |

ChatGPT Ads accepts events up to 7 days old, so past orders are not imported.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |
| **Nothing reaches ChatGPT Ads** | Check that **Tracking → Configure consent** names the banner your store shows. Left on **Not configured**, Product Metrics can't read the visitor's choice and treats it as not given. |

## FAQ

### Where does pm_order_profit get its WooCommerce product costs?

From **WooCommerce Core COGS**, or the **Product meta key** you chose in the plugin. For a product without one, Product Metrics uses the cost of goods in your linked Merchant Center for the same SKU, then your **Product cost fallback (%)**.

### Can I bid on new customers in ChatGPT Ads?

Yes. Product Metrics also sends `pm_new_customer` and `pm_new_customer_profit`. Create a conversion on one in **Ads Manager → Conversions** and select it as the campaign's conversion: ChatGPT Ads bids on the conversion you select. See [New customer bidding](https://www.productmetrics.io/docs/features/new-customer-bidding).

### Should I keep the OpenAI Pixel on my store?

You can. `order_created` uses the order transaction ID, and OpenAI keeps the first event it receives for the same Pixel ID, event name and event ID, so the order counts once.

### Is pm_order_profit sent without ad personalisation consent?

Yes, marked as opted out. It does need analytics consent.
