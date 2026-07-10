# Public-Address Portfolio — CLI Reference

Syntax, parameters, and key return fields for the 4 `onchainos portfolio` subcommands. Verify with `onchainos portfolio <subcommand> --help` when unsure.

## `portfolio chains`

Supported chains (no params). Returns `name`, `shortName`, `chainIndex`, `logoUrl`.

## `portfolio total-value`

```bash
onchainos portfolio total-value --address <address> --chains <chains> [--asset-type <0|1|2>] [--exclude-risk <bool>]
```

`--chains` comma-separated (names or IDs). `--asset-type` default `0` (all / tokens / DeFi). `--exclude-risk` default `true` (ETH/BSC/SOL/BASE only). Returns `totalValue` (USD).

## `portfolio all-balances`

```bash
onchainos portfolio all-balances --address <address> --chains <chains> [--exclude-risk <0|1>] [--filter <0|1>]
```

`--chains` max 50. `--exclude-risk` default `0` (filter risky; ETH/BSC/SOL/BASE only). `--filter` default `0` (filters risk/custom/passive); `1` returns all incl. risk tokens (use when scanning for security risks). Returns `tokenAssets[]`: `chainIndex`, `tokenContractAddress`, `symbol`, `balance` (UI units), `rawBalance` (base units), `tokenPrice`, `isRiskToken`.

## `portfolio token-balances`

```bash
onchainos portfolio token-balances --address <address> --tokens <tokens> [--exclude-risk <0|1>]
```

`--tokens`: `chainIndex:tokenAddress` pairs, comma-separated, max 20 (empty address = native, e.g. `196:` for native OKB). Returns the same `tokenAssets[]` schema as `all-balances`.

## Examples

```bash
onchainos portfolio total-value --address 0xYourWallet --chains "xlayer,solana"
onchainos portfolio all-balances --address 0xYourWallet --chains "xlayer,solana,ethereum"
onchainos portfolio token-balances --address 0xYourWallet --tokens "196:,196:0x74b7f16337b8972027f6196a17a631ac6de26d22"
```
