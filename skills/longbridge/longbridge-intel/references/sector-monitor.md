# longbridge-sector-monitor

Prompt-only analysis skill. Tracks sector rotation over 6–12 months by locating the current economic cycle phase and mapping it to historically favoured sectors. Provides ongoing allocation recommendations rather than a point-in-time snapshot.

## Economic cycle framework

| Phase              | 阶段                                            | Key macro signals                                   | Favoured sectors |
| ------------------ | ----------------------------------------------- | --------------------------------------------------- | ---------------- |
| Recovery / 复苏    | GDP turning up, unemployment falling, rates low | Consumer discretionary, Financials, Real estate     |
| Overheating / 过热 | GDP above trend, inflation rising, rates rising | Energy, Materials, Industrials                      |
| Stagflation / 滞涨 | Growth slowing, inflation still high            | Healthcare, Consumer staples, Utilities             |
| Recession / 衰退   | GDP contracting, unemployment rising            | Utilities, Consumer staples, Government bonds proxy |

## CLI

Run `longbridge <subcommand> --help` to verify exact flags before use:

```bash
# Index constituents to identify sector universe
longbridge constituent <INDEX> --format json

# 120-day kline for sector ETFs / indices (trend tracking)
longbridge kline <SECTOR_ETF> --period day --count 120 --format json

# Capital flow for individual sector symbols
longbridge capital <SYMBOL> --flow --format json

# If unsure about flags:
longbridge constituent --help
longbridge kline --help
longbridge capital --help
```

## Workflow

1. **Clarify scope** — market (A-share / HK / US) and horizon (6-month / 12-month). Default: A-share, 6-month.
2. **Select sector proxies**:
   - A-share: 申万一级行业指数 (e.g. `801750.SH` IT, `801780.SH` Financials, `801730.SH` Utilities)
   - US: SPDR ETFs (`XLK.US`, `XLF.US`, `XLE.US`, `XLV.US`, `XLY.US`, `XLP.US`, `XLU.US`, `XLB.US`)
   - HK: HSI sector sub-indices or representative ETFs
3. **Fetch 120-day kline** for each sector proxy:
   ```bash
   longbridge kline <SECTOR> --period day --count 120 --format json
   ```
4. **Compute trend metrics** in-LLM:
   - 20d, 60d, 120d returns for each sector
   - Trend direction: 20d MA vs 60d MA (above = uptrend)
5. **Fetch capital flow** for top and bottom 3 sectors by 60d return:
   ```bash
   longbridge capital <SECTOR> --flow --format json
   ```
6. **Locate economic cycle phase** using trend patterns and macro context provided by the user (or inferred from sector behaviour):
   - Broad market trend + sector leadership pattern → infer phase
7. **Map to allocation recommendation**: overweight sectors favoured in current phase; underweight laggards.
8. **Output monitoring report**; cite **Longbridge Securities**; end with disclaimer.

## Output

```
Sector Monitor Report — Source: Longbridge Securities
Market: {market}  |  Horizon: {6M / 12M}  |  Date: {date}

[Economic cycle positioning]
Current phase estimate: {Recovery / Overheating / Stagflation / Recession}
Basis: {trend patterns, sector leadership, user-provided macro context}

[Sector trend table (120-day window)]
Sector            | 20d Ret | 60d Ret | 120d Ret | Trend    | Capital Flow
──────────────────|---------|---------|----------|----------|--------------
{Sector A}        | +X%     | +Y%     | +Z%      | Uptrend  | Net inflow
{Sector B}        | ...
...

[Allocation recommendation]
Overweight:  {Sector 1}, {Sector 2}  — favoured in {phase} phase
Neutral:     {Sector 3}, {Sector 4}
Underweight: {Sector 5}, {Sector 6}  — typically lag in {phase} phase

[Cycle transition watch]
Next likely phase: {phase}  |  Trigger signals to watch: {signals}

⚠️ 以上分析仅供参考，不构成投资建议。/ 以上分析僅供參考，不構成投資建議。/ For reference only. Not investment advice.
```

## Error handling

| Situation                       | 简体中文回复                                              | 繁體中文 / English                                                                                                        |
| ------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `command not found: longbridge` | 回退到 MCP；如 MCP 也不可用，请安装 longbridge-terminal。 | 回退到 MCP；如也不可用，請安裝 longbridge-terminal。/ Fall back to MCP; if also unavailable, install longbridge-terminal. |
| stderr `not logged in`          | 请运行 `longbridge auth login` 登录。                     | 請執行 `longbridge auth login`。/ Run `longbridge auth login`.                                                            |
| kline returns < 60 bars         | 趋势分析退化为可用历史，注明数据长度不足。                | 趨勢分析退化為可用歷史，注明數據長度不足。/ Degrade to available history length; note limitation.                         |
| Other stderr                    | 直接显示原始错误，不静默重试。                            | 顯示原始錯誤。/ Surface verbatim — do not retry silently.                                                                 |
