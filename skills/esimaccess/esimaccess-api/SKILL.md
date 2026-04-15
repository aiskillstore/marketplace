---
name: esimaccess-api
description: >
  Manage eSIM Access API operations including balance checks, package listing,
  order creation, eSIM status monitoring, top-ups, cancellations, profile
  management, webhooks, and refund/reissue workflows. Use when user mentions
  eSIM, ICCID, data plan, roaming, SIM card, mobile data package, travel
  connectivity, cellular data usage, or interacts with the eSIM Access API at
  api.esimaccess.com. Also trigger when user asks about balance, top-up,
  order status, QR code provisioning, or uploads a list of ICCIDs or order numbers.
---

# eSIM Access API Skill

Interact with the eSIM Access API for complete eSIM lifecycle management.

## When to Use This Skill

Use this skill when the user:

- Asks about eSIM operations: ordering, top-ups, cancellations, status checks
- Mentions ICCID, order number, QR code, or data usage
- Wants to check account balance or list available data packages
- Asks about roaming, travel data plans, or mobile connectivity
- Needs to manage eSIM profiles (suspend, unsuspend, revoke)
- Wants to configure webhooks for eSIM status notifications
- Asks to cancel and reissue an eSIM (refund/replace workflow)
- References the eSIM Access API or api.esimaccess.com

### Example prompts

- "Check my eSIM Access balance"
- "What packages are available for Japan?"
- "Order a 5GB plan for the US"
- "Check the status of order B26041021130002"
- "How much data has ICCID 89852240810733629810 used?"
- "Top up my eSIM with another 5GB"
- "Cancel this unused eSIM and get a refund"
- "Set up a webhook for order notifications"

## Quick Reference

- **Base URL**: `https://api.esimaccess.com/api/v1/open`
- **Auth**: HMAC-SHA256 signed headers — the accessCode is used as both the API identifier and signing key (see `references/api-reference.md`)
- **Prices**: API values / 10,000 = USD (e.g., 18000 = $1.80)
- **Volumes**: Bytes (1073741824 = 1 GB)
- **Credentials**: Get your accessCode from https://console.esimaccess.com/developer/index

## Operations

### Read (safe)
| Operation | Endpoint | Purpose |
|-----------|----------|---------|
| `check_balance` | `/balance/query` | Account balance in USD |
| `list_regions` | `/package/list` | All supported countries |
| `list_packages` | `/package/list` | Products by country/code |
| `list_topup_packages` | `/package/list` | Top-up options for ICCID |
| `check_order_status` | `/esim/query` | Order details + ICCID |
| `check_esim_status` | `/esim/query` | Full eSIM profile info |
| `check_data_usage` | `/esim/usage/query` | Data consumption stats |
| `query_webhook` | `/webhook/query` | Current webhook config |

### Write (costs money or modifies state)
| Operation | Endpoint | Purpose |
|-----------|----------|---------|
| `create_order` | `/esim/order` | Purchase new eSIM |
| `apply_topup` | `/esim/topup` | Add data to existing eSIM |
| `cancel_esim` | `/esim/cancel` | Cancel unused eSIM (refund) |
| `suspend_profile` | `/esim/suspend` | Temporarily disable |
| `unsuspend_profile` | `/esim/unsuspend` | Re-enable suspended |
| `revoke_profile` | `/esim/revoke` | Permanently disable (no refund) |
| `send_sms` | `/esim/sendSms` | Send SMS to eSIM |
| `setup_webhook` | `/webhook/save` | Configure notification URL |

### Composite Workflows
| Operation | Purpose |
|-----------|---------|
| `refund_and_reissue` | Cancel unused eSIM, verify refund, order replacement with same package |

## Key Rules

1. **Order flow**: `create_order` returns `orderNo`. Poll `check_order_status` every 3s (4 retries) for ICCID. ORDER_STATUS webhook is fallback.
2. **Top-ups**: Use `esimTranNo` (not ICCID). `supportTopUpType === 2` means eligible. Cannot top up after expiry.
3. **Cancel vs Revoke**: Cancel works on unused eSIMs (RELEASED/GOT_RESOURCE) and provides refund. Revoke works on activated eSIMs with no refund.
4. **Usage query**: Requires `esimTranNo`, not ICCID. Do an ICCID lookup via `/esim/query` first if needed.
5. **SMS**: Uses `message` field (not `content`). Only works on activated eSIMs.

## Authentication in Any Language

The `references/api-reference.md` file contains HMAC-SHA256 auth examples in both Node.js and Python. Ask your AI to generate auth code in your preferred language using the signature algorithm documented there.

## Testing

```bash
node scripts/test-esim-api.mjs <accessCode>
```

## Installation

### Any AI agent (via Skills CLI)
```bash
npx skills add esimaccess/esimaccess-api
```

### Manual install
Download from https://app.esimaccess.com/public/skill/ and place in your agent's skills directory.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | This file - skill definition |
| `scripts/test-esim-api.mjs` | 15 end-to-end API tests |
| `references/api-reference.md` | Full API docs: endpoints, auth, status states, webhooks, error codes |
