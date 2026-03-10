---
name: monitoring-observability
description: Set up monitoring, logging, and observability for applications and infrastructure. Use when implementing health checks, metrics collection, log aggregation, or alerting systems. Handles Prometheus, Grafana, ELK Stack, Datadog, and monitoring best practices.
metadata:
  tags: monitoring, observability, logging, metrics, Prometheus, Grafana, alerts
  platforms: Claude, ChatGPT, Gemini
---


# Monitoring & Observability


## When to use this skill

- **Before Production Deployment**: Essential monitoring system setup
- **Performance Issues**: Identify bottlenecks
- **Incident Response**: Quick root cause identification
- **SLA Compliance**: Track availability/response times

## Instructions

### Step 1: Metrics Collection (Prometheus)

**Application Instrumentation** (Node.js):
```typescript
import express from 'express';
import promClient from 'prom-client';

const app = express();

// Default metrics (CPU, Memory, etc.)
promClient.collectDefaultMetrics();

// Custom metrics
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

const httpRequestTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

// Middleware to track requests
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const labels = {
      method: req.method,
      route: req.route?.path || req.path,
      status_code: res.statusCode
    };

    httpRequestDuration.observe(labels, duration);
    httpRequestTotal.inc(labels);
  });

  next();
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', promClient.register.contentType);
  res.end(await promClient.register.metrics());
});

app.listen(3000);
```

**prometheus.yml**:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'my-app'
    static_configs:
      - targets: ['localhost:3000']
    metrics_path: '/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

rule_files:
  - 'alert_rules.yml'
```

### Step 2: Alert Rules

**alert_rules.yml**:
```yaml
groups:
  - name: application_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status_code=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}% (threshold: 5%)"

      # Slow response time
      - alert: SlowResponseTime
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time"
          description: "95th percentile is {{ $value }}s"

      # Pod down
      - alert: PodDown
        expr: up{job="my-app"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Pod is down"
          description: "{{ $labels.instance }} has been down for more than 2 minutes"

      # High memory usage
      - alert: HighMemoryUsage
        expr: |
          (
            node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
          ) / node_memory_MemTotal_bytes > 0.90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}%"
```

### Step 3: Log Aggregation (Structured Logging)

**Winston (Node.js)**:
```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: {
    service: 'my-app',
    environment: process.env.NODE_ENV
  },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error'
    }),
    new winston.transports.File({
      filename: 'logs/combined.log'
    })
  ]
});

// Usage
logger.info('User logged in', { userId: '123', ip: '1.2.3.4' });
logger.error('Database connection failed', { error: err.message, stack: err.stack });

// Express middleware
app.use((req, res, next) => {
  logger.info('HTTP Request', {
    method: req.method,
    path: req.path,
    ip: req.ip,
    userAgent: req.get('user-agent')
  });
  next();
});
```

### Step 4: Grafana Dashboard

**dashboard.json** (example):
```json
{
  "dashboard": {
    "title": "Application Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{route}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status_code=~\"5..\"}[5m])",
            "legendFormat": "Errors"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))"
          }
        ]
      },
      {
        "title": "CPU Usage",
        "type": "gauge",
        "targets": [
          {
            "expr": "rate(process_cpu_seconds_total[5m]) * 100"
          }
        ]
      }
    ]
  }
}
```

### Step 5: Health Checks

**Advanced Health Check**:
```typescript
interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  uptime: number;
  checks: {
    database: { status: string; latency?: number; error?: string };
    redis: { status: string; latency?: number };
    externalApi: { status: string; latency?: number };
  };
}

app.get('/health', async (req, res) => {
  const startTime = Date.now();
  const health: HealthStatus = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    checks: {
      database: { status: 'unknown' },
      redis: { status: 'unknown' },
      externalApi: { status: 'unknown' }
    }
  };

  // Database check
  try {
    const dbStart = Date.now();
    await db.raw('SELECT 1');
    health.checks.database = {
      status: 'healthy',
      latency: Date.now() - dbStart
    };
  } catch (error) {
    health.status = 'unhealthy';
    health.checks.database = {
      status: 'unhealthy',
      error: error.message
    };
  }

  // Redis check
  try {
    const redisStart = Date.now();
    await redis.ping();
    health.checks.redis = {
      status: 'healthy',
      latency: Date.now() - redisStart
    };
  } catch (error) {
    health.status = 'degraded';
    health.checks.redis = { status: 'unhealthy' };
  }

  const statusCode = health.status === 'healthy' ? 200 : health.status === 'degraded' ? 200 : 503;
  res.status(statusCode).json(health);
});
```

## Output format

### Monitoring Dashboard Configuration

```
Golden Signals:
1. Latency (Response Time)
   - P50, P95, P99 percentiles
   - Per API endpoint

2. Traffic (Request Volume)
   - Requests per second
   - Per endpoint, per status code

3. Errors (Error Rate)
   - 5xx error rate
   - 4xx error rate
   - Per error type

4. Saturation (Resource Utilization)
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network bandwidth
```

## Constraints

### Required Rules (MUST)

1. **Structured Logging**: JSON format logs
2. **Metric Labels**: Maintain uniqueness (be careful of high cardinality)
3. **Prevent Alert Fatigue**: Only critical alerts

### Prohibited (MUST NOT)

1. **Do Not Log Sensitive Data**: Never log passwords, API keys
2. **Excessive Metrics**: Unnecessary metrics waste resources

## Best practices

1. **Define SLO**: Clearly define Service Level Objectives
2. **Write Runbooks**: Document response procedures per alert
3. **Dashboards**: Customize dashboards as needed per team

## References

- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Google SRE Book](https://sre.google/books/)

## Metadata

### Version
- **Current Version**: 1.0.0
- **Last Updated**: 2025-01-01
- **Compatible Platforms**: Claude, ChatGPT, Gemini

### Related Skills
- [deployment](../deployment/SKILL.md): Monitoring alongside deployment
- [security](../security/SKILL.md): Security event monitoring

### Tags
`#monitoring` `#observability` `#Prometheus` `#Grafana` `#logging` `#metrics` `#infrastructure`

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
