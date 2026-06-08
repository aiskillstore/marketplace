# longbridge-event-opportunity

Corporate event opportunity scanner — identify pricing dislocations from M&A, buybacks, index changes, equity incentives, and lockup expiries.

## Workflow

1. Extract the symbol or scan recent filings for a universe.
2. Fetch news, filings, corporate actions, and calendar in parallel.
3. Identify event type(s) from the data:

   | Event Type                 | Key Signal             | Historical Edge                             |
   | -------------------------- | ---------------------- | ------------------------------------------- |
   | M&A / Restructuring        | 资产注入公告, 借壳公告 | +15–30% in 20 trading days (A-share avg)    |
   | Major Shareholder Increase | 大股东增持 ≥1%         | +5–12% in 10 days                           |
   | Buyback Programme          | 回购计划公告           | +3–8% in 5 days, sustained support          |
   | Equity Incentive           | 股权激励方案           | +2–6%, binding to 12–36 month vesting       |
   | Index Inclusion            | 指数调整公告           | +3–10% over 5–10 days before effective date |
   | Index Exclusion            | 指数剔除公告           | -3–8% selling pressure                      |
   | Lockup Expiry              | 限售股解禁             | -2–6% around expiry window                  |

4. For each detected event:
   - Summarise the event details (size, timing, counterparties)
   - State the typical historical price reaction pattern
   - Assess current price positioning relative to the event
5. Output a ranked event list for user reference.

> If unsure of exact flag names, run `longbridge <subcommand> --help` before proceeding.

## CLI

```bash
# Recent news and event announcements
longbridge news <SYMBOL> --format json

# Corporate filings (prospectus, announcements)
longbridge filing <SYMBOL> --format json

# Corporate actions (dividends, splits, rights issues)
longbridge corp-action <SYMBOL> --format json

# Upcoming earnings and events calendar
longbridge finance-calendar --format json

# 60-day daily OHLCV for pre/post event price reaction
longbridge kline <SYMBOL> --period day --count 60 --format json
```

## Output structure

```
EVENT ANALYSIS REPORT — <SYMBOL>  <Date>

EVENTS DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Event 1: MAJOR SHAREHOLDER INCREASE
  Announced: <date>
  Details:   <shareholder> increased stake by x.x% to xx.x%
  Amount:    $xxx million
  Historical market reaction reference: +x–x% in 10 trading days post-announcement (historical average)
  Current price vs. announcement: +x.x%
  Signal strength: ★★★★☆

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Event 2: LOCKUP EXPIRY
  Expiry date:  <date>  (xx trading days from now)
  Shares:       xxx million shares (~xx% of free float)
  Avg cost:     $xx.xx (current price: $xx.xx — holders at +xx% gain)
  Selling risk: [High | Moderate | Low]
  Historical market reaction reference: -x–x% in 5 days around expiry (historical average)

RANKED EVENT LIST
#1  <Event type>  Signal: ★★★★☆  Risk: Medium
#2  <Event type>  Signal: ★★★☆☆  Risk: High

---
以上内容仅供参考，不构成投资建议。投资决策请结合自身风险承受能力独立判断。
The above is for informational purposes only and does not constitute investment advice. Investment decisions should be made independently based on your own risk tolerance.
```

## Error handling

| Situation                       | 简体回复                                     | 繁體回復                                     | English reply                                                  |
| ------------------------------- | -------------------------------------------- | -------------------------------------------- | -------------------------------------------------------------- |
| Symbol not found                | 未找到该代码，请确认市场和格式。             | 找不到該代碼，請確認市場和格式。             | Symbol not found — verify exchange and ticker.                 |
| No events detected              | 近期未发现明显事件信号，建议持续关注公告。   | 近期未發現明顯事件信號，建議持續關注公告。   | No significant events detected — monitor filings continuously. |
| Filing data unavailable         | 公告数据暂不可用，请直接查阅交易所官网。     | 公告數據暫不可用，請直接查閱交易所官網。     | Filing data unavailable — check the exchange directly.         |
| `command not found: longbridge` | 请安装 longbridge-terminal 或通过 MCP 连接。 | 請安裝 longbridge-terminal 或透過 MCP 連線。 | Install longbridge-terminal or connect via MCP.                |
| `not logged in`                 | 请运行 `longbridge auth login`。             | 請執行 `longbridge auth login`。             | Run `longbridge auth login`.                                   |
