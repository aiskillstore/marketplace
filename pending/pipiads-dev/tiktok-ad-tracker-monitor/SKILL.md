---
name: tiktok-ad-tracker-monitor
description: Research TikTok ad activity and compare changes through repeated PipiAds searches. Persistent monitor tasks are available only for Facebook advertisers and stores, when the user also requests that coverage.
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

# TikTok Ad Tracker & Monitor

Use this skill to research TikTok ads and compare results over time. The available persistent monitor API supports Facebook advertisers and stores/websites; it does not track TikTok campaigns.

## Setup

1. Visit the official website at [https://pipiads.com/](https://pipiads.com/) to view real-time dashboard data and product UI.
2. Visit [https://www.pipispy.com/](https://www.pipispy.com/) to get your API key and manage billing/recharge.
3. Set the environment variable: `PIPIADS_API_KEY`

## When to Use

- Find trending TikTok ads, recurring creatives, and long-running winners
- Compare TikTok advertiser activity through dated search/detail results
- Review Facebook monitor results when the user also requests Facebook coverage
- Analyze creative hooks, angles, engagement, and delivery duration

## When NOT to Use

- The user only wants Facebook-only ad library research
- The user wants TikTok Shop product/store analytics without ad research
- The user wants general market research outside PipiAds data

## Core Tools

### TikTok Ad Research
- `search_ads` — Search ads and narrow to TikTok with platform filters
- `get_ad_detail` — Inspect a specific ad in detail
- `search_advertisers` — Find advertisers behind TikTok campaigns
- `get_advertiser_detail` — Inspect advertiser details

### Optional Facebook Monitoring

Use these tools only for requested Facebook advertiser or store coverage. Do not pass a TikTok advertiser ID or imply that a Facebook task tracks TikTok activity.
- `search_fb_advertisers` — Find advertiser entry points for monitor setup
- `create_monitor_task` — Create a Facebook monitoring task using exactly one target list, such as `facebook_page_id_list`
- `list_monitor_tasks` — List existing monitor tasks
- `get_monitor_task_detail` — View task details
- `get_monitor_board` — Review monitoring dashboard
- `get_monitor_realtime_overview` — Real-time task overview
- `get_monitor_daily_overview` — Daily performance overview
- `get_monitor_ad_list` — Review monitored ads
- `get_monitor_ad_detail` — Review a monitored ad in detail
- `get_monitor_latest_products` — See newly found products
- `get_monitor_landing_page_list` — Review landing pages
- `cancel_monitor_task` — Stop a monitoring task

## Recommended Workflow

1. Start with `search_ads` and constrain to TikTok, region, and time range.
2. Use `get_ad_detail` to inspect the strongest creatives.
3. For TikTok comparisons, repeat the relevant search/detail queries and state each query's date and filters. Persistent TikTok monitoring is not exposed by this MCP.
4. If the user also requests Facebook monitoring, resolve the matching Facebook page or store and pass one supported target list to `create_monitor_task`. Review its results as Facebook data.

## Cost Awareness

Paid search results typically cost 1 credit each; paid details typically cost 1 credit with the documented repeat-query exemption. Facebook monitor creation costs 1 credit per successful task. Monitoring reads/settings are free according to the API documentation.

Use narrow TikTok searches and distinguish their results from Facebook monitor data.
