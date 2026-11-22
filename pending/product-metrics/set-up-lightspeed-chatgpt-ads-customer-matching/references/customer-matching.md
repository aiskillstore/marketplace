# Lightspeed customer data for ChatGPT Ads (OpenAI Conversions API)

Source: https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-openai (the same page as Markdown: https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send hashed customer data from Lightspeed orders with each ChatGPT Ads event through the OpenAI Conversions API, so ChatGPT Ads can match conversions to people.

With the **OpenAI Conversions API**, every event Product Metrics sends to your ChatGPT Ads pixel carries the shopper's **customer data from the Lightspeed order**, hashed with **SHA-256**, and **browser references**, so ChatGPT Ads can match the conversion to the person who saw or clicked the ad. There is no separate switch: once ChatGPT Ads is connected, each event the visitor consented to includes it.

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your Lightspeed eCom (C-Series) shop connected**: a back-office administrator login (an API key can't sign in), the shop's cluster, hostname and numeric Shop ID, and an enabled API key with its secret that has Read on Content, Products, Customers and Orders, and Read and Write on Settings and Tracking. The shop can't already be connected to another workspace, and it reads **Active** with **Configuration is current** before you link your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).
- **Your shop domain on Cloudflare**, with its DNS record proxied (the orange cloud), and a workspace admin who signs in to Cloudflare once.
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Connect your shop and ChatGPT Ads

Connect your shop with [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed). For [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai), copy your **Pixel ID** in Ads Manager → **Conversions** and create a Conversions API key, then add both under **Tracking → OpenAI Conversions API → Connect OpenAI**.

Connect your store, step by step:

Then add the ChatGPT Ads destination:

**You should see:** **Connection status**, **Credential status** and **Installation status** read **Active**, **Configured** and **Active**, publication reads **Configuration is current**, and the gateway says **Gateway setup complete**; the app says **OpenAI accepted the test event**.

### 2. Set your consent banner

On Lightspeed, Product Metrics reads consent from the banner chosen under **Tracking → Configure consent** (OneTrust, Cookiebot, Usercentrics or Osano).

ChatGPT Ads has no consent mode: an event is only sent with marketing consent (ad user data), and the ChatGPT Ads click and browser references also need ad storage consent. Without ad personalisation consent, the event is sent marked as opted out. See [Consent](https://www.productmetrics.io/docs/using/consent#chatgpt-ads).

**You should see:** **Tracking → Configure consent** names the banner your shop shows.

### 3. Check an order

Place a test order with all cookies accepted, then open **Tracking → OpenAI Conversions API**.

**You should see:** your ChatGPT Ads pixel connected and delivering events, and your paid test order listed.

There is no report of the hashed fields themselves: ChatGPT Ads receives them only inside each event. Delivery errors show in the app under **OpenAI reported a problem**.

## Fields sent

Where each field comes from on Lightspeed:

| Customer data | From | Sent to ChatGPT Ads as |
| --- | --- | --- |
| Email address | The Lightspeed order | `emails_sha256` |
| Phone number | The Lightspeed order | `phone_numbers_sha256`: digits with country code, no `+` |
| First and last name | The Lightspeed order | `first_names_sha256`, `last_names_sha256`: lowercase, no spaces or punctuation |
| Customer ID | Your shop's customer ID | `external_ids_sha256` |
| Postal code, country | The Lightspeed order | `postal_codes`, `countries`, unhashed as ChatGPT Ads asks |
| IP address, user agent | The visitor's browser | `ip_address`, `user_agent`, unhashed |
| Browser reference | The `__obref` cookie | `obref`, unmodified |
| Ad click | The `__oppref` cookie | `oppref`, unmodified |

Raw email addresses, phone numbers, names and customer IDs never leave Product Metrics. A postal code with characters ChatGPT Ads doesn't accept is left out rather than failing the event.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in ChatGPT Ads** | Check that **Tracking → Configure consent** names the banner your store actually shows ([step 2](#2-set-your-consent-banner)). |

## FAQ

### Can I keep the OpenAI Pixel on my site?

Yes. OpenAI deduplicates on Pixel ID, event name and event ID, and keeps the first event it receives.

### Which consent does ChatGPT Ads need on Lightspeed?

ChatGPT Ads has no consent mode: an event is only sent with marketing consent (ad user data), and the click and browser references also need ad storage. Without ad personalisation consent, the event is sent marked as opted out. On Lightspeed, Product Metrics reads it from the banner you choose: OneTrust, Cookiebot, Usercentrics or Osano.

### Can ChatGPT Ads bid on new or returning customers?

Yes. Product Metrics sends `pm_new_customer` and `pm_new_customer_profit` for new customers and `pm_returning_customer` and `pm_returning_customer_profit` for returning ones. ChatGPT Ads bids on the conversion you select in **Ads Manager → Conversions**.

### Are past orders and refunds sent to ChatGPT Ads?

No. OpenAI accepts events up to 7 days old, so historical orders aren't imported, and later refunds and cancellations don't revise events already sent.
