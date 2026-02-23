---
name: gen-paylink-govilo
description: >
  Upload files to Govilo and generate unlock links via Bot API. Use when:
  (1) Creating a Govilo unlock link from a ZIP, folder, or individual files,
  (2) Automating file upload to Govilo R2 storage with presigned URLs,
  (3) Managing Govilo Bot API interactions (presign → upload → create item).
  Requires GOVILO_API_KEY and SELLER_ADDRESS env vars.
  If missing, guides user to register at https://govilo.xyz/.
metadata:
  author: hau823823@gmail.com
  version: "1.0"
  openclaw:
    requires:
      env:
        - GOVILO_API_KEY
        - SELLER_ADDRESS
    primaryEnv: GOVILO_API_KEY
    homepage: https://github.com/hau823823/gen-paylink-govilo
---

# Govilo To Go

Turn any file into a paid unlock link — one command to package, upload, and collect crypto payments. The last mile of automation: from creation to monetization.

## Before Running

Always ask the user for these values before executing the CLI — never guess or use placeholders:

1. **title** — What is the product name?
2. **price** — How much to charge (in USDC)?
3. **description** — Short description of the product (optional, but always ask)

## CLI Command

> Requires [uv](https://docs.astral.sh/uv/). See [references/setup-guide.md](references/setup-guide.md) for install instructions.

Run from this skill's base directory. Use a **dedicated** env file containing only `GOVILO_API_KEY` (and optionally `SELLER_ADDRESS`). Never point `--env-file` at a project `.env` that contains unrelated secrets.

```bash
cd <skill_base_directory>
uv run --env-file <path_to>/.env.govilo create-link \
  --input <path>         \
  --title "Product Name" \
  --price "5.00"         \
  --address "0x..."      \
  --description "optional"
```

If no `.env.govilo` exists, create one before running:

```dotenv
GOVILO_API_KEY=sk_live_xxx
SELLER_ADDRESS=0x...
```

`--input` accepts ZIP file, folder, or individual files (repeatable). Non-ZIP inputs are auto-packaged.

All output is JSON `{"ok": true/false, ...}` with exit code 1 on failure.

## Parameters

| Param           | Required | Source                     | Description                |
| --------------- | -------- | -------------------------- | -------------------------- |
| `--input`       | Yes      | CLI (repeatable)           | ZIP, folder, or file paths |
| `--title`       | Yes      | CLI                        | Product title              |
| `--price`       | Yes      | CLI                        | Price in USDC              |
| `--address`     | No       | CLI > `SELLER_ADDRESS` env | Seller EVM wallet          |
| `--description` | No       | CLI                        | Product description        |

## Workflow

1. Validate config (API Key + seller address)
2. Package inputs → ZIP (if not already ZIP)
3. `POST /api/v1/bot/uploads/presign` → get upload_url + session_id
4. `PUT upload_url` → upload ZIP to R2
5. `POST /api/v1/bot/items` → get unlock_url

## File Limits

- Max ZIP size: 20 MB
- Max files in ZIP: 20

## Setup

Two values are required:

| Variable         | Required | Description                              |
| ---------------- | -------- | ---------------------------------------- |
| `GOVILO_API_KEY` | Yes      | Bot API key from [govilo.xyz][]          |
| `SELLER_ADDRESS` | Yes*     | EVM wallet address on **Base chain**     |

[govilo.xyz]: https://govilo.xyz/

*`SELLER_ADDRESS` can also be passed via `--address` CLI parameter.

See [references/setup-guide.md](references/setup-guide.md) for step-by-step registration and wallet setup instructions.

## API Reference

See [references/bot-api-quick-ref.md](references/bot-api-quick-ref.md) for Bot API endpoints and error codes.
