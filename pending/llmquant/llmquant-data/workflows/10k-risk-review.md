---
name: 10-K Risk Review
description: Review a company's latest 10-K for business, risk, and MD&A evidence using LLMQuant Data SEC filing tools.
input_data_source: LLMQuant Data
pack: data
---

# 10-K Risk Review

## Purpose

Produce an evidence-first risk review from the latest available annual filing. Use this when the user asks for 10-K risks, business quality, MD&A issues, filing-based downside, or a primary-source company read.

---

## Input Data Source

Use **LLMQuant Data** as the input data source for SEC filing metadata, filing sections, and equity price context. State which LLMQuant Data capabilities were used, cite filing dates and periods of report, and do not invent data that was not retrieved.

---

## LLMQuant Data Contract

Required data capabilities:
- SEC filing discovery
- SEC filing section retrieval

Optional data capabilities:
- equity price history
- wiki knowledge search

Freshness:
- Use the latest available 10-K unless the user asks for a specific year.
- State the accession number, filing date, and period of report.
- Do not imply the filing reflects events after its filing date.

Fallback:
- If the latest 10-K is unavailable, report the missing filing and ask for another ticker or year.
- If a section is unavailable, name the missing section and continue only with retrieved sections.

Output:
- Executive summary
- Filing metadata
- Risk evidence table
- MD&A / business trend notes
- Monitoring checklist
- Data used

---

## Workflow

1. Resolve the ticker and target year.
2. Query recent 10-K filing metadata.
3. Select the latest annual filing unless the user specified another period.
4. Read Item `1` for business context, Item `1A` for risk factors, and Item `7` for MD&A.
5. Optionally pull equity price history to frame market reaction or drawdown context.
6. Extract only evidence that appears in retrieved sections.
7. Separate company-disclosed risks from your interpretation of severity.

---

## Output Format

Use:

1. **Bottom Line**: 3-5 bullets on the most important filing risks.
2. **Filing Metadata**: ticker, form, accession number, filed date, period of report, sections read.
3. **Risk Evidence Table**: risk, filing evidence, why it matters, severity, monitoring signal.
4. **MD&A Readthrough**: demand, margin, liquidity, capex, customer, legal, or accounting signals.
5. **What To Monitor Next**: next filing, key metrics, events, or disclosures.
6. **Data Used**: LLMQuant Data capabilities and dates.

---

## Guardrails

- Do not summarize a 10-Q as a 10-K.
- Do not quote long filing passages; paraphrase and cite section names.
- Do not treat risk-factor boilerplate as high severity unless MD&A or business evidence supports it.
- Do not add outside news unless the user supplies it or another LLMQuant Data tool retrieves it.
