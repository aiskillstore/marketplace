# Wallet — CLI Reference

Exact syntax, parameters, and key return fields for `onchainos wallet` subcommands. Verify flags with `onchainos wallet <subcommand> --help` when unsure. Gas Station flags on `send` / `contract-call` are documented here; the Gas Station flow lives in [gas-station.md](gas-station.md).

---

## Account

### `wallet login [email]`

Start login. With `email` → sends OTP. Without `email` → silent API-Key login (reads `OKX_API_KEY` / `OKX_SECRET_KEY` / `OKX_PASSPHRASE` from env).

```bash
onchainos wallet login [email] [--locale <locale>] [--force]
```

| Param | Required | Description |
|---|---|---|
| `email` | No | Email to receive OTP. Omit for AK login. |
| `--locale` | No | OTP email language, underscore form (`zh_CN`, `en_US`, `ja_JP`). Unrecognized values fall back to `en_US`. Omit if language is unclear. |
| `--force` | No | Re-login; skip the account-switch confirmation. Only after a Confirming response (see SKILL.md → Confirming Response). |

Returns `{}` on email-OTP success; `accountId` / `accountName` on silent AK login.

### `wallet verify <otp>`

Verify the emailed OTP to finish login. Returns `accountId`, `accountName`, and `isNew` (true → new user; trigger Policy + Export templates, see [portal-actions.md](wallet-portal-actions.md)).

### `wallet add`

Add a new account under the logged-in user; auto-switches to it (no manual `switch` needed). Returns `accountId`, `accountName`.

### `wallet switch <account_id>`

Switch the active account.

### `wallet status`

Show login status and active account. Returns `email`, `loggedIn`, `currentAccountId`, `currentAccountName`, `accountCount`, and `policy` (null when not set). Policy fields: `singleTxLimit`/`singleTxFlag`, `dailyTransferTxLimit`/`dailyTransferTxFlag`/`dailyTransferTxUsed`, `dailyTradeTxLimit`/`dailyTradeTxFlag`/`dailyTradeTxUsed`. Also surfaces `loginType` (`email` / `ak`).

### `wallet addresses`

Show wallet addresses grouped by chain category (XLayer / EVM / Solana).

```bash
onchainos wallet addresses [--chain <chain>]
```

Re-invoke this (or `wallet status`) to copy any address verbatim — never reproduce an address from memory.

### `wallet qrcode --address <addr>`

Render a Unicode-block QR encoding `--address` verbatim (no URI scheme added). Output is plain art on stdout — render verbatim in a monospace block.

### `wallet logout`

Logout and clear stored credentials.

### `wallet chains`

List supported chains. Use `showName` for display, `realChainIndex` for the `--chain` value.

---

## Balance

### `wallet balance`

```bash
onchainos wallet balance [--all] [--chain <chain>] [--token-address <addr>] [--force]
```

| Param | Default | Description |
|---|---|---|
| `--all` | false | All accounts' assets (batch). Only when the user explicitly asks for all accounts. |
| `--chain` | all | Chain name or ID. Required with `--token-address`. |
| `--token-address` | — | Single token contract address. Requires `--chain`. |
| `--force` | false | Bypass caches; re-fetch accounts + balances. |

Key fields: `totalValueUsd`, `evmAddress`, `solAddress`, `accountCount`, `details[]` (token balance groups). With `--all`, `details` is a map of `accountId` → cache entry (`totalValueUsd`, `updatedAt`, `data`).

Every token in `details[].tokenAssets[]` (or `assets[]`, or `details.<accountId>.data[].tokenAssets[]` for `--all`) contains **exactly these 9 fields**:

| Field | Type | Description |
|---|---|---|
| `symbol` | String | Token symbol (e.g. `"ETH"`) |
| `tokenName` | String | Token full name (e.g. `"Ethereum"`) |
| `chainIndex` | String | Chain identifier (e.g. `"1"`) |
| `tokenAddress` | String | Token contract address; `""` for native tokens |
| `balance` | String | Balance in UI units |
| `rawBalance` | String | Balance in minimal units |
| `decimal` | String | Token decimals |
| `tokenPrice` | String | Token price in USD |
| `usdValue` | String\|Number | Token value in USD (representation preserved as returned) |

---

## Send

### `wallet send`

Send native or contract tokens (ERC-20 / SPL).

```bash
onchainos wallet send --readable-amount <amount> --recipient <address> --chain <chain> \
  [--from <address>] [--contract-token <address>] [--force] \
  [--gas-token-address <address>] [--relayer-id <id>] [--enable-gas-station]
```

