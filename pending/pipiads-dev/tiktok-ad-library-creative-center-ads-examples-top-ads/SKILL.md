---
name: tiktok-ad-library-creative-center-ads-examples-top-ads
description: Research TikTok ad creatives, examples, and top-performing ad patterns using PipiAds TikTok ad discovery tools.
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

# TikTok Ad Library & TikTok Creative Center & TikTok Ads Examples & TikTok Top Ads

Use this skill for TikTok-first creative research, ad inspiration, and top-ad example discovery.

## Setup

1. Visit the official website at [https://pipiads.com/](https://pipiads.com/) to view real-time dashboard data and product UI.
2. Visit [https://www.pipispy.com/](https://www.pipispy.com/) to get your API key and manage billing/recharge.
3. Set the environment variable: `PIPIADS_API_KEY`

## When to Use

- Find TikTok ad examples, top ads, and winning hooks
- Explore TikTok creatives by keyword, region, and engagement
- Analyze advertiser patterns behind strong TikTok campaigns
- Research products and landing pages attached to TikTok ads

## When NOT to Use

- The user wants Facebook monitoring workflows
- The user wants Facebook ad library research
- The user wants TikTok Shop store analytics without ad creative discovery

## Core Tools

- `search_ads` — Search ads and narrow to TikTok
- `get_ad_detail` — Inspect a top TikTok ad
- `search_products` — Find products promoted by TikTok ads
- `get_product_detail` — Inspect product and landing page detail
- `search_advertisers` — Find advertisers behind TikTok creatives
- `get_advertiser_detail` — Review advertiser detail
- `search_stores` — Find stores connected to ad activity
- `get_store_detail` — Inspect a store profile

## Recommended Workflow

1. Start with `search_ads` using TikTok filters plus keyword, region, and time range.
2. Review strong examples with `get_ad_detail`.
3. If the user wants the promoted product or store, follow with product or store detail tools.
4. Summarize hooks, UGC patterns, visual styles, and offer angles.

## Cost Awareness

Each API call consumes credits from your PipiAds account:
- **List/Search**: 1 credit per result returned
- **Detail**: 1 credit per request (free if queried within 3 days)

Ask for niche, region, and time range before broad top-ad searches.
