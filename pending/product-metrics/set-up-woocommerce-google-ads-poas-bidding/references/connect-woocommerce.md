# WooCommerce server-side tracking and profit bidding (POAS)

Source: https://www.productmetrics.io/docs/platforms/woocommerce (the same page as Markdown: https://www.productmetrics.io/docs/platforms/woocommerce.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Connect your WooCommerce store with the Product Metrics plugin, get server-side conversion tracking live in Google Ads, Meta and ChatGPT Ads, and bid on profit, new customers or lifetime value.

The **Product Metrics for WooCommerce** plugin reads every **paid order** (the statuses you choose) with its product costs and customer, and serves tracking from your own WordPress domain. Product Metrics adds **profit**, **new or returning customer** and **lifetime value**, and sends it server-side to each ad channel. No theme code, no Google tag, no DNS change.

- **Install:** the WordPress plugin and a one-time setup token. No code.
- **Product cost:** WooCommerce Core COGS or a product meta key.
- **Consent banner:** OneTrust, Cookiebot, Usercentrics or Osano.

## Prerequisites

- A WordPress administrator login, PHP 8.1 or later, WordPress 6.4 or later, and WP-Cron running (the plugin publishes your settings with it).
- Your shop address, starting with `https://`, at the root of the domain: not in a subfolder, no custom port. And a test payment method.
- A [workspace](https://www.productmetrics.io/docs/using/create-a-workspace) on Pro ([Billing](https://www.productmetrics.io/docs/using/billing)), and editor or admin access.

## In the app

### 1. Connect your store

Go to **Integrations → Ecommerce platforms → Connect WooCommerce**, enter the shop address and select **Create connection**.

**You should see:** a **one-time setup token** for the plugin. It expires, but you can make a new one (below).

> **Warning:** The setup token is a secret. Copy it from the app and never paste it into a chat: Claude and ChatGPT never see it.

### 2. Install the plugin in WordPress

Get **Product Metrics for WooCommerce** from the WooCommerce.com Marketplace, or download the ZIP from Product Metrics. In WordPress Admin: **Plugins → Add Plugin → Upload Plugin**, choose the ZIP (don't unzip it), **Install Now**, **Activate Plugin**.

Then open **WooCommerce → Product Metrics**, paste the token into **One-time setup token** and select **Connect store**.

**You should see:** **Store connected successfully.** and **Webhooks: 2 of 2 active**.

Token expired, or the plugin reinstalled? Ask your assistant to make a new setup token, then copy it from the app.

### 3. Choose orders and costs

Under **Orders & product data**:

1. **Paid order statuses**: select the statuses that mean paid, usually **Processing** and **Completed**.
2. **Product identity**: keep **Variation or product ID (recommended)**, unless your product feed uses **SKU** or another identifier.
3. **Product cost**: **WooCommerce Core COGS (recommended)**, a **Product meta key** for a cost plugin, or **Do not import product cost**. Optional: **Payment cost** and **Actual shipping cost** from an **Order meta key** (what you pay the carrier, not what the customer pays).

Select **Save changes**. When you see **Product Metrics settings were saved**, select **Manage connection** to return to **General**.

**You should see:** **Configuration saved** on **General**.

### 4. Test and import

On **General**, select **Test configuration** (checks up to five recent paid orders). If it reports a problem, fix that setting, save and test again. When it passes, select **Send initial orders** once: you should see **Initial import queued**, and the import continues in the background.

Then select **Verify with next paid order**, place and pay for a test order within ten minutes, and select **Refresh connection status**. If ten minutes pass first, select **Verify with next paid order** again and place another order.

**You should see:** **Live order delivery: Verified**.

### 5. Send the store's orders to a property

In Product Metrics, open **Ecommerce platforms**, select the store (it should say **Active**) and choose the property.

**You should see:** the store ready to track, or what is still left to set up.

### 6. Finish tracking setup

The [setup checklist](https://www.productmetrics.io/docs/using/overview#find-the-next-step) in **Tracking** opens each of these in turn:

- **Consent**: choose your banner (OneTrust, Cookiebot, Usercentrics or Osano), then clear any full-page cache. See [Consent](https://www.productmetrics.io/docs/using/consent).
- **Channels**: connect [Google Ads](https://www.productmetrics.io/docs/channels/google-ads), [Meta](https://www.productmetrics.io/docs/channels/meta) and [ChatGPT Ads (OpenAI)](https://www.productmetrics.io/docs/channels/openai).
- **Google Ads conversion actions**: [create them](https://www.productmetrics.io/docs/using/conversion-actions).
- **Additional costs**: [add what WooCommerce doesn't report](https://www.productmetrics.io/docs/using/costs).

Step by step in **Tracking**:

**You should see:** the badge next to **Tracking** read **Tracking active**. Then [check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on WooCommerce

| | On WooCommerce |
| --- | --- |
| **Install** | WordPress plugin plus a one-time setup token; store at the domain root over HTTPS |
| **Order sent** | When it reaches a status you marked as paid |
| **Product cost** | WooCommerce Core COGS or a product meta key; payment and actual shipping from order meta keys, or your additional costs |
| **Consent** | OneTrust, Cookiebot, Usercentrics or Osano |
| **Customer identity** | Customer account, or billing email for guests |
| **Refunds** | WooCommerce updates the order; Product Metrics reads it again and adjusts the conversion |
| **Remove** | **WooCommerce → Product Metrics → Disconnect store**, then deactivate and delete the plugin. Reinstall with a new token |

## What you get on WooCommerce

Each feature, its channels and the WooCommerce guide for each:

**Features and guides on WooCommerce**

| Feature | Channels | On this platform |
| --- | --- | --- |
| [Server-side conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) | [Google Ads](https://www.productmetrics.io/docs/tracking/server-side/woocommerce-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/server-side/woocommerce-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/server-side/woocommerce-openai) | Orders in your paid statuses; endpoint on your WordPress domain; HPOS supported. |
| [Enhanced Conversions](https://www.productmetrics.io/docs/features/enhanced-conversions) | [Google Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/woocommerce-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/enhanced-conversions/woocommerce-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/woocommerce-openai) | Billing email, phone, name, postcode and country; only with ad user data consent. |
| [Customer lists](https://www.productmetrics.io/docs/features/customer-list) | [Google Ads](https://www.productmetrics.io/docs/tracking/customer-lists/woocommerce-google-ads) | Six Customer Match lists, filled from your WooCommerce orders. |
| [POAS and ROAS bidding](https://www.productmetrics.io/docs/features/poas-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/poas/woocommerce-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/poas/woocommerce-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/poas/woocommerce-openai) | Core COGS or meta keys for product, payment and shipping costs; recorded when read. |
| [New customer bidding](https://www.productmetrics.io/docs/features/new-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/woocommerce-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/new-customers/woocommerce-meta) | Earlier paid orders by account or guest billing email; only your paid statuses count. |
| [Returning customer bidding](https://www.productmetrics.io/docs/features/returning-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/woocommerce-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/returning-customers/woocommerce-meta) | Matched the same way: by account, or guest billing email. |
| [LTV bidding](https://www.productmetrics.io/docs/features/ltv-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/ltv/woocommerce-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/ltv/woocommerce-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/woocommerce-openai) | Observed value from paid WooCommerce orders, not a prediction. |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **"Could not connect the store"** | The setup token is wrong or expired. Make a new one (step 2), paste it and select **Connect store**. |
| **"The store was claimed, but webhook setup did not finish"** | Select **Retry webhook setup**. If webhooks later drop below **2 of 2 active**, use **Repair webhooks** under **Advanced connection tools**. |
| **The shop address is refused** | It must start with `https://`, sit at the domain root and have no custom port. `https://example.com/shop` is not accepted. |
| **"Configuration test failed" or warnings** | Usually the product identity doesn't match your products, or a cost field is empty. Fix it in **Orders & product data**, save and test again before sending initial orders. |
| **The plugin says it is missing its environment file** | The download was incomplete. Download the plugin from Product Metrics again and reinstall. |
| **Fewer conversions than WooCommerce orders** | Only your paid statuses are sent. Check [consent](https://www.productmetrics.io/docs/using/consent): without a supported banner, or with **Not configured**, Product Metrics treats the choice as not given. Clear your full-page cache after changing it. |

## FAQ

### Do I need a developer to set it up on WooCommerce?

No. You install the plugin in WordPress Admin, paste a one-time setup token and choose your paid statuses and cost source. No theme code, no Google tag and no DNS change.

### How is Product Metrics billed on WooCommerce?

Connecting WooCommerce needs Pro, paid through a Stripe subscription. Pro is a graduated share of your rolling 30-day Google Shopping spend, the first €10K each month is free, and server-side tracking is included.

### Where do product costs come from on WooCommerce?

From WooCommerce Core COGS, or a product meta key if a cost plugin stores them. Payment and actual shipping cost can come from order meta keys; anything else you add as [additional costs](https://www.productmetrics.io/docs/using/costs).

### Does it work with my cookie banner?

Yes, with OneTrust, Cookiebot, Usercentrics or Osano. Choose it in **Configure consent**, then clear any full-page cache so visitors get the new setting.
