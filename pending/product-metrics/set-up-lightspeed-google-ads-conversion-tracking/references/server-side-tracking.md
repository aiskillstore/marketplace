# Lightspeed server-side tracking for Google Ads

Source: https://www.productmetrics.io/docs/tracking/server-side/lightspeed-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/lightspeed-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your Lightspeed shop to Google Ads from the server, with the script served from your own domain.

Each purchase is confirmed from **your Lightspeed eCom orders** and sent to Google Ads [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through Google's **Data Manager**. Nothing in the browser talks to Google, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your Lightspeed eCom (C-Series) shop connected**: a back-office administrator login (an API key can't sign in), the shop's cluster, hostname and numeric Shop ID, and an enabled API key with its secret that has Read on Content, Products, Customers and Orders, and Read and Write on Settings and Tracking. The shop can't already be connected to another workspace, and it reads **Active** with **Configuration is current** before you link your property. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).
- **Your shop domain on Cloudflare**, with its DNS record proxied (the orange cloud), and a workspace admin who signs in to Cloudflare once.

## In the app

### 1. Connect Lightspeed and Google Ads

**Store:** add a Lightspeed API key in Product Metrics and sign in to Cloudflare for the gateway. See [Lightspeed](https://www.productmetrics.io/docs/platforms/lightspeed).

**Google Ads:** connect it in onboarding (**Connect Google Ads and Merchant Center**) or on **Integrations**, pick the client account that runs your campaigns and grant Data Manager access. See [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

**You should see:** **Connection status**, **Credential status** and **Installation status** read **Active**, **Configured** and **Active**, publication reads **Configuration is current**, and the gateway says **Gateway setup complete**; your Google Ads account shows on **Integrations**.

### 2. Choose your consent banner

In Product Metrics, open **Tracking → Configure consent** and choose the banner your shop shows: OneTrust, Cookiebot, Usercentrics or Osano. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Configure consent** names the banner your shop actually shows.

### 3. Create the conversion actions

In Product Metrics, select **Tracking** → **Create Google Ads conversions** → **Create 8 conversion actions**. All eight are **secondary**, so nothing changes in your campaigns until you make one primary. See [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions).

Then [add your additional costs](https://www.productmetrics.io/docs/using/costs), so the profit actions carry profit.

**You should see:** the badge next to **Tracking** reads **Tracking active**.

### 4. Check it works

In **Tracking**, open the **Tracking SDK** link under the Cloudflare gateway's **Live endpoints**: it returns JavaScript (the collector only accepts POST requests). Then **place and pay for a test order**.

**You should see:** **Live endpoints** lists the **Tracking SDK** and **Event collector** on your shop domain, and the order appears for the linked property. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on Lightspeed

| | On Lightspeed |
| --- | --- |
| **Script and collector served by** | A Cloudflare gateway (a Worker on your shop's Cloudflare zone), as Lightspeed eCom has no app proxy. Product Metrics never changes your DNS |
| **Purchase confirmed from** | Your Lightspeed eCom orders |
| **Sent** | When Lightspeed marks the order paid (a pay-on-pickup order when it is paid) |
| **Delivered** | Server-side, through Google's Data Manager, to the eight **Product Metrics** conversion actions |
| **Refunds and cancellations** | Lightspeed reports order, invoice and return changes; credit notes become refunds and the Google Ads conversion is adjusted |
| **Consent read from** | OneTrust, Cookiebot, Usercentrics or Osano |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in Google Ads** | Check that **Tracking → Configure consent** names the banner your store actually shows: Product Metrics sends an order only with the consent this page lists. See [Consent](https://www.productmetrics.io/docs/concepts/consent). |

## FAQ

### Why does Lightspeed tracking use Cloudflare?

Lightspeed eCom has no app proxy, so a Cloudflare gateway (a Worker on your shop's Cloudflare zone) serves the script and collector on your shop domain. Product Metrics never changes your DNS.

### When is a pay-on-pickup order sent to Google Ads?

When it is paid. Lightspeed orders are sent once Lightspeed marks them paid, not when they are placed.

### Are Lightspeed credit notes sent to Google Ads?

Yes. Lightspeed reports order, invoice and return changes; credit notes become refunds and the Google Ads conversion is adjusted.

### Will this change my Google Ads bidding straight away?

No. The eight Product Metrics conversion actions start as secondary, so nothing changes in your campaigns until you make one primary in Google Ads.
