# longbridge-buffett-moat-analyzer

Prompt-only Buffett-style moat diagnostic. Given a single ticker, produces a five-dimension verdict — moat / financial health / management / valuation / long-term visibility — closed with a Buffett-voice narrative, an explicit holding-period expectation, and a mandatory data-source appendix whose final row is a one-line reconciliation summary.

## Cognitive frame (do not skip)

Buffett strategy is **long-term ownership of high-quality businesses**, not market timing. Two things every output must surface alongside the score:

1. **Holding-period expectation** — Buffett's reference is "ideally forever, at minimum 3 years." If the user has a < 3-year capital horizon, warn explicitly that this framework is not the right lens.
2. **Price vs business quality** — _"A great business at a fair price is far better than a fair business at a great price."_ The valuation dimension is a margin-of-safety check on a separately-scored quality verdict; never collapse quality and price into one number.

Two failure modes the user must be able to distinguish:

- **"Great business, wait for price"** → moat wide, financials clean, but valuation rich → 🟡 watchlist with a target-price band, not a buy.
- **"Cheap but no moat"** → low PE/PB but moat narrow or absent → ❌ not a Buffett candidate; redirect to Graham (`longbridge-graham-stock-analysis`).

## Workflow

1. **Resolve symbol** to `<CODE>.<MARKET>` (e.g. `00700.HK`, `AAPL.US`, `600519.SH`).
2. **Sector triage**:
   - Bank / insurance / brokerage → moat framework still applies but tweak financial-health dimension (use ROA, NIM, NPL, capital adequacy in place of FCF/leverage). Note this in the report.
   - Pre-revenue / heavy-loss / lifecycle-stage-zero biotech → halt: Buffett framework needs a track record; suggest the user use `longbridge-fundamental` for an early-stage view instead.
   - ST / 退市风险 / listed < 3 years → emit report but tag earnings-stability and capital-allocation dimensions as "insufficient history" and pro-rate scores.
