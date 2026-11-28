---
name: facebook-adspy-facebook-ad-library
description: Research Facebook ad creatives and Meta Ad Library results using PipiAds adspy and ad library tools.
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

# Facebook Adspy & Facebook Ad Library

Use this skill for Facebook-focused ad research across adspy and Meta Ad Library datasets.

## Setup

1. Visit the official website at [https://pipiads.com/](https://pipiads.com/) to view real-time dashboard data and product UI.
2. Visit [https://www.pipispy.com/](https://www.pipispy.com/) to get your API key and manage billing/recharge.
3. Set the environment variable: `PIPIADS_API_KEY`

## When to Use

- Find Facebook ads by keyword, advertiser pattern, region, or engagement
- Search Meta Ad Library ads and products
- Compare Facebook creatives, offers, landing pages, and advertiser behavior
- Inspect specific ads or ad library records in detail

## When NOT to Use

- The user wants monitoring workflows rather than one-off research
- The user wants TikTok-only ads or TikTok Shop analytics
- The user wants natural TikTok content research

## Core Tools

### Facebook Adspy
- `search_ads` — Search ads and narrow to Facebook
- `get_ad_detail` — Inspect a specific ad
- `search_products` — Find products heavily advertised on Facebook
- `get_product_detail` — Product detail
- `search_advertisers` — Find advertisers
- `get_advertiser_detail` — Advertiser detail

### Facebook / Meta Ad Library
- `search_lib_ads` — Search Meta Ad Library ads
- `get_lib_ad_detail` — Get ad library ad detail
- `search_adlibrary_products` — Search Meta Ad Library products
- `get_adlibrary_product_detail` — Get product detail from ad library
- `get_store_ad_trend` — Store ad trend analysis from Meta Ad Library
- `get_store_delivery_analysis` — Delivery analysis
- `get_store_longest_run_ads` — Longest-running ads
- `get_store_most_used_ads` — Most-used ads
- `get_store_fb_pages` — Facebook advertiser pages

## Recommended Workflow

1. Start with `search_ads` or `search_lib_ads` depending on whether the user wants adspy or ad library data.
2. Narrow by region, active days, keyword, and advertiser.
3. Use detail tools on the best candidates.
4. If store-level Facebook patterns matter, use the Meta-oriented store analysis tools.

## Cost Awareness

Each API call consumes credits from your PipiAds account:
- **List/Search**: 1 credit per result returned
- **Detail**: 1 credit per request (free if queried within 3 days)

Prefer a clearly specified platform and region before broad Facebook searches.
