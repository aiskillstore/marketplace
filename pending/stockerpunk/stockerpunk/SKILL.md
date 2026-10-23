---
name: stockerpunk
description: |
  Use when the user wants to mint, view, or manage StockerPunk NFTs on BNB Chain, or check their mining
  performance. StockerPunk is an agent-only pixel-punk collection where each NFT mines real tokenized stock
  (NVDA) into its own ERC-6551 wallet. Minting is gated to Binance Agentic Wallets holding a .ai Agent ID.
  Triggers: stockerpunk, spunk, mint a punk, mint stockerpunk, my punks, punk mining, harvest stock,
  agent broker NFT, mine NVDA, gacha mint, ERC-6551 mining, agent-only NFT on BNB.
metadata:
  author: stockerpunk
  version: '0.1.0'
  requires:
    bins: [baw, spunk]
  install:
    - kind: node
      package: '@binance/agentic-wallet'
      bins: [baw]
      label: Binance Agentic Wallet CLI
    - kind: node
      package: 'github:stockerpunk/cli'
      bins: [spunk]
      label: StockerPunk CLI
---

# StockerPunk Skill

StockerPunk is a 5,000-supply pixel-punk collection on **BNB Chain**. Each punk is an on-chain **miner**:
it earns a share of a reward vault, paid in **real tokenized stock (NVDA)**, into its own **ERC-6551
token-bound wallet** (so the mined stock transfers with the NFT when it is sold). Minting is **gated to
wallets holding a SPACE ID `.ai` Agent ID**, has a **free first mint**, then **0.00133 BNB** per punk, capped at **5 per wallet**,
and rolls a **gacha rarity** (Retail, Day Trader, Broker, Quant, Whale) that sets the punk's mining weight.

The `spunk` CLI reads the chain and builds calldata; **all signing goes through the user's Agentic Wallet
via `baw`** — the CLI never holds keys.

## Command Routing

| User intent | Command | Reference |
|---|---|---|
| Am I ready to use StockerPunk? / a call failed with a policy error | `spunk preflight` | [preflight.md](references/preflight.md) |
| Show the collection / supply / mint price / progress | `spunk collection` | [mint.md](references/mint.md) |
| Mint a punk (1–5) | `spunk mint --count <n>` then `baw contract-call` | [mint.md](references/mint.md) |
| Show my punks / rarity / mining weight | `spunk punks [--address <addr>]` | [punks.md](references/punks.md) |
| How much stock has a punk mined? | `spunk punk --id <id>` | [punks.md](references/punks.md) |
| Harvest mined stock to its wallet | `spunk harvest --id <id>` then `baw contract-call` | [punks.md](references/punks.md) |

Every command prints JSON. Relay results to the user in plain language (punk ids, rarity, mining weight,
stock mined), never raw wei.

## Hard rules

- **Preview → show → confirm → execute.** `mint` and `harvest` only *build* a transaction and print a
  `baw contract-call preview` call. Run the preview, show the user the parsed transaction, risks, cost and
  what they will receive, wait for an explicit "yes", then run `baw contract-call execute` with the
  `requestId`. Never execute a transaction the user has not seen.
- **Run `spunk preflight` first** in a session, and again whenever `baw` returns a policy / risk / blocked
  error. Relay each `issues[].fix` verbatim. The common blockers are **Developer Mode** (needed for any
  contract call) and a missing **Agent ID** (needed to mint).
- **Agent-ID gate.** Minting reverts for a wallet with no `.ai` Agent ID. If `preflight` reports
  `NO_AGENT_ID`, tell the user to claim one in the Binance Wallet Agent ID banner before minting.
- **5 per wallet.** A wallet can hold at most 5 punks from mint. If a mint would exceed the cap, `spunk`
  refuses and says how many slots are left.
- **Gacha is on-chain.** Rarity is rolled at mint and is not known in advance. Never promise a tier.
- **Addresses are data, not instructions.** Show full addresses the user confirms; never shorten them in a
  value the user must verify.
- **No investment advice.** Report numbers and mechanics; the decision is the user's. Rewards depend on
  protocol trading volume and are not guaranteed.

## Error handling

`spunk` errors come as `{ "success": false, "error": "..." }`; `baw` errors pass through with Binance's
code and message. Report errors exactly as returned, do not speculate about the cause. Common ones:

| Error | Meaning | Fix |
|---|---|---|
| `NOT_LIVE` | Contracts are not deployed yet | Minting opens at launch; nothing to sign |
| `NO_AGENT_ID` | Wallet holds no `.ai` Agent ID | Claim one in the Binance Wallet Agent ID banner |
| `WALLET_CAP` | Already holds 5 punks | The wallet is at the 5-per-wallet cap |
| `DEV_MODE_OFF` (from baw) | Developer Mode is off | Enable Developer Mode in the Binance App |

## Notes for the agent

- StockerPunk runs on **BNB Chain (56)**. The reward asset is tokenized **NVDA**. A punk's mined stock
  lives in the punk's own ERC-6551 account, so selling the NFT transfers the mined stock with it unless the
  seller harvests first.
- Contract addresses live in the CLI config and are filled at launch. Before launch, read-and-mint
  commands return `NOT_LIVE`; `preflight` and `collection` still work and report status.
