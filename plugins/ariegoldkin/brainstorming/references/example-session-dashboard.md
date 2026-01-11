# Example Session: Real-Time Dashboard Design

This complete example demonstrates brainstorming workflow for a real-time analytics dashboard.

## Context

User request: "Build me a real-time dashboard to track user activity on my SaaS app."

## Phase 1: Understanding

### Question 1 (Purpose)
**Open-ended:** "What specific user activities do you want to track on this dashboard?"

**User response:** "Logins, API calls, errors, active users right now."

### Question 2 (Constraints)
**Using AskUserQuestion tool:**

```
Question: "What's your data volume and update frequency?"
Header: "Scale Requirements"
Options:
  - "Low volume"
    Description: <1000 users, updates every 5-10 seconds acceptable
  - "Medium volume"
    Description: 1k-50k users, need 1-2 second updates
  - "High volume"
    Description: >50k users, need sub-second updates, streaming data
```

**User selects:** "Medium volume" (10k users, 2-second updates okay)

### Question 3 (Success Criteria)
**Open-ended:** "What decisions will you make based on this dashboard?"

**User response:** "Spot issues quickly (error spikes), see if marketing campaigns are working (login spikes), monitor API health."

### Phase 1 Summary
- **Metrics:** Logins, API calls, errors, active users
- **Scale:** 10k users, 2-second update frequency
- **Goal:** Issue detection, campaign tracking, API health monitoring

## Phase 2: Exploration

### Proposed Approaches

**Using AskUserQuestion tool:**

```
Question: "Which data pipeline architecture should we use?"
Header: "Pipeline Design"
Options:
  - "Database polling"
    Description: Query DB every 2 seconds, simple setup, may strain DB at scale
  - "Server-Sent Events (SSE)"
    Description: Push updates from server, real-time, keeps connections open
  - "WebSockets with aggregation"
    Description: Bidirectional real-time, more complex, supports filters
```

**Trade-off Analysis:**

| Approach | Real-time | Complexity | Scalability | Cost |
|----------|-----------|------------|-------------|------|
| DB Polling | 2s delay | Low | Limited (DB strain) | Low |
| SSE | Instant | Medium | Good (one-way) | Medium |
| WebSockets | Instant | High | Excellent | High (connection overhead) |

**Additional consideration:** "For 10k users with 2-second updates, SSE is optimal. WebSockets are overkill since you don't need bidirectional communication."

**User selects:** "Server-Sent Events" (fits requirements, reasonable complexity)

## Phase 3: Design Presentation

### Section 1: Data Flow Architecture

**Present:**
```
Data Pipeline:
1. Application events → Message queue (Redis Streams)
2. Aggregation worker → Process events every 1 second
3. Aggregate results → Store in Redis cache (2-second TTL)
4. SSE endpoint → Push aggregated data to dashboard
5. Dashboard → Render charts with new data

Components:
- Event Producer: Application server (logs events to Redis Stream)
- Aggregation Worker: Node.js worker (consumes stream, calculates metrics)
- Cache Layer: Redis (stores last 60 seconds of aggregated data)
- SSE Server: Express.js endpoint (/api/dashboard/stream)
- Frontend: React + Chart.js (renders real-time updates)
```

**Validate:** "Does this flow make sense for tracking your user activities?"

**User feedback:** "Yes, but what happens if dashboard disconnects?"

### Section 2: Connection Handling

**Present:**
```
SSE Connection Management:
1. On disconnect → Client auto-reconnects with exponential backoff
2. On reconnect → Server sends last 60s of cached data (catch-up)
3. Heartbeat every 30s → Keep connection alive
4. If aggregation worker fails → Fallback to DB polling (degraded mode)

Reconnection Logic:
- 1st attempt: Immediate
- 2nd attempt: 1 second delay
- 3rd attempt: 2 second delay
- Max delay: 30 seconds
- Give up after: 5 minutes (show "Reconnecting..." UI)

Catch-up Strategy:
- Server tracks last event ID per client
- On reconnect, client sends: Last-Event-ID header
- Server replays events since that ID (max 60s buffer)
```

**Validate:** "Does this handle disconnections appropriately?"

**User feedback:** "Great, what about the actual metrics?"

### Section 3: Metrics & Visualization

**Present:**
```
Dashboard Metrics (auto-updating every 2s):

1. Active Users (right now)
   - Metric: Count of unique user_ids in last 5 minutes
   - Visualization: Large number with sparkline
   - Alert: Red if drops >50% from baseline

2. Logins (per minute)
   - Metric: Count of login events in rolling 1-minute window
   - Visualization: Line chart (last 30 minutes)
   - Alert: Green spike if >2x baseline (campaign success)

3. API Calls (per second)
   - Metric: Count of API events per second
   - Visualization: Area chart (last 10 minutes)
   - Alert: Yellow if >80% of rate limit

4. Error Rate (percentage)
   - Metric: (Error count / Total requests) * 100
   - Visualization: Line chart with threshold markers
   - Alert: Red if >5%

Data Retention:
- Real-time view: Last 60 minutes (Redis)
- Historical: Last 30 days (TimescaleDB)
- Switch view: Toggle between "Last hour" and "Today"
```

**Validate:** "Do these metrics and visualizations match what you need?"

**User feedback:** "Perfect, this covers everything"

## Final Design Summary

**Architecture:** Redis Streams → Aggregation Worker → Redis Cache → SSE → React Dashboard

**Metrics:**
- Active users (5-min window)
- Logins per minute (30-min chart)
- API calls per second (10-min chart)
- Error rate percentage (with alerts)

**Resilience:**
- Auto-reconnect with backoff
- 60-second event replay on reconnect
- Fallback to polling if worker fails
- Heartbeat keep-alive

**Data Storage:**
- Real-time: Redis (60 minutes)
- Historical: TimescaleDB (30 days)

## Implementation Priorities

1. **Phase 1:** Basic SSE endpoint + 4 metrics (2-3 days)
2. **Phase 2:** Reconnection logic + error handling (1 day)
3. **Phase 3:** Historical view + TimescaleDB (2 days)
4. **Phase 4:** Alerting system (optional, 1 day)

## Key Takeaways

1. **Chose SSE over WebSockets** → Simpler, fits requirements (no bidirectional needed)
2. **Redis Streams for events** → Natural fit for streaming data
3. **60-second replay buffer** → Handles disconnections gracefully
4. **Degraded mode fallback** → System stays functional even if worker fails
5. **Clear alert thresholds** → Makes dashboard actionable, not just informational

## What Was Avoided

- **Mistake 1:** Starting with WebSockets → Would be overengineered
- **Mistake 2:** Polling database directly → Would strain DB at 10k users
- **Mistake 3:** No reconnection strategy → Poor user experience on network issues
- **Mistake 4:** Storing everything in memory → Would lose data on restart

This design validates requirements early and makes explicit trade-offs before implementation.
