---
name: campaign-performance-report
description: Produce campaign performance reports from BulkPublish analytics with platform-aware metrics, caveats, and recommendations.
---

# Campaign Performance Report

Turn a date range, campaign label, channel set, or post list into an evidence-based report.

## Workflow

1. Define the reporting window, campaign scope, objectives, comparison period, and audience for the report.
2. Use BulkPublish `list_posts`, `get_analytics`, and `get_post_metrics` as appropriate.
3. Check `metricsSupported` and `supportedMetrics` before reporting any per-platform metric; an unsupported metric is not a measured zero.
4. Keep BulkPublish `linkClicks` separate from platform-native `clicks` and disclose tracking limitations.
5. Summarize results by platform, format, theme, and timing, then give prioritized recommendations linked to observed evidence.

Do not infer conversions, sentiment, reach, or attribution that BulkPublish does not provide.
