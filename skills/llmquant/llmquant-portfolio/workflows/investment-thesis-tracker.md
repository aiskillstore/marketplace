---
name: Investment Thesis Tracker
description: Write, score, monitor, update, and close position theses with structured sell conditions using LLMQuant Data.
input_data_source: LLMQuant Data
pack: research
---

# Investment Thesis Tracker

## Purpose

Turn a position's buy logic into a monitored thesis with explicit sell conditions, status, evidence, drift detection, and action history.

## Input Data Source

Use **LLMQuant Data** for profile linkage, thesis storage, market data, fundamentals, valuation, and event monitoring.

## Data Needed

Required LLMQuant Data inputs:
- research profile retrieval capability to ensure the ticker has a profile.
- thesis retrieval capability, thesis inventory, thesis update capability, and thesis deletion capability for lifecycle.
- equity market snapshot data, company fundamentals data, valuation multiple data, and equity event radar data for trigger monitoring.

Supported sell-condition types:
- Price drop from cost, peak, or thesis date.
- Valuation ceiling such as PE/PB/EV multiple.
- Growth, margin, leverage, or FCF deterioration.
- Event breach such as guidance cut, product failure, regulatory action, or catalyst failure.
- Manual thesis breach text supplied by the user.

## Workflow

1. Clarify whether the user is creating, reviewing, updating, or closing a thesis.
2. Link the thesis to a company profile; create or request a profile if missing.
3. Convert free-form exit logic into structured conditions.
4. Pull current data and evaluate whether any condition is already triggered.
5. Store the thesis and show what will be monitored.

## Output Format

1. **Thesis Status**: active, triggered, closed, or missing.
2. **Buy Thesis**: concise prose backed by retrieved evidence.
3. **Sell Conditions**: structured triggers with data source and threshold.
4. **Current Check**: pass/fail for each condition.
5. **Actions**: update, close, refresh profile, investigate trigger.
6. **Data Used**.

## Guardrails

- Do not silently loosen or remove a user-defined sell condition.
- Distinguish monitored numeric triggers from manual qualitative triggers.
- If current data cannot evaluate a trigger, mark it unknown rather than pass.
