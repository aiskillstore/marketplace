# Google Ads server-side conversion tracking

Source: https://www.productmetrics.io/docs/channels/google-ads (the same page as Markdown: https://www.productmetrics.io/docs/channels/google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Connect Google Ads and Merchant Center, then send every paid order server-side as eight conversion actions: revenue, profit (POAS), new and returning customers and lifetime value.

Product Metrics sends each paid order server-side to Google Ads as **eight conversion actions**, all **secondary** until you make one primary (Full Signal Tracking, included in Pro).

- **You need:** your [store connected](https://www.productmetrics.io/docs/platforms/overview), and a Merchant Center account linked to your Google Ads account in Google.
- **In the app:** **Ecommerce platforms** → your store → **Connect Google Ads**.

## Prerequisites

- Workspace admin, and your [store connected](https://www.productmetrics.io/docs/platforms/overview).
- A Google login with access to the Google Ads account, and a **Merchant Center** account linked to it in Google.
  

## In the app

### 1. Connect Google Ads

Connect Google Ads in onboarding, on the **Connect Google Ads and Merchant Center** step, or later on **Integrations**: select **Continue as** your Google account, and tick **Google Ads** on Google's screen. Pick the **client account** that runs your campaigns, not a manager account.

Connecting it creates your **property**: one Google Ads account in your workspace, with the store assigned to it.

**You should see:** your Google Ads account on **Integrations**, under **Required**. The same Google approval covers Merchant Center.

### 2. Grant Data Manager access

If **Grant Data Manager access** shows, select it and allow access on Google's screen.

**You should see:** **Data Manager access granted**.

### 3. Finish the setup

Next, in this order (platform differences are on your [platform page](https://www.productmetrics.io/docs/platforms/overview)):

1. [Connect Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) and apply the feed setup.
2. [Choose your consent banner](https://www.productmetrics.io/docs/using/consent) in **Tracking → Configure consent**.
3. [Create the conversion actions](https://www.productmetrics.io/docs/using/conversion-actions) in **Tracking → Create Google Ads conversions → Create 8 conversion actions**.
4. [Activate your additional costs](https://www.productmetrics.io/docs/using/costs), or the profit actions stay empty.

Step by step in **Tracking**:

**You should see:** **Conversion actions** read **Tracking ready**; **Setting up** is normal for about 15 minutes.

### 4. Accept the customer data terms

Enhanced Conversions needs Google's customer data terms accepted in your Google Ads account. In **Tracking → Google Ads → Enhanced conversions**, select **Open Google Ads settings**, accept the terms in Google Ads, then select **Re-check**.

**You should see:** **Customer data terms** read **Accepted**. More on this check: [Check tracking](https://www.productmetrics.io/docs/using/check-tracking#3-google-ads).

### 5. Check it works

Open **Tracking**, then **Goals → Conversions** in Google Ads.

**You should see:** the badge read **Tracking active**, and the eight **Product Metrics** actions as secondary under **Goals → Conversions** in Google Ads. **Home** shows **Collecting** at first, then compares them with your current actions 14 days after the first order.

## Customer lists

Product Metrics can also create six Customer Match lists in Google Ads (**Tracking → Google Ads → Customer lists → Create 6 customer lists**) and keep them filled from your orders. See [Customer lists](https://www.productmetrics.io/docs/features/customer-list).

## Other ways to connect

You can also connect through **Product Metrics' manager account**. It invites your Google Ads account, with access to that one account only. Accept the invite in Google Ads under **Admin → Access and security → Managers**. Every click is under **Connect through our manager account instead** in [step 1](#1-connect-google-ads).

If you disconnect Google Ads, the property stays, but its reports and feeds stop updating.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| "Only a manager account is linked" | Manager (MCC) accounts can't receive conversions. Connect the **client account** that runs your campaigns. |
| Connecting the account fails | The message says what's missing: an invite not accepted yet, or a Google sign-in to redo. Do that, then connect again. |
| "Google Ads not connected" or "Google access was revoked" | Select **Reconnect Google Ads** (or run step 1 again). Conversions and waiting refunds resume after. |
| "Google access is missing permissions" | The grant lacks Google Ads or Merchant Center. Run step 1 again and tick both. |
| Some conversion actions were not created | If the message names actions this workspace does not manage, another workspace on this Google Ads account created them: contact support. If it says to try again in a few minutes, it was a temporary Google Ads error: run the step again later. |
| Fewer conversions than store orders | Orders are sent once paid, and follow [consent](https://www.productmetrics.io/docs/using/consent): an order isn't sent if consent is withdrawn after checkout. |

![A banner at the top of Home: The Google Ads connection needs attention, with the Reconnect Google Ads button.](https://www.productmetrics.io/docs/images/app/screens/reconnect-google-01.webp)

*Figure: When Google access needs attention, a banner with Reconnect Google Ads shows at the top of every page.*

## FAQ

### Do I need Merchant Center for Google Ads?

Yes. Merchant Center is required for Google Ads and is part of its setup, not a separate channel. Link it to your Google Ads account in Google, then [connect it](https://www.productmetrics.io/docs/using/merchant-center) right after Google Ads.

### Will purchases be counted twice?

Not while one purchase action is primary. The eight actions start as secondary; when you make one primary, set your old purchase action to secondary, and never make Revenue and Profit primary together.

### Should I remove my Google tag or old conversion actions?

No. Product Metrics creates its own actions next to them as secondary, so nothing changes until you choose. **Home** compares the two 14 days after the first order.

### What happens when an order is refunded?

A refund or cancellation adjusts the Google Ads conversion. Meta and ChatGPT Ads events are not revised.
