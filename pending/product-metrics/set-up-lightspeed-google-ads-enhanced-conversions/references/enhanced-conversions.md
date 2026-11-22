# Lightspeed enhanced conversions for Google Ads

Source: https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send hashed customer data from Lightspeed orders with each Google Ads conversion, only when the visitor allowed ad user data.

On Lightspeed, Product Metrics hashes **email, phone and name from the Lightspeed order** with **SHA-256** and sends them, plus the address's country and postcode, with each purchase conversion through Google's **Data Manager**, only when the visitor allowed **ad user data**. There is no Google tag setting and no code.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **[Server-side tracking for Lightspeed in Google Ads](https://www.productmetrics.io/docs/tracking/server-side/lightspeed-google-ads)** set up first.
- **Your Lightspeed eCom (C-Series) shop connected**: a back-office administrator login (an API key can't sign in), the shop's cluster, hostname and numeric Shop ID, and an enabled API key with its secret that has Read on Content, Products, Customers and Orders, and Read and Write on Settings and Tracking. The shop can't already be connected to another workspace, and it reads **Active** with **Configuration is current** before you link your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).
- **Your shop domain on Cloudflare**, with its DNS record proxied (the orange cloud), and a workspace admin who signs in to Cloudflare once.
- **Admin access to the Google Ads account**, to accept the customer data terms.
  

## In the app

### 1. Check server-side tracking runs

Enhanced conversions are not a separate switch: once the shop sends orders to the **Product Metrics** conversion actions, each order carries the customer data it has.

**You should see:** every Product Metrics conversion action created under **Tracking → Conversion actions**. If not, finish [server-side tracking for Lightspeed in Google Ads](https://www.productmetrics.io/docs/tracking/server-side/lightspeed-google-ads).

### 2. Set consent

In **Tracking → Configure consent**, choose the banner your shop shows: OneTrust, Cookiebot, Usercentrics or Osano. What each choice lets through: [Consent](https://www.productmetrics.io/docs/using/consent#what-each-choice-lets-through).

**You should see:** **Tracking → Configure consent** names the banner your shop actually shows.

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

Place and pay for a test order.

**You should see:** the order for the linked property, and under the Cloudflare gateway in **Tracking**, **Live endpoints** lists the **Tracking SDK** and **Event collector** on your shop domain.

## Fields sent

| Customer data | Where it comes from on Lightspeed | Sent to Google Ads as |
| --- | --- | --- |
| Email address | The Lightspeed order; hashed in the browser before it is sent | Hashed email |
| Phone number | The Lightspeed order | Hashed phone, with the country code and `+` |
| Name, country and postcode | The Lightspeed order's address | Hashed first and last name, with country and postcode unhashed (Google's format), only as a complete set |
| Ad click | The visitor's click on your ad | gclid, gbraid or wbraid, with ad storage consent |
| New or returning customer | The customer's order history | Sent with the conversion |

Product Metrics only sends what the order already has. It adds no checkout fields and guesses nothing.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in Google Ads** | Check that **Tracking → Configure consent** names the banner your store actually shows ([step 2](#2-set-consent)). |

## FAQ

### Do I need Google Tag Manager for Enhanced Conversions?

No. Product Metrics sends the hashed customer data server-side with each order through Google's Data Manager, so there is no Google tag setting and no code on your Lightspeed shop.

### Is the email hashed in the browser on Lightspeed?

Yes. The email is hashed with SHA-256 in the browser before it is sent. Phone and name from the Lightspeed order are hashed too; Google takes country and postcode unhashed.

### Which consent banners work on Lightspeed?

OneTrust, Cookiebot, Usercentrics or Osano. Choose the one your shop shows under **Tracking → Configure consent**.

### What if a visitor declines ad user data?

Google Ads still receives the order when the visitor allowed ad storage, but without the hashed customer data. With neither ad user data nor ad storage, the order isn't sent.
