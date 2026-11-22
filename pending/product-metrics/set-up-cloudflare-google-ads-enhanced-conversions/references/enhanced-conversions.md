# Enhanced conversions for Google Ads on any website with Cloudflare

Source: https://www.productmetrics.io/docs/tracking/enhanced-conversions/cloudflare-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/enhanced-conversions/cloudflare-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send hashed customer data from your website with each Google Ads conversion, only when the visitor allowed ad user data.

On a website with Cloudflare Tracking, Product Metrics hashes **only the email address your site passes to Product Metrics** with **SHA-256** and sends it with each purchase conversion through Google's **Data Manager**, only when the visitor allowed **ad user data**. There is no Google tag setting and no code.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **[Server-side tracking for any website (Cloudflare) in Google Ads](https://www.productmetrics.io/docs/tracking/server-side/cloudflare-google-ads)** set up first.
- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).
- **Admin access to the Google Ads account**, to accept the customer data terms.
  

## In the app

### 1. Check server-side tracking runs

Enhanced conversions are not a separate switch: once the website sends orders to the **Product Metrics** conversion actions, each order carries the customer data it has.

**You should see:** every Product Metrics conversion action created under **Tracking → Conversion actions**. If not, finish [server-side tracking for any website (Cloudflare) in Google Ads](https://www.productmetrics.io/docs/tracking/server-side/cloudflare-google-ads).

### 2. Set consent

In **Tracking → Configure consent**, choose the banner your website shows: OneTrust, Cookiebot, Usercentrics or Osano. What each choice lets through: [Consent](https://www.productmetrics.io/docs/using/consent#what-each-choice-lets-through).

**You should see:** **Tracking → Configure consent** names the banner your website actually shows.

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

Place a test order through to your order confirmation page, then open **Tracking → Check your purchases**.

**You should see:** your order as **Last purchase received**. The check only proves the purchase arrived: it shows no customer data.

## Fields sent

| Customer data | Where it comes from on Any website (Cloudflare) | Sent to Google Ads as |
| --- | --- | --- |
| Email address | Only the email your site passes to Product Metrics; hashed in the browser | Hashed email |
| Phone number | Not available | — |
| Name, country and postcode | Not available | — |
| Ad click | The visitor's click on your ad | gclid, gbraid or wbraid, with ad storage consent |
| New or returning customer | Purchases Product Metrics has seen from this website | Sent with the conversion |

Product Metrics only sends what the website passed. It adds no checkout fields and guesses nothing.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in Google Ads** | Check that **Tracking → Configure consent** names the banner your website actually shows ([step 2](#2-set-consent)). |

## FAQ

### Do I need to change my website's code for this?

No. Enhanced conversions aren't a separate switch: once your website sends orders to the **Product Metrics** conversion actions, each order carries the customer data it has. You accept Google's customer data terms once.

### Are phone and name sent from a website order?

No. A website order has no phone number, name, country or postcode, so Product Metrics sends none of them and guesses nothing.

### Are website customers marked as new or returning?

Yes. Product Metrics marks them from the purchases it has seen from this website and sends that with the conversion.

### What if a visitor declines ad user data?

Google Ads still receives the order when the visitor allowed ad storage, but without the hashed customer data. With neither ad user data nor ad storage, the order isn't sent.
