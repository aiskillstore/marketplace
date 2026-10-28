# Bitcoin UTXO CLI Reference

## Commands

### `wallet utxo available`

Query currently spendable BTC UTXOs. Use returned `sumSats` as the available BTC total; do not derive it from total holdings.

#### Syntax

```bash
onchainos wallet utxo available --chain bitcoin
```

#### Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--chain` | Yes | — | Use `bitcoin`. |

#### Output Template

For each returned asset, use the shared [Bound BRC-20 Assets](#bound-brc-20-assets) template.

### `wallet utxo user-ignored`

Query UTXOs whose asset occupancy the user previously removed from asset protection.

#### Syntax

```bash
onchainos wallet utxo user-ignored --chain bitcoin
```

#### Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--chain` | Yes | — | Use `bitcoin`. |

#### Output Template

For each returned asset, use the shared [Bound BRC-20 Assets](#bound-brc-20-assets) template.

### `wallet utxo unavailable`

Query locked or otherwise unavailable BTC UTXOs. Use only returned categories, amounts, and UTXOs without inference. Use it before replying when the user follows a BTC balance answer by asking what the remaining or unavailable BTC is.

#### Syntax

```bash
onchainos wallet utxo unavailable --chain bitcoin
```

#### Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--chain` | Yes | — | Use `bitcoin`. |

#### Output Template

For each returned asset, use the shared [Bound BRC-20 Assets](#bound-brc-20-assets) template.

### `wallet utxo unlock`

Remove asset protection from selected currently protected UTXOs. Query the latest unavailable view and resolve the user's reference against its current outpoints first. A single amount or asset reference must resolve to exactly one outpoint; if it matches zero or multiple UTXOs, show the matches and wait for the user's decision.

#### Syntax

```bash
onchainos wallet utxo unlock --chain bitcoin (--outpoint <txHash:voutIndex>... | --all) [--operation-token <token>] [--force]
```

#### Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--chain` | Yes | — | Use `bitcoin`. |
| `--outpoint` | One selector required | — | Current protected UTXO in `<txHash>:<voutIndex>` form; repeat for multiple selections. |
| `--all` | One selector required | Disabled | Select every currently protected UTXO instead of individual outpoints. |
| `--operation-token` | Continuation only | — | Use only when supplied by the exact `next` returned after preview. |
| `--force` | Continuation only | Disabled | Use only through the exact `next` returned after explicit confirmation. |

### `wallet utxo lock`

Restore asset protection for selected user-ignored UTXOs. Query the latest user-ignored view and resolve the user's reference against its current outpoints first. A single amount or asset reference must resolve to exactly one outpoint; if it matches zero or multiple UTXOs, show the matches and wait for the user's decision.

#### Syntax

```bash
onchainos wallet utxo lock --chain bitcoin (--outpoint <txHash:voutIndex>... | --all) [--operation-token <token>] [--force]
```

#### Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--chain` | Yes | — | Use `bitcoin`. |
| `--outpoint` | One selector required | — | Current user-ignored UTXO in `<txHash>:<voutIndex>` form; repeat for multiple selections. |
| `--all` | One selector required | Disabled | Select every current user-ignored UTXO instead of individual outpoints. |
| `--operation-token` | Continuation only | — | Use only when supplied by the exact `next` returned after preview. |
| `--force` | Continuation only | Disabled | Use only through the exact `next` returned after explicit confirmation. |

### `wallet utxo reclaim`

Reclaim still-unspent inputs from transactions whose history state is `MEMPOOL_REMOVED`. Query unavailable UTXOs first and use the returned transaction hashes.

#### Syntax

```bash
onchainos wallet utxo reclaim --chain bitcoin --tx-hash <hash> [--tx-hash <hash> ...] [--force]
```

#### Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--chain` | Yes | — | Use `bitcoin`. |
| `--tx-hash` | Yes | — | Original `MEMPOOL_REMOVED` transaction hash; repeat for multiple transactions. |
| `--force` | Continuation only | Disabled | Use only through the exact `next` returned after explicit confirmation. |

## Output Rules

### Bound BRC-20 Assets

`wallet utxo available`, `wallet utxo unavailable`, `wallet utxo user-ignored`, and `wallet utxo brc20-transferable` return `assets` for UTXOs carrying BRC-20 assets.

For each returned asset, append:

```text
This UTXO carries: ${readableAmount} ${symbol} (${protocol}).
Spending this UTXO can permanently lose these assets.
```

For UTXO definitions and user-facing reply templates, see [UTXO FAQ](utxo-faq.md).
