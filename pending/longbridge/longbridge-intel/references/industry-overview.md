# longbridge-industry-overview

Generates an industry panorama report for a given sector or index, synthesising constituent stocks, peer valuation, and industry news into a structured landscape view.

## Workflow

1. Identify the target industry or sector (from explicit mention or inferred from anchor symbol).
2. If an index or ETF covers the sector, fetch its constituents.
3. For each key constituent (top 5–8 by market cap), fetch industry-level valuation data.
4. Fetch recent industry news using representative symbols as proxies.
5. Synthesise into an industry overview report (see Output section).

## CLI

> If you're unsure of exact flag names or defaults, run `longbridge <subcommand> --help` first.

```bash
# Constituent list for a sector index or ETF
longbridge constituent <INDEX_SYMBOL> --format json

# Industry-level valuation comparison (anchored to a representative symbol)
longbridge industry-valuation <SYMBOL> --format json

# Recent news for top-N constituents (run per key company)
longbridge news <SYMBOL> --format json

# Static info for market cap / industry classification
longbridge static <SYMBOL> --format json
```

Common index symbols: `HSI.HK` (Hang Seng), `SPX.US` (S&P 500), `IXIC.US` (Nasdaq), `000300.SH` (CSI 300). Sector ETF examples: `SOXX.US` (semiconductors), `XLK.US` (US tech).

## Output

Structure the response as an industry report:

1. **Industry definition** — scope, SIC/GICS classification, geographic focus
2. **Market sizing** — estimated total addressable market, growth rate, stage (early / growth / mature / declining)
3. **Key players** (table — top 5–8 by market cap):

| Company | Symbol | Market Cap | Revenue Growth | PE  | Market Share Est. |
| ------- | ------ | ---------- | -------------- | --- | ----------------- |

4. **Competitive dynamics** — concentration (HHI), barriers to entry, switching costs, pricing power
5. **Valuation landscape** — PE / PB / PS range (min / median / max) across sector
6. **Thematic catalysts** — top 3–5 industry tailwinds (policy, technology, macro)
7. **Key risks** — top 3 headwinds or structural threats
8. **Conclusion** — overall industry attractiveness rating and investment angle

## Error handling

| Situation                        | Simplified Chinese                           | Traditional Chinese / English                                  |
| -------------------------------- | -------------------------------------------- | -------------------------------------------------------------- |
| `command not found: longbridge`  | 回退到 MCP；否则提示安装 longbridge-terminal | 回退到 MCP；否則提示安裝 / Fall back to MCP; prompt to install |
| `not logged in` / `unauthorized` | 请运行 `longbridge auth login`               | 請運行 `longbridge auth login` / Run `longbridge auth login`   |
| Index symbol not found           | 请提供正确的指数代码，如 SPX.US、HSI.HK      | 請提供正確指數代碼 / Provide a valid index symbol e.g. SPX.US  |
| Other stderr                     | 原样展示错误，不重试                         | 原樣展示，不重試 / Surface verbatim, no silent retry           |
