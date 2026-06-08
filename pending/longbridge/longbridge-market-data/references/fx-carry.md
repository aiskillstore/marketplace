# longbridge-fx-carry

FX carry-trade analysis — evaluate interest-rate differential, historical carry returns, and key risks for currency pairs.

## Common carry pairs

| Pair    | 高息货币 / High-yield | 低息货币 / Low-yield | 典型场景        |
| ------- | --------------------- | -------------------- | --------------- |
| AUD/JPY | AUD                   | JPY                  | Risk-on carry   |
| NZD/USD | NZD                   | USD                  | Commodity carry |
| MXN/JPY | MXN                   | JPY                  | EM carry        |
| TRY/USD | TRY                   | USD                  | High-risk EM    |
| BRL/JPY | BRL                   | JPY                  | EM carry        |

> If unsure of exact flag names, run `longbridge <subcommand> --help` before proceeding.

## Workflow

1. Identify the carry pair(s) from the user's prompt; default to AUD/JPY, NZD/USD, MXN/JPY if unspecified.
2. Fetch current spot rates for all relevant currencies.
3. Look up prevailing benchmark interest rates (use embedded knowledge or `longbridge macro` if available).
4. Calculate annualised carry yield: `(high-yield rate − low-yield rate)`.
5. Fetch historical FX price data (60 days) to estimate realised volatility.
6. Compute simplified Sharpe: `carry_yield / annualised_vol`.
7. Assess tail-risk scenarios (rapid JPY strength / EM stress / risk-off unwind).
8. Output structured summary.

## CLI

```bash
# Spot exchange rates
longbridge exchange-rate --format json

# Historical FX price series (if supported by the CLI)
longbridge kline <FX_PAIR> --period day --count 60 --format json
```

## Output

Present for each pair:

```
Pair      Carry Yield   60d Volatility   Est. Sharpe   Signal
─────────────────────────────────────────────────────────────
AUD/JPY      3.2%           8.4%            0.38       Moderate
NZD/USD      2.1%           6.2%            0.34       Moderate
MXN/JPY      8.5%          14.1%            0.60       High / Risky
```

Follow with a narrative covering: current macro environment, carry unwind risks, position sizing guidance.

## Error handling

| Situation                       | 简体回复                                     | 繁體回復                                     | English reply                                                         |
| ------------------------------- | -------------------------------------------- | -------------------------------------------- | --------------------------------------------------------------------- |
| FX pair not supported           | 该货币对暂不支持，请尝试其他主要货币对。     | 該貨幣對暫不支援，請嘗試其他主要貨幣對。     | This FX pair is not supported — try a major currency pair.            |
| Historical FX data unavailable  | 历史汇率数据不可用，仅提供当前利差分析。     | 歷史匯率數據不可用，僅提供當前利差分析。     | Historical FX data unavailable — providing current differential only. |
| `command not found: longbridge` | 请安装 longbridge-terminal 或通过 MCP 连接。 | 請安裝 longbridge-terminal 或透過 MCP 連線。 | Install longbridge-terminal or connect via MCP.                       |
| `not logged in`                 | 请运行 `longbridge auth login`。             | 請執行 `longbridge auth login`。             | Run `longbridge auth login`.                                          |
