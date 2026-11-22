# Magento server-side tracking for Google Ads

Source: https://www.productmetrics.io/docs/tracking/server-side/magento-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/magento-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every purchase from your Magento store view to Google Ads from the server, with the script served from your own domain.

Each purchase is confirmed from **your Magento orders** and sent to Google Ads [from the server](https://www.productmetrics.io/docs/concepts/server-side-tracking), through Google's **Data Manager**. Nothing in the browser talks to Google, so an [ad blocker](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) has nothing to block.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics (editor is enough for the store and destination steps), with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your Magento store view connected**: Magento 2.4, 2.0 or 1.9 / OpenMage, Magento Admin access, the public HTTPS shop address and the **store-view ID**, and a **developer** with access to your server who installs the Product Metrics module (Composer or ZIP), adds the store view's private configuration file and keeps Magento cron running. The connection reads **Active** before you link your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).

## In the app

### 1. Connect Magento and Google Ads

**Store:** create the module configuration under **Ecommerce platforms → Connect Magento**, have your developer install the module, then verify the store view. See [Magento](https://www.productmetrics.io/docs/platforms/magento).

**Google Ads:** connect it in onboarding (**Connect Google Ads and Merchant Center**) or on **Integrations**, pick the client account that runs your campaigns and grant Data Manager access. See [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

**You should see:** under **Manage Magento**, the connection is **Active** and your property is linked; your Google Ads account shows on **Integrations**.

### 2. Choose your consent banner

In Product Metrics, open **Tracking → Configure consent** and choose the banner your shop shows: OneTrust, Cookiebot, Usercentrics or Osano. **Magento's own cookie restriction notice does not grant consent.** With any other banner, your developer passes the visitor's choices to Product Metrics; anything not set stays denied. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Configure consent** names the banner your store view actually shows.

### 3. Create the conversion actions

In Product Metrics, select **Tracking** → **Create Google Ads conversions** → **Create 8 conversion actions**. All eight are **secondary**, so nothing changes in your campaigns until you make one primary. See [Conversion actions](https://www.productmetrics.io/docs/using/conversion-actions).

Then [add your additional costs](https://www.productmetrics.io/docs/using/costs), so the profit actions carry profit.

**You should see:** the badge next to **Tracking** reads **Tracking active**.

### 4. Check it works

**Place a paid test order** in the connected store view with your payment provider's test mode, and allow a few minutes for cron.

**You should see:** under **Manage Magento**, the desired and active revision numbers are the same, and the order appears for the linked property. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on Magento

| | On Magento |
| --- | --- |
| **Script and collector served by** | The Product Metrics module, on its own paths of your store domain, set for each store view by the module's configuration file. Nothing loads from another domain and there is no script tag |
| **Purchase confirmed from** | Your Magento orders |
| **Sent** | When the order is paid; the module sends changes every two minutes through cron |
| **Delivered** | Server-side, through Google's Data Manager, to the eight **Product Metrics** conversion actions |
| **Refunds and cancellations** | Refunds and cancellations come from the module; the Google Ads conversion is adjusted |
| **Consent read from** | OneTrust, Cookiebot, Usercentrics or Osano, or your own banner, passed on by your developer |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in Google Ads** | Check that **Tracking → Configure consent** names the banner your store actually shows: Product Metrics sends an order only with the consent this page lists. See [Consent](https://www.productmetrics.io/docs/concepts/consent). |

## FAQ

### Do I need a developer for Magento tracking?

Yes, once: a developer with terminal access installs the Product Metrics module with Composer or as a ZIP and makes sure Magento cron runs. Everything after that happens in Product Metrics and Google Ads.

### How fast does a paid Magento order reach Google Ads?

Within minutes: the module sends order changes every two minutes through Magento cron, so cron has to keep running.

### Does Magento's cookie notice count as consent?

No. Magento's own cookie restriction notice does not grant consent. Use OneTrust, Cookiebot, Usercentrics or Osano, or have your developer pass your banner's choices to Product Metrics; anything not set stays denied.

### Are Magento refunds and cancellations sent to Google Ads?

Yes. The module reports refunds and cancellations, and the Google Ads conversion is adjusted.
