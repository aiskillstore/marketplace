# ChatGPT Ads conversion tracking (OpenAI Conversions API)

Source: https://www.productmetrics.io/docs/channels/openai (the same page as Markdown: https://www.productmetrics.io/docs/channels/openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send purchases, add to carts and checkouts to your ChatGPT Ads pixel through the OpenAI Conversions API, with revenue, profit and LTV as custom events to bid on.

Product Metrics sends each paid order from its server to your **ChatGPT Ads (OpenAI)** pixel through the **OpenAI Conversions API**: `order_created`, `items_added` and `checkout_started`, plus revenue, profit and LTV as **custom events** you bid on.

This is **server-side tracking** (Full Signal Tracking). It runs on the same pipeline as [Meta](https://www.productmetrics.io/docs/channels/meta), and setup is the same on every store platform.

- **You need:** your **Pixel ID** and a **Conversions API key** from **ChatGPT Ads Manager → Conversions**.
- **In the app:** **Tracking → OpenAI Conversions API → Connect OpenAI**.
- **What is sent:** `order_created`, `items_added` and `checkout_started`, plus revenue, profit and LTV as custom events.

## Prerequisites

- [Before you start](https://www.productmetrics.io/docs/using/overview): editor or admin access in Product Metrics.
- **Your store connected** ([pick your platform](#per-platform)). ChatGPT Ads can only be added to a property whose store is tracked.
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Get your Pixel ID and Conversions API key

In ChatGPT Ads Manager, open **Conversions**. Copy the **Pixel ID** and create a **Conversions API key** for that pixel. The key is a credential: never paste it into a chat.

### 2. Add the OpenAI destination

Go to **Tracking → OpenAI Conversions API → Connect OpenAI**. Fill in **Pixel ID** and **Conversions API key**, leave **Send events to OpenAI** on, and select **Add destination**.

**You should see:** **Checking with OpenAI…**, then **OpenAI destination saved** and **OpenAI accepted the test event**.

> **Note:** Saving checks the Pixel ID and key with OpenAI first, so a wrong key fails the save. The test event is validated, not saved: it never shows in OpenAI reporting. OpenAI has no test event code.

The key is write-only: Product Metrics shows only its last four characters. A new Pixel ID needs a new key. To pause and keep your settings, turn off **Send events to OpenAI**. **Remove destination** deletes the destination and its key.

### 3. Add conversions in Ads Manager

This step happens in OpenAI. Place a test order first: a conversion shows in Ads Manager only once OpenAI has received the event. In **Ads Manager → Conversions**, create a conversion with the matching custom event name for each value you want to bid on, for example `pm_order_profit`. OpenAI lowercases custom event names. The standard events need no extra step.

Then choose that conversion as the one your ChatGPT Ads campaign optimises for, value-based: `pm_order_profit` to bid on profit ([POAS bidding](https://www.productmetrics.io/docs/bidding/poas/shopify-openai)), `pm_revenue_ltv` or `pm_profit_ltv` to bid on lifetime value ([LTV bidding](https://www.productmetrics.io/docs/bidding/ltv/shopify-openai)).

**You should see:** the conversion in Ads Manager.

### 4. Check delivery

Open **Tracking → OpenAI Conversions API**.

**You should see:** **Conversions API key** read **Accepted by OpenAI**, **Sending** on, and delivery counts. Until OpenAI accepts the first event the destination is unverified, which is normal; an error shows OpenAI's reason.

## Features on ChatGPT Ads

| Feature | On ChatGPT Ads | How |
| --- | --- | --- |
| [Server-side tracking](https://www.productmetrics.io/docs/tracking/server-side/shopify-openai) | Yes | `order_created`, `items_added` and `checkout_started` through the Conversions API |
| [OpenAI Conversions API (customer data)](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-openai) | Yes | Hashed email, phone, name and customer ID, plus postal code, country, IP and user agent |
| [POAS bidding](https://www.productmetrics.io/docs/bidding/poas/shopify-openai) | Yes | `pm_order_profit` custom event, chosen as the campaign's conversion in Ads Manager |
| ROAS | Yes | `order_created` carries revenue; also `pm_order_revenue` |
| [LTV bidding](https://www.productmetrics.io/docs/bidding/ltv/shopify-openai) | Yes | `pm_revenue_ltv` or `pm_profit_ltv` custom event, chosen as the campaign's conversion in Ads Manager |
| [New customer bidding](https://www.productmetrics.io/docs/features/new-customer-bidding) | Yes | `pm_new_customer` and `pm_new_customer_profit` custom events, chosen as the campaign's conversion in Ads Manager |
| [Returning customer bidding](https://www.productmetrics.io/docs/features/returning-customer-bidding) | Yes | `pm_returning_customer` and `pm_returning_customer_profit` custom events, chosen as the campaign's conversion in Ads Manager |
| [Customer lists](https://www.productmetrics.io/docs/features/customer-list) | No | Customer lists go to Google Ads only |

## What ChatGPT Ads receives

**Standard events**, one per action:

| Store action | OpenAI event | Value |
| --- | --- | --- |
| Paid order | `order_created` | Order revenue: products and shipping, minus refunds known at the time. Never negative. |
| Add to cart | `items_added` | The value your storefront reports, when it has one |
| Checkout started | `checkout_started` | The value your storefront reports, when it has one |

Each event lists its products: product ID, quantity and price per unit.

**Custom events**, one per value, each with its own value:

| Conversion | Custom event name |
| --- | --- |
| New customer revenue | `pm_new_customer` |
| New customer profit | `pm_new_customer_profit` |
| Returning customer revenue | `pm_returning_customer` |
| Returning customer profit | `pm_returning_customer_profit` |
| Order revenue | `pm_order_revenue` |
| Order profit | `pm_order_profit` |
| Revenue LTV | `pm_revenue_ltv` |
| Profit LTV | `pm_profit_ltv` |

- **Profit** needs a complete contribution margin, so activate your costs under **Tracking → Profit tracking**. A loss-making order is sent with value 0.
- **LTV** needs a recognised customer and sends what this order adds to the customer's lifetime value, so OpenAI's sum over a customer's orders is their lifetime value.

Every event of an order carries the order's transaction ID.

**Customer data.** With marketing consent, each event includes the shopper's hashed email, phone number, first and last name and your shop's customer ID (all SHA-256), plus postal code, country, IP address and user agent. Product Metrics sends only what the order already has. See [OpenAI Conversions API: customer data](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-openai).

**Consent.** OpenAI has no consent mode: nothing is sent without marketing consent, and Product Metrics applies the rest per field. See [Consent → ChatGPT Ads](https://www.productmetrics.io/docs/using/consent#chatgpt-ads).

**For developers: browser references and event source**

**Browser references.** The SDK writes them only for a property with an OpenAI destination. Both go with the event unmodified.

| Reference | Where it comes from | Kept | Sent as |
| --- | --- | --- | --- |
| `__oppref` | The `oppref` on the landing URL when a visitor lands from a ChatGPT ad, stored as a first-party cookie | 30 days | `oppref` on the event |
| `__obref` | A random ID Full Signal Tracking sets when the OpenAI Pixel hasn't set one | 365 days | `obref` in `user` |

**Source.** An event with a page URL is sent as `web` with its `source_url`. An order confirmed only on the server, with no page, goes as `other`.

## Limits

- **7 days.** OpenAI accepts events up to 7 days old. An order paid more than a week after checkout isn't sent, and historical orders are not imported.
- **Refunds.** Later refunds and cancellations don't revise OpenAI events.
- **No user agent needed.** Unlike Meta, OpenAI takes an event without a browser user agent, so orders confirmed on the server still go.
- **Retries.** When OpenAI limits the rate or doesn't answer, Product Metrics retries the event on its own.

## Running the OpenAI Pixel as well

You can keep the OpenAI Pixel in the browser. OpenAI deduplicates on Pixel ID, event name and event ID, and keeps the first event it receives.

- **order_created** uses the order transaction ID, so it works on its own.
- **items_added** and **checkout_started** need your developer to pass the event ID Product Metrics returns to the pixel call.

For developers: `ProductMetrics.addToCart()` and `ProductMetrics.beginCheckout()` return an `eventId`; pass it to the pixel as `event_id`:

```js
const { eventId } = await ProductMetrics.addToCart({ items })
oaiq('measure', 'items_added', data, { event_id: eventId })
```

## Per platform

ChatGPT Ads works the same on every platform. The only differences are where consent and costs come from:

| Platform | Difference for ChatGPT Ads |
| --- | --- |
| **[Shopify](https://www.productmetrics.io/docs/platforms/shopify)** | Choose **Shopify Customer Privacy** under **Configure consent**, unless your store uses another banner. |
| **[Magento](https://www.productmetrics.io/docs/platforms/magento)** | Magento's cookie restriction notice does not grant consent. Choose a supported banner, or have your developer pass the visitor's choices to Product Metrics; otherwise nothing is sent to OpenAI. |
| **[Cloudflare](https://www.productmetrics.io/docs/platforms/cloudflare)** | Website orders carry no product costs, so profit uses your **Product cost fallback (%)**. |
| **[WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce)**, **[Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed)** and **[Shopware](https://www.productmetrics.io/docs/platforms/shopware)** | No differences for OpenAI. |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **"OpenAI rejected this Conversions API key"** | The key is invalid or revoked. Create a new Conversions API key in **Ads Manager → Conversions**, select **Edit** and paste it into **Conversions API key**. |
| **"This Conversions API key has no access to that Pixel ID"** | The key belongs to another pixel, or the Pixel ID is wrong. Create the key for the same pixel in **Ads Manager → Conversions**. |
| **"Paste the Conversions API key from Ads Manager → Conversions for this pixel"** | You changed the **Pixel ID**: a new pixel needs a new key. |
| **"Set up tracking for this store before connecting OpenAI"** | The property has no tracked store yet. Connect your store first: [choose your platform](https://www.productmetrics.io/docs/platforms/overview). |
| **"The shopper did not consent to marketing, so the event was not sent"** | Expected for shoppers who declined marketing cookies. If it happens for every event, check that **Configure consent** names the banner your store actually shows. |
| **"The event was more than 7 days old, which OpenAI no longer accepts"** | The order was paid more than a week after checkout. Nothing to fix. |
| **"OpenAI rejected the event data."** | The app shows OpenAI's own reason under **OpenAI reported a problem**. Send it to support if it repeats. |
| **A profit event never arrives** | Profit is only sent once the order has a complete contribution margin. Activate your costs under **Tracking → Profit tracking**, then place another test order. |

## FAQ

### Can I bid on profit in ChatGPT Ads?

Yes. Create a conversion on `pm_order_profit` in **Ads Manager → Conversions** and choose it as the campaign's value-based conversion. Profit is sent once the order has a complete contribution margin.

### Are new customers sent to ChatGPT Ads?

Yes: `pm_new_customer` and `pm_new_customer_profit` for new customers and `pm_returning_customer` and `pm_returning_customer_profit` for returning ones, beside revenue, profit and lifetime value. ChatGPT Ads bids on the conversion you select as the campaign's conversion in Ads Manager.

### Do I need to remove the OpenAI Pixel?

No. OpenAI deduplicates on Pixel ID, event name and event ID, and `order_created` uses the order transaction ID, so a purchase counts once.

### Are past orders sent to ChatGPT Ads?

No. OpenAI accepts events up to 7 days old, so historical orders aren't imported.
