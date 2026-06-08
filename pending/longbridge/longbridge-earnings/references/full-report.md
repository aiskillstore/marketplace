# Full Report Workflow (Markdown Research Report)

Read this only when the user explicitly asked for a full report (完整报告 / 深度分析 / 研报 / "full report" / "research report"), or upgraded after a lite summary card.

Deliverable: `[SYMBOL]_Q[N]_[YEAR]_Earnings_Update.md` — a single Markdown file, 12-15 sections. **No DOCX, no Python scripts, no image files** — all tables are Markdown tables, all "charts" are Markdown tables with Unicode `█` bars or compact trend rows.

## Phase 1 — Data Collection

1. **Reuse the lite digest.** If a lite run already printed a `RAW_DIR`, reuse it. Otherwise:

   ```bash
   python3 scripts/collect.py <SYMBOL> --full     # `python` on Windows
   ```

   `--full` adds: balance sheet + cash flow statements, filing list, industry valuation percentiles, peer compare, and rating history. Raw JSON lives in the printed `RAW_DIR` — read those files (Python `json` or jq if available) instead of re-calling the CLI.

2. **Identify the reporting period** from the digest: `SNAPSHOT.fp_end` + the latest CONSENSUS period with `actual` filled. Map period-end date to fiscal quarter using the company's fiscal calendar (Apple FY ends Sep, Nike May, Walmart Jan; most others calendar year). State the detected quarter in the report header — do not pause to ask the user unless the data is contradictory.

3. **Earnings call transcript — ONE web search**: `[Company] Q[X] [Year] earnings call transcript`. Verify the transcript date matches the reporting period. Extract: management tone, guidance, key Q&A themes, notable quotes (with speaker).

4. **Pre-earnings consensus vintage** (for honest beat/miss): the digest's CONSENSUS section already gives estimate-vs-actual with `beat_est`/`miss_est` flags. Only web-search for consensus history if the user disputes the baseline or asks where estimates stood before the print.

5. **US stocks only, if needed**: the filing detail (`longbridge filing detail <SYMBOL> <ID>`) has MD&A and segment detail the structured statements lack. HK/CN filings are PDFs — skip filing detail and rely on `financial-report` + `business-segments` (already in the digest).

**Verify before analysis:** all materials refer to the SAME quarter; the release is within ~3 months (if older, say so and confirm the user still wants it); reported figures come from CLI data, not memory.

## Phase 2 — Analysis

Work through these in order; each becomes a report section.

1. **Beat/miss** — for each KPI (revenue, EBIT, net income, adjusted NI, EPS, adjusted EPS): quantify the variance ($ and %), explain WHY (driver, one-time vs sustainable), connect to thesis. The CONSENSUS digest section has estimate/actual/comp for ~6 periods.
2. **Segments** — from SEGMENTS + (US) filing detail: what out/under-performed, mix shift, trend vs prior quarters.
3. **Margins** — gross/operating/net trajectory (INCOME_STATEMENT has 8 quarters): drivers (pricing, mix, costs, leverage), outlook.
4. **Guidance** — new vs prior vs Street; credibility (sandbagging track record); key assumptions. If none provided, say so explicitly and give your own outlook.
5. **Estimate revisions** — update current FY and next FY: revenue, EBITDA/EBIT, EPS. Show old → new → % change → reason per line.
6. **Valuation** — read [valuation-methodologies.md](valuation-methodologies.md). Three methods with dynamic weighting, full math shown:
   - **DCF (40-60%)** — 8 steps: historical analysis → revenue projections → OpEx → FCF → terminal value → WACC (CAPM, beta) → discount → equity bridge. Bear/Base/Bull scenarios (growth, WACC ±50bps).
   - **Trading Comps (25-40%)** — peers from PEER_COMPARE digest section; P/E + EV/EBITDA; 25th pct (Bear) / median (Base) / 75th pct (Bull).
   - **Precedent Transactions (0-25%)** — only when relevant M&A exists (web search); otherwise redistribute weight to DCF + Comps.
   - State chosen weights and why. Sanity checks: DCF within ±30% of market price (else explain), methods directionally agree, terminal value 50-70% of EV.
