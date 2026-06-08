# longbridge-market-microstructure

Combines orderbook depth, tick-by-tick trades, and capital-flow data to assess bid-ask spread, order-flow imbalance, liquidity depth, and short-term institutional pressure for a single symbol.

> Simplified Chinese / Traditional Chinese / English.

## Workflow

1. Resolve the user's symbol to `<CODE>.<MARKET>` (e.g. `NVDA.US`, `700.HK`, `600519.SH`).
2. Run `longbridge --help` to see available subcommands; run `longbridge <subcommand> --help` to confirm current flags for each.
3. Fetch **orderbook depth** using the depth subcommand with `--format json`.
4. Fetch **recent tick trades** using the trades subcommand with `--format json` (check `--help` for count/range flags).
5. Fetch **capital-flow distribution** (large / medium / small orders) with `longbridge capital <SYMBOL> --format json`.
6. For **HK symbols only**, also fetch `longbridge brokers <SYMBOL> --format json` to identify large broker queues (potential institutional blocks).
7. Compute or estimate:
   - **Weighted bid-ask spread** = (best_ask − best_bid) / mid_price
   - **Depth asymmetry** = (total_bid_volume − total_ask_volume) / (total_bid_volume + total_ask_volume) across all levels
   - **Buy-initiated ratio** = buy-side active trades / total trades (from tick data)
   - **Large-order net pressure** = large_buy_amount − large_sell_amount (from capital snapshot)
   - **Order-wall levels** = price levels with volume ≥ 3× average level volume (potential support/resistance)
8. Output a structured microstructure report (see Output section).

## CLI

```bash
# Discover available subcommands and their flags first
longbridge --help
longbridge <subcommand> --help   # run for each subcommand before use

# Orderbook depth (5/10-level bid/ask)
longbridge <depth-subcommand> NVDA.US --format json

# Recent tick trades (check --help for count/range flags)
longbridge <trades-subcommand> NVDA.US --format json

# Capital flow (large/medium/small order distribution)
longbridge <capital-subcommand> NVDA.US --format json

# Broker queue — HK symbols only
longbridge <brokers-subcommand> 700.HK --format json
```

## Output

Render a structured report with these sections:

| Section             | 简体         | 繁體         | English                     |
| ------------------- | ------------ | ------------ | --------------------------- |
| Spread & liquidity  | 价差与流动性 | 價差與流動性 | Spread & Liquidity          |
| Depth asymmetry     | 盘口不对称   | 盤口不對稱   | Depth Asymmetry             |
| Order-flow pressure | 订单流压力   | 訂單流壓力   | Order-Flow Pressure         |
| Order walls         | 挂单墙       | 掛單牆       | Order Walls                 |
| Direction bias      | 短线方向偏向 | 短線方向偏向 | Short-Term Directional Bias |

Key field translations (LLM maps JSON keys → user language):

| Field                        | 简体                   | 繁體                   | English                        |
| ---------------------------- | ---------------------- | ---------------------- | ------------------------------ |
| `asks / bids`                | 卖盘 / 买盘            | 賣盤 / 買盤            | Ask / Bid                      |
| `price / volume / order_num` | 价格 / 数量 / 委托笔数 | 價格 / 數量 / 委託筆數 | Price / Volume / Order count   |
| `direction`                  | 方向（主买/主卖）      | 方向（主買/主賣）      | Direction (buy/sell initiated) |
| `large_in / large_out`       | 大单流入 / 流出        | 大單流入 / 流出        | Large order in/out             |

**Off-hours caveat**: outside regular trading hours, depth is a closing snapshot and trades are from the prior session — state this explicitly.

**A-share call-auction note**: during 09:15–09:25 CST (pre-open), depth reflects indicative auction prices, not continuous quotes. Mention this when the user's query occurs in that window.

**HK block trades**: trades with `type = block` or large-volume single prints may indicate off-exchange block deals — highlight these separately.

## Error handling

| Situation                       | 简体回复                                    | 繁體回復                                    | English reply                                   |
| ------------------------------- | ------------------------------------------- | ------------------------------------------- | ----------------------------------------------- |
| `command not found: longbridge` | 请安装 longbridge-terminal，或使用 MCP 回退 | 請安裝 longbridge-terminal，或使用 MCP 回退 | Install longbridge-terminal or use MCP fallback |
| stderr `not logged in`          | 请运行 `longbridge auth login`              | 請執行 `longbridge auth login`              | Run `longbridge auth login`                     |
| `brokers` on non-HK symbol      | 经纪商队列仅支持港股                        | 經紀商隊列僅支援港股                        | Broker queue is HK-only                         |
| Other stderr                    | 原样转述，不静默重试                        | 原樣轉述，不靜默重試                        | Relay verbatim, no silent retry                 |
