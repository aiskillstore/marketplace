# Shopify Meta Conversions API Advanced Matching

Source: https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send hashed customer information from Shopify orders with every Meta Conversions API event (Advanced Matching), only when the visitor allowed ad user data.

Every event Product Metrics sends through the **Meta Conversions API** carries customer information so Meta can match it to a person (**Advanced Matching**): on Shopify, **email, phone, name and address from the Shopify order**, hashed with **SHA-256**, plus the visitor's IP address and browser. There is no extra switch: once the destination is saved, every consented event carries it.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps).
- **[Server-side tracking for Shopify in Meta](https://www.productmetrics.io/docs/tracking/server-side/shopify-meta)** set up first.
- **Your Shopify store connected**: a Shopify login that can install apps and edit the theme, the Product Metrics app installed with its app embed on, the store linked to your property, and your subscription started in the app with **Create subscription** (billed through Shopify). See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).

## In the app

### 1. Check the Meta Conversions API is connected

In Product Metrics, open **Tracking → Meta Conversions API**.

**You should see:** your Meta pixel is connected and enabled. Not there yet? Follow [server-side tracking for Shopify in Meta](https://www.productmetrics.io/docs/tracking/server-side/shopify-meta).

### 2. Set consent

In **Tracking → Configure consent**, choose **Shopify Customer Privacy**, unless your store shows OneTrust, Cookiebot, Usercentrics or Osano instead.

Meta has no consent mode, so without **ad user data** the event isn't sent at all. What each choice lets through: [Consent](https://www.productmetrics.io/docs/using/consent#what-each-choice-lets-through).

**You should see:** **Tracking → Configure consent** names the banner your store actually shows.

### 3. Send a test event

In **Tracking → Meta Conversions API**, send a test event. It checks the connection only.

**You should see:** Meta accept the test event.

### 4. Check an order

To see the customer information on a real event, place and pay for a test order: it is sent once Shopify marks it paid. Then, in the Shopify app, open **Tracking** in the app menu and select **Run tracking test**.

**You should see:** the checks **Passing**, and **Tracking is live on your store**.

> **Note:** Meta refuses events more than 7 days old, so an order paid more than a week after checkout never reaches Meta.

## Fields sent

| Customer information parameter | Where it comes from on Shopify | Sent as |
| --- | --- | --- |
| Email, phone | The Shopify order | `em`, `ph`: hashed; phone as digits with the country code |
| First name, last name, postcode, country | The Shopify order's address | `fn`, `ln`, `zp`, `country`: hashed |
| Customer ID | Your Shopify customer ID, when the order has one | `external_id`: hashed |
| IP address, user agent | The visitor's browser | `client_ip_address`, `client_user_agent`: not hashed, as Meta requires |
| Browser and click IDs | Meta's `_fbp` and `_fbc` cookies | `fbp`, `fbc`, with ad storage consent |

Product Metrics only sends what the order already has. It adds no checkout fields and guesses nothing. Sent events aren't revised after a refund.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in Meta** | Check that **Tracking → Configure consent** names the banner your store actually shows ([step 2](#2-set-consent)). |

## FAQ

### Does this replace my Meta pixel?

No. You can keep your browser pixel: Meta counts an event once when the pixel and the Meta Conversions API send the same event name and event ID within 48 hours.

### Is my Shopify customer ID sent to Meta?

Yes, hashed as `external_id` when the order has one. Advanced Matching also gets the hashed email, phone, name, postcode and country from the Shopify order.

### What if a visitor declines ad user data on Shopify?

The event isn't sent to Meta at all, because Meta has no consent mode. Product Metrics reads the choice from Shopify Customer Privacy, or from OneTrust, Cookiebot, Usercentrics or Osano if your store shows one.

### Are past orders and refunds sent to Meta?

No. Meta accepts events up to 7 days old, so past orders aren't imported, and later refunds and cancellations don't revise events already sent.
