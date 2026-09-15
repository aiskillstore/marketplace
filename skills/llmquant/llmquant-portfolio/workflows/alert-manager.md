---
name: Alert Manager
description: Create, update, delete, and explain price, volatility, event, and activity alerts using LLMQuant Data.
input_data_source: LLMQuant Data
pack: research
---

# Alert Manager

## Purpose

Manage actionable alerts for price levels, IV thresholds, volatility regime changes, unusual options activity, earnings windows, and thesis triggers.

## Input Data Source

Use **LLMQuant Data** for alert storage, trigger checks, market data, option data, and event calendars.

## Data Needed

Required LLMQuant Data inputs:
- alert inventory, alert update capability, alert deletion capability, and triggered alert history for alert lifecycle.
- equity market snapshot data for price and volume triggers.
- implied-volatility snapshot data for IV rank, IV percentile, HV, and VRP triggers.
- unusual options activity data for flow triggers.
- equity event calendar data for earnings and corporate event triggers.

Supported alert types:
- Price above/below or support/resistance break.
- IV rank above/below, VRP flip, or VIX tier.
- Unusual activity by premium, volume/open-interest ratio, or trade type.
- Earnings approaching within N days.
- Research thesis condition triggered.

## Workflow

1. Parse the alert condition into symbol, metric, operator, threshold, cadence, and expiration.
2. Pull current data to validate that the metric exists and show current value.
3. Create, update, delete, or list alerts as requested.
4. For triggered alerts, show what fired, when, and why it matters.
5. Suggest a more precise condition if the user's wording is ambiguous.

## Output Format

1. **Alert Action**: created, updated, deleted, listed, or triggered.
2. **Condition**: symbol, metric, threshold, current value, recurrence.
3. **Context**: why the alert matters and which data source powers it.
4. **Next Steps**: analyze ticker, set companion alert, dismiss.
5. **Data Used**.

## Guardrails

- Do not create vague alerts without a measurable trigger.
- Do not mutate existing alerts unless the user clearly requests it.
- If the trigger data is unsupported, explain what data is needed.
