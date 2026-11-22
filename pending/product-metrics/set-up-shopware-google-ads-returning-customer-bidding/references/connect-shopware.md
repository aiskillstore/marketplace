# Shopware server-side tracking and profit bidding (POAS)

Source: https://www.productmetrics.io/docs/platforms/shopware (the same page as Markdown: https://www.productmetrics.io/docs/platforms/shopware.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Connect a Shopware sales channel with the Product Metrics plugin, get server-side conversion tracking live in Google Ads, Meta and ChatGPT Ads, and bid on profit, new customers or lifetime value.

The Product Metrics **plugin** reads every **paid order** from the sales channel you pair, with the purchase price on each line, and serves tracking from a random path on your own Shopware domain. Product Metrics adds **profit**, **new or returning customer** and **lifetime value**, and sends it server-side to each ad channel. No theme code and no Google tag.

- **Install:** the Shopware plugin, paired to one sales channel with a token.
- **Product cost:** the purchase price on each order line.
- **Consent banner:** Shopware's cookie manager, or a supported banner (OneTrust, Cookiebot, Usercentrics or Osano).

## Prerequisites

- Shopware 6.7 with PHP 8.2 or later (the plugin is built for 6.7.14.0; Shopware 5 is not supported), with its scheduled tasks and message workers running: pairing and order sync use them.
- A Shopware administrator login that can upload and activate extensions, and the sales channel to track, with its public HTTPS address under **Sales Channels → your channel → Domains**. One installation tracks one sales channel.
- A [workspace](https://www.productmetrics.io/docs/using/create-a-workspace) on Pro ([Billing](https://www.productmetrics.io/docs/using/billing)), editor or admin access, and a property for the orders.

## In the app

### 1. Connect your store

Go to **Integrations → Ecommerce platforms → Connect Shopware 6**, enter the **Shopware 6 store URL** (your storefront's HTTPS address) and select **Create connection**. The app shows **Connection created** with the hostname Product Metrics verified and a download link.

Check that **Verified Shopware 6 hostname** is your storefront and select **Confirm Shopware 6 hostname** to reveal the **one-time pairing token**. Copy it, download the ZIP, then select **Continue to connection**.

**You should see:** the connection read **Setup required** until the plugin pairs.

> **Warning:** The token is a secret. Copy it from the app and never paste it into a chat: Claude and ChatGPT never see it.

### 2. Install and pair the plugin in Shopware

1. **Install the plugin** from the Shopware Store, or: **Extensions → My extensions → Upload extension**, **Confirm**, choose the ZIP without unzipping, **Install**, and turn its switch on.
2. **Select your sales channel.** Select **Configure** on the Product Metrics card and choose the channel that serves your verified hostname (for example **Storefront**), not **All Sales Channels**. Select **Unlink inheritance** next to **Enable this sales channel**, **Primary HTTPS storefront URL** and **One-time pairing token**.
3. **Pair.** Turn on **Enable this sales channel**, set **Primary HTTPS storefront URL** to exactly the verified address, paste the token into **One-time pairing token**, **Save**.

**You should see:** **Configuration saved**; the token field clears once pairing finishes in the background.

### 3. Check pairing and link a property

In Product Metrics, select **Verify connection** until the store reads **Active**, then choose the property that should receive the orders. **Setup required** means the scheduled task hasn't paired it yet; **Pending / Waiting for runtime publication** means pairing is done and publication is still running. Allow a few sync cycles and verify again.

**You should see:** the store paired. Until the plugin is installed and paired, it reads **Setup required**. Once paired, you see the sync status, pending and quarantined jobs, and the last success and error.

### 4. Finish tracking setup

The [setup checklist](https://www.productmetrics.io/docs/using/overview#find-the-next-step) in **Tracking** opens each of these in turn:

- **Consent**: leave **Not configured** to use Shopware's own cookie manager, or choose OneTrust, Cookiebot, Usercentrics or Osano if your shop shows one. See [Consent](https://www.productmetrics.io/docs/using/consent).
- **Channels**: connect [Google Ads](https://www.productmetrics.io/docs/channels/google-ads), [Meta](https://www.productmetrics.io/docs/channels/meta) and [ChatGPT Ads (OpenAI)](https://www.productmetrics.io/docs/channels/openai).
- **Google Ads conversion actions**: [create them](https://www.productmetrics.io/docs/using/conversion-actions).
- **Additional costs**: product costs come from Shopware; [add payment fees, returns and the rest](https://www.productmetrics.io/docs/using/costs).

Step by step in **Tracking**:

**You should see:** the badge next to **Tracking** read **Tracking active**.

### 5. Check it works

Place a test order through the paired sales channel with your payment provider's test mode and allow a few minutes for sync. Then follow [Check tracking](https://www.productmetrics.io/docs/using/check-tracking), or ask your assistant whether the order arrived.

**You should see:** your test order arrive. With Shopware's own cookie manager, your banner lists **Product Metrics measurement**, with **Product Metrics analytics** and **Product Metrics advertising attribution**.

## How it works on Shopware

| | On Shopware |
| --- | --- |
| **Install** | Shopware plugin, one sales channel per installation, paired with a one-time token |
| **Order sent** | Paid orders from the paired sales channel only |
| **Product cost** | Purchase price on each order line; you add payment fees, returns and the rest |
| **Consent** | Shopware's own cookie manager (**Not configured**), or OneTrust, Cookiebot, Usercentrics or Osano |
| **Customer identity** | Per sales channel: customer account or guest email |
| **Refunds** | Shopware's refund records become a refund on the same order; a cancelled order is marked cancelled. A daily check over the last seven days picks up anything missed |
| **Uninstall** | Uninstalling or deactivating ends the connection for good; reconnect with a new connection and token |

## What you get on Shopware

Each feature, its channels and the Shopware guide for each:

**Features and guides on Shopware**

| Feature | Channels | On this platform |
| --- | --- | --- |
| [Server-side conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) | [Google Ads](https://www.productmetrics.io/docs/tracking/server-side/shopware-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/server-side/shopware-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/server-side/shopware-openai) | Paid orders from the paired sales channel; the script loads from a random path. |
| [Enhanced Conversions](https://www.productmetrics.io/docs/features/enhanced-conversions) | [Google Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopware-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopware-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopware-openai) | Email, phone, name, postcode and country from the order; cookie manager choice applies. |
| [Customer lists](https://www.productmetrics.io/docs/features/customer-list) | [Google Ads](https://www.productmetrics.io/docs/tracking/customer-lists/shopware-google-ads) | Six Customer Match lists, filled from your Shopware orders. |
| [POAS and ROAS bidding](https://www.productmetrics.io/docs/features/poas-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/poas/shopware-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/poas/shopware-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/poas/shopware-openai) | Purchase price per order line at order time; later price changes don't rewrite profit. |
| [New customer bidding](https://www.productmetrics.io/docs/features/new-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/shopware-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/new-customers/shopware-meta) | No earlier paid order in the same sales channel, by account or guest email. |
| [Returning customer bidding](https://www.productmetrics.io/docs/features/returning-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/shopware-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/returning-customers/shopware-meta) | An earlier paid order in the same sales channel. |
| [LTV bidding](https://www.productmetrics.io/docs/features/ltv-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/ltv/shopware-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/ltv/shopware-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/shopware-openai) | Observed value from paid orders within the paired sales channel. |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Stays "Setup required" or "Pending"** | Pairing runs through Shopware's scheduled tasks and message workers. Check both run without errors and the storefront is reachable over HTTPS, then verify again. |
| **The token has expired** | Open the connection in the app and select **Generate one-time setup token**. Paste it into **One-time pairing token** for your sales channel and **Save**. |
| **The pairing settings are greyed out** | They inherit from **All Sales Channels**. Select **Unlink inheritance** next to each of the three settings. |
| **Fewer conversions than Shopware orders** | Only paid orders from the paired sales channel are sent. Check [consent](https://www.productmetrics.io/docs/using/consent): a banner your shop doesn't show means the choice reads as not given. |

## FAQ

### Do I need a developer to set it up on Shopware?

No. You install the plugin in Shopware Administration and paste a one-time pairing token; no theme code and no Google tag. Shopware's scheduled tasks and message workers do need to be running.

### Does Product Metrics work with Shopware 5?

No. The plugin needs Shopware 6.7 with PHP 8.2 or later.

### Does it work with Shopware's own cookie manager?

Yes. Leave consent on **Not configured** and Product Metrics follows Shopware's cookie manager, which then lists **Product Metrics measurement**. If your shop shows OneTrust, Cookiebot, Usercentrics or Osano, choose that instead.

### Does one installation cover all my sales channels?

No. Each installation tracks one sales channel, and only paid orders from that channel are sent.
