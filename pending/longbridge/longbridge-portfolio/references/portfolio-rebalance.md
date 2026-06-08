# longbridge-portfolio-rebalance

Prompt-only analysis skill. Compares current portfolio weights against user-provided target weights, computes drift, and produces a prioritised rebalance trade list with estimated transaction costs. Read-only — does not place orders.

## Workflow

1. Fetch current positions and total portfolio value.
2. Ask user for target weights if not provided (symbol → target % pairs).
3. Fetch current prices for all symbols.
4. Compute current weights and drift vs target.
5. Generate trade list: symbols to buy (underweight) and sell (overweight).
6. Estimate transaction cost (brokerage fee ~0.03–0.1% per trade; note tax impact for gains).
7. Present trade list sorted by drift magnitude (largest first).

## CLI

Run `longbridge <subcommand> --help` to verify exact flags before calling.

```bash
# Current holdings and portfolio value
longbridge portfolio --format json
longbridge positions --format json

# Current prices for each symbol in portfolio or target list (run concurrently)
longbridge quote <SYMBOL> --format json

# Maximum tradeable quantity (optional, for feasibility check)
longbridge max-qty <SYMBOL> --format json
```

## Calculations

| Quantity        | Method                                                        |
| --------------- | ------------------------------------------------------------- | ------------------------------ | --------------------- |
| Current weight  | Position MV ÷ Total portfolio MV                              |
| Target MV       | Total portfolio MV × target weight %                          |
| Required trade  | Target MV − Current MV (positive = buy, negative = sell)      |
| Trade quantity  | Required trade amount ÷ current price (round to lot size)     |
| Drift threshold | Flag if                                                       | current weight − target weight | > 5 percentage points |
| Est. cost       | Trade amount × 0.05% (configurable; note this is approximate) |

## Output template

```
Portfolio Rebalance Plan — Source: Longbridge Securities
Total Portfolio Value: <MV> <currency>
Date: <today>

[Current vs Target Weights]
Symbol    Current%  Target%   Drift     Action      Qty      Est.Cost
AAPL.US   35.2%     30.0%     +5.2%     SELL 12     $1,840   ~$0.9
TSLA.US   12.1%     20.0%     -7.9%     BUY  8      $2,100   ~$1.1
CASH      52.7%     50.0%     +2.7%     —           —        —

[Trade Summary]
- Total buys:  $X,XXX  (~$X.XX in fees)
- Total sells: $X,XXX  (~$X.XX in fees)
- Net cash change: ±$XXX

[Notes]
- Positions within ±5% of target weight are within tolerance and need no action.
- Sell orders on positions with unrealised gains may trigger tax events (US investors).
- Review lot sizes for HK/A-share stocks before placing orders.

⚠️ 仅供参考，不构成投资建议，请自行决策下单。/ 僅供參考，不構成投資建議，請自行決策下單。/ For reference only. Not investment advice. Place orders at your own discretion.
```

## Error handling

| Situation                       | 简体回复                                           | 繁體回復                                           | English reply                                                     |
| ------------------------------- | -------------------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------- |
| `command not found: longbridge` | 回退到 MCP；若也不可用，请安装 longbridge-terminal | 回退到 MCP；若也不可用，請安裝 longbridge-terminal | Fall back to MCP; if unavailable, install longbridge-terminal.    |
| stderr `not logged in`          | 请运行 `longbridge auth login` 登录                | 請運行 `longbridge auth login` 登入                | Run `longbridge auth login`.                                      |
| No target weights provided      | 请告知目标配置，例如：AAPL 30%、TSLA 20%、现金 50% | 請告知目標配置，例如：AAPL 30%、TSLA 20%、現金 50% | Please provide target weights, e.g. AAPL 30%, TSLA 20%, cash 50%. |
| Quote unavailable for a symbol  | 跳过该标的，标注价格数据缺失                       | 略過該標的，標注價格數據缺失                       | Skip that symbol; note price data is unavailable.                 |