| Param | Required | Description |
|---|---|---|
| `--readable-amount` | One of | Human-readable amount; CLI converts to minimal units. Preferred. |
| `--amt` | One of | Raw minimal units. Mutually exclusive with `--readable-amount`. |
| `--recipient` | Yes | Recipient address (0x EVM / Base58 Solana). |
| `--chain` | Yes | Chain name or ID. |
| `--from` | No | Sender; defaults to selected account's address on the chain. |
| `--contract-token` | No | Token contract for ERC-20 / SPL. Omit for native. |
| `--force` | No | Re-run after a confirmed Confirming response. |
| `--gas-token-address`, `--relayer-id`, `--enable-gas-station` | No | Gas Station (Solana). Second-phase values from a Confirming response — never on the first call. See [gas-station.md](gas-station.md). |

Returns `txHash` (normal). Gas Station responses (`gasStationUsed`, `orderId`, Confirming scenes) → [gas-station.md](gas-station.md). On simulation failure, the CLI surfaces `executeErrorMsg` and does not broadcast.

---

## History

Providing any of `--order-id` / `--tx-hash` / `--uop-hash` → **detail mode** (single record); otherwise **list mode** (paged).

```bash
# List
onchainos wallet history [--account-id <id>] [--chain <chain>] [--begin <ms>] [--end <ms>] [--page-num <cursor>] [--limit <n>]
# Detail (any one identifier)
onchainos wallet history --chain <chain> --order-id <id>
onchainos wallet history --chain <chain> --tx-hash <hash> [--address <addr>]
onchainos wallet history --chain <chain> --uop-hash <hash>
```

`--chain` is required in detail mode. Right after a Gas Station broadcast, poll by `--order-id` (txHash may be async).

List mode: always pass --limit (page size, default 20) and --page-num (page number) for paging. Detail mode returns a single record — do not pass --limit.

List fields: `cursor`, `orderList[]` with `txHash`, `txStatus`, `txTime`, `direction` (send/receive), `chainSymbol`, `coinSymbol`, `coinAmount`, `serviceCharge`, `confirmedCount`, `assetChange[]` (`coinSymbol`/`coinAmount`/`direction` in/out). Detail adds `failReason`, `explorerUrl`, `input[]`, `output[]`.

Transaction status: `0` Pending · `1` Success · `2` Failed · `3` Pending confirmation. `txTime` is Unix ms — convert for display.

---

## Contract Call

### `wallet contract-call`

Call an EVM contract (`--input-data`) or Solana program (`--unsigned-tx`) with TEE signing + auto-broadcast. Non-swap interactions only (approve / deposit / withdraw / custom calls) — use `swap execute` for DEX swaps.

```bash
onchainos wallet contract-call --to <contract> --chain <chain> \
  [--amt <minimal_units>] [--input-data <hex>] [--unsigned-tx <base58>] \
  [--gas-limit <n>] [--from <address>] [--mev-protection] [--jito-unsigned-tx <base58>] \
  [--biz-type <type>] [--strategy <name>] [--aa-dex-token-addr <addr>] [--aa-dex-token-amount <amt>] \
  [--gas-token-address <addr>] [--relayer-id <id>] [--enable-gas-station] [--force]
```

| Param | Required | Description |
|---|---|---|
| `--to` | Yes | Contract address. |
| `--chain` | Yes | Chain name or ID. |
| `--amt` | No | Native value in minimal units (payable functions only). Default `"0"`. |
| `--input-data` | EVM | Hex calldata. Required for EVM. |
| `--unsigned-tx` | Solana | Base58 unsigned tx. Required for Solana. |
| `--gas-limit` | No | EVM gas override; auto-estimated if omitted. |
| `--mev-protection` | No | MEV protection (Ethereum / BSC / Base / Solana). See [mev-protection.md](wallet-mev-protection.md). |
| `--jito-unsigned-tx` | No | Jito bundle base58 tx. Required when `--mev-protection` on Solana. Never substitute `--unsigned-tx`. |
| `--biz-type` | No | `transfer` / `dex` / `defi` / `dapp`. |
| `--gas-token-address`, `--relayer-id`, `--enable-gas-station` | No | Gas Station (Solana), second-phase only. See [gas-station.md](gas-station.md). |
| `--force` | No | Re-run after a confirmed Confirming response. |

Exactly one of `--input-data` (EVM) / `--unsigned-tx` (Solana) is required. Returns `txHash`. Run `onchainos security tx-scan` before calling.

---

## Sign Message

### `wallet sign-message`

personalSign (EIP-191, EVM + Solana) or EIP-712 typed data (EVM only).

```bash
onchainos wallet sign-message --chain <chain> --from <address> --message <message> [--type <type>] [--force]
```

| Param | Required | Description |
|---|---|---|
| `--chain` | Yes | Chain name or ID. |
| `--from` | Yes | Signer address. |
| `--message` | Yes | `personal`: arbitrary string. `eip712`: JSON typed-data string. |
| `--type` | No | `personal` (default, EVM + Solana) or `eip712` (EVM only — Solana returns an error). |
| `--force` | No | Re-run after a confirmed Confirming response. |

Returns `signature` (hex on EVM; base58 on Solana, plus `publicKey`).
