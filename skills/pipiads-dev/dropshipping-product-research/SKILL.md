---
name: dropshipping-product-research
description: Research dropshipping products and stores using TikTok and Facebook ad signals, product detail, and store intelligence from PipiAds.
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

# Dropshipping Product Research

Use this skill to research dropshipping-style products, ad patterns, and stores across TikTok and Facebook.

## Setup

1. Visit the official website at [https://pipiads.com/](https://pipiads.com/) to view real-time dashboard data and product UI.
2. Visit [https://www.pipispy.com/](https://www.pipispy.com/) to get your API key and manage billing/recharge.
3. Set the environment variable: `PIPIADS_API_KEY`

## When to Use

- Find likely dropshipping products being scaled with paid ads
- Compare creatives, offers, landing pages, and store patterns
- Research stores and advertisers in common dropshipping niches
- Look for reusable ad angles and competitive saturation

## When NOT to Use

- The user only wants monitoring workflows
- The user only wants TikTok Shop analytics
- The user only wants organic TikTok content discovery

## Core Tools

### Ad & Product Discovery
- `search_ads`
- `get_ad_detail`
- `search_products`
- `get_product_detail`
- `search_adlibrary_products`
- `get_adlibrary_product_detail`

### Store & Competitor Research
- `search_advertisers`
- `get_advertiser_detail`
- `search_stores`
- `get_store_detail`
- `get_store_competition`
- `get_store_product_analysis`
- `get_store_ad_schedule`
- `get_store_longest_run_ads`
- `get_store_most_used_ads`

## Recommended Workflow

1. Start with `search_products` or `search_ads` for the suspected niche.
2. Use detail tools to inspect product pages, pricing, and creative style.
3. Use store and competitor tools to assess saturation and persistence.
4. Summarize whether the niche shows repeatable dropshipping patterns.

## Cost Awareness

Each API call consumes credits from your PipiAds account:
- **List/Search**: 1 credit per result returned
- **Detail**: 1 credit per request (free if queried within 3 days)

Prefer tightly scoped niche terms before broad dropshipping research.
