# StockerPunk — Agent Toolkit

[Website](https://stockerpunk.com) · [X / Twitter](https://x.com/StockerPunk) · [GitHub](https://github.com/StockerPunk/cli)

Mint and manage **StockerPunk** from the terminal or straight from your AI assistant.

StockerPunk is an agent-native pixel-punk collection on **BNB Chain**. Each NFT is an AI broker that mines
real tokenized stock (NVDA) into its own **ERC-6551** wallet. Minting is gated to **Binance Agentic Wallets**
holding a `.ai` Agent ID.

Everything here reads the chain and builds calldata. **Signing always goes through your Agentic Wallet, so no
keys are ever shared.**

This repo ships three things:

- **Agent skill** — drop-in skill so your agent can preflight, mint, list and harvest StockerPunks by name.
- **`spunk` CLI** — a dependency-free command line that reads the chain and builds calldata.
- **MCP server** (`mcp/`) — bridge StockerPunk into Claude, Cursor, or any MCP client.

---

## Prerequisites

1. In the **Binance App**, open your Agentic Wallet, claim a `.ai` **Agent ID**, and enable **Developer Mode**.
2. Install the Agentic Wallet CLI and sign in once:

```bash
npm i -g @binance/agentic-wallet
baw auth signin
```

---

## Agent skill — for Binance agents

Drop the skill into your agent so it knows how to preflight, mint, list and harvest StockerPunks by name.

```bash
npx skills add stockerpunk/cli
```

---

## Command line — `spunk` CLI

A dependency-free CLI that reads the chain and builds calldata. It never holds keys; signing goes through `baw`.

```bash
npm i -g github:StockerPunk/cli
```

```bash
spunk preflight        # sign-in, Dev Mode, Agent ID, slots
spunk collection       # supply, price, progress
spunk mint --count 2   # build a mint, then confirm in baw
spunk punks            # your punks: rarity, weight, NVDA
```

---

## MCP server — Claude, Cursor, any MCP client

Bridge StockerPunk into your AI assistant. Install the server, add it to your MCP config, then just ask your
assistant to mint.

```bash
npm i -g github:StockerPunk/mcp
```

```json
{
  "mcpServers": {
    "stockerpunk": { "command": "spunk-mcp" }
  }
}
```

**Mint from your assistant**

- Ask it to check the StockerPunk collection, and it calls `spunk_collection`.
- Ask it to mint a StockerPunk, and it builds the transaction and shows you the cost and rarity odds.
- Confirm. Signing goes through your Agentic Wallet in the Binance App. The punk starts mining once activated.

---

## Contracts — BNB Chain (chainId 56)

| Contract | Address |
| --- | --- |
| StockerPunk (ERC-721) | `0xfD81e3e5853553D43e4BD3D0bCDE98c69E86c98c` |
| $SPUNK (ERC-20) | `0x5d392B52868077b9Ba5391eeF734820865CD0de6` |
| MiningVault | `0x50F03C2034942f1C032a466F5dBb3a1fc9477504` |
| SpunkAccount — ERC-6551 impl | `0x29dDe0d0f1D2910806901fa7900BE96cCd41DfbA` |
| Agent-ID gate — SPACE ID `.ai` | `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F` |
| NVDA reward — bStock NVDAB | `0x02Fca66C1D1aFB4E2A7884261eB00F63598a7436` |

First mint per wallet is **free**, then **0.00133 BNB** each, capped at **5** per wallet, 5,000 total. The
authoritative price is `mintPriceWei()` on-chain — the CLI reads it live, so always confirm `valueWei` in the
Agentic Wallet preview before signing. Only `.ai` Agent-ID holders can mint; a plain EVM wallet reverts.

---

## License

MIT
