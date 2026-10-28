# BRC-20 CLI Reference

## Commands

### `wallet balance`

Query BRC-20 balance for one ticker.

#### Syntax

```bash
onchainos wallet balance --chain bitcoin --token-address <btc-brc20-ticker> [--force]
```

#### Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--chain` | Yes | — | Use `bitcoin`. |
| `--token-address` | Yes | — | BRC-20 identifier: `btc-brc20-<ticker>`. |
| `--force` | No | Disabled | Bypass balance caches only when the user explicitly asks to refresh or sync. |

#### Output Template

```text
Total balance: ${totalAmount} ${ticker}, worth approximately $${totalUsd}
Currently transferable (already inscribed): ${transferableAmount} ${ticker}, worth approximately $${transferableUsd}, across ${count} transferable inscriptions with denominations ${denominations}
Remaining available to inscribe: ${remainingInscribableAmount} ${ticker}, worth approximately $${remainingInscribableUsd}
```

When `${count}` is zero, use:

```text
Currently transferable (already inscribed): 0 ${ticker}, worth approximately $${transferableUsd}, with no transferable inscriptions
```

### `wallet utxo brc20-transferable`

Query transferable inscriptions for one ticker. With `--readable-amount`, use `selectionPlan`: `EXACT_MATCH` uses a returned combination; `NO_EXACT_MATCH` refreshes the ticker balance before inscription; `SEARCH_LIMIT_EXCEEDED` shows choices without claiming no exact match. Use the Bound BRC-20 Asset template for each returned asset.

#### Syntax

```bash
onchainos wallet utxo brc20-transferable --chain bitcoin --token-address <btc-brc20-ticker> [--readable-amount <amount>]
```

#### Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--chain` | Yes | — | Use `bitcoin`. |
| `--token-address` | Yes | — | BRC-20 identifier: `btc-brc20-<ticker>`. |
| `--readable-amount` | No | — | Human-readable target amount for exact combinations. |

#### Output Template

