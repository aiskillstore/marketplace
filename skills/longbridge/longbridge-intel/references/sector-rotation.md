# longbridge-sector-rotation

Multi-factor sector-rotation scanner. Combines price momentum, capital flow, and valuation to rank industries by cycle leadership across A-share, HK, and US markets.

## Workflow

1. **Clarify scope** — ask the user for market (A-share / HK / US) and time window (20-day / 60-day) if not given. Default: A-share, 20-day momentum.
2. **Select representative sector indices or ETFs** for the market:
   - A-share: 申万一级行业指数 (SW L1); common symbols like `801010.SH` (agriculture), `801020.SH` (mining), `801030.SH` (chemicals), `801040.SH` (steel), `801050.SH` (non-ferrous), `801080.SH` (electronics), `801130.SH` (media), `801140.SH` (retail), `801150.SH` (F&B), `801160.SH` (home appliances), `801170.SH` (auto), `801180.SH` (property), `801200.SH` (retail), `801710.SH` (building materials), `801720.SH` (construction), `801730.SH` (utilities), `801740.SH` (defense), `801750.SH` (IT), `801760.SH` (telecom), `801770.SH` (biotech), `801780.SH` (financials), `801790.SH` (brokers).
   - HK: use sector ETFs or HSI sub-indices.
   - US: use SPDR sector ETFs (`XLK.US`, `XLF.US`, `XLE.US`, `XLV.US`, `XLY.US`, `XLI.US`, `XLP.US`, `XLB.US`, `XLRE.US`, `XLU.US`, `XLC.US`).
3. **Fetch kline data** for each sector symbol to compute momentum. Run `longbridge kline --help` to verify exact flags, then call:
   ```bash
   longbridge kline <SYMBOL> --format json   # run --help for available period/count flags
   ```
4. **Compute momentum score** for each sector (LLM in-context):
   - 20-day return: `(close[-1] / close[-20]) - 1`
   - 60-day return: `(close[-1] / close[-60]) - 1`
5. **Fetch capital flow** for top candidates (up to 5 by momentum). Run `longbridge capital --help` to verify flags, then call:
   ```bash
   longbridge capital <SYMBOL> --format json   # run --help for time-series vs snapshot flags
   ```
6. **Fetch industry valuation** for context:
   ```bash
   longbridge industry-valuation <SYMBOL> --format json
   ```
   Run `longbridge industry-valuation --help` if unsure of flags.
7. **Score and rank**: combine momentum (60%), capital flow direction (25%), valuation discount vs history (15%). Sort descending.
8. **Output the rotation table** (see Output section). Cite Longbridge Securities.

## CLI

Run `--help` before calling any subcommand if unsure of flags.

```bash
# Step 1: kline for momentum (repeat per sector symbol); run --help for period/count flags
longbridge kline 801750.SH --format json

# Step 2: capital flow for shortlisted sectors; run --help for time-series vs snapshot flags
longbridge capital 801750.SH --format json

# Step 3: industry valuation for context
longbridge industry-valuation 801750.SH --format json

# Sector ETFs for US market
longbridge kline XLK.US --format json
longbridge capital XLK.US --format json
```

## Output

Render as a ranked table, then a short narrative:

```
Sector Rotation Snapshot — Source: Longbridge Securities
Market: A-share  |  Time: YYYY-MM-DD  |  Momentum window: 20d / 60d

Rank | Sector       | 20d Ret | 60d Ret | Capital Flow | Valuation | Signal
-----|-------------|---------|---------|-------------|-----------|-------
  1  | IT / 信息技术 | +8.2%  | +15.4%  | Net inflow  | Neutral   | ▲ Leader
  2  | Healthcare / 医疗卫生 | +5.1% | +11.2% | Net inflow | Low | ▲ Leader
 ...
 10  | Property / 房地产 | -3.4% | -8.0% | Net outflow | High | ▼ Laggard

Narrative: IT and Healthcare are in the leading quadrant with positive momentum and
capital inflows. Property and Utilities are lagging. Rotation signal suggests early-cycle
tilt toward growth sectors.

⚠️ 数据仅供参考，不构成投资建议。/ 數據僅供參考，不構成投資建議。/ For reference only. Not investment advice.
```

## Error handling

| Situation                       | 简体                                             | 繁體                                             | English                                                               |
| ------------------------------- | ------------------------------------------------ | ------------------------------------------------ | --------------------------------------------------------------------- |
| `command not found: longbridge` | 回退到 MCP；否则告知用户安装 longbridge-terminal | 回退到 MCP；否則告知用戶安裝 longbridge-terminal | Fall back to MCP; otherwise tell user to install longbridge-terminal. |
| stderr `not logged in`          | 请运行 `longbridge auth login`                   | 請執行 `longbridge auth login`                   | Run `longbridge auth login`.                                          |
| kline returns < 60 bars         | 动量计算退化为可用历史                           | 動量計算退化為可用歷史                           | Degrade momentum to available history length.                         |
| Other stderr                    | 原文显示错误                                     | 原文顯示錯誤                                     | Surface verbatim.                                                     |
