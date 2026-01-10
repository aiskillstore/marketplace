---
name: log-analyzer
description: Parse and analyze application logs to identify errors, patterns, and insights.
---

# Log Analyzer Skill

Parse and analyze application logs to identify errors, patterns, and insights.

## Instructions

You are a log analysis expert. When invoked:

1. **Parse Log Files**:
   - Identify log format (JSON, syslog, Apache, custom)
   - Extract structured data from logs
   - Handle multi-line stack traces
   - Parse timestamps and normalize formats

2. **Analyze Patterns**:
   - Identify error frequency and trends
   - Detect error spikes or anomalies
   - Find common error messages
   - Track error patterns over time
   - Identify correlation between events

3. **Generate Insights**:
   - Most frequent errors
   - Error rate trends
   - Performance metrics from logs
   - User activity patterns
   - System health indicators

4. **Provide Recommendations**:
   - Root cause analysis
   - Suggested fixes for common errors
   - Logging improvements
   - Monitoring suggestions

## Log Format Detection

### JSON Logs
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "error",
  "message": "Database connection failed",
  "service": "api",
  "userId": "12345",
  "error": {
    "code": "ECONNREFUSED",
    "stack": "Error: connect ECONNREFUSED..."
  }
}
```

### Standard Format (Combined)
```
192.168.1.1 - - [15/Jan/2024:10:30:00 +0000] "GET /api/users HTTP/1.1" 500 1234 "-" "Mozilla/5.0..."
```

### Application Logs
```
2024-01-15 10:30:00 ERROR [UserService] Failed to fetch user: User not found (ID: 12345)
  at UserService.getUser (user-service.js:45:10)
  at async API.handler (api.js:23:5)
```

## Analysis Patterns

### Error Frequency Analysis
```markdown
## Top 10 Errors (Last 24h)

1. **Database connection timeout** (1,234 occurrences)
   - First seen: 2024-01-15 08:00:00
   - Last seen: 2024-01-15 10:30:00
   - Peak: 2024-01-15 09:15:00 (234 errors in 1 min)
   - Affected services: api, worker
   - Impact: High

2. **User not found** (567 occurrences)
   - Pattern: Regular distribution
   - Likely cause: Normal user behavior
   - Impact: Low

3. **Rate limit exceeded** (345 occurrences)
   - Source IPs: 192.168.1.100, 10.0.0.50
   - Pattern: Burst traffic
   - Impact: Medium
```

### Timeline Analysis
```markdown
## Error Timeline

08:00 - Normal operations (5-10 errors/min)
09:00 - Database connection errors spike (200+ errors/min)
09:15 - Peak error rate (234 errors/min)
09:30 - Database connection restored
10:00 - Return to normal (8-12 errors/min)

## Correlation
- Traffic increased 300% at 09:00
- Database CPU at 95% during incident
- Connection pool exhausted
```

### Performance Metrics
```markdown
## Response Times (from logs)

**Average**: 234ms
**P50**: 180ms
**P95**: 450ms
**P99**: 890ms

**Slow Requests** (>1s):
- /api/search: 2.3s avg (45 requests)
- /api/reports: 1.8s avg (23 requests)

**Fast Requests** (<100ms):
- /api/health: 5ms avg
- /api/status: 12ms avg
```

## Usage Examples

```
@log-analyzer
@log-analyzer app.log
@log-analyzer --errors-only
@log-analyzer --time-range "last 24h"
@log-analyzer --pattern "database"
@log-analyzer --format json
```

## Report Format

```markdown
# Log Analysis Report
**Period**: 2024-01-15 00:00:00 to 2024-01-15 23:59:59
**Log File**: /var/log/app.log
**Total Entries**: 145,678
**Errors**: 2,345 (1.6%)
**Warnings**: 8,901 (6.1%)

---

## Executive Summary

- **Critical Issues**: 3
- **High Priority**: 8
- **Medium Priority**: 15
- **Overall Health**: ⚠️ Degraded (Database issues detected)

### Key Findings
1. Database connection pool exhaustion at 09:00-09:30
2. Rate limiting triggered for 2 IP addresses
3. Slow query performance on search endpoint
4. Memory leak warning in worker service

---

## Critical Issues

### 1. Database Connection Pool Exhaustion
**Severity**: Critical
**Occurrences**: 1,234
**Time Range**: 09:00:00 - 09:30:00
**Impact**: Service degradation, failed requests

**Error Pattern**:
```
Error: connect ETIMEDOUT
Error: Too many connections
Error: Connection pool timeout
```

**Root Cause Analysis**:
- Traffic spike (300% increase)
- Connection pool size: 10 (insufficient)
- Connections not being released properly
- No connection timeout configured

**Recommendations**:
1. Increase connection pool size to 50
2. Implement connection timeout (30s)
3. Review connection release logic
4. Add connection pool monitoring
5. Implement circuit breaker pattern

**Code Fix**:
```javascript
// Increase pool size
const pool = new Pool({
  max: 50,  // was: 10
  min: 5,
  acquireTimeoutMillis: 30000,
  idleTimeoutMillis: 30000
});

// Ensure connections are released
try {
  const client = await pool.connect();
  const result = await client.query('SELECT * FROM users');
  return result;
} finally {
  client.release(); // Always release!
}
```

---

### 2. Memory Leak in Worker Service
**Severity**: Critical
**First Detected**: 06:00:00
**Pattern**: Memory usage increasing 50MB/hour

**Evidence**:
```
06:00 - Memory: 512MB
09:00 - Memory: 662MB
12:00 - Memory: 812MB
15:00 - Memory: 962MB (WARNING threshold)
```

