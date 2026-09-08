---
name: check-quota
description: Check BulkPublish plan limits and current usage. Use when the user asks about their plan, limits, or remaining quota.
---

# BulkPublish — Quota Reference

## get_quota_usage

Takes no parameters. Returns current plan, limits, and usage.

## Response shape

```
plan          — "free", "pro", or "business"
limits        — max values for each resource (-1 means unlimited)
usage         — current consumption for each resource
subscription  — status, currentPeriodEnd, cancelAtPeriodEnd
```

## Plan limits

| Resource | Free | Pro | Business |
|---|---|---|---|
| Posts/day | 5 | 50 | unlimited |
| Posts/month | 50 | 500 | unlimited |
| Channels | 3 | 15 | 55 |
| Scheduled posts | 10 | 100 | unlimited |
| Storage | 500MB | 5GB | 10GB |
| API calls/day | 100 | 5,000 | 50,000 |
| API keys | 1 | 5 | 10 |
| Recurring schedules | 1 | 10 | unlimited |
| Webhooks | 0 | 5 | 10 |
| Labels | 5 | 50 | unlimited |

## Notes

- Daily limits reset at midnight UTC
- Storage is cumulative — delete old media with `delete_media` to free space
- `-1` in the response means unlimited
- Upgrade at app.bulkpublish.com/settings/billing
