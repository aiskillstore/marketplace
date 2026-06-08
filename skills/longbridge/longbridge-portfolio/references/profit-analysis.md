# longbridge-profit-analysis

Full account P&L analysis — simple return, time-weighted return (TWR), per-symbol attribution, and market-level breakdown — sourced from the user's Longbridge account.

## Workflow

1. Confirm login; if not logged in, tell user to run `longbridge auth login` with Trade scope.
2. Identify the operation: overall P&L / per-symbol detail / by-market / custom date range.
3. Extract date range from context if specified; default to YTD if not stated.
4. Call CLI with `--format json`; run `--help` if unsure about flags.
5. Present: overall return %, absolute gain/loss, TWR (note: eliminates cash-flow timing distortion), top contributors, and breakdown table.

## CLI

Run `longbridge profit-analysis --help` to verify exact flags before use.

```bash
# Overall account P&L with TWR (default: YTD or account lifetime)
longbridge profit-analysis --format json

# Custom date range
longbridge profit-analysis --start 2026-01-01 --end 2026-04-30 --format json

# Per-symbol P&L detail
longbridge profit-analysis detail TSLA.US --format json

# P&L broken down by market
longbridge profit-analysis by-market --market HK --format json

# Check available flags and subcommands
longbridge profit-analysis --help
```

## Output

### Overall P&L

| Field           | 简体           | 繁體           | English                    |
| --------------- | -------------- | -------------- | -------------------------- |
| `simple_return` | 简单收益率     | 簡單收益率     | Simple return              |
| `twr`           | 时间加权收益率 | 時間加權收益率 | Time-weighted return (TWR) |
| `total_profit`  | 总盈亏         | 總盈虧         | Total P&L                  |
| `realized`      | 已实现盈亏     | 已實現盈虧     | Realized P&L               |
| `unrealized`    | 未实现盈亏     | 未實現盈虧     | Unrealized P&L             |
| `period`        | 统计期间       | 統計期間       | Period                     |

**TWR note**: Always explain TWR briefly — _"时间加权收益率消除了追加/取出资金对收益率的影响，是更客观的业绩衡量指标。"_ / _"時間加權收益率消除了追加/取出資金對收益率的影響，是更客觀的業績衡量指標。"_ / _"TWR removes the effect of cash flows (deposits/withdrawals), providing a purer performance measure."_

### Per-symbol detail

Render: symbol, market, cost basis, current value, unrealized P&L, realized P&L, total return %.

### By-market

Render: market (US / HK / CN / SG), total value, P&L, return %.

End every response with:

> ⚠️ 以上数据仅供参考，不构成投资建议。/ 以上數據僅供參考，不構成投資建議。/ For reference only. Not investment advice.

## Error handling

| Situation                        | 简体                                              | 繁體                                              | English                                                                   |
| -------------------------------- | ------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------- |
| `command not found: longbridge`  | 退回 MCP；如未配置，提示安装 longbridge-terminal  | 退回 MCP；如未設定，提示安裝 longbridge-terminal  | Fall back to MCP; if unavailable, ask user to install longbridge-terminal |
| `not logged in` / `unauthorized` | 请运行 `longbridge auth login`（需要 Trade 权限） | 請執行 `longbridge auth login`（需要 Trade 權限） | Run `longbridge auth login` with Trade scope                              |
| Empty result (no trade history)  | 账户暂无交易记录，无法计算盈亏                    | 賬戶暫無交易記錄，無法計算盈虧                    | No trade history found — cannot compute P&L                               |
| Invalid date range               | 日期格式须为 YYYY-MM-DD，开始日期须早于结束日期   | 日期格式須為 YYYY-MM-DD，開始日期須早於結束日期   | Date must be YYYY-MM-DD; start must precede end                           |
| Other stderr                     | 原文转达，不做静默重试                            | 原文轉達，不作靜默重試                            | Relay verbatim; never retry silently                                      |
