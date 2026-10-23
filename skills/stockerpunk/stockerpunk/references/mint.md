# Collection and Mint

## `spunk collection`

Shows the collection state. Works before and after launch.

```bash
spunk collection --json
```

```json
{ "success": true, "live": true, "minted": 1280, "supply": 5000,
  "priceUsd": 1, "priceBnb": "0.00133", "maxPerWallet": 5 }
```

The **first mint per wallet is free**; mints 2 through 5 cost **0.00133 BNB** each (the contract refunds any overpay). `priceBnb`/`priceUsd` above is the standard per-mint price.

Before launch it returns `{ "live": false, "supply": 5000, "priceUsd": 1, "firstMintFree": true }` so you can still describe it.

## `spunk mint --count <n>`

Builds the mint transaction. It does **not** sign — it prints a ready `baw contract-call preview` call.

```bash
spunk mint --count 2 --json
```

- `n` must be 1–5 and must not push the wallet over 5 total.
- The wallet must hold a `.ai` Agent ID (checked on-chain). No Agent ID → `NO_AGENT_ID`.
- Rarity is a gacha roll resolved **on-chain at mint** — never promise a tier.

Output:

```json
{ "success": true, "count": 2, "valueWei": "6200000000000000", "valueBnb": "0.0062",
  "to": "0x…nft", "data": "0xa0712d68…",
  "bawPreview": "baw contract-call preview --binanceChainId 56 --from <addr> --to 0x…nft --value 6200000000000000 --inputData 0xa0712d68… --json" }
```

### The flow (always)
1. Run the `bawPreview` command it prints.
2. Show the user the parsed transaction, risks and the BNB cost.
3. On an explicit "yes", run `baw contract-call execute --requestId <id> --json`.
4. Report the tx hash. The newly minted punks appear under `spunk punks`.

Before launch, `mint` returns `{ "success": false, "error": "NOT_LIVE" }` — tell the user minting opens at
launch; nothing is signed.
