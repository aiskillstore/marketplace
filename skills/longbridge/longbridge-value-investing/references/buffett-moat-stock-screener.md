# longbridge-buffett-moat-stock-screener

Prompt-only Buffett-style screener. Given a market / sector / preference query (no specific ticker), applies Buffett's two-layer model — hard quantitative filter then qualitative moat scoring — and returns a ranked candidate list (3–5 cards) with moat-type tags, Buffett-attitude verdicts, and one-click jumps into `longbridge-buffett-moat-analyzer` for deep diagnostics. Every figure traces to a row in the mandatory **Data Source Appendix** at the end of the output.

## Cognitive frame (do not skip)

Screening is the **upstream entry** to the Buffett workflow: this skill generates candidates from zero; the downstream `longbridge-buffett-moat-analyzer` verifies a single name in depth. Both share the same moat lens — only the interaction shape differs.

Two principles must surface alongside every leaderboard:

1. **Holding-period expectation** — Buffett's reference is "ideally forever, at minimum 3 years." If the user's capital horizon is < 3 years, warn that this framework is the wrong lens regardless of how clean the screen looks.
2. **Quality first, price second** — _"A great business at a fair price is far better than a fair business at a great price."_ A passing row tells the user the **business** is Buffett-grade; whether _this price_ is sane is a Dimension-4 (valuation) check that may downgrade the verdict to "watch and wait for a better price". Never collapse quality and price into one number.

Failure modes the screener must flag honestly:

- **"Great business, wait for price"** → quality passes but valuation 偏贵 / 高估 → 🟡 watchlist with target-price band, not a buy.
- **"Cheap but no moat"** → low PE/PB but moat narrow or absent → not a Buffett candidate; redirect to `longbridge-graham-screener` / `longbridge-graham-stock-analysis`.
- **Sector-disqualified industries** (e.g. airlines — Buffett publicly called the industry "value-destroying") → return an honest empty result with redirect to a closer-to-Buffett sector, not a forced top-N.

## Workflow

1. **Clarify the query** in at most one quick turn. Three input shapes are supported (see §3.2 of the design doc):
   - **Preference-based** (most common): "find me consumer stocks worth long-term holding".
   - **Sector / theme-based**: "Buffett-style names in new energy" / "Buffett's actual US holdings".
   - **Condition-based** (advanced): "A-shares with 10y ROE > 20% and PE < 25".
     If the user just says "recommend stocks" with no constraint, ask 1–2 framing questions (preferred market: A / HK / US? prefer steady — consumer/healthcare/financials — or growth — tech/new-energy?) before screening.
2. **Resolve the universe**:
   - Sector / theme query → start from the index or sector universe via `longbridge constituent <INDEX>` or `longbridge sector-screener` candidate list.
   - Preference / condition query without a stated market → default to the market the user most often references (A-share if Mandarin / Cantonese trader signal, US for English, HK if the user mentioned 港股). Echo the chosen universe back in the Market Summary.
   - Cap batch size at 300 names per screen.
3. **Sector triage** — before any filter:
   - **Excluded** (no scoring, drop with a one-line explanation in the Market Summary): airlines (Buffett: _"value-destroying"_), pre-revenue / pure-loss biotech (no track record), ST / 退市风险 names, listed < 5 years, pure-shell / negative-equity. If the user _explicitly_ asked for one of these (e.g. "Buffett-style airline"), return an honest empty result with a redirect to the most-similar non-excluded sector (e.g. "consumer staples with pricing power" or "regulated utilities with stable returns").
   - **Sector-adjusted hard filter**: banks / insurance / brokerage — replace FCF / leverage rules with ROA / NIM / NPL / CAR (note the substitution per row).
   - **Listed 5–10 years**: pro-rate the earnings-stability sub-score and flag "history-limited" in the row note.
