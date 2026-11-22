# Shopify enhanced conversions for Google Ads

Source: https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send hashed customer data from Shopify orders with each Google Ads conversion, only when the visitor allowed ad user data.

On Shopify, Product Metrics hashes **email, phone and name from the Shopify order** with **SHA-256** and sends them, plus the address's country and postcode, with each purchase conversion through Google's **Data Manager**, only when the visitor allowed **ad user data**. There is no Google tag setting and no code.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **[Server-side tracking for Shopify in Google Ads](https://www.productmetrics.io/docs/tracking/server-side/shopify-google-ads)** set up first.
- **Your Shopify store connected**: a Shopify login that can install apps and edit the theme, the Product Metrics app installed with its app embed on, the store linked to your property, and your subscription started in the app with **Create subscription** (billed through Shopify). See [Shopify](https://www.productmetrics.io/docs/platforms/shopify).
- **Admin access to the Google Ads account**, to accept the customer data terms.
  

## In the app

### 1. Check server-side tracking runs

Enhanced conversions are not a separate switch: once the store sends orders to the **Product Metrics** conversion actions, each order carries the customer data it has.

**You should see:** every Product Metrics conversion action created under **Tracking → Conversion actions**. If not, finish [server-side tracking for Shopify in Google Ads](https://www.productmetrics.io/docs/tracking/server-side/shopify-google-ads).

### 2. Set consent

In **Tracking → Configure consent**, choose **Shopify Customer Privacy**, unless your store shows OneTrust, Cookiebot, Usercentrics or Osano instead. What each choice lets through: [Consent](https://www.productmetrics.io/docs/using/consent#what-each-choice-lets-through).

**You should see:** **Tracking → Configure consent** names the banner your store actually shows.

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

Place and pay for a test order: it is sent once Shopify marks it paid. Then, in the Shopify app, open **Tracking** in the app menu and select **Run tracking test**.

**You should see:** the checks **Passing**, and **Tracking is live on your store**.

## Fields sent

| Customer data | Where it comes from on Shopify | Sent to Google Ads as |
| --- | --- | --- |
| Email address | The Shopify order | Hashed email |
| Phone number | The Shopify order | Hashed phone, with the country code and `+` |
| Name, country and postcode | The Shopify order's address | Hashed first and last name, with country and postcode unhashed (Google's format), only as a complete set |
| Ad click | The visitor's click on your ad | gclid, gbraid or wbraid, with ad storage consent |
| New or returning customer | The customer's order history | Sent with the conversion |

Product Metrics only sends what the order already has. It adds no checkout fields and guesses nothing.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in Google Ads** | Check that **Tracking → Configure consent** names the banner your store actually shows ([step 2](#2-set-consent)). |

## FAQ

### Do I need Google Tag Manager for Enhanced Conversions?

No. Product Metrics sends the hashed customer data server-side with each order through Google's Data Manager, so there is no Google tag setting and no code on your Shopify store.

### Which Shopify order details are sent to Google Ads?

Email, phone and name from the Shopify order, hashed with SHA-256. The name only goes as a complete set with country and postcode, which Google takes unhashed.

### Which consent banner does Product Metrics read on Shopify?

Shopify Customer Privacy, unless your store shows OneTrust, Cookiebot, Usercentrics or Osano instead. Choose it under **Tracking → Configure consent**.

### What if a visitor declines ad user data?

Google Ads still receives the order when the visitor allowed ad storage, but without the hashed customer data. With neither ad user data nor ad storage, the order isn't sent.
