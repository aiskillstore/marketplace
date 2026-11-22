# Lightspeed POAS bidding: ChatGPT Ads tracking with profit

Source: https://www.productmetrics.io/docs/bidding/poas/lightspeed-openai (the same page as Markdown: https://www.productmetrics.io/docs/bidding/poas/lightspeed-openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send profit from Lightspeed orders to ChatGPT Ads through the OpenAI Conversions API and bid on it (POAS).

Every paid Lightspeed order goes to your ChatGPT Ads pixel through the OpenAI Conversions API, server-side, with its profit in the custom event [`pm_order_profit`](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#chatgpt-ads-events). Optimise for it and ChatGPT Ads bids on profit (POAS).

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your Lightspeed eCom (C-Series) shop connected**: a back-office administrator login (an API key can't sign in), the shop's cluster, hostname and numeric Shop ID, and an enabled API key with its secret that has Read on Content, Products, Customers and Orders, and Read and Write on Settings and Tracking. The shop can't already be connected to another workspace, and it reads **Active** with **Configuration is current** before you link your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).
- **Your shop domain on Cloudflare**, with its DNS record proxied (the orange cloud), and a workspace admin who signs in to Cloudflare once.
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Connect your Lightspeed shop and ChatGPT Ads

Connect your store with [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed). Then, under **Tracking → OpenAI Conversions API → Connect OpenAI**, add your **Pixel ID** and a Conversions API key from Ads Manager → **Conversions**: [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai).

Connect your store, step by step:

Then add the ChatGPT Ads destination:

On Lightspeed, Product Metrics reads consent from the banner chosen under **Tracking → Configure consent** (OneTrust, Cookiebot, Usercentrics or Osano). `pm_order_profit` also needs analytics consent. Without ad personalisation consent, the event is sent marked as opted out. See [Consent](https://www.productmetrics.io/docs/using/consent).

**You should see:** **Connection status**, **Credential status** and **Installation status** read **Active**, **Configured** and **Active**, publication reads **Configuration is current**, and the gateway says **Gateway setup complete**; the app says **OpenAI accepted the test event**.

### 2. Activate your additional costs

Product costs come from the cost price on each Lightspeed order line. Lightspeed doesn't report payment fees, so those always come from **External payment fixed cost** and **External payment (%)**. Everything else comes from your **additional costs**.

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

## How it works on Lightspeed

| | On Lightspeed | Sent as |
| --- | --- | --- |
| **Revenue** | The order's revenue | `order_created` (and `pm_order_revenue`) |
| **Product costs** | The cost price on each Lightspeed order line | Taken off profit |
| **Payment fees** | Your additional costs (Lightspeed reports no payment fees) | Taken off profit |
| **Shipping, handling, returns** | Your additional costs | Taken off profit |
| **Profit** | Revenue ex tax − all costs | `pm_order_profit`; 0 for a loss |
| **Refunds** | Your shop reports them | Not sent: ChatGPT Ads events aren't revised |

ChatGPT Ads accepts events up to 7 days old, so past orders are not imported.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |

## FAQ

### Where does pm_order_profit get its Lightspeed product costs?

From the cost price on each Lightspeed order line. For a product without one, Product Metrics uses the cost of goods in your linked Merchant Center for the same SKU, then your **Product cost fallback (%)**.

### Can I bid on new customers in ChatGPT Ads?

Yes. Product Metrics also sends `pm_new_customer` and `pm_new_customer_profit`. Create a conversion on one in **Ads Manager → Conversions** and select it as the campaign's conversion: ChatGPT Ads bids on the conversion you select. See [New customer bidding](https://www.productmetrics.io/docs/features/new-customer-bidding).

### Should I keep the OpenAI Pixel on my shop?

You can. `order_created` uses the order transaction ID, and OpenAI keeps the first event it receives for the same Pixel ID, event name and event ID, so the order counts once.

### Is pm_order_profit sent without ad personalisation consent?

Yes, marked as opted out. It does need analytics consent.