7. **Rating decision** — upgrade/downgrade/maintain, driven by results + guidance + risk/reward at the new target. If estimates moved >5%, the target usually moves too; if unchanged, explicitly maintain.

## Phase 3 — Report Structure (Markdown)

```markdown
# [Company] ([Ticker]) — Q[X] FY[Year] Earnings Update
> [Event-driven headline, e.g. "DTC Strength Offsets Wholesale Weakness — Maintaining BUY, PT $95"]

Rating: **[BUY/HOLD/SELL] (maintained/raised/lowered)** | PT: **$XXX** (prior $XXX) | Price: $XXX | Upside: +XX%
Report date: YYYY-MM-DD | Results date: YYYY-MM-DD

## 1. Earnings Summary            ← verdict (BEAT/INLINE/MISS) + KPI scorecard table + 3-4 ■ takeaway bullets
## 2. Revenue Analysis            ← beat/miss explanation + quarterly progression table (8Q)
## 3. Segment Breakdown           ← segment table with █ share bars + YoY
## 4. Profitability               ← margin trend table (8Q) + drivers (+/− list)
## 5. Key Operating Metrics       ← company-specific KPIs vs expectations
## 6. Guidance & Outlook          ← new vs old vs Street table + credibility assessment
## 7. Earnings Call Highlights    ← tone, themes, 2-3 quotes with speaker attribution
## 8. Updated Estimates           ← old → new → change → reason, current FY + next FY
## 9. Valuation                   ← three methods, weights + rationale, full math
## 10. Bear / Base / Bull         ← range table + WACC × terminal-growth sensitivity table
## 11. Investment Thesis Update   ← per pillar: STRENGTHENED/UNCHANGED/WEAKENED + evidence
## 12. Risks                      ← new/changed risks, brief
## 13. Appendix (optional)        ← quarterly model detail, peer table
## Sources & References           ← all materials as Markdown links with dates
```

**Trend "charts" in Markdown** — quarterly progression with bars:

```markdown
| Quarter | Revenue (B) | YoY | Trend |
|---------|------------:|----:|-------|
| Q2'25A  | 185.9       | +17% | ███████████████▌ |
| Q3'25A  | 194.1       | +14% | ████████████████▏ |
```

**Style rules:**

- Lead with numbers ("Revenue grew 15% to $1.2B", never "strong growth"); "vs." not "versus"; focus on what's NEW — no company-101 padding.
- Year notation: `A` actual (Q3'24A), `E` estimate (Q4'24E).
- Every table gets a `Source:` line (document + date). Every number traceable: company release/filing for actuals, digest CONSENSUS for estimates, transcript (speaker, link) for quotes.
- All citations are Markdown links with meaningful display text — never raw URLs. Filing URLs come from `filings.json` in RAW_DIR.
- Sources & References section at the end of the **file**. Do NOT paste a Sources section into the chat.

## Phase 4 — Deliver

In chat, alongside the file path: a compact recap — verdict, 3 takeaways, estimate changes, rating + PT. Reuse the lite-card format from SKILL.md if the user has not already seen one this conversation.

## Quality Checklist (final pass)

1. Beat/miss leads the report, every variance quantified ($ and %) with WHY.
2. All data from the LATEST quarter; consensus baseline is pre-earnings.
3. Old vs new estimates shown for current FY + next FY, with reasons.
4. Valuation: weights stated and justified; sanity checks pass or divergence explained.
5. PT and rating explicit — changed with rationale, or explicitly maintained.
6. Guidance analyzed (or its absence noted).
7. Thesis pillars each tagged STRENGTHENED / UNCHANGED / WEAKENED with evidence.
8. Every table has a Source line; all links are Markdown links that resolve.
9. Numbers match the company's reported figures exactly; math checks out.
10. Headline is event-driven (not "Quarterly Update"); ticker and quarter correct throughout.
