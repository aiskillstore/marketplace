# Punks and Harvest

## `spunk punks [--address <addr>]`

Lists the punks a wallet holds, with rarity, mining weight and stock mined so far. Defaults to the
connected Agentic Wallet address.

```bash
spunk punks --json
```

```json
{ "success": true, "address": "0x…", "count": 2, "totalWeight": 6.5,
  "punks": [
    { "id": 42, "rarity": "Whale", "weight": 8.0, "minedNvda": "0.5040", "account": "0x…tba" },
    { "id": 77, "rarity": "Broker", "weight": 2.5, "minedNvda": "0.1628", "account": "0x…tba" }
  ] }
```

`account` is the punk's own ERC-6551 wallet, where its mined NVDA accrues.

## `spunk punk --id <id>`

One punk in detail (rarity, weight, mined NVDA, token-bound account).

## `spunk harvest --id <id>`

Builds a harvest transaction that moves the punk's mined NVDA into its ERC-6551 wallet (or to the owner,
per the contract). Like `mint`, it only prints a `baw contract-call preview` call — follow the
preview → confirm → execute flow. Harvesting is optional: if you sell a punk without harvesting, the
mined stock transfers with the NFT.

Before launch these return `{ "success": false, "error": "NOT_LIVE" }`.