3. **Fetch raw data via Longbridge CLI first** (parallel where possible). See [§CLI](#cli). If `longbridge` is missing, fall back to MCP (see [§MCP fallback](#mcp-fallback)). Use WebSearch **only** for items genuinely outside Longbridge (industry outlook, qualitative management signals, brand surveys, regulatory news).
4. **Reconciliation gate** (勾稽校验) — runs **before** any scoring. See [§Reconciliation](#reconciliation-勾稽校验). Two-state outcome:
   - **Pass (every check within tolerance)** → proceed to scoring. A one-line summary of the result still appears at the end of the data-source appendix.
   - **Fail (any check exceeds tolerance)** → halt scoring, emit a halt message naming the failing check and gap, still print the data-source appendix and reconciliation summary.
5. **Five-dimension scoring** — each dimension gets a 1–5 star rating with concrete evidence. See `references/scoring.md` for the rubric per dimension.
6. **Holding-period mapping** — derive expected minimum hold from moat width (★★★★★ → 5y+, ★★★★ → 3–5y, ★★★ → 1–3y, ★★ or below → not a Buffett candidate). See `references/scoring.md` §Holding-period.
7. **Output** the report defined in `references/output.md` — diagnostic card → 5-dimension detail → Buffett-voice narrative → user education block → **Data Source Appendix (mandatory)** ending with the reconciliation summary line. Close with the disclaimer variant matching the user's input language (single-language only — see `references/output.md` §Disclaimer variants).

## CLI

Run `longbridge <subcommand> --help` to verify exact flags before each call — do not hard-code flag names without verification. Primary calls (run in parallel):

```bash
# Balance sheet — leverage, equity (PB / ROE denominator), debt
longbridge financial-report <SYMBOL> --kind BS --report af --format json    # last 5 annual (10y ideal — fetch as many as available)
longbridge financial-report <SYMBOL> --kind BS --report qf --format json    # last 4 quarterly

# Income statement — ROE, gross margin, earnings stability, EPS trend
longbridge financial-report <SYMBOL> --kind IS --report af --format json
longbridge financial-report <SYMBOL> --kind IS --report qf --format json

# Cash flow — FCF = OCF − Capex, capex intensity, buyback / dividend cash outflow
longbridge financial-report <SYMBOL> --kind CF --report af --format json
longbridge financial-report <SYMBOL> --kind CF --report qf --format json

# Snapshot: PE, PB, market cap, dividend yield, shares outstanding
longbridge calc-index <SYMBOL> --format json
longbridge quote <SYMBOL> --format json

# Long-window history for valuation-vs-history band
longbridge kline <SYMBOL> --period day --count 2500 --format json           # ~10 years for PE/PB percentile

# Dividend & buyback history (capital allocation track record)
longbridge dividend <SYMBOL> --format json
longbridge corporate <SYMBOL> --format json                                  # buyback / split / spin-off

# Ownership & insider activity (management alignment, capital allocation signals)
longbridge ownership <SYMBOL> --format json
longbridge insresearch <SYMBOL> --format json

# Company profile + industry classification (for moat-type hypothesis)
longbridge basicinfo <SYMBOL> --format json
longbridge company-profile <SYMBOL> --format json

# Peer set for moat / margin / ROE benchmarking
longbridge peer-comparison <SYMBOL> --format json
```

### WebSearch fallback — only for items not available from Longbridge

| Missing data                                        | WebSearch query pattern                                                 |
| --------------------------------------------------- | ----------------------------------------------------------------------- |
| Industry runway / disruption risk                   | `"<industry> 2025 outlook"`, `"<industry> disruption risk"`             |
| Brand / pricing-power signals                       | `"<company> price increase 2024 2025"`, `"<brand> brand value ranking"` |
| Management qualitative track record                 | `"<CEO name> capital allocation"`, `"<CEO name> shareholder letter"`    |
| Regulatory / policy overhangs                       | `"<sector> regulation <region> 2025"`                                   |
| Latest insider transactions if `ownership` is stale | `"<ticker> insider selling 2025"`                                       |

Every WebSearch-sourced figure must be tagged `[Source: WebSearch — <publisher>, <date>, <url>]` in the appendix; never silently mix it with Longbridge data.

## Reconciliation (勾稽校验)

Before any scoring, verify the fetched figures are internally consistent. Reconciliation is **user-visible in this skill** — a one-line summary always appears as the final row of the Data Source Appendix (per the design doc's transparency requirement). If a check fails, scoring halts entirely.

| Check                   | Formula                                                             | Tolerance                           |
| ----------------------- | ------------------------------------------------------------------- | ----------------------------------- |
| IS↔BS link              | Net income(t) ≈ Δ Retained earnings(BS, t) − dividends paid(CF, t)  | ±3%                                 |
| IS↔CF link              | Net income + D&A + impairments + ΔWC ≈ Operating CF                 | ±5%                                 |
| CF↔BS link              | ΔCash from CF statement = Cash(t) − Cash(t−1) on BS                 | ±1%                                 |
| FCF sanity              | Operating CF − Capex(CF) ≈ FCF used in valuation dimension          | exact (must match what you display) |
| BS — current assets sum | Cash + AR + Inventory + Other CA ≈ Total current assets             | ±2%                                 |
| BS — liabilities sum    | ST debt + LT debt + Other liabilities ≈ Total liabilities           | ±2%                                 |
| ROE inputs              | Net income / Avg shareholders' equity ≈ reported ROE (if disclosed) | ±1pp                                |
| Market cap              | `calc-index` shares × current price ≈ market cap from `quote`       | ±2%                                 |
| Period alignment        | All statements from the same fiscal period (or the lag is named)    | exact                               |

Output rules for reconciliation:

- **All pass within tolerance** → final appendix row uses the clean-pass variant from `references/output.md` §Reconciliation summary, rendered in the user's input language only (English / 简体 / 繁體 — pick one).
- **Some residuals within tolerance but material to displayed figures** → final appendix row lists each material residual on its own sub-line, e.g. `IS↔CF residual −2.1% (within ±5%) — affects FCF row of the valuation dimension`.
- **Any check fails > tolerance** → halt scoring; emit the halt message defined in `references/output.md` and still print the appendix with the reconciliation summary describing the failure.

## Output

Single-stock diagnostic with 7 fixed sections (full template in `references/output.md`):

1. **Diagnostic summary card** — star ratings on 5 dimensions, 综合评级 / Overall Rating: ★★★★★ — [强护城河/宽护城河/待观察/不符合标准 / Strong moat / Wide moat / Watch / Does not meet criteria], badge color (🟢🟡🟠🔴), suggested minimum holding period.
2. **Dimension 1 — Business model & moat** — moat type (brand / network / cost / switching / resource), width (wide / narrow / none), pricing-power evidence, 3–5 supporting points.
3. **Dimension 2 — Financial health** — ROE 10y track, FCF persistence, leverage, gross-margin trajectory, capex intensity. Each metric vs Buffett threshold with current value.
4. **Dimension 3 — Management & capital allocation** — insider holding & changes, buyback/dividend history, M&A track record, alignment signals.
5. **Dimension 4 — Valuation & margin of safety** — PE/PB vs 10y history percentile, PEG, simplified DCF concept value, safety-margin tier (充足 / 一般 / 偏贵 / 高估).
6. **Dimension 5 — Long-term visibility** — industry ceiling, disruption risk, regulatory exposure, global runway.
7. **Buffett-voice narrative + user education block** — first-person narrative in Buffett's register (concrete, plain-spoken, dryly humorous), then the **mandatory user education block** covering holding-period expectation, position-building rhythm, and the disclaimer variant matching the user's input language (one language only).

Followed by the **Data Source Appendix (mandatory)** — every figure in sections [1]–[7] traceable to a row with source, fetch time, and period; **final row is the reconciliation summary line** (pass / within-tolerance residual list / or failure description).

> ⚠️ 以上内容仅供参考，不构成投资建议。投资决策请结合自身风险承受能力独立判断。/ 以上內容僅供參考，不構成投資建議。投資決策請結合自身風險承受能力獨立判斷。/ For reference only. Not investment advice. Please make investment decisions independently based on your own risk tolerance.

## Error handling

| Situation                                        | 简体回复                                                             | 繁體回覆                                                             | English reply                                                                                                            |
| ------------------------------------------------ | -------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `command not found: longbridge`                  | 回退到 MCP；若不可用，请安装 longbridge-terminal。                   | 回退到 MCP；若不可用，請安裝 longbridge-terminal。                   | Fall back to MCP; if unavailable install longbridge-terminal.                                                            |
| stderr `not logged in` / `unauthorized`          | 请运行 `longbridge auth login`。                                     | 請執行 `longbridge auth login`。                                     | Run `longbridge auth login`.                                                                                             |
| Sector = pre-revenue / loss-making early biotech | 巴菲特框架需要业绩纪录；建议改用 `longbridge-fundamental` 早期视角。 | 巴菲特框架需要業績紀錄；建議改用 `longbridge-fundamental` 早期視角。 | Buffett framework needs a track record; use `longbridge-fundamental` for an early-stage view.                            |
| Reconciliation fails > tolerance                 | 明确披露失败项与差距，不输出评分；附录仍输出且勾稽汇总行注明失败。   | 明確披露失敗項與差距，不輸出評分；附錄仍輸出且勾稽匯總行註明失敗。   | Disclose failing check and gap; do not emit scores; appendix still printed and reconciliation summary marks the failure. |
| Listed < 3 years                                 | 盈利稳定性与资本配置维度按已披露年限按比例打分，并在附录注明。       | 盈利穩定性與資本配置維度按已披露年限比例打分，並於附錄註明。         | Pro-rate earnings-stability and capital-allocation scores; note in appendix.                                             |
| Other stderr                                     | 原样透传错误，不静默重试。                                           | 原樣透傳錯誤，不靜默重試。                                           | Surface stderr verbatim; never silently retry.                                                                           |
| Industry/qualitative WebSearch returns nothing   | 维度评分仅用财务证据，标注「定性数据缺失」。                         | 維度評分僅用財務證據，標註「定性數據缺失」。                         | Score the dimension on financial evidence only and tag "qualitative data unavailable".                                   |