For each returned asset, use the shared [Bound BRC-20 Asset](#bound-brc-20-asset) template.

### `wallet send`

Transfer BRC-20 with a current exact combination from `wallet utxo brc20-transferable`. When the user must choose between returned combinations, show them and wait for a choice. Run `wallet send` initially without `--force`.

The initial command refreshes the selected outpoints, validates their availability, uniqueness, and amount sum, signs, and returns ordinary `confirming` before broadcast. Display the complete confirmation and use the BRC-20 Transfer Confirmation template. Execute `next` only after explicit confirmation. If the user supplies a new sat/vB value, rerun without `--force`, display the fresh preview, and use the Custom Fee Rate template.

The confirmed continuation returns `state=PENDING`, `txHash`, and `orderId`.

#### Syntax

```bash
onchainos wallet send --chain bitcoin --contract-token <btc-brc20-ticker> --readable-amount <amount> --recipient <address> --brc20-outpoint <txHash:voutIndex> [--brc20-outpoint <txHash:voutIndex> ...] [--fee-rate <sat-per-vB>] [--from <address>] [--force]
```

#### Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--chain` | Yes | — | Use `bitcoin`. |
| `--contract-token` | Yes | — | BRC-20 identifier: `btc-brc20-<ticker>`. |
| `--readable-amount` | Yes | — | Exact human-readable BRC-20 amount. |
| `--recipient` | Yes | — | Recipient Bitcoin address. |
| `--brc20-outpoint` | Yes | — | Selected transferable inscription in `<txHash>:<voutIndex>` form; repeat for every selected input. |
| `--fee-rate` | No | Service default | Fee rate for this transaction only (minimum `0.1` sat/vB). |
| `--from` | No | Active wallet address | Sender address; defaults to the active wallet. |
| `--force` | Continuation only | Disabled | Use only through the exact `next` returned after explicit confirmation. |

Query a submitted direct transfer through the shared wallet history flow, not inscription status:

```bash
onchainos wallet history --chain bitcoin (--tx-hash <hash> | --order-id <id>)
```

#### Output Template

```text
Confirm broadcasting and creating this inscription at the current fee rate? To change it, reply with a new sat/vB value.
```

When the user supplies a new fee rate, also state:

```text
The custom fee rate applies only to this transaction and does not change the default fee rate for future transactions.
```

### `wallet inscription create`

Create an asynchronous transfer inscription to the current Bitcoin address only after an explicit request. If no direct-transfer combination exists, refresh the ticker balance before offering it.

Run initially without `--force`. It stops after `unsignedInfo` and returns ordinary `confirming` with `scene="btc_inscription"`; `preview.feeReadable` is nullable, and nothing has been signed or submitted. Display the complete preview and the same fee-rate prompt and one-transaction fee statement used by `wallet send`. A new sat/vB value requires a fresh preview without `--force`.

The confirmed `next` signs, calls `sign-tx`, and batch-broadcasts the ordered inscription transactions. Show returned `state=INSCRIBING`, `txHash`, `orderId`, `broadcasts`, and `nextSteps.checkInscriptionStatus` verbatim, render the Inscription Submission template, and stop. Do not query automatically or auto-send after `READY_TO_TRANSFER`.

#### Syntax

```bash
onchainos wallet inscription create --chain bitcoin --token-address <btc-brc20-ticker> --readable-amount <amount> [--from <address>] [--fee-rate <sat-per-vB>] [--operation-token <token>] [--force]
```

#### Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--chain` | Yes | — | Use `bitcoin`. |
| `--token-address` | Yes | — | BRC-20 identifier: `btc-brc20-<ticker>`. |
| `--readable-amount` | Yes | — | Exact human-readable amount to inscribe. |
| `--from` | No | Active wallet address | Sender address; defaults to the active wallet. |
| `--fee-rate` | No | Service default | Fee rate for this inscription only (minimum `0.1` sat/vB). |
| `--operation-token` | Continuation only | — | Use only when supplied by the exact `next` returned after preview. |
| `--force` | Continuation only | Disabled | Use only through the exact `next` returned after explicit confirmation. |

#### Output Template

Substitute only returned values and the fee from the confirmed preview. Omit unavailable values.

```text
The inscription transaction was submitted but is not fully confirmed:

- Asset: ${readableAmount} ${ticker}
- Current status: ${state}
- Bitcoin confirmations: ${confirmations}
- Reveal order ID: ${orderId}
- Reveal txHash: ${txHash}
- Current inscription fee: ${inscriptionFeeSats} sats
- Transferability: ${transferability}

You can reply "Check the result", and I will run this complete command for you:

${nextSteps.checkInscriptionStatus}
```

### `wallet inscription status`

Check one submitted BRC-20 inscription after the user asks for its result. Run once; if pending, show the returned status and continuation, then stop. Do not loop, poll, sleep, or promise automatic checks. `READY_TO_TRANSFER` provides read-only `nextSteps.queryBrc20TransferableUtxos` to refresh the transferable list.

#### Syntax

```bash
onchainos wallet inscription status --chain bitcoin (--tx-hash <hash> | --order-id <id>)
```

#### Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--chain` | Yes | — | Use `bitcoin`. |
| `--tx-hash` | One ID required | — | Reveal transaction hash. |
| `--order-id` | One ID required | — | Reveal order ID. |

## Command Constraints

Use a synthetic BRC-20 token address: `btc-brc20-<ticker>`. The CLI normalizes its ticker to lowercase and converts `--readable-amount` to token minimal units. Direct transfers use complete service-returned inscription UTXOs whose token amounts sum to the requested amount.

## Output Rules

### Bound BRC-20 Asset

```text
This UTXO carries: ${readableAmount} ${symbol} (${protocol}).
Spending this UTXO can permanently lose these assets.
```
