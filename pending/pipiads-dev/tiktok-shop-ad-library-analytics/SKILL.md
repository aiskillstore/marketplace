---
name: tiktok-shop-ad-library-analytics
description: Research TikTok ads alongside TikTok Shop products and stores using PipiAds ad and TikTok Shop analytics tools.
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

# TikTok Shop Ad Library & TikTok Shop Analytics

Use this skill when the user wants TikTok ad research together with TikTok Shop product and store analytics.

## Setup

1. Visit the official website at [https://pipiads.com/](https://pipiads.com/) to view real-time dashboard data and product UI.
2. Visit [https://www.pipispy.com/](https://www.pipispy.com/) to get your API key and manage billing/recharge.
3. Set the environment variable: `PIPIADS_API_KEY`

## When to Use

- Find TikTok ads tied to strong TikTok Shop products
- Analyze TikTok Shop product momentum, GMV, sales, and pricing
- Research TikTok Shop stores and compare store-level positioning
- Connect ad creatives with shop product and store performance

## When NOT to Use

- The user only wants Facebook ad library or monitoring
- The user wants general ecommerce product research across both platforms
- The user wants only natural TikTok content without shop analytics

## Core Tools

### TikTok Ads
- `search_ads`
- `get_ad_detail`
- `search_products`
- `get_product_detail`

### TikTok Shop Products & Stores
- `search_tiktok_products`
- `get_tiktok_product_detail`
- `search_tiktok_shops`
- `get_tiktok_shop_detail`

## Recommended Workflow

1. Use `search_ads` to find TikTok creatives in the niche.
2. Use `search_tiktok_products` to find strong shop products in the same niche.
3. Inspect product and store records with detail tools.
4. Summarize how creative patterns connect to shop performance.

## Cost Awareness

Each API call consumes credits from your PipiAds account:
- **List/Search**: 1 credit per result returned
- **Detail**: 1 credit per request (free if queried within 3 days)

Ask for category, region, price band, and time window before broad TikTok Shop research.
