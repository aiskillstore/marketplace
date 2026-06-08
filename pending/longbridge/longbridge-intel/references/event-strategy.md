# longbridge-event-strategy

Event-driven investment strategy framework — identify corporate events (M&A, spinoffs, buybacks, index rebalancing, lockup expiry) that create pricing dislocations, score sentiment, analyse historical price reactions, and size positions accordingly. Uses Longbridge news, filings, calendar, and candlestick data as signal inputs.

## Workflow

### Step 1 — Event identification

Run `longbridge news` and `longbridge filing` for the target symbol to surface recent corporate events. Run `longbridge finance-calendar` to identify upcoming scheduled events (earnings, dividends, index reviews).

### Step 2 — Sentiment scoring

Analyse the news/filing content for event type and directional sentiment:

| Event type                | 简体          | 繁體          | English           |
| ------------------------- | ------------- | ------------- | ----------------- |
| M&A announcement          | 并购公告      | 並購公告      | M&A announcement  |
| Index inclusion/exclusion | 指数纳入/剔除 | 指數納入/剔除 | Index rebalancing |
| Lockup expiry             | 限售股解禁    | 限售股解禁    | Lockup expiry     |
| Share buyback             | 股份回购      | 股份回購      | Share buyback     |
| Spinoff / separation      | 分拆上市      | 分拆上市      | Spinoff           |

### Step 3 — Historical price reaction

Run `longbridge kline` (daily, 60 days around prior similar events) to measure the historical price reaction window (T-5 to T+20).

### Step 4 — Historical reaction summary

Based on event type and historical reaction magnitude, summarise the observed price reaction range and volatility characteristics for this class of event. Present the data as historical reference only; do not provide entry timing, stop-loss levels, target prices, or holding-period recommendations.

## CLI

```bash
# Corporate news and filings
longbridge news <SYMBOL> --format json
longbridge filing <SYMBOL> --format json

# Upcoming events calendar (earnings, dividends, index reviews)
longbridge finance-calendar --format json

# Historical daily candlestick for price-reaction analysis
longbridge kline <SYMBOL> --period day --count 60 --format json
```

> Run `longbridge news --help`, `longbridge filing --help`, and `longbridge kline --help` to verify flags.

## Output

For a given symbol and event, produce a structured event brief:

1. **Event summary** — type, date, source.
2. **Sentiment score** — bullish / neutral / bearish with rationale.
3. **Historical reaction reference** — average T+5/T+10/T+20 return range and volatility for this event type (if data available), presented as historical statistics only.

---

以上内容仅供参考，不构成投资建议。投资决策请结合自身风险承受能力独立判断。
The above is for informational purposes only and does not constitute investment advice. Investment decisions should be made independently based on your own risk tolerance.

## Error handling

| Situation                       | 简体回复                       | 繁體回覆                       | English reply                      |
| ------------------------------- | ------------------------------ | ------------------------------ | ---------------------------------- |
| `command not found: longbridge` | 请先安装 longbridge-terminal   | 請先安裝 longbridge-terminal   | Install longbridge-terminal first  |
| `not logged in`                 | 请运行 `longbridge auth login` | 請執行 `longbridge auth login` | Run `longbridge auth login`        |
| No relevant news found          | 提示近期无相关事件公告         | 提示近期無相關事件公告         | No relevant corporate events found |
| Other stderr                    | 原样展示，不重试               | 原樣展示，不重試               | Surface verbatim, do not retry     |
