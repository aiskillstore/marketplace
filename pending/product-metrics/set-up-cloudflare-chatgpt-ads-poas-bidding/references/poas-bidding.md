# Cloudflare POAS bidding: ChatGPT Ads tracking with profit

Source: https://www.productmetrics.io/docs/bidding/poas/cloudflare-openai (the same page as Markdown: https://www.productmetrics.io/docs/bidding/poas/cloudflare-openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send profit from website purchases to ChatGPT Ads through the OpenAI Conversions API and bid on it (POAS).

Every paid website purchase goes to your ChatGPT Ads pixel through the OpenAI Conversions API, server-side, with its profit in the custom event [`pm_order_profit`](https://www.productmetrics.io/docs/concepts/conversion-actions-and-events#chatgpt-ads-events). Optimise for it and ChatGPT Ads bids on profit (POAS).

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Connect your website and ChatGPT Ads

Connect your website with [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare). Then, under **Tracking → OpenAI Conversions API → Connect OpenAI**, add your **Pixel ID** and a Conversions API key from Ads Manager → **Conversions**: [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai).

Connect your website, step by step:

Then add the ChatGPT Ads destination:

On Cloudflare Tracking, Product Metrics reads consent from the banner chosen under **Tracking → Configure consent** (OneTrust, Cookiebot, Usercentrics or Osano). `pm_order_profit` also needs analytics consent. Without ad personalisation consent, the event is sent marked as opted out. See [Consent](https://www.productmetrics.io/docs/using/consent).

**You should see:** the gateway card says **Gateway setup complete**; the app says **OpenAI accepted the test event**.

### 2. Activate your additional costs

A website sends no product costs, so profit uses your **Product cost fallback (%)** of each line's revenue. Set it to what your products cost you as a share of their price; profit is only as accurate as this number. Everything else comes from your **additional costs**.

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

**You should see:** **Sending: On** and the delivery counts; your test order is received.

## How it works on a website

| | On a website | Sent as |
| --- | --- | --- |
| **Revenue** | The order's revenue | `order_created` (and `pm_order_revenue`) |
| **Product costs** | None sent: your **Product cost fallback (%)** of each line's revenue | Taken off profit |
| **Payment fees** | Your additional costs | Taken off profit |
| **Shipping, handling, returns** | Your additional costs | Taken off profit |
| **Profit** | Revenue ex tax − all costs | `pm_order_profit`; 0 for a loss |
| **Refunds** | Tracked by Product Metrics in profit | Not sent: ChatGPT Ads events aren't revised |

ChatGPT Ads accepts events up to 7 days old, so past orders are not imported.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders arrive with revenue only** | A cost of the order is still unknown. Complete your costs under **Profit tracking → Edit costs**: an order is sent with profit only once every cost is known ([profit rules](https://www.productmetrics.io/docs/concepts/profit#rules)). |

## FAQ

### Does POAS work without product costs on my website?

Yes. Profit uses your **Product cost fallback (%)** of each line's revenue plus your additional costs, so set the fallback to what your products cost you as a share of their price.

### Can I bid on new customers in ChatGPT Ads?

Yes. Product Metrics also sends `pm_new_customer` and `pm_new_customer_profit`. Create a conversion on one in **Ads Manager → Conversions** and select it as the campaign's conversion: ChatGPT Ads bids on the conversion you select. See [New customer bidding](https://www.productmetrics.io/docs/features/new-customer-bidding).

### Should I keep the OpenAI Pixel on my website?

You can. `order_created` uses the order transaction ID, and OpenAI keeps the first event it receives for the same Pixel ID, event name and event ID, so the order counts once.

### Is pm_order_profit sent without ad personalisation consent?

Yes, marked as opted out. It does need analytics consent.
