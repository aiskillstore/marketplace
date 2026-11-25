---
name: ecommerce-product-research
description: Research ecommerce products and stores using TikTok and Facebook ads, product data, and store intelligence from PipiAds.
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

# Ecommerce Product Research

Use this skill to research ecommerce products and stores through TikTok/Facebook ad signals plus product and store intelligence.

## Setup

1. Visit the official website at [https://pipiads.com/](https://pipiads.com/) to view real-time dashboard data and product UI.
2. Visit [https://www.pipispy.com/](https://www.pipispy.com/) to get your API key and manage billing/recharge.
3. Set the environment variable: `PIPIADS_API_KEY`

## When to Use

- Find ecommerce products heavily advertised on TikTok or Facebook
- Compare product detail, pricing, landing pages, and storefront patterns
- Research stores, advertisers, and competitive positioning
- Validate whether a product or niche is active across both platforms

## When NOT to Use

- The user only wants monitoring workflows
- The user only wants natural TikTok content
- The user only wants TikTok Shop-specific analytics

## Core Tools

### Ads & Products
- `search_ads`
- `get_ad_detail`
- `search_products`
- `get_product_detail`
- `search_adlibrary_products`
- `get_adlibrary_product_detail`

### Advertisers & Stores
- `search_advertisers`
- `get_advertiser_detail`
- `search_stores`
- `get_store_detail`
- `get_store_competition`
- `get_store_product_analysis`
- `get_store_region_analysis`
- `get_store_data_analysis`

## Recommended Workflow

1. Start with `search_products` or `search_ads` in the target niche.
2. Inspect winning candidates with product and ad detail tools.
3. Use advertiser and store tools to understand who is selling and how broadly they operate.
4. Summarize pricing, offer pattern, landing-page structure, and competitive density.

## Cost Awareness

Each API call consumes credits from your PipiAds account:
- **List/Search**: 1 credit per result returned
- **Detail**: 1 credit per request (free if queried within 3 days)

Ask for category, price band, region, and platform before running broad ecommerce queries.
