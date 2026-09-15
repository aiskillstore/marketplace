---
name: Ticker Smart-Money Holders
description: Identify top 13F holders and crowding signals for a U.S. ticker using LLMQuant Data.
input_data_source: LLMQuant Data
pack: data
---

# Ticker Smart-Money Holders

## Purpose

Show which institutional managers in the LLMQuant Data 13F universe hold a ticker, how concentrated the ownership appears, and what the limitations of 13F data are.

---

## Input Data Source

Use **LLMQuant Data** as the input data source for 13F holder lists, manager holdings, report periods, and scope notices. State which LLMQuant Data capabilities were used, cite the ranking period and period of report, and do not invent data that was not retrieved.

---

## LLMQuant Data Contract

Required data capabilities:
- ticker-level 13F holder data

Optional data capabilities:
- manager-level 13F holdings data
- equity price history

Freshness:
- Use the latest available 13F universe unless the user specifies a year and quarter.
- State the ranking period, manager period of report, and scope notice.
- Explain that 13F data is delayed, long-only, U.S.-listed, and excludes shorts and many non-equity exposures.

Fallback:
- If the ticker has no holders in scope, report that this is within the LLMQuant Data Top 1000 universe, not the full SEC filer universe.
- If a manager is requested but unavailable, report the resolver or scope limitation.

Output:
- Holder summary
- Top holders table
- Crowding interpretation
- Caveats
- Data used

---

## Workflow

1. Normalize the ticker.
2. Query 13F holder lists for the ticker.
3. Rank holders by reported position value.
4. Compare top holder values with manager reportable value when available.
5. Identify concentration, recognizable specialist holders, broad passive-like ownership, or lack of sponsor interest.
6. Keep conclusions modest because 13F data is delayed and incomplete.

---

## Output Format

Use:

1. **Bottom Line**
2. **13F Metadata**: ticker, ranking period, total holders in scope, aggregate value.
3. **Top Holders Table**: manager, rank, position value, shares, period of report.
4. **Crowding Read**: concentration, sponsorship, and limitations.
5. **Follow-Up Checks**: manager-specific holdings, price action, filing read, or peer comparison.
6. **Data Used**

---

## Guardrails

- Do not call 13F holdings "current ownership."
- Do not infer short positions from absence of a long filing.
- Do not compare against full-market ownership unless that data was retrieved.
- Do not hide Top 1000 universe limitations.
