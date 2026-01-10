---
name: Observability & Monitoring
description: Structured logging, metrics, distributed tracing, and alerting strategies
version: 1.0.0
category: Operations & Reliability
agents: [backend-system-architect, code-quality-reviewer, ai-ml-engineer]
keywords: [observability, monitoring, logging, metrics, tracing, alerts, Prometheus, OpenTelemetry]
---

# Observability & Monitoring Skill

Comprehensive frameworks for implementing observability including structured logging, metrics, distributed tracing, and alerting.

## When to Use

- Setting up application monitoring
- Implementing structured logging
- Adding metrics and dashboards
- Configuring distributed tracing
- Creating alerting rules
- Debugging production issues

## Three Pillars of Observability

```
┌─────────────────┬─────────────────┬─────────────────┐
│     LOGS        │     METRICS     │     TRACES      │
├─────────────────┼─────────────────┼─────────────────┤
│ What happened   │ How is system   │ How do requests │
│ at specific     │ performing      │ flow through    │
│ point in time   │ over time       │ services        │
└─────────────────┴─────────────────┴─────────────────┘
```

## Structured Logging

### Log Levels

| Level | Use Case |
|-------|----------|
| **ERROR** | Unhandled exceptions, failed operations |
| **WARN** | Deprecated API, retry attempts |
| **INFO** | Business events, successful operations |
| **DEBUG** | Development troubleshooting |

### Best Practice

```typescript
// Good: Structured with context
logger.info('User action completed', {
  action: 'purchase',
  userId: user.id,
  orderId: order.id,
  duration_ms: 150
});

// Bad: String interpolation
logger.info(`User ${user.id} completed purchase`);
```

> See `templates/structured-logging.ts` for Winston setup and request middleware

## Metrics Collection

### RED Method (Rate, Errors, Duration)

Essential metrics for any service:
- **Rate** - Requests per second
- **Errors** - Failed requests per second
- **Duration** - Request latency distribution

### Prometheus Buckets

```typescript
// HTTP request latency
buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5]

// Database query latency
buckets: [0.001, 0.01, 0.05, 0.1, 0.5, 1]
```

> See `templates/prometheus-metrics.ts` for full metrics configuration

## Distributed Tracing

### OpenTelemetry Setup

Auto-instrument common libraries:
- Express/HTTP
- PostgreSQL
- Redis

### Manual Spans

```typescript
tracer.startActiveSpan('processOrder', async (span) => {
  span.setAttribute('order.id', orderId);
  // ... work
  span.end();
});
```

> See `templates/opentelemetry-tracing.ts` for full setup

## Alerting Strategy

### Severity Levels

| Level | Response Time | Examples |
|-------|---------------|----------|
| **Critical (P1)** | < 15 min | Service down, data loss |
| **High (P2)** | < 1 hour | Major feature broken |
| **Medium (P3)** | < 4 hours | Increased error rate |
| **Low (P4)** | Next day | Warnings |

### Key Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| ServiceDown | `up == 0` for 1m | Critical |
| HighErrorRate | 5xx > 5% for 5m | Critical |
| HighLatency | p95 > 2s for 5m | High |
| LowCacheHitRate | < 70% for 10m | Medium |

> See `templates/alerting-rules.yml` for Prometheus alerting rules

## Health Checks

### Kubernetes Probes

| Probe | Purpose | Endpoint |
|-------|---------|----------|
| **Liveness** | Is app running? | `/health` |
| **Readiness** | Ready for traffic? | `/ready` |
| **Startup** | Finished starting? | `/startup` |

### Readiness Response

```json
{
  "status": "healthy|degraded|unhealthy",
  "checks": {
    "database": { "status": "pass", "latency_ms": 5 },
    "redis": { "status": "pass", "latency_ms": 2 }
  },
  "version": "1.0.0",
  "uptime": 3600
}
```

> See `templates/health-checks.ts` for implementation

## Observability Checklist

### Implementation
- [ ] JSON structured logging
- [ ] Request correlation IDs
- [ ] RED metrics (Rate, Errors, Duration)
- [ ] Business metrics
- [ ] Distributed tracing
- [ ] Health check endpoints

### Alerting
- [ ] Service outage alerts
- [ ] Error rate thresholds
- [ ] Latency thresholds
- [ ] Resource utilization alerts

### Dashboards
- [ ] Service overview
- [ ] Error analysis
- [ ] Performance metrics

## Extended Thinking Triggers

Use Opus 4.5 extended thinking for:
- **Incident investigation** - Correlating logs, metrics, traces
- **Alert tuning** - Reducing noise, catching real issues
- **Architecture decisions** - Choosing monitoring solutions
- **Performance debugging** - Cross-service latency analysis

## Templates Reference

| Template | Purpose |
|----------|---------|
| `structured-logging.ts` | Winston logger with request middleware |
| `prometheus-metrics.ts` | HTTP, DB, cache metrics with middleware |
| `opentelemetry-tracing.ts` | Distributed tracing setup |
| `alerting-rules.yml` | Prometheus alerting rules |
| `health-checks.ts` | Liveness, readiness, startup probes |
