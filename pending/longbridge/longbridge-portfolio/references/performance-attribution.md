# longbridge-performance-attribution

Decomposes a portfolio's return into attributable components using Brinson-Hood-Beebower sector attribution and multi-factor regression. Answers: "did I add value through industry allocation or stock selection?" and "how much of my alpha is market beta vs true skill?".

## Workflow

1. **Fetch portfolio positions**: `longbridge positions --format json`
2. **Fetch portfolio P&L**: `longbridge portfolio --format json`
3. **Fetch benchmark daily candles** (default: SPX.US for US, HSI.HK for HK, 000300.SH for CN):
   `longbridge kline <BENCHMARK> --period day --count 252 --format json`
4. **Fetch each position's daily candles** (up to 10 positions; skip if > 10, note limitation):
   `longbridge kline <SYMBOL> --period day --count 252 --format json`
5. **Brinson Attribution** (use current weights from positions; group by industry):
   - Allocation effect = (w_p,i − w_b,i) × (r_b,i − r_b)
   - Selection effect = w_b,i × (r_p,i − r_b,i)
   - Interaction = (w_p,i − w_b,i) × (r_p,i − r_b,i)
   - Total active return = sum of all three
6. **Factor decomposition** (OLS regression of portfolio excess return on factors):
   - Market: (r_benchmark − r_f)
   - Momentum: (60-day return rank)
   - Report α (intercept), β_market, with t-stats
7. **Timing (T-M model)**: regress portfolio excess return on (r_b − r_f) + (r_b − r_f)²; γ > 0 indicates positive timing ability.

Run `longbridge positions --help` and `longbridge portfolio --help` to verify current flag names.

## CLI

```bash
longbridge positions --help
longbridge portfolio --help
longbridge kline --help

longbridge positions --format json
longbridge portfolio --format json
longbridge kline <BENCHMARK> --period day --count 252 --format json
longbridge kline <SYMBOL>    --period day --count 252 --format json
```

## Output

| Component          | 简体      | 繁體      | English              |
| ------------------ | --------- | --------- | -------------------- |
| Allocation effect  | 配置效应  | 配置效應  | Allocation effect    |
| Selection effect   | 选股效应  | 選股效應  | Selection effect     |
| Interaction effect | 交互效应  | 交互效應  | Interaction effect   |
| Market beta        | 市场β     | 市場β     | Market β             |
| Alpha (Jensen)     | 超额收益α | 超額收益α | Jensen α             |
| Timing ability γ   | 择时系数  | 擇時係數  | Timing coefficient γ |

Output: Brinson table by industry → factor decomposition → timing verdict → 3-sentence interpretive summary. Cite **Longbridge Securities** / **数据来源：长桥证券** / **數據來源：長橋證券**.

## Error handling

| Situation                        | 简体回复                                        | 繁體回復                                        | English reply                                   |
| -------------------------------- | ----------------------------------------------- | ----------------------------------------------- | ----------------------------------------------- |
| `command not found: longbridge`  | 回退到 MCP 或提示安装 longbridge-terminal       | 回退到 MCP 或提示安裝 longbridge-terminal       | Fall back to MCP or install longbridge-terminal |
| `not logged in` / `unauthorized` | 请运行 `longbridge auth login`（需 Trade 权限） | 請執行 `longbridge auth login`（需 Trade 權限） | Run `longbridge auth login` with Trade scope    |
| Empty positions                  | 账户暂无持仓，无法归因                          | 賬戶暫無持倉                                    | No positions found; nothing to attribute        |
| > 10 positions                   | 持仓超过10只，仅归因前10大持仓                  | 持倉超過10只                                    | Attribution limited to top-10 positions         |
| Other stderr                     | 直接显示原始错误                                | 直接顯示原始錯誤                                | Surface verbatim                                |
