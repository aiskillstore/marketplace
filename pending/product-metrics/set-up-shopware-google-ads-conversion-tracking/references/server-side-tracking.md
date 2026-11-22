# Shopware server-side tracking for Google Ads

Source: https://www.productmetrics.io/docs/tracking/server-side/shopware-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/shopware-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your Shopware sales channel to Google Ads from the server, with the script served from your own domain.

Each purchase is confirmed from **your Shopware orders** and sent to Google Ads [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through Google's **Data Manager**. Nothing in the browser talks to Google, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your Shopware sales channel connected**: Shopware 6.7 (this plugin build supports 6.7.14.0) with PHP 8.2+, an administrator who can upload extensions, Shopware's scheduled tasks and message workers running, and the channel's public HTTPS address under **Sales Channels → your channel → Domains**. You pair one sales channel with a one-time token; it reads **Active** before you link your property. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).

## In the app

### 1. Connect Shopware and Google Ads

**Store:** install the Product Metrics plugin and pair your sales channel with a one-time token. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).

**Google Ads:** connect it in onboarding (**Connect Google Ads and Merchant Center**) or on **Integrations**, pick the client account that runs your campaigns and grant Data Manager access. See [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

**You should see:** in Product Metrics, the store reads **Active** after **Verify connection**; your Google Ads account shows on **Integrations**.

### 2. Choose your consent banner

Using Shopware's own cookie manager? Leave **Tracking → Configure consent** on **Not configured**: the extension adds a **Product Metrics measurement** group with **Product Metrics analytics** and **Product Metrics advertising attribution**. Choose OneTrust, Cookiebot, Usercentrics or Osano only if your shop shows one of those banners instead. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Configure consent** names the banner your sales channel actually shows.

### 3. Create the conversion actions

In Product Metrics, select **Tracking** → **Create Google Ads conversions** → **Create 8 conversion actions**. All eight are **secondary**, so nothing changes in your campaigns until you make one primary. See [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions).

Then [add your additional costs](https://www.productmetrics.io/docs/using/costs), so the profit actions carry profit.

**You should see:** the badge next to **Tracking** reads **Tracking active**.

### 4. Check it works

**Place a paid test order** through the paired sales channel with your payment provider's test mode, and give Shopware a few minutes to sync it.

**You should see:** your cookie banner lists **Product Metrics measurement** (with Shopware's own cookie manager). More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on Shopware

| | On Shopware |
| --- | --- |
| **Script and collector served by** | The Shopware extension, on a path generated for your sales channel (`/<random>/c/<token>`). No Cloudflare step, no script tag; one installation tracks one sales channel |
| **Purchase confirmed from** | Your Shopware orders |
| **Sent** | When the order from the paired sales channel is paid |
| **Delivered** | Server-side, through Google's Data Manager, to the eight **Product Metrics** conversion actions |
| **Refunds and cancellations** | Shopware's refund records become refunds and cancellations are marked; the Google Ads conversion is adjusted. A daily check covers the last seven days |
| **Consent read from** | Shopware's own cookie manager, or OneTrust, Cookiebot, Usercentrics or Osano |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Nothing reaches Google Ads** | Check that **Tracking → Configure consent** names the banner your store shows, or reads **Not configured** if it uses Shopware's own cookie manager. |

## FAQ

### Do I need Google Tag Manager on Shopware?

No. The Shopware extension serves the script and collector on a path generated for your sales channel. No script tag and no Cloudflare step.

### Can one installation track several Shopware sales channels?

No. One installation tracks one sales channel: the one you paired with the one-time token. Only paid orders from that channel are sent.

### Are Shopware refunds sent to Google Ads?

Yes. Shopware's refund records become refunds and cancellations are marked, so the Google Ads conversion is adjusted. A daily check covers the last seven days.

### Do I need to remove my existing Google Ads tag?

No. Your existing tags keep running next to the eight Product Metrics actions. When you make a Product Metrics action primary, set your old purchase action to secondary so a purchase isn't counted twice.
