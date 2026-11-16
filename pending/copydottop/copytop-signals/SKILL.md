---
name: copytop-signals
description: Read live crypto trading signals, trader intel and alerts from copy.top (top traders on fomo, pump.fun and hyperliquid). Use when the user asks what smart traders are buying, wants to vet a trader or a coin, wants a leaderboard, or wants alerts when several top traders buy the same coin. Read-only, no wallet, no key needed.
---

# copy.top signals

copy.top tracks what top traders buy and sell on fomo, pump.fun and hyperliquid. Its MCP server is public and read-only: it cannot see an account or place an order.

## Connect

If the `copytop` MCP server is not connected yet, add it:

```
claude mcp add --transport http copytop https://copy.top/mcp
```

Any MCP client: `{"mcpServers":{"copytop":{"type":"http","url":"https://copy.top/mcp"}}}`. Use the address without `www`.

No MCP client? Call it over HTTP:

```
curl -s https://copy.top/mcp -H "content-type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_hot_coins","arguments":{"window":"1h"}}}'
```

## Tools

| Tool | Use it for |
|---|---|
| `search` | resolve a name, @handle, $ticker or address first |
| `get_hot_coins` | the signal feed: coins tracked traders are buying now (1h or 24h, optional max market cap) |
| `get_alerts` | events since a cursor: confluence, big trade, thesis |
| `get_live_trades` | the raw tape of the latest buys and sells |
| `get_hot_index` | coins ranked 0-100 by attention (traders, callers, x activity) |
| `get_money_flow` | coins ranked by dollars bought or sold |
| `get_dex_paid` | coins whose team just paid for a dexscreener profile |
| `get_leaderboard` | ranked traders (window, sort, platform fomo or pumpfun, fair play filter) |
| `get_trader` | one trader: pnl, roi, win rate, fair play, open positions, latest trades, theses |
| `get_token` | one coin: price, market cap, who holds it, who sold, theses |
| `get_theses` | traders' written reasons for holding a coin |

## How to work

1. Resolve names with `search`, then pass the `handle` or `chain` + `address` the tools return. Never invent an address.
2. A handle starting with `pf_` is a pump.fun account; the others are fomo traders.
3. To vet a signal: `get_hot_coins` → `get_token` on the coin → `get_trader` on its first buyers. Check `fairPlay` (clean, watch, flagged) and whether top traders are still in (`topStillIn`) before calling it strong.
4. For alerts: call `get_alerts`, keep the `cursor` it returns, pass it back as `since` on the next call. Once a minute is plenty. Set `min_top_traders`, `min_trade_usd` and `max_mcap_usd` to the user's taste.
5. Every trader and coin result carries a `url`. Give it to the user when they want to copy a trader or buy: orders are confirmed by the user on copy.top, never by you.

## Limits

- 20 calls a minute without a key. `search`, `get_trader` and `get_token` are limited to 6 a minute. On "too many", wait and retry.
- Figures are data, not advice. Past performance does not predict results. Say so when the user is about to act on a signal.
