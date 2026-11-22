# Lightspeed eCom server-side tracking and profit bidding (POAS)

Source: https://www.productmetrics.io/docs/platforms/lightspeed (the same page as Markdown: https://www.productmetrics.io/docs/platforms/lightspeed.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Connect Lightspeed eCom (C-Series) with an API key and Cloudflare, get server-side conversion tracking live in Google Ads, Meta and ChatGPT Ads, and bid on profit, new customers or lifetime value.

Lightspeed tells Product Metrics about every **paid order** through webhooks Product Metrics registers for you, with the cost price on each line. A **Cloudflare gateway** on your shop domain serves the tracking. Product Metrics adds **profit**, **new or returning customer** and **lifetime value**, and sends it server-side to each ad channel. No code and no Google tag.

- **Install:** an API key in Lightspeed, then a Cloudflare sign-in. No code.
- **Product cost:** the cost price on each order line.
- **Consent banner:** OneTrust, Cookiebot, Usercentrics or Osano.

## Prerequisites

- A Lightspeed eCom (C-Series) back-office administrator login (email and password: an API key can't sign in to the back office), on the Europe or United States cluster, for a shop that isn't connected to another Product Metrics workspace.
- The shop's public hostname and numeric **Store ID**, and an enabled API key with its matching secret, with the permissions in step 1.
- A shop domain that runs through Cloudflare with its DNS record proxied (the orange cloud) and a Cloudflare login for that account. Product Metrics never changes your DNS.
- A [workspace](https://www.productmetrics.io/docs/using/create-a-workspace) on Pro ([Billing](https://www.productmetrics.io/docs/using/billing)), a property for the orders, and a workspace admin for the Cloudflare step.

## In the app

### 1. Create the API key in Lightspeed

1. Sign in to the Lightspeed back office with your administrator email and password. Select **Help** (bottom left) and note the **Store ID** below your name, and the public shop hostname Lightspeed reports, including your own domain if the shop uses one.
2. Open **Settings → Store Settings → Developers**, select **New API key** (Dutch: **Nieuwe API key**), name it **Product Metrics**, **Save**. Or open the key you already use for Product Metrics: it keeps its saved settings, so check them against the table.
3. Under **SETTINGS**, enable the key and set these, leaving **Write** unticked for Content, Products, Customers and Orders:

| Section | Read | Write |
| --- | --- | --- |
| Content (Inhoud) | ✓ | |
| Products (Producten) | ✓ | |
| Customers (Klanten) | ✓ | |
| Orders | ✓ | |
| Settings (Instellingen) | ✓ | ✓ |
| Tracking | ✓ | ✓ |

4. **Save** (**Opslaan**). A new key starts disabled with nothing ticked. Write access to Settings lets Product Metrics add its shop script for you; a disabled key or a missing permission stops the connection.
5. Under **DETAILS**, copy the API key, select **Show** and copy the matching API secret.

**You should see:** the key enabled, with the API key and secret copied.

### 2. Connect your store

Go to **Ecommerce platforms → Connect Lightspeed**, fill in **Cluster**, **Store hostname**, **Shop ID**, **API key** and **API secret**, and select **Connect Lightspeed**.

**Cluster** is EU for shops on `.webshopapp.com` and US for `.shoplightspeed.com`; a shop on its own domain keeps its original cluster. **Store hostname** is the shop's hostname without `/admin`, and **Shop ID** is the Store ID.

> **Warning:** The API key and secret are credentials. Enter them in the app and keep them out of chats. An assistant never needs them repeated back.

Keep the window open while Product Metrics checks the key, saves the connection, registers its order webhooks and detects your shop language.

**You should see:** **Connection status Active**, **Credential status Configured** and **Installation status Active**, then **Configuration is current** under **Manage Lightspeed → Connection details and removal**. A connection can be **Active** while publication is still pending: wait and reopen **Manage Lightspeed** before you link a property.

### 3. Send the shop's orders to a property

Once publication reads **Configuration is current**, link the property: in **Tracking → Complete your tracking setup**, select **Link the store to this property**, or use the property assignments under **Manage Lightspeed**.

**You should see:** **Link the store to this property** ticked.

### 4. Connect Cloudflare

A browser step for a workspace admin. In **Tracking**, under **Install storefront tracking**:

1. Select **Connect Cloudflare** and approve access on Cloudflare's screen. Product Metrics asks only for Account Read, Zone Read, DNS Records Read, Workers Scripts Write, Workers Routes Write and Offline Access.
2. Choose the **Cloudflare account** and the **Cloudflare zone** your shop domain is in.
3. Select **Set up gateway** and keep the page open (usually under a minute).

Product Metrics then points its Lightspeed shop script at your domain. Nothing to paste into your theme.

**You should see:** **Gateway setup complete**.

### 5. Finish tracking setup

The [setup checklist](https://www.productmetrics.io/docs/using/overview#find-the-next-step) in **Tracking** opens each of these in turn:

- **Consent**: choose your banner (OneTrust, Cookiebot, Usercentrics or Osano). See [Consent](https://www.productmetrics.io/docs/using/consent).
- **Channels**: connect [Google Ads](https://www.productmetrics.io/docs/channels/google-ads) (with Data Manager access), [Meta](https://www.productmetrics.io/docs/channels/meta) and [ChatGPT Ads (OpenAI)](https://www.productmetrics.io/docs/channels/openai).
- **Google Ads conversion actions**: [create them](https://www.productmetrics.io/docs/using/conversion-actions).
- **Additional costs**: product costs come from Lightspeed; [add the rest](https://www.productmetrics.io/docs/using/costs), including payment fees.

Step by step in **Tracking**:

**You should see:** the badge next to **Tracking** read **Tracking active**.

### 6. Check it works

Place and pay for a test order, then follow [Check tracking](https://www.productmetrics.io/docs/using/check-tracking), or ask your assistant whether the order arrived. Under the Cloudflare gateway, **Live endpoints** lists the **Tracking SDK** and **Event collector** on your domain. The collector accepts only POST, so opening it in a browser isn't a test.

**You should see:** the **Tracking SDK** link return JavaScript, and your test order arrive.

## How it works on Lightspeed

| | On Lightspeed |
| --- | --- |
| **Install** | Lightspeed API key and secret, plus Cloudflare approved once by a workspace admin |
| **Order sent** | When Lightspeed marks it paid |
| **Product cost** | Cost price on each order line; payment fees from your additional costs |
| **Consent** | OneTrust, Cookiebot, Usercentrics or Osano |
| **Customer identity** | Lightspeed's new-customer flag and order history |
| **Refunds** | Lightspeed reports order, invoice and return changes; credit notes become a refund on the same order, a cancelled order is marked cancelled |
| **Remove** | **Manage Lightspeed → Remove connection**: type the hostname, tick the acknowledgement, confirm. The Cloudflare gateway is removed too |

## What you get on Lightspeed

Each feature, its channels and the Lightspeed guide for each:

**Features and guides on Lightspeed**

| Feature | Channels | On this platform |
| --- | --- | --- |
| [Server-side conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) | [Google Ads](https://www.productmetrics.io/docs/tracking/server-side/lightspeed-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/server-side/lightspeed-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/server-side/lightspeed-openai) | Sent once paid (pay-on-pickup when paid); a Cloudflare gateway serves the script. |
| [Enhanced Conversions](https://www.productmetrics.io/docs/features/enhanced-conversions) | [Google Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/lightspeed-openai) | The email is hashed in the browser; sent only with ad user data consent. |
| [Customer lists](https://www.productmetrics.io/docs/features/customer-list) | [Google Ads](https://www.productmetrics.io/docs/tracking/customer-lists/lightspeed-google-ads) | Six Customer Match lists, filled from your Lightspeed orders. |
| [POAS and ROAS bidding](https://www.productmetrics.io/docs/features/poas-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/poas/lightspeed-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/poas/lightspeed-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/poas/lightspeed-openai) | Cost price per order line; payment fees from your [additional costs](https://www.productmetrics.io/docs/using/costs). |
| [New customer bidding](https://www.productmetrics.io/docs/features/new-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/lightspeed-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/new-customers/lightspeed-meta) | Lightspeed's new-customer flag plus the customer's order history. |
| [Returning customer bidding](https://www.productmetrics.io/docs/features/returning-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/lightspeed-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/returning-customers/lightspeed-meta) | Orders from customers who bought before, as their own conversion. |
| [LTV bidding](https://www.productmetrics.io/docs/features/ltv-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/ltv/lightspeed-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/ltv/lightspeed-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/lightspeed-openai) | Observed value from paid orders, not a prediction. |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **"The Lightspeed credentials could not be verified"** | Check the cluster, Shop ID, key and secret, and that the key is enabled with the permissions in step 1. |
| **"This store is already connected"** | The shop is connected in another workspace. Remove that connection first, with its owner's agreement. |
| **Active, but publication stays pending** | Wait and reopen **Manage Lightspeed**. If it stays pending, check the error shown or contact support. |
| **"Proxy the storefront DNS record first"** | Turn on the orange cloud for the shop's DNS record in Cloudflare, then choose the zone again. |
| **"Update the storefront domain first"** | The zone doesn't contain your shop domain. Select **Change storefront domain**, enter the hostname customers use without `https://`, and choose the zone again. |
| **"Some permissions were not granted"** | Select **Connect Cloudflare** again and approve every permission. |

## FAQ

### Do I need a developer to set it up on Lightspeed?

No. You create an API key in the Lightspeed back office, enter it in Product Metrics and approve Cloudflare once. Product Metrics registers its order webhooks and adds its shop script for you; nothing goes into your theme.

### Which Lightspeed shops does it work with?

Lightspeed eCom (C-Series), on the Europe or United States cluster.

### How is Product Metrics billed on Lightspeed?

Connecting Lightspeed needs Pro, paid through a Stripe subscription. Server-side tracking is included in Pro, not billed separately.

### Where do product costs come from on Lightspeed?

From the cost price on each Lightspeed order line. Lightspeed reports no payment fees, so add those with your other [additional costs](https://www.productmetrics.io/docs/using/costs).
