# Meta Conversions API Advanced Matching on any website with Cloudflare

Source: https://www.productmetrics.io/docs/tracking/enhanced-conversions/cloudflare-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/enhanced-conversions/cloudflare-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send hashed customer information from your website's orders with every Meta Conversions API event (Advanced Matching), only when the visitor allowed ad user data.

Every event Product Metrics sends through the **Meta Conversions API** carries customer information so Meta can match it to a person (**Advanced Matching**): on a website with Cloudflare Tracking, **only the email address your site passes to Product Metrics**, hashed with **SHA-256**, plus the visitor's IP address and browser. There is no extra switch: once the destination is saved, every consented event carries it.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking).
- **[Server-side tracking for any website (Cloudflare) in Meta](https://www.productmetrics.io/docs/tracking/server-side/cloudflare-meta)** set up first.
- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).

## In the app

### 1. Check the Meta Conversions API is connected

In Product Metrics, open **Tracking → Meta Conversions API**.

**You should see:** your Meta pixel is connected and enabled. Not there yet? Follow [server-side tracking for any website (Cloudflare) in Meta](https://www.productmetrics.io/docs/tracking/server-side/cloudflare-meta).

### 2. Set consent

In **Tracking → Configure consent**, choose the banner your website shows: OneTrust, Cookiebot, Usercentrics or Osano.

Meta has no consent mode, so without **ad user data** the event isn't sent at all. What each choice lets through: [Consent](https://www.productmetrics.io/docs/using/consent#what-each-choice-lets-through).

**You should see:** **Tracking → Configure consent** names the banner your website actually shows.

### 3. Send a test event

In **Tracking → Meta Conversions API**, send a test event. It checks the connection only.

**You should see:** Meta accept the test event.

### 4. Check an order

To see the customer information on a real event, place a test order through to your order confirmation page, then open **Tracking → Check your purchases**.

**You should see:** your order as **Last purchase received**. The check only proves the purchase arrived: it shows no customer data.

> **Note:** Meta refuses events more than 7 days old, so an order paid more than a week after checkout never reaches Meta.

## Fields sent

| Customer information parameter | Where it comes from on Any website (Cloudflare) | Sent as |
| --- | --- | --- |
| Email | Only the email your site passes to Product Metrics; hashed in the browser | `em`: hashed |
| Phone, name, postcode, country | Not available | — |
| Customer ID | Not available  | — |
| IP address, user agent | The visitor's browser | `client_ip_address`, `client_user_agent`: not hashed, as Meta requires |
| Browser and click IDs | Meta's `_fbp` and `_fbc` cookies | `fbp`, `fbc`, with ad storage consent |

Product Metrics only sends what the website passed. It adds no checkout fields and guesses nothing. Sent events aren't revised after a refund.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in Meta** | Check that **Tracking → Configure consent** names the banner your website actually shows ([step 2](#2-set-consent)). |

## FAQ

### Does this replace my Meta pixel?

No. You can keep your browser pixel: Meta counts an event once when the pixel and the Meta Conversions API send the same event name and event ID within 48 hours.

### Are phone and name sent from a website order?

No. A website order has no phone number, name, postcode or country, so Advanced Matching can't use them and Product Metrics guesses nothing.

### What if a visitor declines ad user data?

The event isn't sent to Meta at all, because Meta has no consent mode. Product Metrics reads the choice from the banner your website shows: OneTrust, Cookiebot, Usercentrics or Osano.

### Are past orders and refunds sent to Meta?

No. Meta accepts events up to 7 days old, so past orders aren't imported, and later refunds and cancellations don't revise events already sent. Product Metrics still tracks them in your profit and lifetime value.
