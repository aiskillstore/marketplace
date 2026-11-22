# Meta Conversions API and Advanced Matching

Source: https://www.productmetrics.io/docs/channels/meta (the same page as Markdown: https://www.productmetrics.io/docs/channels/meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send purchases to your Meta pixel through the Meta Conversions API with Advanced Matching, with revenue, profit, new and returning customer and lifetime value events you can bid on.

Product Metrics confirms each purchase from your store's order data and sends it from its server to your **Meta pixel** through the **Meta Conversions API**. Meta receives `AddToCart`, `InitiateCheckout` and `Purchase`, plus one **custom event** per value (revenue, profit, new and returning customer, lifetime value). Each event carries hashed customer data for **Advanced Matching**: see [Customer data](https://www.productmetrics.io/docs/features/enhanced-conversions).

This is **server-side tracking** (Full Signal Tracking), included in Pro. Unlike Google Ads, you create the custom conversions yourself, and there are no customer lists.

- **You need:** your **Pixel or Dataset ID** and a Conversions API **access token** from Meta Events Manager.
- **In the app:** **Tracking → Meta Conversions API → Connect Meta**.
- **What is sent:** `AddToCart`, `InitiateCheckout` and `Purchase`, plus one custom event per value, with hashed customer data for Advanced Matching.

## Prerequisites

