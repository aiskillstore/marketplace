<!-- Reference only. Actual rendering: thesis_review._render_postmortem() -->
# Postmortem: {{ thesis_id }}

**Ticker:** {{ ticker }}
**Type:** {{ thesis_type }}
**Status:** {{ status }}

## Thesis

{{ thesis_statement }}

## Timeline

| Event | Date | Price |
|-------|------|-------|
| Created | {{ created_at }} | — |
| Entry | {{ entry_actual_date }} | {{ entry_actual_price }} |
| Exit | {{ exit_actual_date }} | {{ exit_actual_price }} |

## Outcome

| Metric | Value |
|--------|-------|
| P&L ($) | {{ pnl_dollars }} |
| P&L (%) | {{ pnl_pct }} |
| Holding Days | {{ holding_days }} |
| Exit Reason | {{ exit_reason }} |
| MAE (%) | {{ mae_pct }} |
| MFE (%) | {{ mfe_pct }} |

## Position

| Metric | Value |
|--------|-------|
| Shares | {{ shares }} |
| Position Value | {{ position_value }} |
| Risk ($) | {{ risk_dollars }} |

## Evidence at Entry

{{ evidence_list }}

## Kill Criteria

{{ kill_criteria_list }}

## Lessons Learned

{{ lessons_learned }}
