# Capability: Trenches

7 commands for meme token discovery, developer analysis, bundle detection, and co-investor tracking.

## Step 0 — Read vs Write Re-Route (run before every other step)

This capability is **READ-ONLY research**. Before running any `onchainos memepump` command, re-classify the user's intent as read or write:

- **WRITE intent → STOP and invoke `okx-dapp-discovery`** (which installs `pump-fun-plugin`):
  - English action verbs: `buy`, `sell`, `swap`, `snipe`, `ape`, `purchase`, `trade` + a pump.fun token / address
  - Chinese action verbs: `买`, `卖`, `购买`, `兑换`, `交换`, `狙击`, `梭哈`, `帮我买`, `我想买`, `买最火的币`, `买这个`, `买一些`
  - Examples that MUST re-route: "snipe this pump.fun token 0xabc", "狙击 pump.fun 上的 0xabc", "买这个 pump.fun token", "帮我买最火的 pump.fun 币"
  - **狙击 disambiguation**: bare verb "狙击 + token/address" is a write op (sniping action) → re-route. ONLY when paired with analytical nouns ("捆绑狙击者", "sniper detection", "who sniped", "狙击者分析") does it stay here as a read op.

- **READ intent → stay in this capability** (default for all `memepump` commands):
  - Dev reputation / launch history / rug history (`开发者信息`, `dev history`, `开发者跑路记录`)
  - Bundle / sniper detection (`捆绑狙击者`, `bundler analysis`, `who sniped this`)
  - Bonding curve progress, similar tokens by same dev, who-aped/同车 wallets
  - Token list scans (`memepump tokens`, `扫链`, `打狗`, `新盘`)

If you have already started running commands and only then realise the user's intent is a write op, halt mid-flow and invoke `okx-dapp-discovery` — do not run any `swap`/`execute` from inside this capability.

## Keyword Glossary

> If the user's query contains Chinese text (中文) or mentions a protocol name (pumpfun, bonkers, believe, etc.), read `references/trenches-keyword-glossary.md` for keyword-to-command mappings and protocol ID lookups.

## Related Workflows

When one of the following commands is used, show the related workflow hint after displaying results:

| Command | Workflow | File |
|---------|----------|------|
| `memepump tokens` | New Token Screening | `~/.onchainos/workflows/new-token-screening.md` |
| `memepump tokens --stage MIGRATED` | Daily Brief | `~/.onchainos/workflows/daily-brief.md` |
| `memepump token-dev-info`, `memepump token-bundle-info` | Smart Money Signals | `~/.onchainos/workflows/smart-money-signals.md` |
| `memepump token-details`, `memepump token-dev-info`, `memepump token-bundle-info` | Token Research | `~/.onchainos/workflows/token-research.md` |

> Hint format: *"You can also try out our **[workflow name]** workflow for more comprehensive results. Would you like to try it?"*

## Commands

| # | Command | Use When |
|---|---|---|
| 1 | `onchainos memepump chains` | Discover supported chains and protocols |
| 2 | `onchainos memepump tokens --chain <chain> [--stage <stage>]` | Browse/filter meme tokens by stage (default: NEW) — **trenches / 扫链** |
| 3 | `onchainos memepump token-details --address <address>` | Deep-dive into a specific meme token |
| 4 | `onchainos memepump token-dev-info --address <address>` | Developer reputation and holding info |
| 5 | `onchainos memepump similar-tokens --address <address>` | Find similar tokens by same creator |
| 6 | `onchainos memepump token-bundle-info --address <address>` | Bundle/sniper analysis |
| 7 | `onchainos memepump aped-wallet --address <address>` | Aped (same-car/同车) wallet list |

### Step 1: Collect Parameters

- Missing chain → default to Solana (`--chain solana`); verify support with `onchainos memepump chains` first
- Missing `--stage` for memepump-tokens → default to `NEW`; only ask if the user's intent clearly points to a different stage
- Stage coverage: `NEW` and `MIGRATING` include tokens created within the last **24 h**; `MIGRATED` includes tokens whose migration completed within the last **3 days**
- User mentions a protocol name → first call `onchainos memepump chains` to get the protocol ID, then pass `--protocol-id-list <id>` to `memepump-tokens`. Do NOT use the **Token** capability to search for protocol names as tokens.

### Step 2: Call and Display

- Translate field names per the Keyword Glossary — never dump raw JSON keys
- For `memepump-token-dev-info`, present as a developer reputation report
- For `memepump-token-details`, present as a token safety summary highlighting red/green flags
- When listing tokens from `memepump-tokens`, never merge or deduplicate entries that share the same symbol. Different tokens can have identical symbols but different contract addresses — each is a distinct token and must be shown separately. Always include the contract address to distinguish them.
- Translate field names: `top10HoldingsPercent` → "top-10 holder concentration", `rugPullCount` → "rug pull count", `bondingPercent` → "bonding curve progress"

### Step 3: Suggest Next Steps

Present next actions conversationally — never expose command paths to the user.

| After | Suggest |
|---|---|
| `memepump chains` | `memepump tokens` |
| `memepump tokens` | `memepump token-details`, `memepump token-dev-info` |
| `memepump token-details` | `memepump token-dev-info`, `memepump similar-tokens`, `memepump token-bundle-info` |
| `memepump token-dev-info` | `memepump token-bundle-info`, `market kline` |
| `memepump similar-tokens` | `memepump token-details` |
| `memepump token-bundle-info` | `memepump aped-wallet` |
| `memepump aped-wallet` | `token advanced-info`, `market kline`, `swap execute` |

## Data Freshness

Render `requestTime` (Unix ms) as-is — the upstream snapshot time. Do NOT chain off a previous response's `requestTime`.

## Additional Resources

For detailed params and return field schemas for a specific command:
- Run: `grep -A 80 "## [0-9]*\. onchainos memepump <command>" references/trenches-cli-reference.md`
- Only read the full `references/trenches-cli-reference.md` if you need multiple command details at once.

## Real-time WebSocket Monitoring

For real-time meme token scanning, use the `onchainos ws` CLI:

```bash
# New meme token launches on Solana
onchainos ws start --channel dex-market-memepump-new-token-openapi --chain-index 501

# Meme token metric updates (market cap, volume, bonding curve)
onchainos ws start --channel dex-market-memepump-update-metrics-openapi --chain-index 501

# Poll events
onchainos ws poll --id <ID>
```

For custom WebSocket scripts/bots, read **`references/trenches-ws-protocol.md`** for the complete protocol specification.

## Troubleshooting

> Edge cases, error codes, and region restrictions: read `references/trenches-troubleshooting.md`.
