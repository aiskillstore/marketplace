# Magento enhanced conversions for Google Ads

Source: https://www.productmetrics.io/docs/tracking/enhanced-conversions/magento-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/enhanced-conversions/magento-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send hashed customer data from Magento orders with each Google Ads conversion, only when the visitor allowed ad user data.

On Magento, Product Metrics hashes **the Magento order, plus the logged-in customer's details and the guest email that the module passes to the script** with **SHA-256** and sends it with each purchase conversion through Google's **Data Manager**, only when the visitor allowed **ad user data**. There is no Google tag setting and no code.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **[Server-side tracking for Magento in Google Ads](https://www.productmetrics.io/docs/tracking/server-side/magento-google-ads)** set up first.
- **Your Magento store view connected**: Magento 2.4, 2.0 or 1.9 / OpenMage, Magento Admin access, the public HTTPS shop address and the **store-view ID**, and a **developer** with access to your server who installs the Product Metrics module (Composer or ZIP), adds the store view's private configuration file and keeps Magento cron running. The connection reads **Active** before you link your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).
- **Admin access to the Google Ads account**, to accept the customer data terms.
  

## In the app

### 1. Check server-side tracking runs

Enhanced conversions are not a separate switch: once the store view sends orders to the **Product Metrics** conversion actions, each order carries the customer data it has.

**You should see:** every Product Metrics conversion action created under **Tracking → Conversion actions**. If not, finish [server-side tracking for Magento in Google Ads](https://www.productmetrics.io/docs/tracking/server-side/magento-google-ads).

### 2. Set consent

In **Tracking → Configure consent**, choose the banner your shop shows: OneTrust, Cookiebot, Usercentrics or Osano. **Magento's own cookie restriction notice does not grant consent.** With any other banner, your developer passes the visitor's choices to Product Metrics: see [Consent](https://www.productmetrics.io/docs/concepts/consent). Without either, ad user data stays denied and no customer data is sent. What each choice lets through: [Consent](https://www.productmetrics.io/docs/using/consent#what-each-choice-lets-through).

**You should see:** **Tracking → Configure consent** names the banner your store view actually shows.

### 3. Accept Google's customer data terms

Google rejects conversions with customer data until the account accepts its terms. Only you can do this, in Google Ads.

1. In Product Metrics, open **Tracking → Google Ads**. Under **Enhanced conversions**, look at **Customer data terms**.
2. If it reads **Not accepted**, select **Open Google Ads settings**. Under **Customer data terms**, choose **View terms** and agree.
3. If **Data Manager acceptance** reads **Rejected**, select **Turn on enhanced conversions**. In Google Ads, open **Goals → Settings**, expand **Customer data use**, tick **Turn on enhanced conversions**, then agree and save.
4. Select **Re-check** in Product Metrics.

> **Note:** If Product Metrics says **Terms are managed on account** with another number, that is your manager account. Accept the terms there.

**You should see:** **Ready** under **Enhanced conversions**. **Re-check** runs a new check. What each state means:

| In the app | What to do |
| --- | --- |
| **Ready** | Nothing. Customer data goes with every consented order. |
| **Setting up** | Wait. Data Manager needs about 15 minutes to recognise new conversion actions. |
| **Action required** | Accept the customer data terms, or turn on enhanced conversions (step 3). |
| **Check failed** | Reconnect Google Ads, or select **Re-check** in a moment. |
| **Not checked yet** | Open **Tracking → Google Ads** and select **Re-check**. |
| **No Google Ads account** | Connect Google Ads first. |

### 4. Check an order

Place a paid test order in the connected store view with your payment provider's test mode, and allow a few minutes for cron.

**You should see:** under **Manage Magento**, the desired and active revision numbers are the same, and the order appears for the linked property.

## Fields sent

| Customer data | Where it comes from on Magento | Sent to Google Ads as |
| --- | --- | --- |
| Email address | The Magento order; the module also passes the guest email | Hashed email |
| Phone number | The Magento order | Hashed phone, with the country code and `+` |
| Name, country and postcode | The Magento order's address | Hashed first and last name, with country and postcode unhashed (Google's format), only as a complete set |
| Ad click | The visitor's click on your ad | gclid, gbraid or wbraid, with ad storage consent |
| New or returning customer | The customer's order history | Sent with the conversion |

Product Metrics only sends what the order already has. It adds no checkout fields and guesses nothing.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in Google Ads** | Check that **Tracking → Configure consent** names the banner your store actually shows ([step 2](#2-set-consent)). |

## FAQ

### Does Magento need a developer for Enhanced Conversions?

Only to install the Product Metrics module once, for server-side tracking. Enhanced conversions add no Google tag setting and no code on top of that.

### Are guest checkout orders matched in Google Ads?

Yes. The module passes the guest email with the order, and the logged-in customer's details for signed-in shoppers. Both are hashed with SHA-256.

### Does Magento's cookie notice count as consent?

No. Choose OneTrust, Cookiebot, Usercentrics or Osano under **Tracking → Configure consent**, or have your developer pass the visitor's choices. Without either, no customer data is sent.

### What if a visitor declines ad user data?

Google Ads still receives the order when the visitor allowed ad storage, but without the hashed customer data. With neither ad user data nor ad storage, the order isn't sent.
