# Shopify lifetime value (LTV) bidding in ChatGPT Ads

Source: https://www.productmetrics.io/docs/bidding/ltv/shopify-openai (the same page as Markdown: https://www.productmetrics.io/docs/bidding/ltv/shopify-openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send each customer's lifetime revenue and profit from Shopify orders to ChatGPT Ads through the OpenAI Conversions API and bid on it.

With every paid Shopify order from a recognised customer, Product Metrics sends `pm_revenue_ltv` and `pm_profit_ltv` to your ChatGPT Ads pixel. Each carries **what this order adds** to the customer's lifetime value: observed value from paid orders, not a prediction ([LTV bidding](https://www.productmetrics.io/docs/features/ltv-bidding)).

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics.
- **Your Shopify store connected**: a Shopify login that can install apps and edit the theme, the Product Metrics app installed with its app embed on, the store linked to your property, and your subscription started in the app with **Create subscription** (billed through Shopify). See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Connect your Shopify store and ChatGPT Ads

Install the Product Metrics app from the Shopify App Store, select **Link Shopify store**, turn on its app embed and link the store to your property ([Shopify](https://www.productmetrics.io/docs/platforms/shopify)). Then, in Ads Manager → **Conversions**, copy your **Pixel ID** and create a Conversions API key, and add both under **Tracking → OpenAI Conversions API → Connect OpenAI** ([ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai)).

Connect your store, step by step:

Then add the ChatGPT Ads destination:

On Shopify, Product Metrics reads consent from **Shopify Customer Privacy** (choose it under **Tracking → Configure consent**). ChatGPT Ads has no consent mode: an event is only sent with marketing consent (ad user data), and the LTV events also need analytics consent. Without ad personalisation consent, the event is sent marked as opted out. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** the Shopify app says **You're set up**, with ticks for **Shopify permissions**, **App embed** and **Checkout pixel**; the app says **OpenAI accepted the test event**.

### 2. Activate your additional costs

Skip this step if you only want Revenue LTV. Product costs come from each variant's **cost per item** in Shopify. Payment fees are the actual Shopify Payments fees where Shopify reports them; other gateways use **External payment fixed cost** and **External payment (%)**. Everything else comes from your [additional costs](https://www.productmetrics.io/docs/using/costs): activate them under **Tracking → Add your additional costs**.

> **Note:** Profit LTV is only sent when every cost of the order is known. Revenue LTV doesn't need costs. A loss-making order adds 0.

**You should see:** the **Profit tracking** section says your additional costs are active.

### 3. Add conversions for the LTV events

This step happens in ChatGPT Ads. Place a test order first, as a customer with an email address, so ChatGPT Ads has received the events.

1. In ChatGPT Ads Manager, open **Conversions**.
2. Create a conversion with the custom event name `pm_revenue_ltv`, and one with `pm_profit_ltv`.

**You should see:** the conversions show in Ads Manager. `pm_profit_ltv` only arrives once your costs are active.

### 4. Bid on lifetime value in ChatGPT Ads

In your ChatGPT Ads campaign, choose an LTV event as the conversion to optimise for, and optimise for its value. ChatGPT Ads then bids on each customer's lifetime value.

| You optimise on | Conversion |
| --- | --- |
| Lifetime revenue | `pm_revenue_ltv` |
| Lifetime profit | `pm_profit_ltv` |

**You should see:** the campaign's conversion is `pm_revenue_ltv` or `pm_profit_ltv`.

### 5. Check it works

Open **Tracking → OpenAI Conversions API**, then ask your assistant about your test order: "I just placed a test order. Did Product Metrics get it?" See [Check tracking](https://www.productmetrics.io/docs/using/check-tracking).

**You should see:** **Sending: On** and the delivery counts, and your test order with its revenue, profit and customer.

## How it works on Shopify

| | On Shopify | Sent as |
| --- | --- | --- |
| **Customer recognised by** | The customer ID on the Shopify order, else email address, else phone number | No customer, no LTV event |
| **Revenue LTV** | Products and shipping this order adds | `pm_revenue_ltv` |
| **Profit LTV** | Profit this order adds, once costs are known | `pm_profit_ltv`; 0 for a loss |
| **Earlier orders** | Only orders Product Metrics has seen count | Not imported |
| **Refunds** | Your store reports them | Not sent: ChatGPT Ads events aren't revised |

ChatGPT Ads accepts events up to 7 days old.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in ChatGPT Ads** | Check that **Tracking → Configure consent** names the banner your store actually shows: Product Metrics sends an order only with the consent this page lists. See [Consent](https://www.productmetrics.io/docs/concepts/consent). |

## FAQ

### What does ChatGPT Ads receive for each order?

The custom events `pm_revenue_ltv` and `pm_profit_ltv`, sent server-side through the OpenAI Conversions API. Each carries what this order adds, so the sum over a customer's orders is their lifetime value.

### Which Shopify orders get an LTV event?

Orders from a recognised customer: the Shopify customer ID on the order, else its email address, else its phone number. An order without a customer gets no LTV event.

### Are orders from before I connected sent to ChatGPT Ads?

No. Orders from before you connected aren't imported, and ChatGPT Ads accepts events up to 7 days old, so lifetime value starts from the orders Product Metrics has seen.

### Can ChatGPT Ads bid on new customers instead of LTV?

Yes. Create a conversion on `pm_new_customer` and `pm_new_customer_profit` in **Ads Manager → Conversions** and select it instead of the LTV one: ChatGPT Ads bids on the conversion you select.
