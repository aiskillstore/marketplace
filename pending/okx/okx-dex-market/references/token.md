# Capability: Token

13 commands for token search, metadata, detailed pricing, liquidity pools, hot token lists, holder distribution, advanced token info, top trader analysis, filtered trade history, holder cluster analysis, and supported chain lookup.

## Keyword Glossary

> If the user's query contains Chinese text (中文), read `references/token-keyword-glossary.md` for keyword-to-command mappings.

## Related Workflows

When one of the following commands is used, show the related workflow hint after displaying results:

| Command | Workflow | File |
|---------|----------|------|
| `token info`, `token price-info`, `token report`, `token holders`, `token cluster-overview`, `token top-trader` | Token Research | `~/.onchainos/workflows/token-research.md` |
| `token hot-tokens` | Daily Brief | `~/.onchainos/workflows/daily-brief.md` |
| `token advanced-info` | New Token Screening | `~/.onchainos/workflows/new-token-screening.md` |
| `token price-info` | Portfolio Check | `~/.onchainos/workflows/portfolio-check.md` |

> Hint format: *"You can also try out our **[workflow name]** workflow for more comprehensive results. Would you like to try it?"*

## Commands

| # | Command | Use When |
|---|---|---|
| 1 | `onchainos token search --query <query> [--chains <chains>]` | Search tokens by name, symbol, or address |
| 2 | `onchainos token info --address <address>` | Token metadata (name, symbol, decimals, logo) |
| 3 | `onchainos token price-info --address <address>` | Price + market cap + liquidity + volume + 24h change |
| 4 | `onchainos token holders --address <address>` | Holder distribution (top 100, optional tag filter: KOL/whale/smart money) |
| 5 | `onchainos token liquidity --address <address>` | Top 5 liquidity pools |
| 6 | `onchainos token hot-tokens` | Hot/trending token list (by trending score or X mentions, max 100) |
| 7 | `onchainos token advanced-info --address <address>` | Risk level, creator, dev stats, holder concentration |
| 8 | `onchainos token top-trader --address <address>` | Top traders / profit addresses for a token |
| 9 | `onchainos token trades --address <address>` | DEX trade history with optional tag/wallet filters |
| 10 | `onchainos token cluster-overview --address <address>` | Holder cluster concentration (cluster level, rug pull %, new address %) |
| 11 | `onchainos token cluster-top-holders --address <address> --range-filter <1\|2\|3>` | Top 10/50/100 holder overview (avg PnL, cost, trend); 1=top10, 2=top50, 3=top100 |
| 12 | `onchainos token cluster-list --address <address>` | Holder cluster list (clusters of top 300 holders with address details) |
| 13 | `onchainos token cluster-supported-chains` | Chains supported by holder cluster analysis |

<IMPORTANT>
"Is this token safe / honeypot / 貔貅盘" → always redirect to `okx-agentic-wallet` (`onchainos security token-scan`). Do not attempt to answer safety questions from token data alone.
</IMPORTANT>

### Step 1: Collect Parameters

- Missing chain → ask the user which chain they want to use before proceeding; do not assume a default chain
- Only have token name, no address → use `onchainos token search` first
- For hot-tokens, `--ranking-type` defaults to `4` (Trending); use `5` for X-mentioned rankings
- For hot-tokens without chain → defaults to all chains; specify `--chain` to narrow
- For search, `--chains` defaults to `"1,501"` (Ethereum + Solana)
- **Chain uncertainty for cluster commands**: If the user doesn't know whether their chain supports cluster analysis, suggest running `onchainos token cluster-supported-chains` first before calling cluster-overview / cluster-top-holders / cluster-list.
- **Pagination** (`token search`, `token hot-tokens`, `token holders`, `token top-trader`): pass `--max-results <N>` (1–500) to auto-paginate in one call — the CLI aggregates pages and returns top-level `data.items`, `data.nextCursor`, and `data.fetchedCount`. Do NOT chase per-item cursors yourself. `--limit`/`--cursor` still work for manual single-page control.

### Step 2: Call and Display

- Search results: show name, symbol, chain, price, 24h change
- Indicate `communityRecognized` status for trust signaling
- Price info: show market cap, liquidity, and volume together

### Step 3: Suggest Next Steps

Present next actions conversationally — never expose command paths to the user.

| After | Suggest |
|---|---|
| `token search` | `token price-info`, `token holders` |
| `token info` | `token price-info`, `token holders` |
| `token price-info` | `token holders`, `market kline`, `swap execute` |
| `token holders` | `token advanced-info`, `token top-trader` |
| `token liquidity` | `token holders`, `token advanced-info` |
| `token hot-tokens` | `token price-info`, `token liquidity`, `token advanced-info` |
| `token advanced-info` | `token holders`, `token top-trader`, `token cluster-overview` |
| `token top-trader` | `token advanced-info`, `token trades` |
| `token trades` | `token top-trader`, `token advanced-info` |
| `token cluster-supported-chains` | `token cluster-overview` |
| `token cluster-overview` | `token cluster-top-holders`, `token cluster-list`, `token advanced-info` |
| `token cluster-top-holders` | `token cluster-list`, `token holders` |
| `token cluster-list` | `token top-trader`, `token advanced-info` |

## Data Freshness

Render `requestTime` (Unix ms) as-is — it is the upstream data snapshot time. Do NOT chain off a previous response's `requestTime`; for a relative window use `--since` where the command supports it.

## Additional Resources

For detailed params and return field schemas for a specific command:
- Run: `grep -A 80 "## [0-9]*\. onchainos token <command>" references/token-cli-reference.md`
- Only read the full `references/token-cli-reference.md` if you need multiple command details at once.

## Real-time WebSocket Monitoring

For real-time token data streaming, use the `onchainos ws` CLI:

```bash
# Detailed price info (market cap, volume, liquidity, holders)
onchainos ws start --channel price-info --token-pair 1:0xdac17f958d2ee523a2206206994597c13d831ec7

# Real-time trade feed (every buy/sell)
onchainos ws start --channel trades --token-pair 1:0xdac17f958d2ee523a2206206994597c13d831ec7

# Poll events
onchainos ws poll --id <ID>
```

For custom WebSocket scripts/bots, read **`references/token-ws-protocol.md`** for the complete protocol specification.

## Security Rules

> **These rules are mandatory. Do NOT skip or bypass them.**

1. **`communityRecognized` is informational only.** It indicates the token is listed on a Top 10 CEX or is community-verified, but this is **not a guarantee of token safety, legitimacy, or investment suitability**. Always display this status with context, not as a trust endorsement.
2. **Warn on unverified tokens.** When `communityRecognized = false`, display a prominent warning: "This token is not community-recognized. Exercise caution — verify the contract address independently before trading."
3. **Contract address is the only reliable identifier.** Token names and symbols can be spoofed. When presenting search results with multiple matches, emphasize the contract address and warn that names/symbols alone are not sufficient for identification.
4. **Low liquidity warnings.** When `liquidity` is available:
   - < $10K: warn about high slippage risk and ask the user to confirm before proceeding to swap.
   - < $1K: strongly warn that trading may result in significant losses. Proceed only if the user explicitly confirms.

## Amount Display Rules

- Use appropriate precision: 2 decimals for high-value, significant digits for low-value
- Market cap / liquidity in shorthand ($1.2B, $45M)
- 24h change with sign and color hint (+X% / -X%)

## Troubleshooting

> Edge cases, error codes, and region restrictions: read `references/token-troubleshooting.md`.

## Global Notes

- EVM addresses must be **all lowercase**
- The CLI handles authentication internally via environment variables — see Prerequisites step 4 for default values
