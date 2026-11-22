# Shopware Meta Conversions API Advanced Matching

Source: https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopware-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopware-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send hashed customer information from Shopware orders with every Meta Conversions API event (Advanced Matching), only when the visitor allowed ad user data.

Every event Product Metrics sends through the **Meta Conversions API** carries customer information so Meta can match it to a person (**Advanced Matching**): on Shopware, **the order's email, plus phone, name, postcode and country from the billing address**, hashed with **SHA-256**, plus the visitor's IP address and browser. There is no extra switch: once the destination is saved, every consented event carries it.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking).
- **[Server-side tracking for Shopware in Meta](https://www.productmetrics.io/docs/tracking/server-side/shopware-meta)** set up first.
- **Your Shopware sales channel connected**: Shopware 6.7 (this plugin build supports 6.7.14.0) with PHP 8.2+, an administrator who can upload extensions, Shopware's scheduled tasks and message workers running, and the channel's public HTTPS address under **Sales Channels → your channel → Domains**. You pair one sales channel with a one-time token; it reads **Active** before you link your property. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).

## In the app

### 1. Check the Meta Conversions API is connected

In Product Metrics, open **Tracking → Meta Conversions API**.

**You should see:** your Meta pixel is connected and enabled. Not there yet? Follow [server-side tracking for Shopware in Meta](https://www.productmetrics.io/docs/tracking/server-side/shopware-meta).

### 2. Set consent

Using Shopware's own cookie manager? Leave **Tracking → Configure consent** on **Not configured**: the extension adds a **Product Metrics measurement** group with **Product Metrics analytics** and **Product Metrics advertising attribution**, and the visitor's choice for **Product Metrics advertising attribution** decides what goes with each order. Choose OneTrust, Cookiebot, Usercentrics or Osano only if your shop shows one of those banners instead.

Meta has no consent mode, so without **ad user data** the event isn't sent at all. What each choice lets through: [Consent](https://www.productmetrics.io/docs/using/consent#what-each-choice-lets-through).

**You should see:** **Tracking → Configure consent** names the banner your sales channel actually shows.

### 3. Send a test event

In **Tracking → Meta Conversions API**, send a test event. It checks the connection only.

**You should see:** Meta accept the test event.

### 4. Check an order

To see the customer information on a real event, place a paid test order through the paired sales channel with your payment provider's test mode, and give Shopware a few minutes to sync it.

**You should see:** the order in Product Metrics and, with Shopware's own cookie manager, **Product Metrics measurement** in your cookie banner.

> **Note:** Meta refuses events more than 7 days old, so an order paid more than a week after checkout never reaches Meta.

## Fields sent

| Customer information parameter | Where it comes from on Shopware | Sent as |
| --- | --- | --- |
| Email, phone | The order's email; phone from the billing address | `em`, `ph`: hashed; phone as digits with the country code |
| First name, last name, postcode, country | The order's billing address | `fn`, `ln`, `zp`, `country`: hashed |
| Customer ID | Your Shopware customer ID, when the order has one | `external_id`: hashed |
| IP address, user agent | The visitor's browser | `client_ip_address`, `client_user_agent`: not hashed, as Meta requires |
| Browser and click IDs | Meta's `_fbp` and `_fbc` cookies | `fbp`, `fbc`, with ad storage consent |

Product Metrics only sends what the order already has. It adds no checkout fields and guesses nothing. Sent events aren't revised after a refund.

## FAQ

### Does this replace my Meta pixel?

No. You can keep your browser pixel: Meta counts an event once when the pixel and the Meta Conversions API send the same event name and event ID within 48 hours.

### Where do the phone and name come from on Shopware?

From the order's billing address, together with postcode and country; the email comes from the Shopware order. Advanced Matching receives all of them hashed with SHA-256.

### Can I use Shopware's own cookie manager for Meta?

Yes. Leave **Tracking → Configure consent** on **Not configured** and the visitor's choice for **Product Metrics advertising attribution** decides what goes with each order. Meta has no consent mode, so without ad user data no event is sent.

### Are past orders and refunds sent to Meta?

No. Meta accepts events up to 7 days old, so past orders aren't imported, and later refunds and cancellations don't revise events already sent.
