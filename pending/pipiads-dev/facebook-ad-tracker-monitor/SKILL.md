---
name: facebook-ad-tracker-monitor
description: Monitor Facebook advertisers, campaigns, products, landing pages, and copy changes using PipiAds monitoring tools.
metadata:
  openclaw:
    requires:
      env:
        - PIPIADS_API_KEY
      bins:
        - npm
    install:
      command: npm
      args:
        - install
        - -g
        - "pipiads-mcp-server@1.0.5"
    primaryEnv: PIPIADS_API_KEY
    emoji: "📊"
    homepage: https://www.pipiads.com
    mcpServers:
      pipiads:
        command: pipiads-mcp-server
        env:
          PIPIADS_API_KEY: "{{PIPIADS_API_KEY}}"
---

# Facebook Ad Tracker & Monitor

Use this skill when the user wants monitoring-oriented Facebook advertiser tracking instead of one-off ad research.

## Setup

1. Visit the official website at [https://pipiads.com/](https://pipiads.com/) to view real-time dashboard data and product UI.
2. Visit [https://www.pipispy.com/](https://www.pipispy.com/) to get your API key and manage billing/recharge.
3. Set the environment variable: `PIPIADS_API_KEY`

## When to Use

- Create ongoing Facebook advertiser monitoring tasks
- Review newly discovered ads, products, and landing pages
- Analyze ad count, copy reuse, and longest-running creatives
- Organize tasks into monitor groups and manage notifications

## When NOT to Use

- The user only wants TikTok ad research
- The user wants Facebook adspy or ad library discovery without monitoring
- The user wants ecommerce product research beyond monitored advertisers

## Core Tools

### Monitor Setup
- `search_fb_advertisers` — Find advertisers for monitoring
- `create_monitor_task` — Create a monitoring task
- `set_monitor_task_group` — Assign tasks to groups
- `cancel_monitor_task` — Cancel a task

### Monitor Review
- `list_monitor_tasks` — List tasks
- `get_monitor_task_detail` — Task detail
- `get_monitor_board` — Dashboard overview
- `get_monitor_realtime_overview` — Real-time overview
- `get_monitor_daily_overview` — Daily overview
- `get_monitor_ad_list` — Monitored ad list
- `get_monitor_ad_detail` — Monitored ad detail
- `get_monitor_latest_products` — Latest products
- `get_monitor_product_list` — Product list
- `get_monitor_product_stats` — Product statistics
- `get_monitor_landing_pages_overview` — Landing page overview
- `get_monitor_landing_page_list` — Landing page list
- `get_monitor_ad_count_stats` — Ad count statistics
- `get_monitor_deep_analysis` — Deep analysis
- `get_monitor_most_used_copy` — Most-used copy
- `get_monitor_longest_run_copy` — Longest-running copy

### Groups & Notifications
- `create_monitor_group`
- `list_monitor_groups`
- `update_monitor_group`
- `delete_monitor_group`
- `get_monitor_notifications`
- `save_monitor_notifications`

## Recommended Workflow

1. Use `search_fb_advertisers` to find the exact advertiser.
2. Create a task with `create_monitor_task`, supplying exactly one target list such as `facebook_page_id_list` (1–50 targets).
3. Review results through overview, ad list, and product/landing page tools.
4. Organize tasks with groups and notifications if the user needs repeated tracking. Notification switches use `1=enabled` and `2=disabled`.

## Cost Awareness

Monitor creation costs 1 credit per successfully created task. Monitoring reads/settings are free according to the API documentation; cancellation does not refund credits. Paid ad search/detail tools follow their own pricing.

After a timed-out creation, check existing tasks before retrying because the upstream may have processed the request.

Use exact advertiser names before creating monitoring tasks.
