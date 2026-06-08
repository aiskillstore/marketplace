# longbridge-portfolio-diagnosis

Prompt-only analysis skill. Pulls live account data and recent price history to give a comprehensive portfolio health-check: concentration, sector mix, currency breakdown, factor tilt, cross-holding correlation, and benchmark deviation.

## Workflow

1. Fetch account data with `longbridge portfolio` and `longbridge positions`.
2. For correlation analysis, fetch 60-day daily kline for each holding concurrently.
3. Compute diagnostics in the LLM (see Calculations section).
4. Present a structured diagnosis report.

## CLI

Run `longbridge <subcommand> --help` to verify exact flags before calling.

```bash
# Step 1: account summary + positions
longbridge portfolio --format json
longbridge positions --format json

# Step 2: 60-day price history for each holding (run concurrently per symbol)
longbridge kline <SYMBOL> --period day --count 60 --format json

# Step 3: sector/valuation context per holding
longbridge calc-index <SYMBOL> --format json
```

## Calculations

Compute the following in the LLM from fetched data:

| Metric               | Method                                                                                   |
| -------------------- | ---------------------------------------------------------------------------------------- |
| Top-5 concentration  | Sum of top-5 positions by market value ÷ total portfolio value                           |
| Sector distribution  | Group positions by `industry` / `sector` field; compute % of total MV                    |
| Currency exposure    | Group by currency of listing; compute % of total MV                                      |
| Factor tilt          | Large-cap (market cap > $10B) vs small-cap; PE < 15 / dividend yield > 3% = value tilt   |
| Pairwise correlation | Pearson correlation of 60-day daily returns; flag pairs with r > 0.8 as high correlation |
| Benchmark deviation  | If user provides a benchmark (e.g. SPX, HSI), compare sector weights                     |

## Output template

```
Portfolio Diagnosis — Source: Longbridge Securities
Date: <today>

[Concentration]
- Top-5 holdings: <names> = <N>% of portfolio
- Risk: {Low (<40%) / Medium (40-60%) / High (>60%)}

[Sector Distribution]
- <Sector>: <N>%  (target suggestion if heavily concentrated)
- ...

[Currency Exposure]
- USD: <N>%  HKD: <N>%  CNY: <N>%  Other: <N>%

[Factor Tilt]
- Large-cap: <N>%  Small-cap: <N>%
- Value tilt: <N>%  Growth tilt: <N>%

[Correlation Risk]
- High-correlation pairs (r > 0.8): <list>
- Diversification note: ...

[Summary & Suggestions]
- Key risks: ...
- Suggested actions: ...

⚠️ 仅供参考，不构成投资建议。/ 僅供參考，不構成投資建議。/ For reference only. Not investment advice.
```

## Error handling

| Situation                           | 简体回复                                           | 繁體回復                                           | English reply                                                              |
| ----------------------------------- | -------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------------------------------- |
| `command not found: longbridge`     | 回退到 MCP；若也不可用，请安装 longbridge-terminal | 回退到 MCP；若也不可用，請安裝 longbridge-terminal | Fall back to MCP; if unavailable, ask user to install longbridge-terminal. |
| stderr `not logged in`              | 请运行 `longbridge auth login` 登录                | 請運行 `longbridge auth login` 登入                | Run `longbridge auth login` to authenticate.                               |
| Empty positions                     | 账户暂无持仓，无法诊断                             | 賬戶暫無持倉，無法診斷                             | No holdings found; cannot run diagnosis.                                   |
| kline data unavailable for a symbol | 跳过该标的相关性计算，标注数据缺失                 | 略過該標的相關性計算，標注數據缺失                 | Skip correlation for that symbol; note data gap.                           |
