---
name: adspy-ad-library-tiktok-facebook
description: Research TikTok and Facebook ads plus Meta Ad Library results in one combined cross-platform PipiAds skill.
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

# Adspy & Ad Library: TikTok & Facebook

Use this skill when the user wants one workflow spanning TikTok adspy, Facebook adspy, and Meta Ad Library research.

## Setup

1. Visit the official website at [https://pipiads.com/](https://pipiads.com/) to view real-time dashboard data and product UI.
2. Visit [https://www.pipispy.com/](https://www.pipispy.com/) to get your API key and manage billing/recharge.
3. Set the environment variable: `PIPIADS_API_KEY`

## When to Use

- Compare ad trends across TikTok and Facebook
- Search both adspy datasets and Meta Ad Library data
- Validate whether a product or advertiser appears across multiple surfaces
- Research creatives, products, advertisers, and stores across both platforms

## When NOT to Use

- The user only wants monitoring workflows
- The user only wants TikTok Shop analytics
- The user only wants natural TikTok content discovery

## Core Tools

### Adspy
- `search_ads`
- `get_ad_detail`
- `search_products`
- `get_product_detail`
- `search_advertisers`
- `get_advertiser_detail`
- `search_stores`
- `get_store_detail`

### Ad Library
- `search_lib_ads`
- `get_lib_ad_detail`
- `search_adlibrary_products`
- `get_adlibrary_product_detail`
- `get_store_ad_trend`
- `get_store_delivery_analysis`
- `get_store_longest_run_ads`
- `get_store_most_used_ads`
- `get_store_fb_pages`

## Recommended Workflow

1. Start with `search_ads` for cross-platform adspy discovery.
2. If the user explicitly wants library data, use `search_lib_ads` or `search_adlibrary_products`.
3. Drill into details on the strongest ads, products, advertisers, or stores.
4. Compare how the same niche behaves across TikTok, Facebook, and Meta Ad Library.

## Cost Awareness

Each API call consumes credits from your PipiAds account:
- **List/Search**: 1 credit per result returned
- **Detail**: 1 credit per request (free if queried within 3 days)

Clarify whether the user wants adspy, ad library, or both before running broad searches.
