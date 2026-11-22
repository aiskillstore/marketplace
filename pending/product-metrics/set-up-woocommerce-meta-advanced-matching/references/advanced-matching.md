# WooCommerce Meta Conversions API Advanced Matching

Source: https://www.productmetrics.io/docs/tracking/enhanced-conversions/woocommerce-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/enhanced-conversions/woocommerce-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send hashed customer information from WooCommerce orders with every Meta Conversions API event (Advanced Matching), only when the visitor allowed ad user data.

Every event Product Metrics sends through the **Meta Conversions API** carries customer information so Meta can match it to a person (**Advanced Matching**): on WooCommerce, **the order's billing email, phone, name, postcode and country**, hashed with **SHA-256**, plus the visitor's IP address and browser. There is no extra switch: once the destination is saved, every consented event carries it.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking).
- **[Server-side tracking for WooCommerce in Meta](https://www.productmetrics.io/docs/tracking/server-side/woocommerce-meta)** set up first.
- **Your WooCommerce store connected**: a WordPress administrator login, WordPress 6.4+ and PHP 8.1+ with WP-Cron running, and the shop at the root of an HTTPS domain (no subfolder, no custom port). You install the Product Metrics plugin, connect it with a one-time setup token, choose your paid order statuses and link the store to your property. See [WooCommerce](https://www.productmetrics.io/docs/platforms/woocommerce).

## In the app

### 1. Check the Meta Conversions API is connected

In Product Metrics, open **Tracking → Meta Conversions API**.

**You should see:** your Meta pixel is connected and enabled. Not there yet? Follow [server-side tracking for WooCommerce in Meta](https://www.productmetrics.io/docs/tracking/server-side/woocommerce-meta).

### 2. Set consent

In **Tracking → Configure consent**, choose the banner your store shows: OneTrust, Cookiebot, Usercentrics or Osano. After you change it, clear your full-page cache so every page loads the new setting. With **Not configured**, nothing is treated as allowed.

Meta has no consent mode, so without **ad user data** the event isn't sent at all. What each choice lets through: [Consent](https://www.productmetrics.io/docs/using/consent#what-each-choice-lets-through).

**You should see:** **Tracking → Configure consent** names the banner your store actually shows.

### 3. Send a test event

In **Tracking → Meta Conversions API**, send a test event. It checks the connection only.

**You should see:** Meta accept the test event.

### 4. Check an order

To see the customer information on a real event, in WordPress, select **Verify with next paid order** under **WooCommerce → Product Metrics**, place and pay for a test order within ten minutes, then select **Refresh connection status**.

**You should see:** **Live order delivery** reads **Verified**.

> **Note:** Meta refuses events more than 7 days old, so an order paid more than a week after checkout never reaches Meta.

## Fields sent

| Customer information parameter | Where it comes from on WooCommerce | Sent as |
| --- | --- | --- |
| Email, phone | The order's billing details | `em`, `ph`: hashed; phone as digits with the country code |
| First name, last name, postcode, country | The order's billing address | `fn`, `ln`, `zp`, `country`: hashed |
| Customer ID | Your WooCommerce customer ID, when the order has one | `external_id`: hashed |
| IP address, user agent | The visitor's browser | `client_ip_address`, `client_user_agent`: not hashed, as Meta requires |
| Browser and click IDs | Meta's `_fbp` and `_fbc` cookies | `fbp`, `fbc`, with ad storage consent |

Product Metrics only sends what the order already has. It adds no checkout fields and guesses nothing. Sent events aren't revised after a refund.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Nothing reaches Meta** | Check that **Tracking → Configure consent** names the banner your store shows. Left on **Not configured**, Product Metrics can't read the visitor's choice and treats it as not given. |

## FAQ

### Does this replace my Meta pixel?

No. You can keep your browser pixel: Meta counts an event once when the pixel and the Meta Conversions API send the same event name and event ID within 48 hours.

### Does Advanced Matching use billing or shipping details?

The billing details: the order's billing email, phone, name, postcode and country, hashed with SHA-256. Your WooCommerce customer ID goes as `external_id` when the order has one.

### What if a visitor declines ad user data?

The event isn't sent to Meta at all, because Meta has no consent mode. After you change the banner under **Tracking → Configure consent**, clear your full-page cache so every page reads the new setting.

### Are past orders and refunds sent to Meta?

No. Meta accepts events up to 7 days old, so past orders aren't imported, and later refunds and cancellations don't revise events already sent.
