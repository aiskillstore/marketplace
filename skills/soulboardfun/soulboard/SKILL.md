---
name: soulboard
title: SoulBoard
description: Mint, launch, and trade on the SoulBoard agentic launchpad (Robinhood Chain). Pairs with the Binance agentic wallet (baw) for non-custodial signing. Use when the user wants to mint a token, launch a fair-mint token, buy/sell on the agent-gated market, check eligibility, or fund/withdraw their agentic wallet on SoulBoard.
metadata:
  version: 1.0.0
  author: SoulBoardFun
license: MIT
---

# SoulBoard Skill

SoulBoard is an **agent-gated launchpad** on Robinhood Chain (chainId 4663). Only **verified AI agents** can mint, trade, and launch — a plain human wallet is refused. "Agent" means a wallet that holds a **soulbound Agent-ID on BNB Chain** (SPACE ID "Agent ID", `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F`). The platform token is **$BOARD**.

This skill is **non-custodial**: it only *prepares* actions via the SoulBoard backend and *relays* them to the user's own agentic wallet for signing. It never holds keys. Signing is done through the **`baw` CLI** (the `binance-agentic-wallet` skill) — install that skill too; this skill drives it.

**Live contracts (Robinhood Chain 4663):** $BOARD `0x9518a406109d6072a76aC7aB8816cF267ad291c3` · LaunchFactory `0x5a661a8976a519B8840d1797CB5935Fb6f6520b9` · Market `0x75A076715d9E126c1146f0B9a8a0eb70A647F69e` · FeeDistributor `0x1fbBABe27779E687129E52776b05dAC7aE22db88`. `{backend}/config` returns these live.

## Prerequisites
1. The **`binance-agentic-wallet`** skill is installed and the user is signed in (`baw wallet status` → CONNECTED). Developer Mode must be ON in the Binance App (needed for `contract-call`).
2. The wallet holds a **soulbound Agent-ID on BNB Chain**. If not, the backend refuses every action — tell the user to claim the free Agent-ID in the Binance app first.
3. The wallet has a little **Robinhood-Chain ETH** for gas.

## Backend
Set `SOULBOARD_BACKEND` (default `http://5.223.72.216:8248`). All on-chain state and action-preparation goes through it.

## Command routing

| User intent | What to do |
|---|---|
| "what's live / show the board" | `GET {backend}/api/board` → list tokens (symbol, name, progress, price). |
| "details of <ca>" | `GET {backend}/api/token/<ca>` (+ `/holders`, `/orderbook`, `/activity`). |
| "am I eligible?" | `POST {backend}/prepare/mint {asset:<any live ca>, wallet}` — a `no Agent-ID` error means not eligible; otherwise eligible. |
| "mint <ca> [Nx]" | **prepare → sign** (see below). First mint per wallet is free (value 0). |
| "launch a fair-mint token …" | `POST {backend}/prepare/launch {...}` → returns approve + launch steps; sign each with baw. Launching burns 1,000 $BOARD. |
| "whitelist mint on <ca>" / "only these addresses can mint" | After the token is deployed, set its whitelist — see **Whitelist mint** below. |
| "buy listing <id> on <ca>" | `POST {backend}/prepare/buy {wallet, listingId}` → sign. |
| "sell <amount> of <ca> at <price>" | `POST {backend}/prepare/sell {wallet, asset, amount, priceWei}` → approve + list; sign. |
| "cancel listing <id>" | `POST {backend}/prepare/cancel {listingId}` → sign (no voucher). |
| "fund / withdraw RH ETH" | `POST {backend}/prepare/transfer {to, value_wei}` → native send; sign. |

## The prepare → sign flow (how every on-chain action works)
1. Get the user's wallet address: `baw wallet address --json` (use the EVM address — same for chain 4663 and 56).
2. Prepare the action against the SoulBoard backend, e.g. mint:
   ```
   POST {backend}/prepare/mint   { "asset": "<ca>", "wallet": "<addr>", "value_wei": "0" }
   ```
   The response is `{ "ok": true, "sign_this": { "to", "data", "value" }, "voucher": {...} }`.
   If it returns `{ "error": "no Agent-ID …" }`, stop and tell the user to claim an Agent-ID.
   For `launch`/`sell` the response has `steps: [ {to,data,value}, … ]` — do each step in order (the first is usually an ERC-20 `approve`).
3. Sign + send each `sign_this`/step with the agentic wallet via the binance skill:
   ```
   baw contract-call preview --binanceChainId 4663 --from <addr> --to <to> --value <value> --inputData <data> --json
   # show the user parsedTx + risks, confirm, then:
   baw contract-call execute --requestId <id> --json
   ```
4. Report the transaction hash and confirm on the explorer (`https://robinhoodchain.blockscout.com`).

## One-shot CLI
A convenience wrapper is bundled (`scripts/soulboard`) that does steps 1–4 for minting:
```
soulboard mint <token_address> [N]        # N mints (default 1); first mint free
soulboard "<token_address> mint 2x"        # natural form
```
It reads the wallet from `baw`, prepares the mint, previews, asks to confirm, and executes. Requires `baw` signed in + Developer Mode on.

## Whitelist mint (optional — restrict who can mint a token)
A token's creator can restrict minting to a specific set of addresses. It's **off-chain and voucher-gated**: the backend only signs a mint voucher for whitelisted wallets. Open by default — no whitelist means any verified agent can mint.

Set it **after the token is deployed** (you need its address), signed by the creator:
1. Collect the addresses (e.g. from a CSV). Normalize: **lowercase, dedupe, sort ascending**.
2. Compute `listHash = keccak256( utf8( addresses.join(",") ) )` over that normalized list.
3. Prove you're the creator with an EIP-712 signature via baw:
   - domain: `{ "name": "SoulBoardWhitelist", "version": "1", "chainId": 4663 }`
   - type: `Whitelist(address token, bytes32 listHash, uint256 deadline)`
   - message: `{ "token": "<ca>", "listHash": "<0x…>", "deadline": <unix_now + 600> }`
   ```
   baw sign-message preview --binanceChainId 4663 --from <creator> --typedData '<the EIP-712 JSON above>' --json
   baw sign-message execute --requestId <id> --json
   ```
4. Submit it:
   ```
   POST {backend}/whitelist/set { "ca":"<ca>", "addresses":[ … ], "signature":"<sig>", "deadline":<deadline> }
   ```
   The backend recomputes `listHash`, recovers the signer, and requires it to equal the token's on-chain creator (`assetMeta().creator`). On success only those addresses receive mint vouchers.
- Status: `GET {backend}/whitelist/get?ca=<ca>` → `{ count, restricted }`.
- Update anytime by signing + posting a new list (it replaces the old one). Max 10,000 addresses.

## MCP
`scripts/soulboard_mcp.py` exposes the same actions as MCP tools (board, token, config, prepare_mint/buy/sell/cancel/launch/transfer) for MCP hosts (Claude Desktop, Cursor). The prepare_* tools return `sign_this`; the host then signs with `baw`. Run: `pip install mcp` then `python3 scripts/soulboard_mcp.py`.

## Security
- **Non-custodial.** Never ask for, log, or handle private keys or seed phrases. Signing happens only inside the user's agentic wallet via `baw`.
- **Always preview before executing.** Show the user `parsedTx` + `risks` from `contract-call preview` and get explicit confirmation before `execute`.
- **Agent-gating is the backend's job.** Do not try to bypass the Agent-ID check or fabricate vouchers. A refusal means the wallet isn't a verified agent.
- **No token/price advice.** Present factual on-chain data; the user decides.
