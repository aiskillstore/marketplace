# SLO Alerting Patterns

## Prometheus Recording Rules

```yaml
groups:
  - name: sli_recording
    interval: 30s
    rules:
      # Availability SLI (28-day window)
      - record: sli:http_availability:ratio
        expr: |
          sum(rate(http_requests_total{status!~"5.."}[28d]))
          /
          sum(rate(http_requests_total[28d]))

      # Latency SLI (requests < 500ms)
      - record: sli:http_latency:ratio
        expr: |
          sum(rate(http_request_duration_seconds_bucket{le="0.5"}[28d]))
          /
          sum(rate(http_request_duration_seconds_count[28d]))

  - name: slo_recording
    interval: 5m
    rules:
      # Error budget remaining (percentage)
      - record: slo:http_availability:error_budget_remaining
        expr: |
          (sli:http_availability:ratio - 0.999) / (1 - 0.999) * 100

      # Burn rates for different windows
      - record: slo:http_availability:burn_rate_5m
        expr: |
          (1 - (
            sum(rate(http_requests_total{status!~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          )) / (1 - 0.999)

      - record: slo:http_availability:burn_rate_1h
        expr: |
          (1 - (
            sum(rate(http_requests_total{status!~"5.."}[1h]))
            /
            sum(rate(http_requests_total[1h]))
          )) / (1 - 0.999)

      - record: slo:http_availability:burn_rate_6h
        expr: |
          (1 - (
            sum(rate(http_requests_total{status!~"5.."}[6h]))
            /
            sum(rate(http_requests_total[6h]))
          )) / (1 - 0.999)
```

## Multi-Window Burn Rate Alerts

Why multi-window? Single-window alerts are either too noisy (short window) or too slow (long window). Combining windows reduces false positives.

```yaml
groups:
  - name: slo_alerts
    rules:
      # Fast burn: 14.4x rate over 1 hour
      # Consumes 2% error budget in 1 hour
      - alert: SLOErrorBudgetBurnFast
        expr: |
          slo:http_availability:burn_rate_1h > 14.4
          and
          slo:http_availability:burn_rate_5m > 14.4
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Fast error budget burn - {{ $value | printf \"%.1f\" }}x rate"
          description: "At current rate, error budget exhausted in {{ printf \"%.1f\" (div 100 $value) }} hours"

      # Slow burn: 6x rate over 6 hours
      # Consumes 5% error budget in 6 hours
      - alert: SLOErrorBudgetBurnSlow
        expr: |
          slo:http_availability:burn_rate_6h > 6
          and
          slo:http_availability:burn_rate_30m > 6
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Slow error budget burn - {{ $value | printf \"%.1f\" }}x rate"

      # Budget exhausted
      - alert: SLOErrorBudgetExhausted
        expr: slo:http_availability:error_budget_remaining < 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "SLO error budget exhausted"
          description: "Error budget: {{ $value | printf \"%.1f\" }}%"
```

## Burn Rate Reference

| Burn Rate | Budget Consumed/Hour | Time to Exhaust |
|-----------|---------------------|-----------------|
| 1x | 0.14% | 28 days |
| 6x | 0.86% | ~5 days |
| 14.4x | 2% | ~2 days |
| 36x | 5% | ~19 hours |

## Grafana Dashboard

```
┌────────────────────────────────────┐
│ SLO Status                          │
│ Current: 99.95% | Target: 99.9%    │
│ Status: ✓ Meeting SLO              │
├────────────────────────────────────┤
│ Error Budget                        │
│ Remaining: 65%                      │
│ ████████████░░░░░░░░ 65%           │
│ ~18 days at current burn rate      │
├────────────────────────────────────┤
│ Burn Rate (by window)              │
│ 5m:  1.2x  ░                       │
│ 1h:  0.8x  ░                       │
│ 6h:  0.5x  ░                       │
│ 28d: 0.3x  ░                       │
└────────────────────────────────────┘
```

### Key Queries

```promql
# Current SLO compliance
sli:http_availability:ratio * 100

# Error budget remaining
slo:http_availability:error_budget_remaining

# Days until exhausted at current burn
slo:http_availability:error_budget_remaining / 100 * 28
/ max(slo:http_availability:burn_rate_1h, 1)
```

## SLO Definition Template

```yaml
slos:
  - name: api_availability
    description: "API requests complete successfully"
    target: 99.9
    window: 28d
    sli:
      good: sum(rate(http_requests_total{status!~"5.."}[28d]))
      total: sum(rate(http_requests_total[28d]))
    alerts:
      fast_burn:
        burn_rate: 14.4
        short_window: 5m
        long_window: 1h
        severity: critical
      slow_burn:
        burn_rate: 6
        short_window: 30m
        long_window: 6h
        severity: warning

  - name: api_latency_p95
    description: "API requests complete within 500ms"
    target: 99.0
    window: 28d
    sli:
      good: sum(rate(http_request_duration_seconds_bucket{le="0.5"}[28d]))
      total: sum(rate(http_request_duration_seconds_count[28d]))
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Single window alerts | Too noisy or too slow | Use multi-window |
| Missing burn rate | Don't know velocity | Add burn rate recording rules |
| 100% SLO target | No error budget | Accept 99.9% or lower |
| No dashboard | Can't see trends | Build SLO dashboard first |
| Alert on SLI directly | Missing context | Alert on burn rate instead |