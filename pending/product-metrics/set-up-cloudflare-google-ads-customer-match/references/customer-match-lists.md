# Customer Match lists in Google Ads on any website with Cloudflare

Source: https://www.productmetrics.io/docs/tracking/customer-lists/cloudflare-google-ads (the same page as Markdown: https://www.productmetrics.io/docs/tracking/customer-lists/cloudflare-google-ads.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Create six Customer Match lists in Google Ads and keep them filled from your website, from first-time buyers to lapsed customers.

Product Metrics creates six **Customer Match** lists in your Google Ads account and keeps them up to date from your website orders, moving each customer to the right lists after every purchase (for example from **First-time buyers** to **Second-time buyers**). You choose where to use them: Product Metrics never changes your campaigns.

## Prerequisites

- **[Workspace admin](https://www.productmetrics.io/docs/using/team#1-choose-a-role)** in Product Metrics, with Pro (Full Signal Tracking). Google Ads needs [Merchant Center](https://www.productmetrics.io/docs/using/merchant-center) connected.
- **Your website on Cloudflare Tracking**: its domain on Cloudflare DNS with the record proxied (the orange cloud), a workspace admin who signs in to Cloudflare and approves Product Metrics (that is the whole setup), and the website linked to your property. See [Any website (Cloudflare)](https://www.productmetrics.io/docs/platforms/cloudflare).
- **Google Ads connected** to your property, with its conversion actions created and conversion tracking on in Google Ads, and a Google login allowed to manage the account, to accept the Customer Match terms. See [Google Ads](https://www.productmetrics.io/docs/channels/google-ads).

## In the app

### 1. Check your website recognises customers

Place a test order.

> **Note:** Want earlier orders to count? **Custom Store / Webhook Integration** lets a developer send every order from your backend, including the customer's order history.

**You should see:** your test order as the last purchase received.

### 2. Set consent

In **Tracking → Configure consent**, choose the banner your website shows: OneTrust, Cookiebot, Usercentrics or Osano. A customer **joins** a list only when the visitor allowed both **ad user data** and **ad personalisation**. **Leaving** a list never needs consent: Product Metrics always removes a customer who no longer qualifies. See [Consent](https://www.productmetrics.io/docs/concepts/consent).

**You should see:** **Configure consent** names the banner your website actually shows.

### 3. Accept the Customer Match terms

Google Ads only accepts customer lists once the account has accepted its Customer Match terms. You do this yourself in the Google Ads web interface.

**You should see:** creating the lists in the next step doesn't fail with a Customer Match terms error.

### 4. Create the lists

Product Metrics creates the six lists ([who joins each](https://www.productmetrics.io/docs/features/customer-list#the-six-lists)), or adopts matching ones it already manages, and tags each with its Google Ads customer type.

In Product Metrics, select **Tracking** → **Google Ads** → **Customer lists** → **Create 6 customer lists**.

**You should see:** all six lists created. If some lists exist already, the button reads **Create 2 missing customer lists** or **Set up 1 customer list**.

### 5. Use the lists in your campaigns

In Google Ads, the lists appear with your other audience lists as **Product Metrics - [list] - [your website]**. For example:

- Exclude **All customers** from a campaign that should only find new customers.
- Use **Lapsed customers** to win back customers who haven't ordered in six months.
- Tell Performance Max who your **High-value customers** are.

Customers join with their next purchase after the lists exist; the lists fill up from there.

**You should see:** the lists show members in Google Ads.

## How it works on a website

| | On a website |
| --- | --- |
| **Customer** | The email address your purchase page passes to Product Metrics |
| **Counted orders** | Purchases your order confirmation page reports |
| **History** | The page reports no order history, so a customer's history starts with the first purchase Product Metrics receives from your website. Refunds and cancellations count. |
| **Sent to Google** | Hashed email and phone and, when all four are known, hashed first and last name with unhashed country and postcode, from what your purchase page passes to Product Metrics |
| **High-value threshold** | Profit when every order in the window has known costs, else revenue. Set once 50 customers ordered in the last 365 days; recalculated every 30 days |

Each member stays on a list for 540 days. Everything is hashed with SHA-256 and sent through Google's Data Manager. A privacy request that deletes a customer's data removes them from every list.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Creating the lists fails with a Customer Match terms error** | Accept the Customer Match terms in the Google Ads web interface, then create the lists again. |

## FAQ

### Are refunds and cancellations reflected in the lists?

Yes. Product Metrics tracks refunds and cancellations on your website, and a refund removes the customer from the list.

### Do my customers' earlier orders count?

No. A customer's history starts with the first purchase Product Metrics receives from your website. To include earlier orders, a developer can send the customer's order history through **Custom Store / Webhook Integration**.

### Which cookie banners work with website customer lists?

OneTrust, Cookiebot, Usercentrics or Osano. A customer joins a list only when the visitor allowed both ad user data and ad personalisation.

### Can I use these customer lists in Meta?

No. Customer lists are Google Ads only: Product Metrics doesn't create Meta Custom Audiences.
