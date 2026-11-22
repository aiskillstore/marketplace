# Shopify server-side tracking and profit bidding (POAS)

Source: https://www.productmetrics.io/docs/platforms/shopify (the same page as Markdown: https://www.productmetrics.io/docs/platforms/shopify.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Connect your Shopify store, get server-side conversion tracking live in Google Ads, Meta and ChatGPT Ads, and bid on profit, new customers or lifetime value.

Shopify tells Product Metrics about every **paid order**, with its product costs and customer. Product Metrics adds **profit**, **new or returning customer** and **lifetime value**, and sends it server-side to each ad channel you connect. No code and no Google tag: the app's script runs through Shopify's app proxy on your own store domain.

- **Install:** the Shopify app and its app embed. No code.
- **Product cost:** from Shopify. You add shipping, handling, returns and payment fees.
- **Consent banner:** Shopify Customer Privacy, or a supported banner (OneTrust, Cookiebot, Usercentrics or Osano).

## Prerequisites

- A Shopify login that can install apps and edit the theme.
- A [workspace](https://www.productmetrics.io/docs/using/create-a-workspace). You can also create one while linking the store.
- A Shopify subscription for the app: it checks your setup without one, but collects nothing until it starts. Shopify stores don't need Product Metrics Pro billing; you pay through Shopify.

## In the app

### 1. Install the Shopify app

In Product Metrics, go to **Ecommerce platforms → Connect Shopify → Open Shopify App Store**. In Shopify, select **Install** and approve the permissions Shopify lists (orders, products, customers, themes, and a checkout pixel).

**You should see:** the Product Metrics app open in Shopify Admin.

### 2. Link the store

In the app, select **Connect Product Metrics account**, sign in, choose the workspace and accounts this store belongs to, and select **Link Shopify store**.

**You should see:** **One step left: save the app embed**.

### 3. Save the app embed

Select **Open theme editor**, turn on **Product Metrics** under **App embeds**, and select **Save**. The checkout pixel connects on its own.

### 4. Start the subscription

Select **Create subscription** and approve the charge in Shopify: one subscription with a spending cap you approve, and you pay only for what you use.

**You should see:** **You're set up** with three ticks: **Shopify permissions**, **App embed** and **Checkout pixel**.

![The Product Metrics app home in Shopify admin for Example Store: a You're set up banner, ticks for Shopify permissions, App embed and Checkout pixel, and the Open dashboard, Test your storefront and Run a tracking test buttons.](https://www.productmetrics.io/docs/images/app/shopify-app.svg)

*Figure: The Product Metrics app in Shopify once setup is done.*

### 5. Finish tracking setup

The rest is the same on every platform: the [setup checklist](https://www.productmetrics.io/docs/using/overview#find-the-next-step) in **Tracking → Complete your tracking setup** opens each step in turn:

- **Consent**: choose **Shopify Customer Privacy**, unless your store shows OneTrust, Cookiebot, Usercentrics or Osano. See [Consent](https://www.productmetrics.io/docs/using/consent).
- **Channels**: connect [Google Ads](https://www.productmetrics.io/docs/channels/google-ads), [Meta](https://www.productmetrics.io/docs/channels/meta) and [ChatGPT Ads (OpenAI)](https://www.productmetrics.io/docs/channels/openai).
- **Google Ads conversion actions**: [create them](https://www.productmetrics.io/docs/using/conversion-actions).
- **Additional costs**: product costs come from Shopify; [add the rest](https://www.productmetrics.io/docs/using/costs).

Step by step in **Tracking**:

**You should see:** the badge next to **Tracking** read **Tracking active**.

### 6. Check it works

In Shopify, the app says **Tracking is live on your store** once it sees storefront activity. Then select **Tracking → Run tracking test** in the app. In Product Metrics, check **Tracking** too:

**You should see:** **Passing**, **Needs attention** or **Listening** per check. More in [Check tracking](https://www.productmetrics.io/docs/using/check-tracking).

## How it works on Shopify

| | On Shopify |
| --- | --- |
| **Install** | Shopify App Store app plus the app embed in your theme; the checkout pixel connects on its own |
| **Order sent** | When Shopify marks it paid |
| **Product cost** | From Shopify; you add shipping, handling, returns and payment fees |
| **Consent** | Shopify Customer Privacy, or OneTrust, Cookiebot, Usercentrics or Osano |
| **Refunds and cancellations** | Shopify reports them; Product Metrics adjusts the conversion it sent |
| **Billing** | One Shopify subscription with a spending cap. Uninstalling the app cancels it and stops tracking |

## What you get on Shopify

Each feature, its channels and the Shopify guide for each:

| Feature | Channels | On this platform |
| --- | --- | --- |
| [Server-side conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) | [Google Ads](https://www.productmetrics.io/docs/tracking/server-side/shopify-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/server-side/shopify-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/server-side/shopify-openai) | Sent once Shopify marks the order paid; the script runs through Shopify's app proxy. |
| [Enhanced Conversions](https://www.productmetrics.io/docs/features/enhanced-conversions) | [Google Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/shopify-openai) | Sent only with ad user data consent in Shopify Customer Privacy or your banner. |
| [Customer lists](https://www.productmetrics.io/docs/features/customer-list) | [Google Ads](https://www.productmetrics.io/docs/tracking/customer-lists/shopify-google-ads) | Six Customer Match lists, filled from your Shopify orders. |
| [POAS and ROAS bidding](https://www.productmetrics.io/docs/features/poas-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/poas/shopify-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/poas/shopify-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/poas/shopify-openai) | Product costs from Shopify, plus your [additional costs](https://www.productmetrics.io/docs/using/costs). |
| [New customer bidding](https://www.productmetrics.io/docs/features/new-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/shopify-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/new-customers/shopify-meta) | Each paid order is new or returning, from whether the customer bought before. |
| [Returning customer bidding](https://www.productmetrics.io/docs/features/returning-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/shopify-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/returning-customers/shopify-meta) | Orders from customers who bought before, as their own conversion. |
| [LTV bidding](https://www.productmetrics.io/docs/features/ltv-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/ltv/shopify-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/ltv/shopify-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/shopify-openai) | Observed value from paid Shopify orders, not a prediction. |

## Troubleshooting

| Message | Fix |
| --- | --- |
| "One step left: save the app embed" | The app embed is off, or the theme wasn't saved. Select **Open theme editor**, turn on **Product Metrics** under **App embeds**, select **Save**, then **Check settings** in the app. |
| "A few permissions are missing" or "New version ready" | Select **Upgrade now** and approve the permissions Shopify lists. |
| "Shopify denied access to the checkout pixel" | Shown under **Checkout tracking needs attention**. Check the app's permissions, then select **Check setup again**. |
| "We couldn't reach Product Metrics tracking" | Wait a moment, then select **Check setup again**. |
| "Product Metrics doesn't recognise this store's link" | Link the store again, then select **Check setup again**. |
| "Contact Product Metrics support" | Select **Contact support**. |
| "This store needs support to finish connecting" | The store is linked to another Product Metrics workspace. Nothing is billed or overwritten. Choose that workspace when you link, disconnect it there first, or select **Contact support**. |
| Fewer conversions than Shopify orders | Orders are sent when Shopify marks them paid. Check that [consent](https://www.productmetrics.io/docs/using/consent) names the banner your store shows: customer data goes only with ad user data, and the click only with ad storage too. |

## FAQ

### Do I need a developer to set it up on Shopify?

No. You install the app from the Shopify App Store, turn on the app embed in your theme editor and start the subscription; the checkout pixel connects on its own. No code and no Google tag.

### How is Product Metrics billed on Shopify?

Through one Shopify subscription with a spending cap you approve, and you pay only for what you use. You don't need a separate Pro subscription. Uninstalling the app cancels it and stops tracking.

### Does it work with my cookie banner?

Yes, with Shopify Customer Privacy, OneTrust, Cookiebot, Usercentrics or Osano. Choose the one your store shows in **Configure consent**; customer data is sent only with ad user data consent.

### Where do product costs come from on Shopify?

From Shopify itself. You add shipping, handling, returns and payment fees once as additional costs in **Tracking**, and profit includes them.
