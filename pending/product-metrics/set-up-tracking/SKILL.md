---
name: set-up-tracking
description: >-
  Set up Product Metrics server-side conversion tracking end to end for a store owner, with the productmetrics
  CLI or the Product Metrics MCP server (search and execute tools): sign in, create or pick the
  workspace, connect the store (Shopify, WooCommerce, Shopware, Lightspeed, Magento or any website
  through Cloudflare Tracking), connect Google Ads and Meta, create the conversion actions, set
  consent and additional costs, and confirm the first purchase arrives. Use it when someone asks to
  "set up Product Metrics", "install tracking", "connect my store", "start sending profit to Google
  Ads", or asks what is left to set up. Browser steps (Google consent, Shopify approval, checkout,
  Cloudflare sign-in) are handed to the person as a URL.
---

# Set up Product Metrics tracking

You take a store owner from nothing to **tracking active**: their paid orders reach Google Ads (and Meta, if they use it) server-side, with revenue, profit, new or returning customer and lifetime value. You drive the steps that have an API; the person does the steps that need them in a browser or in their store admin. Docs: https://www.productmetrics.io/docs/quickstart.

Write for a store owner, not a developer. Short sentences. Say what you did, what they need to do, and what comes next.

## 0. Pick the interface

Use whichever is available, in this order:

1. **The `productmetrics` CLI.** Check with `productmetrics status --json`. Read `productmetrics help agents` once. Pass `--json` to every command.
2. **The Product Metrics MCP server** (`https://www.productmetrics.io/mcp`), through its `search` and `execute` tools. `search` reads the API spec; `execute` runs `codemode.request(...)` calls. Never guess a path or body: search first.

Every API operation has an id like `stores.connect`. In the CLI it is `productmetrics stores connect`; in MCP it is the operation with that `operationId`. Before a command you have not used, run `productmetrics <group> <command> --help --json` (or `search` for the operation) for its exact flags.

If neither is available, send the person to https://www.productmetrics.io/docs/cli/overview or https://www.productmetrics.io/docs/mcp/connect and stop.

## Rules

- **All conversion actions by agents are secondary.** Product Metrics creates its actions as secondary and leaves existing ones as they are. What the account bids on is the person's choice: making an action primary (and the old purchase action secondary) in Google Ads (**Goals → Conversions**, or a campaign-specific goal), and picking the conversion a Meta ad set or ChatGPT Ads campaign optimises on, is their step by every route, also when they ask you to do it. Tell them exactly what to click, wait until they say it is done, then read it back with `productmetrics google-ads get-conversion-actions --property-id <property_id> --json` (`goal_status`). The bidding choice belongs to the advertiser, and one primary purchase action keeps bidding right and counts every purchase once.
- **Discover, never guess.** Ids (`company_id`, `property_id`, installation and scope ids) come from earlier results. Never invent one.
- **Writes:** pass `--auto-idempotency-key` (MCP: `idempotencyKey: crypto.randomUUID()`) where the command's `--help` lists it: `companies create`, `stores connect` and `tracking update-margin-policy`. On a failed write, retry with the key the error hint names, so nothing is created twice. Other writes take no key (the CLI refuses one): after a failure, read to check whether the change happened before retrying.
- **Browser steps.** When a command exits with code 4 or returns `next_action: { "type": "browser", "url": … }` (MCP: an operation marked `x-browser-step` returns a URL), give the person the URL, say what they will see, wait until they say they are done, then read the state again. You cannot click through these for them. A WooCommerce or Shopware 6 store exits 4 with `next_action: { "type": "store_plugin", "expires_at": … }` instead: the person pastes the setup token (print it with `--show-secrets`) into the Product Metrics plugin in their store admin before it expires.
- **Secrets.** Never ask for, print or store passwords, tokens or API keys, except where the API needs the person's own credential:
  - **Lightspeed** `apiKey` and `apiSecret`, and the **Meta** Conversions API `accessToken`: ask the person for them, pass them straight to the command, and never repeat them back, log them or put them in a summary.
  - A **setup token** (WooCommerce, Shopware) is hidden in output. With the CLI, run the command again with `--show-secrets` only to show it to the person. Through MCP it comes back hidden: tell the person to copy it from **Ecommerce platforms** in the Product Metrics app.
