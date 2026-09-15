---
name: Company Profile
description: Build or refresh a persistent company research profile using LLMQuant Data fundamentals, valuation bands, red flags, events, and filings.
input_data_source: LLMQuant Data
pack: research
---

# Company Profile

## Purpose

Create a reusable company research profile that captures identity, fundamentals, valuation history, red flags, events, latest filing context, and refresh status.

## Input Data Source

Use **LLMQuant Data** as the source for company identity, market data, profile storage, filings, event radar, and valuation history.

## Data Needed

Required LLMQuant Data inputs:
- research profile retrieval capability, research profile update capability, and research profile deletion capability for profile lifecycle.
- equity market snapshot data for price, market, sector, liquidity, and update timestamp.
- company fundamentals data for margins, growth, returns, leverage, and FCF.
- historical valuation data for PE/PB/PS/EV multiples across at least 5-10 years when available.
- equity event radar data for earnings, guidance, product, litigation, M&A, and regulatory events.
- SEC filing discovery and SEC filing section retrieval for latest 10-K/10-Q context and risk updates.

## Workflow

1. Determine whether the user wants to create, view, refresh, list, or delete profiles.
2. For create or refresh, pull fresh company data and filings before writing the profile.
3. Compute valuation percentiles and red flags from retrieved data.
4. Surface stale profiles if `last_updated_at` is older than the skill's threshold.
5. Store only sourced profile fields and note missing data.

## Output Format

1. **Profile Summary**: ticker, company, market, sector, latest price, last updated.
2. **Valuation Band**: current multiple, percentile, historical context.
3. **Red Flags**: severity, evidence, source date.
4. **Event Radar**: most recent events and dates.
5. **Profile Actions**: refresh, attach thesis, compare, archive.
6. **Data Used**: data capabilities and coverage notes.

## Guardrails

- Do not create profile facts without an LLMQuant Data source.
- Treat profile storage as user-specific and do not reveal other users' data.
- If valuation history is incomplete, label the percentile as partial or unavailable.
