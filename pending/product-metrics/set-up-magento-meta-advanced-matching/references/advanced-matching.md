# Magento Meta Conversions API Advanced Matching

Source: https://www.productmetrics.io/docs/tracking/enhanced-conversions/magento-meta (the same page as Markdown: https://www.productmetrics.io/docs/tracking/enhanced-conversions/magento-meta.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send hashed customer information from Magento orders with every Meta Conversions API event (Advanced Matching), only when the visitor allowed ad user data.

Every event Product Metrics sends through the **Meta Conversions API** carries customer information so Meta can match it to a person (**Advanced Matching**): on Magento, **the Magento order, plus the logged-in customer's details and the guest email that the module passes to the script**, hashed with **SHA-256**, plus the visitor's IP address and browser. There is no extra switch: once the destination is saved, every consented event carries it.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking).
- **[Server-side tracking for Magento in Meta](https://www.productmetrics.io/docs/tracking/server-side/magento-meta)** set up first.
- **Your Magento store view connected**: Magento 2.4, 2.0 or 1.9 / OpenMage, Magento Admin access, the public HTTPS shop address and the **store-view ID**, and a **developer** with access to your server who installs the Product Metrics module (Composer or ZIP), adds the store view's private configuration file and keeps Magento cron running. The connection reads **Active** before you link your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).

## In the app

### 1. Check the Meta Conversions API is connected

In Product Metrics, open **Tracking → Meta Conversions API**.

**You should see:** your Meta pixel is connected and enabled. Not there yet? Follow [server-side tracking for Magento in Meta](https://www.productmetrics.io/docs/tracking/server-side/magento-meta).

### 2. Set consent

In **Tracking → Configure consent**, choose the banner your shop shows: OneTrust, Cookiebot, Usercentrics or Osano. **Magento's own cookie restriction notice does not grant consent.** With any other banner, your developer passes the visitor's choices to Product Metrics: see [Consent](https://www.productmetrics.io/docs/concepts/consent). Without either, ad user data stays denied and no customer data is sent.

Meta has no consent mode, so without **ad user data** the event isn't sent at all. What each choice lets through: [Consent](https://www.productmetrics.io/docs/using/consent#what-each-choice-lets-through).

**You should see:** **Tracking → Configure consent** names the banner your store view actually shows.

### 3. Send a test event

In **Tracking → Meta Conversions API**, send a test event. It checks the connection only.

**You should see:** Meta accept the test event.

### 4. Check an order

To see the customer information on a real event, place a paid test order in the connected store view with your payment provider's test mode, and allow a few minutes for cron.

**You should see:** under **Manage Magento**, the desired and active revision numbers are the same, and the order appears for the linked property.

> **Note:** Meta refuses events more than 7 days old, so an order paid more than a week after checkout never reaches Meta.

## Fields sent

| Customer information parameter | Where it comes from on Magento | Sent as |
| --- | --- | --- |
| Email, phone | The Magento order; the module also passes the guest email | `em`, `ph`: hashed; phone as digits with the country code |
| First name, last name, postcode, country | The Magento order's address | `fn`, `ln`, `zp`, `country`: hashed |
| Customer ID | Your Magento customer ID, when the order has one | `external_id`: hashed |
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

### Are guest checkout orders matched in Meta?

Yes. The module passes the guest email, which Advanced Matching receives hashed as `em`, with the name, postcode and country from the Magento order's address.

### Does Magento's cookie notice count as consent for Meta?

No. Choose OneTrust, Cookiebot, Usercentrics or Osano, or have your developer pass the visitor's choices. Meta has no consent mode, so without ad user data no event is sent.

### Are past orders and refunds sent to Meta?

No. Meta accepts events up to 7 days old, so past orders aren't imported, and later refunds and cancellations don't revise events already sent.
