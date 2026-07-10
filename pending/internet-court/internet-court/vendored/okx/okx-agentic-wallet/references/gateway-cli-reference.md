# Transaction Gateway — CLI Reference

Syntax, parameters, and key return fields for the 6 `onchainos gateway` subcommands. Verify with `onchainos gateway <subcommand> --help` when unsure.

## `gateway chains`

Supported chains (no params). Returns `chainIndex`, `name`, `shortName`, `logoUrl`.

## `gateway gas --chain <chain>`

Current gas prices. Returns `normal` / `min` / `max` (legacy), `supporteip1559`, and `eip1559Protocol.{suggestBaseFee, baseFee, proposePriorityFee, safePriorityFee, fastPriorityFee}`. Solana: `proposePriorityFee`, `safePriorityFee`, `fastPriorityFee`, `extremePriorityFee`.

## `gateway gas-limit`

```bash
onchainos gateway gas-limit --from <address> --to <address> --chain <chain> [--amount <minimal_units>] [--data <hex>]
```

`--amount` default `"0"`; `--data` for contract interactions. Returns `gasLimit`.

## `gateway simulate`

```bash
onchainos gateway simulate --from <address> --to <address> --data <hex> --chain <chain> [--amount <minimal_units>]
```

Returns `intention`, `assetChange[]` (`symbol`, `rawValue`), `gasUsed`, `failReason` (empty = success), `risks[]`.

## `gateway broadcast`

Broadcast a fully signed transaction (this CLI does not sign).

```bash
onchainos gateway broadcast --signed-tx <tx> --address <address> --chain <chain> [--mev-protection]
```

| Param | Required | Description |
|---|---|---|
| `--signed-tx` | Yes | Fully signed tx (hex for EVM, base58 for Solana). |
| `--address` | Yes | Sender wallet address. |
| `--chain` | Yes | Chain name or ID. |
| `--mev-protection` | No | Boolean; enables MEV protection on EVM (`enableMevProtection: true`). See [gateway.md](gateway.md) → MEV Protection. |

Returns `orderId` (for status queries) and `txHash`.

## `gateway orders`

```bash
onchainos gateway orders --address <address> --chain <chain> [--order-id <id>]
```

Returns `cursor` and `orders[]`: `orderId`, `txHash`, `chainIndex`, `address`, `txStatus` (`1` Pending · `2` Success · `3` Failed), `failReason`.
