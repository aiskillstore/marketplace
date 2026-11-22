# Shopware ChatGPT Ads server-side tracking (OpenAI Conversions API)

Source: https://www.productmetrics.io/docs/tracking/server-side/shopware-openai (the same page as Markdown: https://www.productmetrics.io/docs/tracking/server-side/shopware-openai.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Send every paid Shopware order to your ChatGPT Ads pixel from the server, through the OpenAI Conversions API.

Every paid Shopware order is confirmed from your store's own order data and sent [from Product Metrics' server](https://www.productmetrics.io/docs/concepts/server-side-tracking) to your **ChatGPT Ads pixel** as `order_created`. This is [server-side, adblocker-proof conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking).

## Prerequisites

- **[Editor or admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** on the property in Product Metrics, with Pro (Full Signal Tracking).
- **Your Shopware sales channel connected**: Shopware 6.7 (this plugin build supports 6.7.14.0) with PHP 8.2+, an administrator who can upload extensions, Shopware's scheduled tasks and message workers running, and the channel's public HTTPS address under **Sales Channels → your channel → Domains**. You pair one sales channel with a one-time token; it reads **Active** before you link your property. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).
- **Access to ChatGPT Ads Manager → Conversions**, to copy your Pixel ID and create a Conversions API key.

## In the app

### 1. Connect your Shopware store and ChatGPT Ads

**Store:** install the Product Metrics plugin and pair your sales channel with a one-time token and link it to your property. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).

**ChatGPT Ads:** in Ads Manager → **Conversions**, copy your **Pixel ID** and create a Conversions API key, then add both under **Tracking → OpenAI Conversions API → Connect OpenAI**. See [ChatGPT Ads](https://www.productmetrics.io/docs/channels/openai).

**You should see:** in Product Metrics, the store reads **Active** after **Verify connection**; the app says **OpenAI accepted the test event**.

### 2. Set your consent banner

On Shopware, leave **Tracking → Configure consent** on **Not configured** to use Shopware's own cookie manager, unless your shop shows OneTrust, Cookiebot, Usercentrics or Osano. ChatGPT Ads has no consent mode: an event is only sent with marketing consent (ad user data). Without ad personalisation consent, the event is sent marked as opted out. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Tracking → Configure consent** names the banner your store shows.

### 3. Check it works

**Place a paid test order** with marketing cookies accepted through the paired sales channel with your payment provider's test mode, and give Shopware a few minutes to sync it.

**You should see:** your cookie banner lists **Product Metrics measurement** (with Shopware's own cookie manager). More checks: [Check tracking works](https://www.productmetrics.io/docs/using/check-tracking).

## Events sent

| On Shopware | Sent to ChatGPT Ads as | Carries |
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
| **Nothing reaches ChatGPT Ads** | Check that **Tracking → Configure consent** names the banner your store shows, or reads **Not configured** if it uses Shopware's own cookie manager. |

## FAQ

### Which Shopware sales channel is sent to ChatGPT Ads?

Only the one paired with the extension: one installation tracks one sales channel, and its paid orders go to ChatGPT Ads as `order_created`.

### Can I keep the OpenAI Pixel on Shopware?

Yes. OpenAI deduplicates on Pixel ID, event name and event ID, and keeps the first event it receives. `order_created` uses the order transaction ID, so it deduplicates on its own.

### Can I bid on profit in ChatGPT Ads?

Yes. POAS and LTV bidding work on ChatGPT Ads: see [POAS bidding on Shopware in ChatGPT Ads](https://www.productmetrics.io/docs/bidding/poas/shopware-openai).

### Does ChatGPT Ads get new and returning customers?

Not yet. ChatGPT Ads gets revenue, profit (POAS) and LTV through the OpenAI Conversions API; new and returning customer bidding runs in Google Ads and Meta.