- **Deletes** (`access: destructive`, `--yes`, MCP `confirm: true`): only when the person explicitly asks.

## 1. Sign in

```bash
productmetrics status --json
```

If `signed_in` is false, ask the person to run `productmetrics login` in their own terminal (it opens a browser). In CI, `PM_TOKEN` is set instead. With MCP, the person signs in when they add the connector; if `execute` says the connection only has MCP access, ask them to remove and re-add Product Metrics in their AI app and allow read, setup and write.

## 2. Read where setup stands

```bash
productmetrics onboarding get-state --json
productmetrics setup get-status --json
productmetrics whoami --json
```

`setup get-status` is the map for every later step. Read `journey_stage`, `user.google_grant`, and `hub.company.next_action` / `hub.property.next_action`. Once you know the workspace and property, read it again with them:

```bash
productmetrics setup get-status \
  --company-id <company_id> \
  --property-id <property_id> \
  --json
```

## 3. Workspace

If `journey_stage` is `needs_workspace` and the person runs ads for their own business:

```bash
productmetrics companies create --name "<store name>" --auto-idempotency-key --json
```

Agencies don't create workspaces this way: send them to the app. Keep the returned `companyId`.

## 4. Google access and the Google Ads account

1. If `user.google_grant` is `none`, `missing_scope` or `revoked`:
   ```bash
   productmetrics google get-connect-link --scope ads --json
   ```
   Give the person `url`. They approve Google Ads and Merchant Center on Google's screen. Then read `setup get-status` again.
2. List the accounts their Google login reaches and ask which one runs their campaigns (a client account, not a manager/MCC account):
   ```bash
   productmetrics google-ads list-accounts --json
   ```
3. Connect it. This creates the property:
   ```bash
   productmetrics google-ads create-property-connection \
     --company-id <company_id> \
     --connection-mode user_oauth \
     --customer-id <customer_id> \
     --name "<store name>" \
     --json
   ```
   Keep the `property_id`. For the invite route instead (`central_read_only`), follow the `connect-google-ads` skill.

Full detail: https://www.productmetrics.io/docs/channels/google-ads.

## 5. Connect the store

Check what is already connected first, so nothing is connected twice:

```bash
productmetrics tracking get-commerce-configuration --company-id <company_id> --json
```

Ask the person which platform they use. Every platform but Shopify needs Pro before it connects (Shopify bills through the Shopify app), so first save the platform and start the subscription:

```bash
productmetrics stores select-platform --company-id <company_id> --platform woocommerce --json
productmetrics billing create-checkout-link --company-id <company_id> --json
```

`--platform` is one of `shopify`, `woocommerce`, `shopware6`, `lightspeed_c_series`, `magento`, `custom` (a website without a store platform) or `other` (with `--other-platform-name`). The checkout link exits 4: give the person the URL (it needs a workspace admin; nothing is charged until they complete the page). Checkout refuses with `needs_store_setup` until a platform is saved. Once they have paid, `setup get-status --company-id <company_id>` shows `company.billing` done. Then:

| Platform | What you run | What the person does |
| --- | --- | --- |
| Shopify | `productmetrics stores connect --company-id <id> --provider shopify --auto-idempotency-key --json` | Opens `authorizationUrl` (exit 4), approves the app in Shopify, turns on the **Product Metrics** app embed in the theme editor and saves. https://www.productmetrics.io/docs/platforms/shopify |
| WooCommerce | `productmetrics stores connect --company-id <id> --provider woocommerce --store-url https://<shop> --auto-idempotency-key --json` | Installs the Product Metrics plugin, pastes the setup token under **WooCommerce → Product Metrics** before it expires. https://www.productmetrics.io/docs/platforms/woocommerce |
| Shopware | `productmetrics stores connect --company-id <id> --provider shopware6 --store-url https://<shop> --auto-idempotency-key --json` | Installs the plugin and pastes the token for the sales channel. Check with `productmetrics tracking get-shopware6-status`. https://www.productmetrics.io/docs/platforms/shopware |
| Lightspeed | `productmetrics stores connect --company-id <id> --provider lightspeed_c_series --cluster eu --shop-domain <hostname> --shop-id <store id> --api-key <key> --api-secret <secret> --auto-idempotency-key --json` (`--cluster us` for `.shoplightspeed.com`) | Creates an enabled API key in the back office and gives you key and secret (never repeat them). Then signs in to Cloudflare in **Tracking** for the storefront gateway. https://www.productmetrics.io/docs/platforms/lightspeed |
| Magento | No API: app only | A developer installs the module; the owner follows https://www.productmetrics.io/docs/platforms/magento |
| Any website (Cloudflare Tracking) | `productmetrics tracking create-website-installation --company-id <id> --verified-domain <shop hostname> --json` | Signs in to Cloudflare in **Tracking** and selects **Set up gateway**. https://www.productmetrics.io/docs/platforms/cloudflare |