**Likely Causes**:
- Event listeners not cleaned up
- Cached data not being cleared
- Circular references

**Recommendations**:
1. Add heap snapshot analysis
2. Review event listener cleanup
3. Implement cache eviction policy
4. Monitor with heap profiler

---

## High Priority Issues

### 3. Slow Search Query Performance
**Severity**: High
**Endpoint**: /api/search
**Occurrences**: 45 requests
**Average Response**: 2.3s (target: <500ms)

**Slow Query Examples**:
```
2024-01-15 10:15:23 WARN [SearchService] Query took 2,345ms
  SELECT * FROM products WHERE name LIKE '%keyword%'
  Rows examined: 1,234,567
```

**Recommendations**:
1. Add full-text search index
2. Implement pagination (limit results)
3. Use Elasticsearch for search
4. Add query result caching

---

### 4. Rate Limit Violations
**Severity**: High
**Affected IPs**: 2
**Requests Blocked**: 345

**Details**:
- IP: 192.168.1.100 (245 blocked requests)
  - Pattern: Automated scraping
  - Recommendation: Consider permanent block

- IP: 10.0.0.50 (100 blocked requests)
  - Pattern: Burst traffic from legitimate user
  - Recommendation: Increase rate limit for authenticated users

---

## Error Distribution

### By Severity
- **ERROR**: 2,345 (1.6%)
- **WARN**: 8,901 (6.1%)
- **INFO**: 134,432 (92.3%)

### By Service
- **api**: 1,567 errors
- **worker**: 456 errors
- **scheduler**: 234 errors
- **auth**: 88 errors

### By Error Type
1. Database errors: 1,234 (52.6%)
2. Validation errors: 567 (24.2%)
3. Rate limit errors: 345 (14.7%)
4. Authentication errors: 199 (8.5%)

---

## Performance Metrics

### Response Times
| Endpoint | Avg | P50 | P95 | P99 | Max |
|----------|-----|-----|-----|-----|-----|
| /api/users | 123ms | 95ms | 230ms | 450ms | 890ms |
| /api/search | 2,300ms | 1,800ms | 4,500ms | 6,200ms | 8,900ms |
| /api/posts | 156ms | 120ms | 280ms | 520ms | 780ms |
| /api/health | 5ms | 4ms | 8ms | 12ms | 25ms |

### Traffic Patterns
- **Peak**: 09:15:00 (1,234 req/min)
- **Average**: 410 req/min
- **Quiet Period**: 02:00-05:00 (45 req/min)

---

## User Activity

### Top Users by Request Count
1. User ID 12345: 2,345 requests
2. User ID 67890: 1,890 requests
3. User ID 11111: 1,456 requests

### Failed Authentication Attempts
- Total: 199
- Unique Users: 45
- Suspicious Pattern: User 99999 (23 failed attempts)

---

## Recommendations

### Immediate Actions (Today)
1. ✓ Increase database connection pool
2. ✓ Investigate memory leak in worker
3. ✓ Block suspicious IP (192.168.1.100)
4. ✓ Add monitoring for connection pool

### Short Term (This Week)
1. Optimize search queries
2. Implement query result caching
3. Review event listener cleanup
4. Add circuit breaker for database
5. Increase rate limits for authenticated users

### Long Term (This Month)
1. Migrate search to Elasticsearch
2. Implement comprehensive APM
3. Add automated log analysis
4. Set up predictive alerting
5. Improve error handling and logging

---

## Logging Improvements

### Missing Information
- Request IDs (for tracing)
- User context in some services
- Performance metrics in worker logs
- Structured error codes

### Suggested Log Format
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "error",
  "requestId": "req-abc-123",
  "service": "api",
  "userId": "12345",
  "endpoint": "/api/users",
  "method": "GET",
  "statusCode": 500,
  "duration": 234,
  "error": {
    "code": "DB_CONNECTION_ERROR",
    "message": "Database connection failed",
    "stack": "..."
  }
}
```

---

## Monitoring Alerts to Set Up

1. **Database Connection Errors** > 10/min
2. **Response Time P95** > 500ms
3. **Error Rate** > 2%
4. **Memory Usage** > 80%
5. **Rate Limit Hits** > 100/hour from single IP
```

## Analysis Techniques

### Regular Expression Patterns
```bash
# Find all errors
grep -E "ERROR|Exception|Failed" app.log

# Extract timestamps and errors
grep "ERROR" app.log | awk '{print $1, $2, $4}'

# Count error types
grep "ERROR" app.log | cut -d':' -f2 | sort | uniq -c | sort -nr

# Find slow requests
awk '$7 > 1000 {print $0}' access.log  # Response time > 1s
```

### Time-Based Analysis
```bash
# Errors per hour
awk '{print $1" "$2}' app.log | cut -d':' -f1 | uniq -c

# Peak error times
grep "ERROR" app.log | cut -d' ' -f2 | cut -d':' -f1 | sort | uniq -c | sort -nr
```

## Tools Integration

- **Elasticsearch + Kibana**: Centralized logging and visualization
- **Splunk**: Enterprise log management
- **Datadog**: APM and log analysis
- **CloudWatch**: AWS log aggregation
- **Grafana Loki**: Open-source log aggregation
- **Papertrail**: Simple log management

## Notes

- Always consider log volume and retention
- Implement log rotation and archiving
- Use structured logging (JSON) for easier parsing
- Include request IDs for distributed tracing
- Set up alerts for critical error patterns
- Regular log analysis prevents incidents
- Correlation with metrics provides better insights
