# Magento ChatGPT Ads server-side tracking (OpenAI Conversions API)

Source: https://www.productmetrics.io/docs/tracking/server-side/magento-openai (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/magento-openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every paid Magento order to your ChatGPT Ads pixel from the server, through the OpenAI Conversions API.

Every paid Magento order is confirmed from your store's own order data and sent [from Product Metrics' server](https://www.productmetrics.io/docs/concepts/server-side-tracking) to your **ChatGPT Ads pixel** as `order_created`. This is [server-side, adblocker-proof conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking).

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your Magento store view connected**: Magento 2.4, 2.0 or 1.9 / OpenMage, Magento Admin access, the public HTTPS shop address and the **store-view ID**, and a **developer** with access to your server who installs the Product Metrics module (Composer or ZIP), adds the store view's private configuration file and keeps Magento cron running. The connection reads **Active** before you link your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Connect your Magento store and ChatGPT Ads

**Store:** create the module configuration under **Ecommerce platforms → Connect Magento**, have your developer install the module, then verify the store view and link it to your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).

**ChatGPT Ads:** in Ads Manager → **Conversions**, copy your **Pixel ID** and create a Conversions API key, then add both under **Tracking → OpenAI Conversions API → Connect OpenAI**. See [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai).

**You should see:** under **Manage Magento**, the connection is **Active** and your property is linked; the app says **OpenAI accepted the test event**.

### 2. Set your consent banner

Magento's cookie restriction notice does not grant consent. Choose OneTrust, Cookiebot, Usercentrics or Osano under **Tracking → Configure consent**, or have your developer pass the visitor's choices to Product Metrics.

ChatGPT Ads has no consent mode: an event is only sent with marketing consent (ad user data). Without ad personalisation consent, the event is sent marked as opted out. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Tracking → Configure consent** names the banner your store shows.

### 3. Check it works

**Place a paid test order** with marketing cookies accepted in the connected store view with your payment provider's test mode, and allow a few minutes for cron.

**You should see:** under **Manage Magento**, the desired and active revision numbers are the same, and the order appears for the linked property. More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## Events sent

| On Magento | Sent to ChatGPT Ads as | Carries |
| --- | --- | --- |
| Paid order | `order_created` | Revenue, products, the transaction ID as `id` |
| Add to cart | `items_added` | Products, and the value when your storefront reports one |
| Checkout started | `checkout_started` | Products, and the value when your storefront reports one |
| Ad click from ChatGPT | `oppref` (from the `__oppref` cookie) | Needs ad storage consent |
| Browser | `obref` (from the `__obref` cookie), IP address, user agent | `obref` needs ad storage consent |

ChatGPT Ads accepts events up to 7 days old, so past orders are not imported, and later refunds don't revise sent events.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Orders are missing in ChatGPT Ads** | Check that **Tracking → Configure consent** names the banner your store actually shows: Product Metrics sends an order only with the consent this page lists. See [Consent](https://www.productmetrics.io/docs/concepts/consent). |

## FAQ

### Do I need a developer for ChatGPT Ads on Magento?

Once, to install the Product Metrics module and make sure Magento cron runs. The module then sends order changes every two minutes.

### Can I keep the OpenAI Pixel on Magento?

Yes. OpenAI deduplicates on Pixel ID, event name and event ID, and keeps the first event it receives. `order_created` uses the order transaction ID, so it deduplicates on its own.

### Can I bid on profit in ChatGPT Ads?

Yes. POAS and LTV bidding work on ChatGPT Ads: see [POAS bidding on Magento in ChatGPT Ads](https://www.productmetrics.io/docs/bidding/poas/magento-openai).

### Does ChatGPT Ads get new and returning customers?

Not yet. ChatGPT Ads gets revenue, profit (POAS) and LTV through the OpenAI Conversions API; new and returning customer bidding runs in Google Ads and Meta.