4. **Fetch raw data via Longbridge CLI first** (parallel, ≤20 symbols per wave). See [§CLI](#cli). MCP fallback if `longbridge` is missing (see [§MCP fallback](#mcp-fallback)). **WebSearch only for items genuinely outside Longbridge**: industry outlook / disruption signals, brand-strength surveys, Buffett's own 13F holdings disclosure, qualitative management track record. Every WebSearch hit gets a publisher + URL + access-date row in the appendix.
5. **Layer 1 — Hard quantitative filter** (binary pass/fail). Symbols failing ≥ 2 filters drop out by default. See [§Filters](#filters) for the table; full thresholds in `references/criteria.md`.
6. **Per-row reconciliation gate**: if balance-sheet sum / current-assets sum / shares×price mismatches the reported total by >3%, drop the row from the leaderboard with a "数据异常" note in the data-anomaly footer. Do not silently smooth.
7. **Layer 2 — Qualitative moat scoring** on every name that passed Layer 1 plus reconciliation. Five-dimension weighted composite (0–100):
   - Moat type & width (35%) · Capital allocation (20%) · Earnings predictability (20%) · Valuation reasonableness (15%) · Long-term industry runway (10%).
     Full rubric in `references/criteria.md`. Each dimension also gets a 1–5 star rating shown on the candidate card.
8. **Verdict matrix** — combine Layer 2 quality stars (moat + financials) with valuation tier. See `references/criteria.md` §Verdict matrix. Maps to one of three card verdicts:
   - 🟢 **符合巴菲特筛股标准 / Meets Buffett criteria** — wide moat + clean financials + price 充足/一般.
   - 🟡 **部分符合，关注估值变化 / Partially meets criteria** — wide moat + clean financials + price 偏贵.
   - 🔴 **当前不符合标准 / Does not meet criteria** — wide moat but price 高估, OR moat narrow at any price (redirect to Graham).
9. **Holding-period mapping** — derive expected min hold from moat width (★★★★★ → 5y+, ★★★★ → 3–5y, ★★★ → 1–3y, ★★ or below → not a Buffett candidate). See `references/criteria.md`.
10. **Rank and emit 3–5 candidate cards** (not a giant leaderboard — the design doc's deliberate cap). Follow the candidate-card template in `references/output.md`.
11. **Mandatory closing blocks** (every output, no exceptions):
    - Selection rationale (2–3 sentences on why these names, current market caveat, deep-dive priority).
    - Holding-period & user-education block (Buffett-style vs short-term expectations table — rendered in the user's language only).
    - **Data Source Appendix** — every figure on every card traceable; every WebSearch row carries publisher + URL + date.
    - Trilingual disclaimer from `references/output.md`.
12. **Deep-dive CTA** on every card, rendered in the user's input language only (e.g. _"Deep-dive → run `longbridge-buffett-moat-analyzer <CODE>`"_ for English, _"深度诊断 → 运行 `longbridge-buffett-moat-analyzer <CODE>`"_ for 简体, _"深度診斷 → 執行 `longbridge-buffett-moat-analyzer <CODE>`"_ for 繁體). Pick one.

## CLI

Run `longbridge <subcommand> --help` to verify exact flags before each call — the CLI is the source of truth; do not hard-code flag spellings from memory.

```bash
# Universe
longbridge constituent <INDEX>   --format json     # e.g. 000300.SH, HSI.HK, SPX.US

# Per-symbol snapshot (run in parallel, batches of ≤20)
longbridge calc-index   <SYMBOL> --format json     # PE / PB / market cap / ROE / dividend yield / sector tag
longbridge quote        <SYMBOL> --format json     # current price + suspended flag
longbridge basicinfo    <SYMBOL> --format json     # listing date / industry classification

# Per-symbol fundamentals (run in parallel)
longbridge financial-report <SYMBOL> --kind BS --report af --format json   # 5–10y annual — leverage, equity, debt ratio
longbridge financial-report <SYMBOL> --kind IS --report af --format json   # 5–10y annual — ROE, gross margin, earnings stability
longbridge financial-report <SYMBOL> --kind CF --report af --format json   # 5–10y annual — FCF = OCF − Capex
longbridge financial-report <SYMBOL> --kind BS --report qf --format json   # last 4Q — recent trajectory
longbridge financial-report <SYMBOL> --kind IS --report qf --format json
longbridge financial-report <SYMBOL> --kind CF --report qf --format json

# Long-window history for valuation-vs-history percentile (Layer 2 Dimension 4)
longbridge kline <SYMBOL> --period day --count 2500 --format json          # ~10 years

# Dividend & buyback (capital allocation track record — Layer 2 Dimension 2)
longbridge dividend  <SYMBOL> --format json
longbridge corporate <SYMBOL> --format json                                 # buyback / split / spin-off

# Ownership & insider flow (management alignment)
longbridge ownership   <SYMBOL> --format json
longbridge insresearch <SYMBOL> --format json

# Company profile (moat-type hypothesis seed)
longbridge company-profile <SYMBOL> --format json

# Peer set for moat / margin / ROE benchmarking
longbridge peer-comparison <SYMBOL> --format json

# Optional pre-narrowing if the user gave a sector / theme phrase
longbridge sector-screener --industry "<industry>" --format json
```

### WebSearch fallback — only for items not available from Longbridge

| Missing data                                                                   | WebSearch query pattern                                                         |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| Industry runway / disruption risk                                              | `"<industry> 2025 outlook"`, `"<industry> disruption risk"`                     |
| Brand / pricing-power signals                                                  | `"<company> price increase 2024 2025"`, `"<brand> brand value ranking"`         |
| Buffett's actual disclosed holdings (for "13F" / "Berkshire holdings" queries) | `"Berkshire Hathaway 13F <year>"`, `"Warren Buffett portfolio holdings <year>"` |
| Management qualitative track record                                            | `"<CEO name> capital allocation"`, `"<CEO name> shareholder letter"`            |
| Regulatory / policy overhangs                                                  | `"<sector> regulation <region> 2025"`                                           |
| Latest insider transactions if `ownership` is stale                            | `"<ticker> insider selling 2025"`                                               |

Every WebSearch-sourced figure must be tagged `[Source: WebSearch — <publisher>, <date>, <url>]` in the appendix; never silently mix it with Longbridge data.

## Filters

User-overridable. Defaults from Buffett's publicly stated reference points. Threshold detail and the Layer-2 composite weights live in `references/criteria.md`.

### Layer 1 — Hard quantitative filter (pass / fail gate)

| Filter              | Buffett threshold                    | Source field                                                        | Sector adjustment                                                      |
| ------------------- | ------------------------------------ | ------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| ROE (5y avg)        | ≥ 15%                                | derived from `financial-report --kind IS` (NI) ÷ avg equity from BS | Banks: use ROA ≥ 1.0% + NIM stability                                  |
| Debt-to-asset ratio | ≤ 50%                                | BS — total liabilities ÷ total assets                               | Banks / insurance / brokers: substitute CAR / leverage-adjusted equity |
| Free cash flow      | positive every year for last 3 years | `financial-report --kind CF` (OCF − Capex)                          | Banks: substitute operating-cash-flow proxy from interest income       |
| Years listed        | ≥ 5 years                            | `basicinfo.listing_date`                                            | None — strict, pro-rate at 5–10y window                                |
| Gross margin (TTM)  | ≥ 30%                                | `financial-report --kind IS` (gross profit ÷ revenue)               | Heavy industry / utilities: relax to ≥ 20% with note                   |

Symbols that fail ≥ 2 filters drop out by default; user can relax to "fail ≤ 3" on request. Any override is echoed back in the Market Summary.

### Layer 2 — Qualitative moat scoring (weighted composite, 0–100)

Applied only to Layer-1 passers. Five dimensions, weights below. Full sub-criteria, evidence rules, and star mapping in `references/criteria.md`.

| Dimension                 | Weight | Plain-language framing                                                            |
| ------------------------- | ------ | --------------------------------------------------------------------------------- |
| Moat type & width         | 35%    | Brand / network / cost / switching / regulatory / resource — wide / narrow / none |
| Capital allocation        | 20%    | Dividend & buyback discipline, M&A track record, insider stake                    |
| Earnings predictability   | 20%    | Earnings-volatility, cyclicality, revenue-mix stability                           |
| Valuation reasonableness  | 15%    | PE / PB / dividend-yield percentile vs 10y history, simplified DCF concept band   |
| Long-term industry runway | 10%    | Industry ceiling, disruption, regulatory exposure                                 |

Default rank key = Layer-2 composite (high to low). User can override to: moat-stars-only, ROE desc, valuation-tier (cheapest first), or "Berkshire holdings only".

## Special handling

| Cohort                                                    | Treatment                                                                                                                                                                                                                                                                             |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Airlines                                                  | **Excluded** — Buffett publicly called the industry "value-destroying". If the user explicitly asked for "Buffett-style airline", return an honest empty result and redirect to the nearest non-excluded sector (e.g. regulated utilities, consumer staples) with one-line rationale. |
| Pre-revenue / pure-loss biotech / hot-IPO concept names   | **Excluded** — Buffett framework needs a track record. Redirect to `longbridge-fundamental` for an early-stage view.                                                                                                                                                                  |
| ST / 退市风险 / listed < 5 years                          | **Excluded from default top-N**; show on request with the row prepended ⚠️ and a "history-limited" note.                                                                                                                                                                              |
| Listed 5–10 years                                         | Pro-rate earnings-stability sub-score on available years; mark row "history-limited".                                                                                                                                                                                                 |
| Banks / insurance / brokers                               | **Included** with the sector-adjusted hard filter (ROA / NIM / NPL / CAR). Note substitution per row and in the Market Summary.                                                                                                                                                       |
| Reconciliation fail >3%                                   | Drop from leaderboard; surface in "数据异常待复核" footer with the failing check named.                                                                                                                                                                                               |
| "最便宜的巴菲特风格股票" / "cheapest Buffett-style" query | Surface the distinction between _cheap_ and _margin of safety_. Show Layer-2 valuation tier (充足 / 一般 / 偏贵 / 高估) prominently; rank by valuation tier inside the wide-moat cohort, not by raw PE.                                                                               |
| "巴菲特真实持仓" / "Buffett's actual holdings" query      | Pull Berkshire's latest 13F via WebSearch (publisher + URL + filing date in the appendix), then run Layer 2 on the holdings as a secondary lens — note that 13F lag (≥45 days) can be material.                                                                                       |

## Output

3–5 candidate cards, **not a giant leaderboard**. Full card template, selection rationale block, holding-period education table, and the mandatory **Data Source Appendix** structure live in `references/output.md`. Minimum card fields:

```
Name (Code) · Market · Sector              Quality stars: ★★★★★
Moat type: {brand / network / cost / switching / regulatory / resource}
Top-3 highlights (quantitative first): {ROE x%}, {Gross margin x%}, {FCF / capex intensity}
评级参考: 🟢 符合巴菲特筛股标准 / 🟡 部分符合，关注估值变化 / 🔴 当前不符合标准
Valuation read: {充足 / 一般 / 偏贵 / 高估} — current price vs 10y band
Min. holding period: {5y+ / 3–5y / 1–3y}
[深度诊断这只股票 → longbridge-buffett-moat-analyzer <CODE>]
```

After the cards, every output must include:

1. **Selection rationale** — 2–3 sentences on (a) why these names together, (b) market caveats right now, (c) which one to deep-dive first.
2. **Holding-period & user-education block** — single-language table (in the user's input language) comparing Buffett-style expectations vs short-term/speculative expectations (holding time / entry pattern / drawdown tolerance / position logic / action frequency).
3. **Data Source Appendix (MANDATORY)** — every field on every card, every Longbridge endpoint hit, every WebSearch hit (publisher + URL + access date). The final line is a per-row reconciliation summary (clean pass / within-tolerance residuals / per-row drops).
4. **Disclaimer** — disclaimer variant matching the user's input language only, picked from `references/output.md` §Disclaimer variants. Never print multiple language variants. Every output must end with the following statement (in the user's input language):
   - 简体：以上内容仅供参考，不构成投资建议。投资决策请结合自身风险承受能力独立判断。
   - 繁體：以上內容僅供參考，不構成投資建議。投資決策請結合自身風險承受能力獨立判斷。
   - English: The above is for informational purposes only and does not constitute investment advice. Please make investment decisions independently based on your own risk tolerance.

## Error handling

| Situation                                                                      | 简体回复                                                                                                         | 繁體回覆                                                                                                         | English reply                                                                                                                                    |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `command not found: longbridge`                                                | 回退到 MCP；若不可用，请安装 longbridge-terminal。                                                               | 回退到 MCP；若不可用，請安裝 longbridge-terminal。                                                               | Fall back to MCP; if unavailable install longbridge-terminal.                                                                                    |
| stderr `not logged in` / `unauthorized`                                        | 请运行 `longbridge auth login`。                                                                                 | 請執行 `longbridge auth login`。                                                                                 | Run `longbridge auth login`.                                                                                                                     |
| `constituent` / `sector-screener` returns empty                                | 未能获取候选池，请确认指数或行业关键词。                                                                         | 未能獲取候選池，請確認指數或行業關鍵詞。                                                                         | Cannot fetch universe; verify the index or sector keyword.                                                                                       |
| User-named sector is on the excluded list (e.g. 航空 / pre-revenue biotech)    | 该行业整体不符合巴菲特筛股逻辑（已说明原因），推荐改看 {替代行业}；如仍想分析，可改用 `longbridge-fundamental`。 | 該行業整體不符合巴菲特篩股邏輯（已說明原因），推薦改看 {替代行業}；如仍想分析，可改用 `longbridge-fundamental`。 | The sector does not fit Buffett's framework (reason given); suggest {alternative sector}; for early-stage analysis use `longbridge-fundamental`. |
| BS / IS / CF partial fetch for a symbol                                        | 该标的数据不完整，跳过并在「数据异常」脚注列出。                                                                 | 該標的數據不完整，跳過並於「數據異常」腳註列出。                                                                 | Symbol has incomplete fundamentals; skipped and listed in the data-anomaly footer.                                                               |
| Industry runway / qualitative data missing (Longbridge + WebSearch both empty) | 维度评分仅用财务证据，标注「定性数据缺失」。                                                                     | 維度評分僅用財務證據，標註「定性數據缺失」。                                                                     | Score the dimension on financial evidence only and tag "qualitative data unavailable".                                                           |
| Per-row reconciliation gap >3%                                                 | 从候选卡片剔除并在「数据异常」附录列出失败项及差异。                                                             | 自候選卡片剔除並於「數據異常」附錄列出失敗項及差異。                                                             | Drop from candidate cards; list failing check + gap in data-anomaly appendix.                                                                    |
| User gave no market / preference at all                                        | 触发引导式提问：偏好市场（A/HK/美）？稳健（消费/医药/金融）还是有成长性（科技/新能源）？                         | 觸發引導式提問：偏好市場（A/HK/美）？穩健（消費/醫藥/金融）還是有成長性（科技/新能源）？                         | Ask one framing turn: preferred market (A / HK / US)? Steady (consumer / healthcare / financials) or growthier (tech / new-energy)?              |
| Other stderr                                                                   | 原样透传错误，不静默重试。                                                                                       | 原樣透傳錯誤，不靜默重試。                                                                                       | Surface stderr verbatim; never silently retry.                                                                                                   |
