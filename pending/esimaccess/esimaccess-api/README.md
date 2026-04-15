# esimaccess-api

An AI agent skill for the [eSIM Access API](https://api.esimaccess.com). Works with Claude Code, Cursor, Windsurf, Copilot, Codex, Cline, and 40+ other AI coding agents. See the [landing page](https://app.esimaccess.com/public/skill/) for details.

## Install

```bash
npx skills add esimaccess/esimaccess-api
```

## What it does

17 operations covering the full eSIM lifecycle:

- **Read**: balance, packages, order status, eSIM status, data usage, webhooks
- **Write**: create orders, top-ups, suspend/unsuspend, cancel, revoke, SMS, webhooks
- **Composite**: refund and reissue (cancel + re-order in one step)

## Setup

1. Get your access code from the [eSIM Access Developer Console](https://console.esimaccess.com/developer/index)
2. Install the skill with `npx skills add esimaccess/esimaccess-api`
3. Tell your AI: "Fetch my esimaccess-api balance" with your access code

## Testing

```bash
node scripts/test-esim-api.mjs <accessCode>
```

Runs 15 end-to-end tests covering balance, packages, ordering, polling, usage, webhooks, suspend/unsuspend, SMS, cancel with refund verification, and final balance check.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition with operations, rules, and trigger phrases |
| `references/api-reference.md` | Full API docs: endpoints, auth (Node.js + Python), status states, webhooks, error codes |
| `scripts/test-esim-api.mjs` | 15 end-to-end API tests |

## Links

- [Landing page](https://app.esimaccess.com/public/skill/)
- [Developer Console](https://console.esimaccess.com/developer/index)
- [skills.sh](https://skills.sh)