Afterwards, read `tracking get-commerce-configuration` until the store is `active`.

## 6. Link the store to the property

```bash
productmetrics tracking get-configuration \
  --company-id <company_id> \
  --property-id <property_id> \
  --json
```

From it take the installation id and the storefront scope id. If the scope is not assigned to the property:

```bash
productmetrics tracking assign-property \
  --company-id <company_id> \
  --scope-id <scope_id> \
  --installation-id <installation_id> \
  --property-id <property_id> \
  --json
```

`tracking_ready` means done; `tracking_setup_required` names the `setup_reason` still to fix. Run `productmetrics tracking assign-property --help --json` for its exact body fields before calling it.

## 7. Conversion actions

Only once the store connection is `active`:

```bash
productmetrics google-ads create-conversion-actions --property-id <property_id> --json
productmetrics google-ads get-conversion-actions --property-id <property_id> --json
```

They are created as **secondary** actions; nothing changes bidding until the person makes one primary in Google Ads (**Goals → Conversions**). That step is theirs (see Rules). Running it again is safe: actions that already exist come back `unchanged`.

## 8. Consent and additional costs (app steps)

There is no API for these. Tell the person, in **Tracking → Complete your tracking setup**:

- **Configure consent**: choose the banner the store actually shows (Shopify Customer Privacy, OneTrust, Cookiebot, Usercentrics or Osano; Shopware's own cookie manager is **Not configured**). https://www.productmetrics.io/docs/using/consent
- **Add your additional costs**: check shipping, handling, returns and payment fees, then **Activate additional costs**. For Cloudflare Tracking also set **Product cost fallback (%)**. Profit is sent only once these are active. https://www.productmetrics.io/docs/using/costs

## 9. Enhanced Conversions and the Meta Conversions API

```bash
productmetrics tracking get-enhanced-conversions \
  --company-id <company_id> \
  --property-id <property_id> \
  --json
```

If the customer data terms are not accepted, the person accepts them in Google Ads (**Goals → Settings → Customer data use**).

For Meta, ask the person for their pixel id and a Conversions API access token from Meta Events Manager (never repeat the token), then:

```bash
productmetrics destinations set-meta \
  --company-id <company_id> \
  --property-id <property_id> \
  --body '{
    "pixelId": "<pixel_id>",
    "accessToken": "<token>",
    "testEventCode": null,
    "enabled": true
  }' \
  --json
productmetrics destinations test-meta \
  --company-id <company_id> \
  --property-id <property_id> \
  --json
productmetrics destinations list-meta --company-id <company_id> --json
```

Run `productmetrics destinations set-meta --help --json` first for the exact fields (`testEventCode` is required and may be null). https://www.productmetrics.io/docs/channels/meta

## 10. Verify the first purchase

Ask the person to place and pay for a test order. Then:

- **Website (Cloudflare Tracking):** `productmetrics tracking get-last-purchase --company-id <company_id> --installation-id <installation_id> --json` until it shows that order.
- **Store platforms:** `productmetrics orders list --company-id <company_id> --storefront-scope-id <scope_id> --limit 5 --json` and find the order.

Finish with `productmetrics setup get-status` and the `check-tracking` skill.

## Report back

1. What is now set up (store, Google Ads account, Meta, conversion actions).
2. What the person still has to do, as a numbered list with the exact app labels.
3. How you checked it works, with the test order's number and value.

If a step failed, quote the error message and request id, and say what to try next. Don't invent states you did not read.
