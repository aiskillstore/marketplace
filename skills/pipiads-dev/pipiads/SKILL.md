---
name: pipiads
description: AI-powered TikTok & Facebook Adspy and Ad Library research for ads, products, stores, landing pages, advertisers, and competitors. Find trending ads, analyze creative hooks, discover winning products, monitor campaigns, and perform image-based search.
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

# PipiAds - TikTok & Facebook Adspy Intelligence

AI-powered TikTok & Facebook Adspy and Ad Library research for ads, products, stores, landing pages, advertisers, and competitors.

## When to Use

Use this skill when the user wants to:

- Find trending or long-running TikTok or Facebook ads
- Research competitors, advertisers, stores, landing pages, or campaigns
- Discover winning products or fast-rising TikTok Shop items
- Analyze store performance, regional distribution, ad copy, delivery trends, creative hooks, or recurring ad angles
- Research ad trends across ecommerce, DTC, dropshipping, TikTok Shop, apps, games, drama, and AI tools
- Monitor advertisers or campaigns over time
- Search for ads, products, stores, or TikTok Shop items using an image

## When NOT to Use

Do not use this skill when:

- The user only wants general web search results or news
- The user wants creative strategy without underlying ad intelligence data
- The user asks for analytics outside TikTok, Facebook, Meta Ad Library, or PipiAds-supported commerce data
- A broad query would waste credits when a narrower query or clarification is needed first

## Setup

