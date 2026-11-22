# Lightspeed Meta Conversions API Advanced Matching

Source: https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send hashed customer information from Lightspeed orders with every Meta Conversions API event (Advanced Matching), only when the visitor allowed ad user data.

Every event Product Metrics sends through the **Meta Conversions API** carries customer information so Meta can match it to a person (**Advanced Matching**): on Lightspeed, **email, phone, name and address from the Lightspeed order**, hashed with **SHA-256**, plus the visitor's IP address and browser. There is no extra switch: once the destination is saved, every consented event carries it.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking).
- **[Server-side tracking for Lightspeed in Meta](https://www.productmetrics.io/docs/tracking/server-side/lightspeed-meta)** set up first.
- **Your Lightspeed eCom (C-Series) shop connected**: a back-office administrator login (an API key can't sign in), the shop's cluster, hostname and numeric Shop ID, and an enabled API key with its secret that has Read on Content, Products, Customers and Orders, and Read and Write on Settings and Tracking. The shop can't already be connected to another workspace, and it reads **Active** with **Configuration is current** before you link your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).
- **Your shop domain on Cloudflare**, with its DNS record proxied (the orange cloud), and a workspace admin who signs in to Cloudflare once.

## In the app

### 1. Check the Meta Conversions API is connected

In Product Metrics, open **Tracking → Meta Conversions API**.

**You should see:** your Meta pixel is connected and enabled. Not there yet? Follow [server-side tracking for Lightspeed in Meta](https://www.productmetrics.io/docs/tracking/server-side/lightspeed-meta).

### 2. Set consent

In **Tracking → Configure consent**, choose the banner your shop shows: OneTrust, Cookiebot, Usercentrics or Osano.

Meta has no consent mode, so without **ad user data** the event isn't sent at all. What each choice lets through: [Consent](https://www.productmetrics.io/docs/using/consent#what-each-choice-lets-through).

**You should see:** **Tracking → Configure consent** names the banner your shop actually shows.

### 3. Send a test event

In **Tracking → Meta Conversions API**, send a test event. It checks the connection only.

**You should see:** Meta accept the test event.

### 4. Check an order

To see the customer information on a real event, place and pay for a test order.

**You should see:** the order for the linked property, and under the Cloudflare gateway in **Tracking**, **Live endpoints** lists the **Tracking SDK** and **Event collector** on your shop domain.

> **Note:** Meta refuses events more than 7 days old, so an order paid more than a week after checkout never reaches Meta.

## Fields sent

| Customer information parameter | Where it comes from on Lightspeed | Sent as |
| --- | --- | --- |
| Email, phone | The Lightspeed order; the email is hashed in the browser | `em`, `ph`: hashed; phone as digits with the country code |
| First name, last name, postcode, country | The Lightspeed order's address | `fn`, `ln`, `zp`, `country`: hashed |
| Customer ID | Your Lightspeed customer ID, when the order has one | `external_id`: hashed |
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

### Is the email hashed in the browser on Lightspeed?

Yes. The email is hashed with SHA-256 in the browser, and the phone, name, postcode and country from the Lightspeed order are hashed before Advanced Matching receives them.

### What if a visitor declines ad user data on Lightspeed?

The event isn't sent to Meta at all, because Meta has no consent mode. Product Metrics reads the choice from the banner your shop shows: OneTrust, Cookiebot, Usercentrics or Osano.

### Are past orders and refunds sent to Meta?

No. Meta accepts events up to 7 days old, so past orders aren't imported, and later refunds and cancellations don't revise events already sent.
