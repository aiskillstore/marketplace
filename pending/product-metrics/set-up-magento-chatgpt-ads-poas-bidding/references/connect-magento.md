# Magento server-side tracking and profit bidding (POAS)

Source: https://www.productmetrics.io/docs/platforms/magento (the same page as Markdown: https://www.productmetrics.io/docs/platforms/magento.md)

**For the agent:** all conversion actions by agents are secondary. Steps on this page that make an action primary, or select the conversion a campaign or ad set bids or optimises on, are the person's: give them the exact clicks, wait until they say it is done, then read the state back.

Have your developer install the Product Metrics Magento module, get server-side conversion tracking live in Google Ads, Meta and ChatGPT Ads, and bid on profit, new customers or lifetime value.

The Product Metrics **module** reads every **paid order** from Magento, with its product costs and customer, and serves tracking from your own domain. Product Metrics adds **profit**, **new or returning customer** and **lifetime value**, and sends it server-side to each ad channel. Works with Magento 2.4, Magento 2.0 and Magento 1.9 / OpenMage.

- **Install:** a module on your server (Composer or ZIP): a developer installs it once. Everything else you do yourself, in Product Metrics and Magento Admin.
- **Product cost:** the cost on each order item. You add shipping, handling, returns and payment fees.
- **Consent banner:** a supported banner (OneTrust, Cookiebot, Usercentrics or Osano), or your own banner connected with `ProductMetrics.setConsent()`.

## Prerequisites

