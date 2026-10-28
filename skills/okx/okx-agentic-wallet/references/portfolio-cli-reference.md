# Public-Address Portfolio — CLI Reference

## Commands

### `portfolio chains`

Supported chains (no params). Returns `name`, `shortName`, `chainIndex`, `logoUrl`.

### `portfolio total-value`

```bash
onchainos portfolio total-value --address <address> --chains <chains> [--asset-type <0|1|2>] [--exclude-risk <bool>]
```

`--chains` comma-separated (names or IDs). `--asset-type` default `0` (all / tokens / DeFi). `--exclude-risk` default `true` (ETH/BSC/SOL/BASE only). Returns `totalValue` (USD).

### `portfolio all-balances`

```bash
onchainos portfolio all-balances --address <address> --chains <chains> [--exclude-risk <0|1>] [--filter <0|1>]
```

`--chains` max 50. `--exclude-risk` default `0` (filter risky; ETH/BSC/SOL/BASE only). `--filter` default `0` (filters risk/custom/passive); `1` returns all incl. risk tokens (use when scanning for security risks). Returns `tokenAssets[]`: `chainIndex`, `tokenContractAddress`, `symbol`, `balance` (UI units), `rawBalance` (base units), `tokenPrice`, `isRiskToken`.

### `portfolio token-balances`

```bash
onchainos portfolio token-balances --address <address> --tokens <tokens> [--exclude-risk <0|1>]
```

`--tokens`: `chainIndex:tokenAddress` pairs, comma-separated, max 20 (empty address = native, e.g. `196:` for native OKB). Returns the same `tokenAssets[]` schema as `all-balances`.
