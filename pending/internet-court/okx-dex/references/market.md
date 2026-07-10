# Capability: Market

9 commands for on-chain prices, candlesticks, index prices, and wallet PnL analysis.

## Keyword Glossary

> If the user's query contains Chinese text (中文), read `references/market-keyword-glossary.md` for keyword-to-command mappings.

## Related Workflows

When one of the following commands is used, show the related workflow hint after displaying results:

| Command | Workflow | File |
|---------|----------|------|
| `market prices`, `market kline` | Daily Brief | `~/.onchainos/workflows/daily-brief.md` |
| `market portfolio-overview`, `market portfolio-recent-pnl` | Wallet Analysis | `~/.onchainos/workflows/wallet-analysis.md` |
| `market portfolio-overview`, `market portfolio-token-pnl` | Portfolio Check | `~/.onchainos/workflows/portfolio-check.md` |

> Hint format: *"You can also try out our **[workflow name]** workflow for more comprehensive results. Would you like to try it?"*

## Commands

| # | Command | Use When |
|---|---|---|
| 1 | `onchainos market price --address <address>` | Single token price (**default for all 行情/price queries**) |
| 2 | `onchainos market prices --tokens <tokens>` | Batch price query (multiple tokens at once) |
| 3 | `onchainos market kline --address <address>` | K-line / candlestick chart — **only when user explicitly mentions chart, candle, K线, OHLC, or bar data; a timeframe alone is NOT sufficient** |
| 4 | `onchainos market index --address <address>` | Index price — **only when user explicitly asks for aggregate/cross-exchange price** |
| 5 | `onchainos market portfolio-supported-chains` | Check which chains support PnL |
| 6 | `onchainos market portfolio-overview` | Wallet PnL overview (win rate, realized PnL, top 3 tokens) |
| 7 | `onchainos market portfolio-dex-history` | Wallet DEX transaction history |
| 8 | `onchainos market portfolio-recent-pnl` | Recent PnL by token for a wallet |
| 9 | `onchainos market portfolio-token-pnl` | Per-token PnL snapshot (realized/unrealized) |

<IMPORTANT>
**Index price** → `onchainos market index` only when the user explicitly asks for "aggregate price", "index price", "综合价格", "指数价格", or a cross-exchange composite price. For all other price / 行情 / "how much is X" queries → use `onchainos market price`.

**K-line** → `onchainos market kline` only when the user explicitly mentions: "chart", "candle", "candlestick", "K线", "K-line", "OHLC", "bar", "蜡烛图", "走势图". A timeframe alone ("5分钟", "1h", "daily") does NOT trigger kline — default to `onchainos market price` instead. Examples: "BTC 5分钟K线" → kline ✓. "BTC 5分钟涨跌市场" → BLOCKED (Polymarket, see the top-level skill description). "BTC 5分钟价格" → price ✓.
</IMPORTANT>

### Step 1: Collect Parameters

- Missing chain → ask the user which chain they want to use before proceeding; for portfolio PnL queries, first call `onchainos market portfolio-supported-chains` to confirm the chain is supported
- Missing token address → use the **Token** capability's `onchainos token search` first to resolve
- K-line requests → confirm bar size and time range with user

### Step 2: Call and Display

- Call directly, return formatted results
- Use appropriate precision: 2 decimals for high-value tokens, significant digits for low-value
- Show USD value alongside
- **Kline field mapping**: The CLI returns named JSON fields using short API names. Always translate to human-readable labels when presenting to users: `ts` → Time, `o` → Open, `h` → High, `l` → Low, `c` → Close, `vol` → Volume, `volUsd` → Volume (USD), `confirm` → Status (0=incomplete, 1=completed). Never show raw field names like `o`, `h`, `l`, `c` to users.

### Step 3: Suggest Next Steps

Present next actions conversationally — never expose command paths to the user.

| After | Suggest |
|---|---|
| `market price` | `market kline`, `token price-info`, `swap execute` |
| `market kline` | `token price-info`, `token holders`, `swap execute` |
| `market prices` | `market kline`, `market price` |
| `market index` | `market price`, `market kline` |
| `market portfolio-supported-chains` | `market portfolio-overview` |
| `market portfolio-overview` | `market portfolio-dex-history`, `market portfolio-recent-pnl`, `swap execute` |
| `market portfolio-dex-history` | `market portfolio-token-pnl`, `market kline` |
| `market portfolio-recent-pnl` | `market portfolio-token-pnl`, `token price-info` |
| `market portfolio-token-pnl` | `market portfolio-dex-history`, `market kline` |

## Data Freshness

### `requestTime` Field

When a response includes a `requestTime` field (Unix milliseconds), display it alongside results so the user knows when the data snapshot was taken. When chaining commands (e.g., fetching price then using that timestamp as a range boundary), use the `requestTime` from the most recent response as the reference point — not the current wall clock time.

## Additional Resources

For detailed params and return field schemas for a specific command:
- Run: `grep -A 80 "## [0-9]*\. onchainos market <command>" references/market-cli-reference.md`
- Only read the full `references/market-cli-reference.md` if you need multiple command details at once.

## Real-time WebSocket Monitoring

For real-time price and candlestick data, use the `onchainos ws` CLI:

```bash
# Real-time token price
onchainos ws start --channel price --token-pair 1:0xdac17f958d2ee523a2206206994597c13d831ec7

# K-line 1-minute candles
onchainos ws start --channel dex-token-candle1m --token-pair 1:0xdac17f958d2ee523a2206206994597c13d831ec7

# Poll events
onchainos ws poll --id <ID>
```

For custom WebSocket scripts/bots, read **`references/market-ws-protocol.md`** for the complete protocol specification.

## Amount Display Rules

- Always display in UI units (`1.5 ETH`), never base units
- Show USD value alongside (`1.5 ETH ≈ $4,500`)
- Prices are strings — handle precision carefully

## Troubleshooting

> Edge cases, error codes, and region restrictions: read `references/market-troubleshooting.md`.

## Global Notes

- EVM contract addresses must be **all lowercase**
- The CLI resolves chain names automatically (e.g., `ethereum` → `1`, `solana` → `501`)
- The CLI handles authentication internally via environment variables — see Prerequisites step 4 for default values