- Magento administrator access, editor or admin access to your [workspace](https://www.productmetrics.io/docs/using/create-a-workspace), and Magento cron running: the module sends order changes every two minutes through cron.
- A developer with terminal access and Composer (recommended for Magento 2.4), or private file access for the ZIP. They need your exact Magento and PHP release, the installation directory and the account PHP and cron run as. On Magento 2, they check PHP has enough memory first: Adobe recommends 1G for compilation.
- For a live store, a backup and a maintenance window. For the test order: a linked property, consent set up, cron running and your payment provider's test mode.
- Your public HTTPS shop address and the **store-view ID** to track. Each store view connects on its own.

## In the app

### 1. Create the module configuration

1. **Find the store-view ID.** In Magento Admin, open **Stores → All Stores** (Magento 1.9 / OpenMage: **System → Manage Stores**) and select your store view in the **Store View** column (for example **Default Store View**), not the website or store. The number after `/store_id/` in the address is the ID. On Magento 2.4, once the module is installed, **Magento Admin → Product Metrics** also shows each store view's ID and public address. Note the public HTTPS shop address too, not the Admin address.
2. **Create the configuration.** In Product Metrics, open **Ecommerce platforms → Connect Magento** and fill in **Magento version** (**Magento 1.9 / OpenMage** or **Magento 2**), **Store URL** and **Store view ID**. Leave **Advanced custom checkout mapping** closed unless your shop has a custom checkout. Select **Create module configuration**.
3. **Download the file.** Select **Download 1.json** (the number is your store-view ID). It holds a private key: share it with your developer privately, never in a screenshot or shared chat.

**You should see:** the configuration file downloaded.

### 2. Your developer installs the module

Your developer installs the module on your server with Composer or as a ZIP, adds the configuration file and makes sure Magento cron runs. Magento Admin can't do this. Product Metrics shows the exact commands, filled in for your release, in its Magento setup guide; the same steps are under [For your developer](#for-your-developer).

On Magento 2.4 you can import the file yourself once the module is installed: **Magento Admin → Product Metrics**, choose the **Store view**, choose the file under **Private JSON configuration**, select **Import configuration**.

**You should see:** after an import in Magento Admin, **Configuration saved privately**.

### 3. Verify the module

Once the module, configuration file and cron are in place, select **Verify installed module** in Product Metrics. If it says **Module verified. Tracking configuration is still publishing.**, wait and select **Check publication**, then **Finish Magento setup** if it appears.

**You should see:** the connection **Active** under **Manage Magento → Connection details and removal**, with the same desired and active revision numbers.

### 4. Send the orders to a property

Under **Manage Magento**, choose the property that should receive the store view's orders.

### 5. Finish tracking setup

The [setup checklist](https://www.productmetrics.io/docs/using/overview#find-the-next-step) in **Tracking** opens each of these in turn:

- **Consent**: choose your banner. See [Consent](https://www.productmetrics.io/docs/using/consent).
- **Channels**: connect [Google Ads](https://www.productmetrics.io/docs/channels/google-ads) (with Data Manager access), [Meta](https://www.productmetrics.io/docs/channels/meta) and [ChatGPT Ads (OpenAI)](https://www.productmetrics.io/docs/channels/openai).
- **Google Ads conversion actions**: [create them](https://www.productmetrics.io/docs/using/conversion-actions).
- **Additional costs**: product costs come from the Magento order; [add the rest](https://www.productmetrics.io/docs/using/costs).

Step by step in **Tracking**:

**You should see:** the badge next to **Tracking** read **Tracking active**.

### 6. Check it works

Place a paid test order in the connected store view and allow a few minutes for cron. Then follow [Check tracking](https://www.productmetrics.io/docs/using/check-tracking), or ask your assistant whether the order arrived.

**You should see:** your test order arrive. If it doesn't, send the order number and store-view ID to support.

## How it works on Magento

| | On Magento |
| --- | --- |
| **Install** | A developer: Composer or ZIP, Magento cron, one configuration file per store view |
| **Product cost** | The cost on each order item (order currency = base currency); you add the rest |
| **Consent** | OneTrust, Cookiebot, Usercentrics or Osano, or your own banner (your developer connects it) |
| **Customer identity** | Per store view: customer account or guest email |
| **Refunds** | Refunded orders are sent without a profit figure |
| **Several store views** | One module installation; one configuration and file per store view |
| **Remove** | **Manage Magento → Remove connection**; the developer disables and removes the module and moves the old file out. Reinstall with a new file, never the old one |

## What you get on Magento

Each feature, its channels and the Magento guide for each:

| Feature | Channels | On this platform |
| --- | --- | --- |
| [Server-side conversion tracking](https://www.productmetrics.io/docs/features/ad-blocker-proof-tracking) | [Google Ads](https://www.productmetrics.io/docs/tracking/server-side/magento-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/server-side/magento-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/server-side/magento-openai) | The module serves the script and collector on random paths of your domain. |
| [Enhanced Conversions](https://www.productmetrics.io/docs/features/enhanced-conversions) | [Google Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/magento-google-ads) · [Meta](https://www.productmetrics.io/docs/tracking/enhanced-conversions/magento-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/tracking/enhanced-conversions/magento-openai) | Logged-in customer details and guest email, only with ad user data consent. |
| [Customer lists](https://www.productmetrics.io/docs/features/customer-list) | [Google Ads](https://www.productmetrics.io/docs/tracking/customer-lists/magento-google-ads) | Six Customer Match lists, filled from your Magento orders. |
| [POAS and ROAS bidding](https://www.productmetrics.io/docs/features/poas-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/poas/magento-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/poas/magento-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/poas/magento-openai) | Cost per order item when order and base currency match; refunds go without profit. |
| [New customer bidding](https://www.productmetrics.io/docs/features/new-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/new-customers/magento-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/new-customers/magento-meta) | Per store view, by customer account or guest email; cancelled orders don't count. |
| [Returning customer bidding](https://www.productmetrics.io/docs/features/returning-customer-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/returning-customers/magento-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/returning-customers/magento-meta) | Same matching as new customers: per store view. |
| [LTV bidding](https://www.productmetrics.io/docs/features/ltv-bidding) | [Google Ads](https://www.productmetrics.io/docs/bidding/ltv/magento-google-ads) · [Meta](https://www.productmetrics.io/docs/bidding/ltv/magento-meta) · [ChatGPT Ads](https://www.productmetrics.io/docs/bidding/ltv/magento-openai) | Observed value from paid orders, not a prediction. |

## For your developer

Use **one** method: Composer or ZIP, never both. Run everything from the Magento root, as the account that runs PHP and cron.

| Magento release | Package | Module |
| --- | --- | --- |
| Magento 2.4 (tested on 2.4.7) | `productmetrics/magento2` | `ProductMetrics_Magento` |
| Magento 2.0 (tested on 2.0.18) | `productmetrics/magento20` | `ProductMetrics_Magento20` |
| Magento 1.9 / OpenMage (tested on 1.9.4.5) | `productmetrics/magento1` | `ProductMetrics_MagentoIntegration` |

Release not listed? Contact Product Metrics support before installing.

### Install the module

**Composer (Magento 2.4):**

```bash
cd /path/to/magento
composer config repositories.productmetrics composer https://app.productmetrics.io/api/magento-composer
composer require productmetrics/magento2:0.5.11 --update-no-dev
composer show productmetrics/magento2
```

**ZIP:**

```bash
# Download for Magento 2.4 / 2.0 / 1.9 / OpenMage from the
# Product Metrics setup dialog: productmetrics-magento2.zip,
# productmetrics-magento20.zip or productmetrics-magento1.zip
unzip /private/downloads/productmetrics-magento2.zip
```

Use the exact version the setup guide shows. Composer installs under `vendor/productmetrics/magento2`; don't add a copy under `app/code`. Magento 2.0 and 1.9 / OpenMage need extra Composer steps the guide lists. The ZIP lands in `app/code/ProductMetrics/Magento` (2.4), `app/code/ProductMetrics/Magento20` (2.0), or `app/code/local/ProductMetrics/MagentoIntegration` with `app/etc/modules/ProductMetrics_MagentoIntegration.xml` (1.9 / OpenMage).

### Deploy (Magento 2)

On 2.0 use `ProductMetrics_Magento20`, and before compiling move any existing `var/di` folder to a private backup: Magento 2.0 refuses to compile while it is there. On 1.9 / OpenMage, skip this and flush the cache in **Magento Admin → System → Cache Management → Flush Magento Cache** instead.

```bash
php bin/magento module:enable ProductMetrics_Magento
php bin/magento setup:upgrade
php bin/magento setup:di:compile
php bin/magento cache:clean
```

Stop at the first error. Adobe recommends a PHP memory limit of 1G for compilation; the CLI limit can differ from the web one.

### Add the configuration file

Skip this if the owner imported the file in Magento Admin. Replace `1` with the store-view ID and `www-data` with the PHP and cron account:

```bash
mkdir -p var/productmetrics/installations
cp /private/downloads/1.json var/productmetrics/installations/1.json
chown www-data:www-data var/productmetrics/installations var/productmetrics/installations/1.json
chmod 0700 var/productmetrics/installations
chmod 0600 var/productmetrics/installations/1.json
stat -c "%a %U:%G %n" var/productmetrics/installations var/productmetrics/installations/1.json
```

Expect `700` for the folder and `600` for the file. A file other users can read is rejected. Each store view needs its own file.

### Run cron

Product Metrics runs a job every two minutes, as the same account and PHP version that can read the configuration file.

| Release | Schedule cron |
| --- | --- |
| Magento 2.4 | `php bin/magento cron:install` |
| Magento 2.0 | No `cron:install`: add `* * * * * cd /path/to/magento && /path/to/php bin/magento cron:run` to that account's crontab |
| Magento 1.9 / OpenMage | `* * * * * cd /path/to/magento && /path/to/php cron.php` |

Then check `cron_schedule` for successful runs of the Product Metrics job; a single manual run doesn't prove the schedule works.

### Consent with your own banner

With OneTrust, Cookiebot, Usercentrics or Osano nothing is needed. With any other banner, call `ProductMetrics.setConsent()` after `ProductMetrics.whenReady()` with the visitor's `analytics_storage`, `ad_storage`, `ad_user_data` and `ad_personalization` choices, and again when they withdraw. Anything not set stays denied. Magento's cookie restriction notice does not grant consent.

### Content Security Policy

If the shop sets one, allow the module's script path on your own domain.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Verify installed module fails** | Check HTTPS reachability, the store-view ID, and that the package matches your Magento release. Your developer checks that the configuration file belongs to the PHP and cron account and only that account can read it. Then verify again. |
| **"Allowed memory size exhausted"** | Your developer reruns that one command with a higher memory limit (for example 1G), once the server has the memory. |
| **"crontab: not found"** | The server has no cron scheduler. Your developer or host has to enable one; without cron, order changes don't reach Product Metrics. |
| **The Product Metrics menu is missing in Magento Admin** | The module isn't enabled yet, or your admin role can't see it. Ask your developer to check the install steps, and check your admin permissions. |
| **Import configuration reports folder permissions or an existing configuration** | Your developer resolves it on the server first; then import again. |

## FAQ

### Do I need a developer for Magento?

Yes, once. The module is installed on your server with Composer or as a ZIP, which Magento Admin can't do. Everything after that you do yourself, in Product Metrics and Magento Admin.

### Which Magento versions does Product Metrics support?

Magento 2.4, Magento 2.0 and Magento 1.9 / OpenMage. If your release isn't one of these, contact Product Metrics support before installing.

### Does it work with my cookie banner?

OneTrust, Cookiebot, Usercentrics and Osano work without extra work. Any other banner needs your developer to connect it with `ProductMetrics.setConsent()`; Magento's cookie restriction notice does not grant consent.

### Where do product costs come from on Magento?

From the cost on each Magento order item, when the order currency matches the base currency. You add shipping, handling, returns and payment fees as [additional costs](https://www.productmetrics.io/docs/using/costs).
