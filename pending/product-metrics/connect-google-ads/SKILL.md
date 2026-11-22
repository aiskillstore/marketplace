---
name: connect-google-ads
description: >-
  Connect a Google Ads account and its Merchant Center to Product Metrics with the productmetrics CLI or
  the Product Metrics MCP server (search and execute tools). Use it when someone asks to "connect
  Google Ads", "add another Google Ads account", "link Merchant Center", fix a Google Ads connection
  in status error or revoked, or when setup shows needs_property or a missing Google grant. Covers
  the person's own Google sign-in (user_oauth) and the manager-link invite (central_read_only). The
  Google consent and the invite acceptance happen in the person's browser; the skill hands them the
  URL and checks the result.
---

# Connect Google Ads to Product Metrics

Connecting a Google Ads account creates a **property** in the workspace: one store's Google Ads account. Every later step (conversion actions, POAS bidding, reports) needs it. Docs: https://www.productmetrics.io/docs/channels/google-ads.

Use the `productmetrics` CLI with `--json` when it is installed (`productmetrics status --json`), otherwise the MCP `search` and `execute` tools. Operation ids map to CLI commands: `google_ads.create_property_connection` is `productmetrics google-ads create-property-connection`. Check flags with `productmetrics <group> <command> --help --json` (MCP: `search` for the operation) before the first call. Never invent ids: they come from earlier results.

**All conversion actions by agents are secondary.** Product Metrics creates its actions as secondary and leaves existing ones as they are. What the account bids on is the person's choice: making an action primary (and the old purchase action secondary) in Google Ads (**Goals → Conversions**, or a campaign-specific goal), and picking the conversion a Meta ad set or ChatGPT Ads campaign optimises on, is their step by every route, also when they ask you to do it. Tell them exactly what to click, wait until they say it is done, then read it back with `productmetrics google-ads get-conversion-actions --property-id <property_id> --json` (`goal_status`). The bidding choice belongs to the advertiser, and one primary purchase action keeps bidding right and counts every purchase once.

## 1. Find the workspace and what is missing

```bash
productmetrics whoami --json
productmetrics setup get-status --company-id <company_id> --json
productmetrics google-ads list-property-connections --company-id <company_id> --json
```

- `user.google_grant` `user_oauth` or `central_read_only`: Google is reachable.
- `none`, `missing_scope` or `revoked`: the person must grant access first (step 2).
- `list-property-connections` shows accounts already connected and their status (`active`, `revoked`, `error`). Don't connect one twice.

`list-property-connections`, `send-invite` and `create-property-connection` need a workspace admin. A 403 means the person should ask their admin.

## 2. Grant Google access (browser step)

```bash
productmetrics google get-connect-link --scope ads --json
```

Give the person the `url`. They sign in to Product Metrics if asked and tick Google Ads (and Merchant Center) on Google's screen. Nothing changes until they do. Then read `productmetrics setup get-status` again. Use `--scope merchant` only when Google Ads is connected and Merchant Center access is missing.

## 3a. Connect with the person's Google sign-in (`user_oauth`)

```bash
productmetrics google-ads list-accounts --json
```

Show the accounts by name and customer id and ask which one runs the store's campaigns. Pick the **client** account: manager (MCC) accounts are refused. If the account is reached through a manager, pass its id as `--login-customer-id`.

```bash
productmetrics google-ads create-property-connection \
  --company-id <company_id> \
  --connection-mode user_oauth \
  --customer-id <customer_id> \
  --name "<store name>" \
  --json
```

Keep the returned property id.

## 3b. Connect through an invite (`central_read_only`)

Use this when the person's Google login cannot reach the account, or they prefer to accept an invite.

```bash
productmetrics google-ads send-invite \
  --company-id <company_id> \
  --customer-id <customer_id> \
  --json
```

Tell the person: in Google Ads, open **Admin → Access and security → Managers** and accept the Product Metrics invite. The API cannot accept it. When they say it is done:

```bash
productmetrics google-ads list-pending-invites --company-id <company_id> --json
productmetrics google-ads create-property-connection \
  --company-id <company_id> \
  --connection-mode central_read_only \
  --customer-id <customer_id> \
  --json
```

A 409 says the invite is still pending, already accepted or claimed by another workspace.

## 4. Merchant Center (required for Google Ads)

```bash
productmetrics merchant-center create-connection \
  --property-id <property_id> \
  --merchant-id <merchant_id> \
  --json
productmetrics merchant-center inspect-auto-setup --property-id <property_id> --json
```

`merchant_id` must be linked to that Google Ads account in Google; otherwise the answer is 409 `no_merchant_center_links`. Show the person the plan from `inspect-auto-setup`, including any `confirm_reuse` source names, and apply only what they confirm:

```bash
# read the fields first
productmetrics merchant-center apply-auto-setup --property-id <property_id> --help --json
productmetrics merchant-center get-auto-setup-status --property-id <property_id> --json
```

Sources from other tools are never touched. Docs: https://www.productmetrics.io/docs/using/merchant-center.

## 5. Fix a broken connection

If a connection shows `error`, or the person just accepted an invite or renewed their Google sign-in:

```bash
productmetrics google-ads recheck-property-connection \
  --property-id <property_id> \
  --json
```

A 409 says what is still missing. Don't call `delete-property-connection` unless the person explicitly asks to disconnect: it stops reports and conversions for that property.

## 6. Next

- Conversion actions: `productmetrics google-ads get-conversion-actions --property-id <property_id> --json`. If missing, create them (`set-up-tracking` skill, step 7).
- Check the whole setup with the `check-tracking` skill.

## Report back

Say which Google Ads account (name and customer id) is now connected to which property, its status, and what the person still has to do. Never print tokens. If a call failed, quote its message and request id.
