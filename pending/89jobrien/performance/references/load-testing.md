---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: performance
---

# Load Testing and Stress Testing

Comprehensive guide for load testing, stress testing, capacity planning, and performance benchmarking.

## Load Testing

### Purpose

Test system under expected load to verify:

- System handles expected traffic
- Response times meet requirements
- Error rates are acceptable
- Resource usage is within limits

### Tools

**k6:**

- Script-based load testing
- JavaScript test scripts
- Good for API testing
- Cloud and on-premise

**Artillery:**

- YAML-based configuration
- Easy to get started
- Good for HTTP APIs
- Supports WebSockets

**JMeter:**

- GUI-based test creation
- Comprehensive features
- Good for complex scenarios
- Java-based

**Locust:**

- Python-based
- Code-based test scenarios
- Distributed testing
- Real-time web UI

### k6 Example

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],   // Error rate < 1%
  },
};

export default function() {
  const res = http.get('https://api.example.com/users');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

### Artillery Example

```yaml
config:
  target: 'https://api.example.com'
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 120
      arrivalRate: 50
      name: "Sustained load"
scenarios:
  - name: "Get users"
    flow:
      - get:
          url: "/users"
          expect:
            - statusCode: 200
            - contentType: json
```

## Stress Testing

### Purpose

Find breaking points and system limits:

- Maximum capacity
- Failure points
- Degradation patterns
- Recovery behavior

### Approach

1. Start with baseline load
2. Gradually increase load
3. Monitor system behavior
4. Identify failure point
5. Analyze degradation patterns

### Example: Stress Test Scenario

```javascript
export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Baseline
    { duration: '2m', target: 100 },  // Increase
    { duration: '2m', target: 200 },  // Increase more
    { duration: '2m', target: 400 },  // Push limits
    { duration: '2m', target: 800 },  // Find breaking point
    { duration: '5m', target: 800 },  // Hold at breaking point
    { duration: '2m', target: 0 },    // Ramp down
  ],
};
```

## Capacity Planning

### Purpose

Determine resource needs for:

- Future growth
- Peak traffic periods
- Scaling requirements
- Cost estimation

### Analysis Process

1. **Measure Current Capacity**
   - Maximum concurrent users
   - Peak throughput
   - Resource utilization at peak

2. **Project Future Needs**
   - Expected growth rate
   - Peak traffic estimates
   - Seasonal variations

3. **Calculate Requirements**
   - Server capacity needed
   - Database scaling needs
   - Network bandwidth requirements

4. **Plan Scaling Strategy**
   - Horizontal vs vertical scaling
   - Auto-scaling triggers
   - Cost optimization

### Example: Capacity Analysis

```markdown
## Capacity Planning Analysis

### Current State
- **Peak Concurrent Users**: 1,000
- **Peak Throughput**: 500 req/s
- **Server Utilization**: 70% CPU, 60% memory
- **Database Connections**: 50/100

### Projected Growth
- **6 months**: 2,000 concurrent users (2x)
- **12 months**: 4,000 concurrent users (4x)

### Scaling Requirements
- **Servers**: 2x current capacity (4 servers → 8 servers)
- **Database**: Upgrade to larger instance or add read replicas
- **Load Balancer**: Current capacity sufficient
- **CDN**: Already in place, no changes needed

### Cost Estimate
- **Current**: $500/month
- **6 months**: $1,000/month
- **12 months**: $2,000/month
```

## Performance Benchmarks

### Key Metrics

**Response Time:**

- p50 (median)
- p95 (95th percentile)
- p99 (99th percentile)
- Max response time

**Throughput:**

- Requests per second
- Transactions per second
- Concurrent users supported

**Error Rate:**

- Percentage of failed requests
- Error types and frequencies
- Error distribution over time

**Resource Utilization:**

- CPU usage
- Memory usage
- Network bandwidth
- Disk I/O

### Benchmark Targets

**API Endpoints:**

- p95 response time: < 500ms
- p99 response time: < 1000ms
- Error rate: < 0.1%
- Throughput: > 1000 req/s

**Database:**

- Query time: < 100ms (p95)
- Connection pool: < 80% utilization
- Lock contention: Minimal

**Frontend:**

- LCP: < 2.5s
- FID: < 100ms
- CLS: < 0.1
- TTI: < 3.5s

## Test Scenarios

### Baseline Test

**Purpose**: Establish performance baseline

**Configuration:**

- Low, steady load
- Measure normal performance
- Identify normal resource usage

### Spike Test

**Purpose**: Test system response to sudden load increases

**Configuration:**

- Sudden load increase
- Measure recovery time
- Test auto-scaling

### Endurance Test

**Purpose**: Test system stability over time

**Configuration:**

- Sustained load for extended period
- Check for memory leaks
- Monitor resource degradation

### Volume Test

**Purpose**: Test system with large data volumes

**Configuration:**

- Large dataset
- High transaction volume
- Test database performance

## Best Practices

### Test Design

1. **Define Requirements**: Set performance targets first
2. **Realistic Scenarios**: Use realistic user behavior
3. **Progressive Testing**: Start with baseline, then increase
4. **Monitor Resources**: Track CPU, memory, network
5. **Analyze Results**: Identify bottlenecks and optimize

### Test Execution

1. **Start Small**: Begin with low load
2. **Gradual Increase**: Ramp up slowly
3. **Monitor Continuously**: Watch metrics in real-time
4. **Document Results**: Record all findings
5. **Iterate**: Run multiple test cycles

### Result Analysis

1. **Identify Bottlenecks**: Find slow components
2. **Correlate Metrics**: Link performance to resources
3. **Compare Baselines**: Track improvements
4. **Document Findings**: Record all insights
5. **Recommend Actions**: Provide actionable fixes

## Common Issues Found

### Under Load

**High Response Times:**

- Database bottlenecks
- Slow external APIs
- Insufficient resources
- Inefficient algorithms

**High Error Rates:**

- Resource exhaustion
- Timeout issues
- Connection pool exhaustion
- Rate limiting

**Resource Exhaustion:**

- Memory leaks
- Connection leaks
- CPU saturation
- Disk I/O limits

## Tools Comparison

### k6

- **Best for**: API testing, CI/CD integration
- **Pros**: Script-based, good reporting, cloud support
- **Cons**: Requires JavaScript knowledge

### Artillery

- **Best for**: Quick API tests, YAML configuration
- **Pros**: Easy to use, good documentation
- **Cons**: Less flexible than code-based tools

### JMeter

- **Best for**: Complex scenarios, GUI users
- **Pros**: Comprehensive features, GUI interface
- **Cons**: Resource intensive, Java-based

### Locust

- **Best for**: Python developers, distributed testing
- **Pros**: Python-based, real-time UI, distributed
- **Cons**: Less mature than JMeter
