# longbridge-etf-analysis

Prompt-only analysis skill. Analyses ETFs across five dimensions: product profile, tracking error, liquidity, premium/discount, and allocation fit — supporting both US-listed ETFs and A-share ETFs.

## CLI

Run `longbridge <subcommand> --help` to verify exact flags.

```bash
# ETF quote — price, volume, market cap, turnover
longbridge quote <ETF_SYMBOL> --format json

# Constituent holdings — underlying stocks and weights
longbridge constituent <ETF_SYMBOL> --format json

# Historical price — compute tracking error vs index
longbridge kline <ETF_SYMBOL> --period day --count 60 --format json

# Index / benchmark price for comparison
longbridge kline <BENCHMARK_SYMBOL> --period day --count 60 --format json

# Valuation indices (PE/PB of ETF if available)
longbridge calc-index <ETF_SYMBOL> --format json
```

## Five-dimension analysis

### 1. Product profile

Extract from `quote` + `constituent` output:

- Underlying index tracked
- AUM / total market cap (proxy)
- Expense ratio (if available in quote metadata; otherwise note "check fund prospectus")
- Inception date / listing exchange

### 2. Tracking error

- Fetch ETF daily kline and benchmark daily kline (60 bars).
- Daily return difference: `d_i = r_ETF_i − r_index_i`
- Tracking error (annualised): `TE = std(d) × √252`
- Interpretation: TE < 0.3% excellent; 0.3–1% acceptable; > 1% investigate.

### 3. Liquidity

From `quote`:

- Average daily volume and turnover
- Bid-ask spread (if tick data available; otherwise use turnover-rate as proxy)
- Liquidity flag: turnover-rate > 0.5% = liquid; < 0.1% = illiquid (A-share ETFs)

### 4. Premium / discount (NAV vs market price)

- For A-share ETFs: `premium = (market price − NAV) / NAV × 100%`
- NAV may not be in real-time quote; note this and use EOD NAV if available.
- Persistent premium > 2% or discount < −2% signals arbitrage opportunity or liquidity issue.
- For US ETFs: premium/discount is typically < 0.1% due to continuous creation/redemption.

### 5. Allocation fit

- Index type: broad market (SPY/QQQ/510300) vs sector (XLK/515790) vs factor (value/growth/momentum)
- Currency and market exposure
- Overlap analysis: if user holds multiple ETFs, flag significant holdings overlap from `constituent`

## Workflow

1. Resolve ETF symbol to `<CODE>.<MARKET>` (e.g. `SPY.US`, `510300.SH`).
2. Concurrently fetch: `quote`, `constituent`, ETF kline, benchmark kline.
3. Compute TE, assess liquidity, estimate premium/discount.
4. Summarise all five dimensions.
5. Output structured report (template below). Cite Longbridge Securities.

## Output template

```
{ETF Symbol} analysis — Source: Longbridge Securities

[1. Product profile]
- Index tracked: {name}  |  Exchange: {ex}
- AUM proxy (mkt cap): {$X}  |  Expense ratio: {X% / see prospectus}

[2. Tracking error (60-day)]
- Annualised TE: X%  → {excellent / acceptable / elevated}

[3. Liquidity]
- Avg daily volume: {X}  |  Turnover rate: X%  → {liquid / moderate / illiquid}
- Bid-ask spread estimate: {X% / data unavailable}

[4. Premium / Discount]
- Latest: {+X% premium / −X% discount / ~flat}
- Note: {A-share ETF — NAV published after close / US ETF — near-zero typical}

[5. Allocation fit]
- Type: {broad market / sector / factor}
- Key holdings (top 5): {list from constituent}
- Currency exposure: {USD / CNY / HKD}

[Summary]
{2–3 sentence overall assessment}

⚠️ 以上分析仅供参考，不构成投资建议。/ 以上分析僅供參考，不構成投資建議。/ For reference only. Not investment advice.
```

## Error handling

| Situation                       | 简体回复                                         | 繁體回復                                         | English reply                                                 |
| ------------------------------- | ------------------------------------------------ | ------------------------------------------------ | ------------------------------------------------------------- |
| `command not found: longbridge` | 切换到 MCP；若不可用，请安装 longbridge-terminal | 切換至 MCP；若不可用，請安裝 longbridge-terminal | Fall back to MCP; if unavailable, install longbridge-terminal |
| stderr `not logged in`          | 请执行 `longbridge auth login`                   | 請執行 `longbridge auth login`                   | Run `longbridge auth login`                                   |
| `constituent` returns empty     | 持仓数据暂不可用，跳过重叠分析                   | 持倉數據暫不可用，跳過重疊分析                   | Constituent data unavailable; skipping overlap analysis       |
| Benchmark kline unavailable     | 无法计算跟踪误差，仅显示 ETF 本身收益            | 無法計算追蹤誤差，僅顯示 ETF 本身收益            | Cannot compute TE; showing ETF return only                    |