1. Visit the official website at [https://pipiads.com/](https://pipiads.com/) to view real-time dashboard data and product UI.
2. Visit [https://www.pipispy.com/](https://www.pipispy.com/) to get your API key and manage billing/recharge.
3. Set the environment variable: `PIPIADS_API_KEY`

## Installation Note

This skill installs and runs the published npm package `pipiads-mcp-server@1.0.5` as a local MCP server.

Default install:

`npm install -g pipiads-mcp-server@1.0.5`

If you prefer stricter isolation, use this skill in a dedicated development environment, container, or non-critical workstation.

## Trust & Execution Model

This skill installs `pipiads-mcp-server@1.0.5` from the npm registry and runs it locally as an MCP server.

This means:

- npm install scripts may run during installation
- the installed package executes on the local machine
- all API access is mediated through that local MCP server

If you require stricter controls, review the npm package contents and run it in an isolated environment before using it on a primary workstation.

## Verification

This skill depends on:

- official website: `https://pipiads.com/`
- API portal: `https://www.pipispy.com/`
- npm package: `pipiads-mcp-server@1.0.5`

Review the package source, publisher, and release history if you need stronger supply-chain assurance before installation.

## Data Handling

This skill sends search queries and optional image inputs to the external PipiAds service through the PipiAds API.

Do not send:

- sensitive personal data
- private customer information
- confidential campaign assets
- unnecessary image inputs

Use image search only when the provided image is safe to transmit to a third-party service.

## Cost Awareness

Pricing depends on the endpoint:

- **List/Search**: 1 credit per result returned
- **Detail**: 1 credit per request (free if queried within 3 days)
- **Monitoring**: 1 credit per successful task creation; reads/settings are free. Cancellation does not refund credits.
- **Image submission**: free; result searches follow their own endpoint pricing.

Prefer narrow queries before broad searches. If the user request is underspecified, clarify platform, region, time range, category, or target object before searching.

## Core Workflow

1. Identify the target object: ad, product, TikTok Shop product, store, advertiser, app, or monitor task
2. Clarify the platform and scope when missing: TikTok, Facebook, Meta Ad Library, region, time range, category, price band, or performance threshold
3. Start with the relevant search/list tool to narrow the candidate set
4. Use detail or analysis tools to inspect the most relevant candidates
5. If the user wants ongoing tracking, use the monitor tools
6. If the user provides an image, use the AI image search workflow

## Quick Reference

| User intent | Recommended tools |
| --- | --- |
| Find trending ads | `search_ads`, `get_ad_detail` |
| Find products being heavily advertised | `search_products`, `get_product_detail` |
| Explore Meta Ad Library products | `search_adlibrary_products`, `get_adlibrary_product_detail` |
| Research TikTok Shop products or stores | `search_tiktok_products`, `get_tiktok_product_detail`, `search_tiktok_shops`, `get_tiktok_shop_detail` |
| Research advertisers, stores, or landing-page patterns | `search_advertisers`, `get_advertiser_detail`, `search_stores`, `get_store_detail` |
| Analyze store competition, creative hooks, or campaign patterns | Store Analysis tools |
| Search Meta Ad Library ads | `search_lib_ads`, `get_lib_ad_detail` |
| Check rankings for products, apps, or developers | Ranking tools |
| Search apps or app developers | `search_apps`, `get_app_detail`, `search_app_developers`, `get_app_developer_detail` |
| Search natural TikTok traffic videos | `search_natural_videos` |
| Create or manage monitoring | Ad Monitor tools + Monitor Groups & Notifications tools |
| Search by image similarity | AI Image Search tools |

## Best Practices

- Default to asking for platform if the user does not specify TikTok vs Facebook
- Ask for region and time range before broad searches whenever those constraints materially affect results
- Prefer search/list first, then detail, to avoid unnecessary credit usage
- For competitor analysis, identify the advertiser or store first, then drill into store analysis or monitor tools
- For monitoring operations, confirm the exact target if the user’s request is ambiguous
- For image search, always submit first, then poll status, then fetch summary/results
- When the user asks for “best” or “winning” ads/products, translate that into explicit metrics such as views, likes, duration, GMV, sales, or ranking filters

## Available Tools (73 total)

### Ad Spy
- `search_ads` — Search ad videos across TikTok and Facebook by keyword, region, platform, engagement metrics, ad spend, delivery days
- `get_ad_detail` — Get detailed info for a specific ad by video ID

### Ad Products
- `search_products` — Search e-commerce products advertised on TikTok/Facebook
- `get_product_detail` — Get product detail including images, price, landing page, Shopify data
- `search_adlibrary_products` — Search Meta Ad Library products
- `get_adlibrary_product_detail` — Get Meta Ad Library product detail

### TikTok Shop
- `search_tiktok_products` — Search TikTok Shop products by sales, GMV, price, trends
- `get_tiktok_product_detail` — Get TikTok Shop product detail
- `search_tiktok_shops` — Search TikTok Shop stores
- `get_tiktok_shop_detail` — Get TikTok Shop store detail

### Advertisers & Stores
- `search_advertisers` — Search advertiser leaderboard
- `get_advertiser_detail` — Get advertiser detail
- `search_stores` — Search store ranking list
- `get_store_detail` — Get store detail by ID

### Store Analysis (13 tools)
- `get_store_competition` — Competition analysis
- `get_store_data_analysis` — All-platform data analysis
- `get_store_play_cost` — Play cost statistics
- `get_store_region_analysis` — Regional ad distribution
- `get_store_ad_copy_analysis` — TikTok ad copy analysis
- `get_store_ad_schedule` — Ad campaign schedule
- `get_store_product_analysis` — Product analysis
- `get_store_rank_data` — Traffic ranking data
- `get_store_ad_trend` — Meta Ad Library ad trend
- `get_store_delivery_analysis` — Meta Ad Library delivery analysis
- `get_store_longest_run_ads` — Longest-running ad content
- `get_store_most_used_ads` — Most-used ad content
- `get_store_fb_pages` — Facebook advertiser pages

### Meta Ad Library
- `search_lib_ads` — Search Meta Ad Library ads
- `get_lib_ad_detail` — Get ad detail by ID

### Rankings
- `get_product_ranking` — Ad product ranking
- `get_new_product_ranking` — New product ranking
- `get_app_ranking` — Top apps ranking
- `get_new_app_ranking` — New apps ranking
- `get_app_dev_ranking` — App developers ranking

### Apps
- `search_apps` — Search apps on TikTok/Facebook
- `get_app_detail` — Get app detail
- `search_app_developers` — Search app developers
- `get_app_developer_detail` — Get developer detail

### Natural Traffic
- `search_natural_videos` — Search TikTok natural traffic videos

### Ad Monitor (20 tools)
- `search_fb_advertisers` — Search Facebook advertisers for monitoring
- `create_monitor_task` — Create monitoring task
- `list_monitor_tasks` — List monitoring tasks
- `get_monitor_task_detail` — Task details
- `cancel_monitor_task` — Cancel task
- `get_monitor_board` — Dashboard overview
- `set_monitor_task_group` — Assign task to group
- `get_monitor_realtime_overview` — Real-time overview
- `get_monitor_daily_overview` — Daily overview
- `get_monitor_landing_pages_overview` — Landing pages overview
- `get_monitor_latest_products` — Latest products
- `get_monitor_product_list` — Product list
- `get_monitor_landing_page_list` — Landing page list
- `get_monitor_ad_count_stats` — Ad count statistics
- `get_monitor_deep_analysis` — Deep campaign analysis
- `get_monitor_most_used_copy` — Most-used ad copy
- `get_monitor_longest_run_copy` — Longest-running ad copy
- `get_monitor_ad_list` — Ad list
- `get_monitor_ad_detail` — Ad detail
- `get_monitor_product_stats` — Product statistics

### Monitor Groups & Notifications
- `create_monitor_group` — Create group
- `list_monitor_groups` — List groups
- `update_monitor_group` — Update group
- `delete_monitor_group` — Delete group
- `get_monitor_notifications` — Get notification settings
- `save_monitor_notifications` — Save notification settings

### AI Image Search (8 tools)
- `ai_search_submit_image` — Submit image for visual search
- `ai_search_image_status` — Check processing status
- `ai_search_image_summary` — Get result summary
- `ai_search_image_ads` — Search similar ads
- `ai_search_image_products` — Search similar products
- `ai_search_image_stores` — Search similar stores
- `ai_search_image_tiktok_products` — Search similar TikTok products
- `ai_search_image_tiktok_shops` — Search similar TikTok shops

## Recommended Workflows

### 1. Ad Research Workflow

Use when the user wants to find winning creatives, trending campaigns, or competitor ads.

1. Start with `search_ads`
2. Narrow by keyword, region, platform, delivery days, spend, or engagement filters
3. Inspect the strongest candidates with `get_ad_detail`
4. Summarize patterns such as hooks, offer angles, duration, or cross-region distribution

### 2. Product Discovery Workflow

Use when the user wants advertised products or product validation.

1. Start with `search_products` or `search_adlibrary_products`
2. Filter by platform, views, timing, niche, or storefront characteristics
3. Use `get_product_detail` or `get_adlibrary_product_detail` for deeper analysis
4. Highlight pricing, landing page patterns, Shopify signals, and creative overlap

### 3. TikTok Shop Workflow

Use when the user asks for rising TikTok Shop products or stores.

1. Use `search_tiktok_products` or `search_tiktok_shops`
2. Narrow by sales, GMV, price, category, or growth trend
3. Use `get_tiktok_product_detail` or `get_tiktok_shop_detail`
4. Summarize momentum, pricing, and store/product positioning

### 4. Store / Competitor Analysis Workflow

Use when the user wants to understand a store’s advertising behavior.

1. Identify the store with `search_stores` or use a known store ID
2. Fetch baseline info with `get_store_detail`
3. Choose the right analysis tool based on the question:
   - competition → `get_store_competition`
   - product mix → `get_store_product_analysis`
   - region mix → `get_store_region_analysis`
   - copy patterns → `get_store_ad_copy_analysis`
   - campaign timing → `get_store_ad_schedule`
   - trend / longest-run / reuse → corresponding store analysis tools

### 5. Meta Ad Library Workflow

Use when the user explicitly wants Meta/Facebook Ad Library results.

1. Start with `search_lib_ads` or `search_adlibrary_products`
2. Filter as tightly as possible
3. Use `get_lib_ad_detail` or `get_adlibrary_product_detail` for specific items

### 6. Monitoring Workflow

Use when the user wants ongoing tracking instead of one-time research.

1. Identify the Facebook advertiser with `search_fb_advertisers`
2. Create a task using `create_monitor_task` with exactly one target list, such as `facebook_page_id_list`, containing 1–50 targets. Persistent monitoring supports Facebook advertisers and stores/websites, not TikTok campaigns.
3. Organize tasks with groups if needed
4. Review ongoing results via monitor overview, ad list, product list, landing page list, or deep analysis tools
5. Cancel tasks with `cancel_monitor_task` when the user no longer needs tracking

### 7. AI Image Search Workflow

Use when the user provides an image and wants visually similar ads, products, stores, or TikTok Shop items.

1. Submit exactly one `image_url` (public HTTP/HTTPS) or `image_data` (Base64 bytes or image data URL, max 10 MiB) with `ai_search_submit_image`. The result is an image ID string.
2. Check processing state with `ai_search_image_status`. Continue when it returns `SEARCH_COMPLETED`; stop on `ANALYSIS_FAILURE` or `SEARCH_FAILURE`.
3. Read the overview with `ai_search_image_summary`
4. Fetch the matching result type:
   - ads → `ai_search_image_ads`
   - products → `ai_search_image_products`
   - stores → `ai_search_image_stores`
   - TikTok products → `ai_search_image_tiktok_products`
   - TikTok shops → `ai_search_image_tiktok_shops`

## Monitor Task Notes

The following tools modify remote state and should be used intentionally:

- `create_monitor_task`
- `cancel_monitor_task`
- `set_monitor_task_group`
- `create_monitor_group`
- `update_monitor_group`
- `delete_monitor_group`
- `save_monitor_notifications`

Before creating, updating, grouping, or deleting monitoring resources, make sure the advertiser, group, or notification target is clear.

Notification switches use `1=enabled` and `2=disabled`. Do not blindly retry a timed-out creation: the upstream may already have created the task. Check existing tasks before attempting another write.

## Usage Examples

- "Search for trending TikTok ads about phone cases in the US"
- "Find Shopify products with over 100k views in the last 30 days"
- "Show me the top advertisers on Facebook this week"
- "Get store competition analysis for store ID c2d5b2547218a"
- "Create a monitor task for advertiser XYZ"
- "Search TikTok Shop products with rising sales in beauty category"

## Scope

This skill ONLY:

- Calls the PipiAds API through the configured MCP server
- Searches and analyzes advertising intelligence data available through PipiAds
- Retrieves ads, products, stores, advertisers, apps, rankings, monitor data, and related analysis results exposed by PipiAds
- Sends image inputs only when the user explicitly requests image-based search
- Creates or manages monitoring resources only when the user explicitly asks for that outcome

This skill NEVER:

- Guarantees a product, ad, or store will be profitable
- Replaces general market research outside supported PipiAds data
- Scrape websites directly outside the PipiAds service
- Access local files unless the user explicitly provides an image for upload
- Send credentials other than the configured `PIPIADS_API_KEY`
- Assume broad default search scopes when key constraints are missing
- Use monitor-management tools unless the requested change is clear

## Credits

See Cost Awareness above for endpoint-specific charges. A successful MCP result includes the original API data as both JSON text and `structuredContent.data`.
