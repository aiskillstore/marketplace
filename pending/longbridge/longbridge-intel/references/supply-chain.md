# longbridge-supply-chain

Industry supply-chain deep-dive — map the value chain, identify bottlenecks, and assess investment opportunities across tiers.

## Workflow

1. Identify the target industry from the prompt.
2. Use knowledge to map the supply-chain tiers: upstream (raw materials / components), midstream (manufacturing / processing), downstream (end-product / distribution / end-user).
3. For key representative companies at each tier, fetch financial data to compare gross margins and profitability.
4. Identify bottleneck nodes based on gross margin premium, market concentration, and switching cost.
5. Fetch recent news for supply-chain events (shortages, geopolitics, new entrants).
6. Output a structured supply-chain map and investment commentary.

> If unsure of exact flag names, run `longbridge <subcommand> --help` before proceeding.

## CLI

```bash
# Supply-chain news and industry dynamics
longbridge news <SYMBOL> --format json

# Income statement for gross margin comparison across tiers
longbridge financial-report <SYMBOL> --kind IS --format json

# Industry valuation context
longbridge industry-valuation <SYMBOL> --format json
```

Run for each representative company at each tier to compare margins and profitability.

## Output structure

```
# <Industry> Supply Chain Map

## Upstream (上游)
Key materials / components, key companies, avg gross margin, bargaining power

## Midstream (中游)
Processing / manufacturing, key companies, avg gross margin, bargaining power

## Downstream (下游)
End products / services / distribution, key companies, avg gross margin

## Bottleneck Analysis (咽喉环节)
Which tier / company controls pricing, why, and for how long

## Investment Implications
- Highest-margin tier: ...
- Most defensible position: ...
- Near-term catalyst: ...
- Risk: ...
```

## Error handling

| Situation                       | 简体回复                                             | 繁體回復                                             | English reply                                                                   |
| ------------------------------- | ---------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------- |
| Industry too vague              | 请提供更具体的行业或公司名称（如"半导体"或"TSMC"）。 | 請提供更具體的行業或公司名稱（如"半導體"或"TSMC"）。 | Please specify an industry or anchor company (e.g. "semiconductors" or "TSMC"). |
| Company data unavailable        | 该公司财务数据暂不可用，已跳过该环节比较。           | 該公司財務數據暫不可用，已略過該環節比較。           | Company financials unavailable — skipping that tier comparison.                 |
| `command not found: longbridge` | 请安装 longbridge-terminal 或通过 MCP 连接。         | 請安裝 longbridge-terminal 或透過 MCP 連線。         | Install longbridge-terminal or connect via MCP.                                 |
| `not logged in`                 | 请运行 `longbridge auth login`。                     | 請執行 `longbridge auth login`。                     | Run `longbridge auth login`.                                                    |
