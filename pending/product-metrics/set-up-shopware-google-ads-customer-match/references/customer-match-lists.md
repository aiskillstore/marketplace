# Shopware Customer Match lists in Google Ads

Source: https://www.productmetrics.io/docs/tracking/customer-lists/shopware-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/customer-lists/shopware-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Create six Customer Match lists in Google Ads and keep them filled from Shopware, from first-time buyers to lapsed customers.

Product Metrics creates six **Customer Match** lists in your Google Ads account and keeps them up to date from your Shopware orders, moving each customer to the right lists after every paid order (for example from **First-time buyers** to **Second-time buyers**). You choose where to use them: Product Metrics never changes your campaigns.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics, with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your Shopware sales channel connected**: Shopware 6.7 (this plugin build supports 6.7.14.0) with PHP 8.2+, an administrator who can upload extensions, Shopware's scheduled tasks and message workers running, and the channel's public HTTPS address under **Sales Channels → your channel → Domains**. You pair one sales channel with a one-time token; it reads **Active** before you link your property. See [Shopware](https://www.productmetrics.io/docs/platforms/shopware).
- **Google Ads connected** to your property, with its conversion actions created and conversion tracking on in Google Ads, and a Google login allowed to manage the account, to accept the Customer Match terms. See [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

## In the app

### 1. Check your Shopware sales channel recognises customers

To check a recent order, ask your assistant: "Are my last five Shopware orders from new or returning customers?"

**You should see:** whether your test order's customer was recognised, as new or returning.

### 2. Set consent

In **Tracking → Configure consent**, leave **Not configured** to use Shopware's own cookie manager, or choose OneTrust, Cookiebot, Usercentrics or Osano if your shop shows one of those. With Shopware's cookie manager, the visitor's choice for **Product Metrics advertising attribution** decides what goes with the order. A customer **joins** a list only when the visitor allowed both **ad user data** and **ad personalisation**. **Leaving** a list never needs consent: Product Metrics always removes a customer who no longer qualifies. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Configure consent** names the banner your Shopware sales channel actually shows.

### 3. Accept the Customer Match terms

Google Ads only accepts customer lists once the account has accepted its Customer Match terms. You do this yourself in the Google Ads web interface.

**You should see:** creating the lists in the next step doesn't fail with a Customer Match terms error.

### 4. Create the lists

Product Metrics creates the six lists ([who joins each](https://www.productmetrics.io/docs/features/customer-list#the-six-lists)), or adopts matching ones it already manages, and tags each with its Google Ads customer type.

In Product Metrics, select **Tracking** → **Google Ads** → **Customer lists** → **Create 6 customer lists**.

**You should see:** all six lists created. If some lists exist already, the button reads **Create 2 missing customer lists** or **Set up 1 customer list**.

### 5. Use the lists in your campaigns

In Google Ads, the lists appear with your other audience lists as **Product Metrics - [list] - [your store]**. For example:

- Exclude **All customers** from a campaign that should only find new customers.
- Use **Lapsed customers** to win back customers who haven't ordered in six months.
- Tell Performance Max who your **High-value customers** are.

Customers join with their next paid order after the lists exist; the lists fill up from there.

**You should see:** the lists show members in Google Ads.

## How it works on Shopware

| | On Shopware |
| --- | --- |
| **Customer** | The Shopware **customer account**, else the guest email, else the phone number |
| **Counted orders** | Paid orders in the paired sales channel |
| **History** | One installation tracks one sales channel, so a customer is counted within the paired sales channel. A guest who later orders with an account starts again under their account. |
| **Sent to Google** | Hashed email and phone and, when all four are known, hashed first and last name with unhashed country and postcode, from the Shopware order: email, plus phone, name, postcode and country from the billing address |
| **High-value threshold** | Profit when every order in the window has known costs, else revenue. Set once 50 customers ordered in the last 365 days; recalculated every 30 days |

Each member stays on a list for 540 days. Everything is hashed with SHA-256 and sent through Google's Data Manager. A privacy request that deletes a customer's data removes them from every list.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Creating the lists fails with a Customer Match terms error** | Accept the Customer Match terms in the Google Ads web interface, then create the lists again. |

## FAQ

### Are my existing Shopware customers added to the lists?

No. Customers join with their next paid order after the lists exist, and the lists fill up from there.

### Does Shopware's own cookie manager work for consent?

Yes. Leave **Configure consent** on **Not configured**, and the visitor's choice for **Product Metrics advertising attribution** decides what goes with the order. OneTrust, Cookiebot, Usercentrics and Osano work too.

### How are customers counted across Shopware sales channels?

One installation tracks one sales channel, so a customer is counted within the paired sales channel only.

### Can I use these customer lists in Meta?

No. Customer lists are Google Ads only: Product Metrics doesn't create Meta Custom Audiences.