- [Before you start](https://www.productmetrics.io/docs/using/overview): editor or admin access in Product Metrics ([Team](https://www.productmetrics.io/docs/using/team)).
- Your store connected and linked to a property ([pick your platform](#your-store-platform)).
- Access to your pixel in Meta Events Manager.

## In the app

### 1. Get your pixel ID and access token

In Meta Events Manager:

1. Open the pixel your ads use and copy the number under its name: your **Pixel or Dataset ID**.
2. Open the pixel's **Settings** and choose **Generate access token** under **Conversions API**. Copy the token.
3. Optional: copy a code from **Test events**, to send test events while you set up.

The access token is a credential. Product Metrics never shows it again after you save it; it keeps only the last characters as a hint.

### 2. Add the Meta destination

Go to **Tracking → Meta Conversions API → Connect Meta**. Fill in **Pixel or Dataset ID**, **Access token** and, optionally, **Test event code**. Leave **Send events to Meta** on and select **Add destination**.

> **Warning:** Keep the access token out of shared chats. Enter it in the app. An assistant must ask you for it, and never invents, reuses or repeats it.

**You should see:** **Meta destination saved**.

### 3. Place a test order

With a test event code saved, place a test order on your store.

**You should see:** the events under **Test events** in Events Manager. A test event checks the connection only.

### 4. Create custom conversions in Meta

An event appears in Meta's selector only after Meta receives it, so do this after the test order. In Events Manager:

1. **Custom conversions → Create custom conversion**.
2. Select your pixel and the event, and add the rule `pm_purpose` equals the purpose.
3. Choose **Purchase** as the category. Use the event's value and currency, and leave the fixed value unset.

The full table is on [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions#custom-conversions-in-meta). Profit events don't appear while your margin data is incomplete.

**You should see:** one custom conversion per event you want to bid on.

### 5. Remove the test event code

While a test event code is saved, events go to **Test events** and don't count in reporting. Once your test order has arrived, clear **Test event code** in the Meta destination and save.

The token stays saved when the pixel doesn't change. To pause sending and keep the settings, turn **Send events to Meta** off.

### 6. Check delivery

Open **Tracking → Meta Conversions API**.

**You should see:** the destination **Active**, **Access token** saved, **Sending** on, and events counted as **Delivered**, **Pending**, **Retrying** or **Failed**. If it shows an error, see [Troubleshooting](#troubleshooting).

## What Product Metrics sends to Meta

| | Sent to Meta |
| --- | --- |
| **Standard events** | `AddToCart`, `InitiateCheckout` and `Purchase`. The Purchase value is order revenue: products and shipping, minus refunds. Each Purchase lists the products bought |
| **Custom events** | One per value: `PMOrderRevenue`, `PMOrderProfit`, new and returning customer, and LTV. The full list with each `pm_purpose` is on [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions#custom-conversions-in-meta) |
| **Profit** | Needs a complete contribution margin: [add your costs](https://www.productmetrics.io/docs/using/costs). Meta accepts no negative value, so a loss-making order is sent with value 0, and its real profit goes along as a separate parameter |
| **LTV** | Needs a linked customer and sends only what this order adds, with the observed total alongside when available. Observed, not predicted |
| **Customer data (Meta Conversions API)** | With consent to marketing, each event carries the hashed email, name, postal code and country, plus IP address and browser, so Meta can match it to a person. Meta's browser IDs go only when the shopper also allowed ad storage |
| **Consent** | From the banner under **Tracking → Configure consent**, the same setting Google Ads uses ([Consent](https://www.productmetrics.io/docs/using/consent)) |
| **Limits** | Meta accepts events up to 7 days old, so past orders aren't imported. Later refunds and cancellations don't revise Meta events |

## Running the Meta Pixel as well

Keep your browser pixel if you like. Meta counts an event once when the pixel and the Conversions API send the same event name and event ID within 48 hours.

- **Purchase** uses the order transaction ID, so it works on its own.
- **AddToCart** and **InitiateCheckout** need your developer to pass the event ID Product Metrics returns to the pixel call.

For developers: `ProductMetrics.addToCart()` and `ProductMetrics.beginCheckout()` return an `eventId` to pass to the pixel:

```js
const { eventId } = await ProductMetrics.addToCart({ items })
fbq('track', 'AddToCart', params, { eventID: eventId })
```

## Your store platform

The Meta steps are the same on every platform. Connect your store first with its platform guide.

- [Shopify](https://www.productmetrics.io/docs/platforms/shopify)
- [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce)
- [Magento](https://www.productmetrics.io/docs/platforms/magento)
- [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed)
- [Shopware](https://www.productmetrics.io/docs/platforms/shopware)
- [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare)

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **"Access token is invalid or expired"** | Generate a new token in Events Manager and save it (step 2). |
| **"The access token has no access to this pixel"** | Generate the token from the same pixel. |
| **"No access token is saved for this pixel"** | Add a token. A changed Pixel or Dataset ID needs a new token too. |
| **"The shopper did not consent to marketing, so the event was not sent"** | Expected for shoppers who declined. If it shows for every event, check that [consent](https://www.productmetrics.io/docs/using/consent) names your banner. |
| **"The event was more than 7 days old"** | Orders marked paid more than a week after checkout can't go to Meta. |
| **"The pixel changed after this event was queued"** | Events waiting during the change weren't sent to the new pixel; new events go there. |
| **"The custom conversion for this event is not set up correctly"** | The event name and `pm_purpose` rule must match the table on [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions#custom-conversions-in-meta). |
| **A profit event doesn't show up in Meta's selector** | Profit events need a complete margin. [Add your costs](https://www.productmetrics.io/docs/using/costs), then place another test order. |
| **Events show under Test events but not in reporting** | A test event code is still saved: clear it (step 5). |

Meta rate limits and timeouts are retried on their own. To stop for good, delete the destination. That removes the stored token, so setting up again needs a new one.

## FAQ

### Does this replace my Meta pixel?

No. Product Metrics sends events to your Meta pixel through the Meta Conversions API, and you can keep the browser pixel. Meta counts an event once when both send the same event name and event ID within 48 hours; `Purchase` uses the order transaction ID, so it needs no extra step.

### Is this Meta Advanced Matching?

Yes. With marketing consent, each Meta Conversions API event carries the hashed email, name, postal code and country, plus IP address and browser, for Advanced Matching.

### Are past orders sent to Meta?

No. Meta accepts events up to 7 days old, so Product Metrics sends orders from the moment tracking is live.

### Can I bid on profit in Meta?

Yes. Create a custom conversion on the `PMOrderProfit` event in Events Manager and optimise your campaign on it. It is sent once the order has a complete contribution margin; a loss-making order goes with value 0.
