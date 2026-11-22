# Magento Customer Match lists in Google Ads

Source: https://www.productmetrics.io/docs/tracking/customer-lists/magento-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/customer-lists/magento-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Create six Customer Match lists in Google Ads and keep them filled from Magento, from first-time buyers to lapsed customers.

Product Metrics creates six **Customer Match** lists in your Google Ads account and keeps them up to date from your Magento orders, moving each customer to the right lists after every paid order (for example from **First-time buyers** to **Second-time buyers**). You choose where to use them: Product Metrics never changes your campaigns.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics, with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your Magento store view connected**: Magento 2.4, 2.0 or 1.9 / OpenMage, Magento Admin access, the public HTTPS shop address and the **store-view ID**, and a **developer** with access to your server who installs the Product Metrics module (Composer or ZIP), adds the store view's private configuration file and keeps Magento cron running. The connection reads **Active** before you link your property. See [Magento](https://www.productmetrics.io/docs/platforms/magento).
- **Google Ads connected** to your property, with its conversion actions created and conversion tracking on in Google Ads, and a Google login allowed to manage the account, to accept the Customer Match terms. See [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

## In the app

### 1. Check your Magento store view recognises customers

> **Note:** Running several store views? Each one is its own connection with its own customers. Create the lists for each property its store view feeds.

To check a recent order, ask your assistant: "Are my last five Magento orders from new or returning customers?"

**You should see:** whether your test order's customer was recognised, as new or returning.

### 2. Set consent

In **Tracking → Configure consent**, choose the banner your shop shows: OneTrust, Cookiebot, Usercentrics or Osano. With another banner, your developer passes the visitor's choices to Product Metrics. A customer **joins** a list only when the visitor allowed both **ad user data** and **ad personalisation**. **Leaving** a list never needs consent: Product Metrics always removes a customer who no longer qualifies. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

> **Warning:** Magento's cookie restriction notice grants nothing. Without a supported banner or your developer passing the choices, visitors count as not having consented, and their customers get no list membership.

**You should see:** **Configure consent** names the banner your Magento store view actually shows.

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

## How it works on Magento

| | On Magento |
| --- | --- |
| **Customer** | The Magento **customer account**, else the guest email, else the phone number |
| **Counted orders** | Paid Magento orders; cancelled orders don't count |
| **History** | Each store view is its own connection, so a customer is counted per store view: the same person buying in two store views counts as two customers. A guest who later orders with an account starts again under their account. |
| **Sent to Google** | Hashed email and phone and, when all four are known, hashed first and last name with unhashed country and postcode, from the Magento order, plus the logged-in customer's details and guest email the module passes on |
| **High-value threshold** | Profit when every order in the window has known costs, else revenue. Set once 50 customers ordered in the last 365 days; recalculated every 30 days |

Each member stays on a list for 540 days. Everything is hashed with SHA-256 and sent through Google's Data Manager. A privacy request that deletes a customer's data removes them from every list.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Creating the lists fails with a Customer Match terms error** | Accept the Customer Match terms in the Google Ads web interface, then create the lists again. |

## FAQ

### Are my existing Magento customers added to the lists?

No. Customers join with their next paid order after the lists exist, and the lists fill up from there.

### Does Magento's cookie restriction notice count as consent?

No. Use OneTrust, Cookiebot, Usercentrics or Osano, or have your developer pass the visitor's choices to Product Metrics. Otherwise visitors count as not having consented and their customers get no list membership.

### How are customers counted across Magento store views?

Per store view: each store view is its own connection, so the same person buying in two store views counts as two customers. Create the lists for each property a store view feeds.

### Do cancelled Magento orders count?

No. Only paid Magento orders count towards a customer's orders.
