# Setup Guide

## Prerequisites

This skill requires [uv](https://docs.astral.sh/uv/) — a fast Python package manager and runner.

### Install uv

    # macOS / Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Windows
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

    # Or via Homebrew
    brew install uv

`uv run` automatically resolves Python >=3.11 and the `requests` dependency from `pyproject.toml` — no manual `pip install` needed.

## Required Values

Two values are required before using this tool:
- `GOVILO_API_KEY` — Bot API authentication token
- `SELLER_ADDRESS` — Your wallet address on Base chain

## 1. API Key

### Get Your API Key

1. Go to https://govilo.xyz/
2. Sign up for an account (Gmail auth login)
3. Open the left sidebar menu → click **Settings**
4. Scroll to the **API Key** section → click **Manage API Key**
5. Create a new key and copy it (format: `sk_live_xxx`)

### Configure

Create a **dedicated** env file (e.g. `.env.govilo`) containing only Govilo credentials:

    # .env.govilo
    GOVILO_API_KEY=sk_live_xxx

> **Important:** Do not use a shared project `.env` that may contain unrelated secrets.
> Always use a dedicated file like `.env.govilo` to avoid accidental leakage.

### Verify

    cd skills/gen-paylink-govilo
    uv run --env-file .env.govilo create-link --help

If the key is missing or invalid, the tool outputs:

    {"ok": false, "error": "API Key not configured. ..."}

## 2. Seller Address

### Requirements

- **Chain:** Base (Base Mainnet only, Chain ID: 8453)
- **Format:** EVM address — `0x` + 40 hex characters
- Example: `0x1234567890abcdef1234567890abcdef12345678`

### Get Your Address

**MetaMask:**

1. Install MetaMask browser extension (https://metamask.io/)
2. Create or import a wallet
3. Switch network to **Base** (add if not listed: Chain ID `8453`, RPC `https://mainnet.base.org`)
4. Click the account name at the top to copy your address

**Coinbase Wallet:**

1. Install Coinbase Wallet (https://www.coinbase.com/wallet)
2. Create or import a wallet
3. Switch network to **Base**
4. Tap **Receive** → copy your address

### Configure

**Option A — Environment variable** (recommended for repeated use):

Add to your `.env.govilo` file:

    SELLER_ADDRESS=0xYourWalletAddress

**Option B — CLI parameter** (per-command override):

    create-link --address "0xYourWalletAddress" ...

CLI `--address` takes priority over `SELLER_ADDRESS` env var.

> **Tip:** You can also set a **Default Payout Address** on the Govilo website
> (Settings → Default Payout Address → paste your `0x...` address → **Save**).
> This address is pre-filled when creating new links on the web UI, but the CLI
> still requires `SELLER_ADDRESS` env var or `--address` parameter.
