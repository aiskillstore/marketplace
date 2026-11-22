# Server-side tracking for Google Ads on any website with Cloudflare

Source: https://www.productmetrics.io/docs/tracking/server-side/cloudflare-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/cloudflare-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your website to Google Ads from the server, with the script served from your own domain.

Each purchase is confirmed from **the purchase your order confirmation page reports** and sent to Google Ads [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through Google's **Data Manager**. Nothing in the browser talks to Google, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).

## In the app

### 1. Connect your website and Google Ads

**Website:** add your website in Product Metrics, then sign in to Cloudflare. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).

**Google Ads:** connect it in onboarding (**Connect Google Ads and Merchant Center**) or on **Integrations**, pick the client account that runs your campaigns and grant Data Manager access. See [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

**You should see:** the gateway card says **Gateway setup complete**; your Google Ads account shows on **Integrations**.

### 2. Choose your consent banner

In Product Metrics, open **Tracking → Configure consent** and choose the banner your website shows: OneTrust, Cookiebot, Usercentrics or Osano. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Configure consent** names the banner your website actually shows.

### 3. Create the conversion actions

In Product Metrics, select **Tracking** → **Create Google Ads conversions** → **Create 8 conversion actions**. All eight are **secondary**, so nothing changes in your campaigns until you make one primary. See [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions).

Then [add your additional costs](https://www.productmetrics.io/docs/using/costs), so the profit actions carry profit (on a website, set **Product cost fallback (%)**: website orders carry no product costs).

**You should see:** the badge next to **Tracking** reads **Tracking active**.

### 4. Check it works

**Place a test order** through to the order confirmation page.

**You should see:** **Tracking → Check your purchases** shows **Last purchase received** within two minutes, and **Live endpoints** lists the **Tracking SDK** and **Event collector** on your domain. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on a website

| | On a website |
| --- | --- |
| **Script and collector served by** | A Cloudflare gateway (a Worker on your website's Cloudflare zone) that serves the **Tracking SDK** and **Event collector** on your own domain. Setup is only signing in to Cloudflare: no code, and Product Metrics never changes your DNS |
| **Purchase confirmed from** | The purchase your order confirmation page reports |
| **Sent** | When your order confirmation page reports the purchase; if it reports the same order twice, the first report wins |
| **Delivered** | Server-side, through Google's Data Manager, to the eight **Product Metrics** conversion actions |
| **Refunds and cancellations** | Product Metrics adjusts the conversion when the order is refunded or cancelled |
| **Consent read from** | OneTrust, Cookiebot, Usercentrics or Osano |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in Google Ads** | Check that **Tracking → Configure consent** names the banner your website actually shows: Product Metrics sends an order only with the consent this page lists. See [Consent](https://www.productmetrics.io/docs/concepts/consent). |

## FAQ

### Do I need to change my website's code or DNS?

No. Setup is signing in to Cloudflare: a gateway on your Cloudflare zone serves the Tracking SDK and Event collector on your own domain, and Product Metrics never changes your DNS.

### How do the profit actions work without product costs?

Website orders carry no product costs, so set **Product cost fallback (%)** and add your additional costs under [Costs](https://www.productmetrics.io/docs/using/costs). **Product Metrics - Profit** then carries profit for POAS bidding.

### Are refunds on my website sent to Google Ads?

Yes. Product Metrics adjusts the conversion when the order is refunded or cancelled.

### What if the confirmation page reports an order twice?

The first report wins, so reloading the order confirmation page doesn't send a second conversion.
