---
name: tiktok-made-me-buy-it
description: Discover TikTok natural traffic videos and organic product-picking signals with PipiAds natural video search tools.
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

# TikTok Made Me Buy It

Use this skill for organic TikTok product discovery based on natural traffic video data.

## Setup

1. Visit the official website at [https://pipiads.com/](https://pipiads.com/) to view real-time dashboard data and product UI.
2. Visit [https://www.pipispy.com/](https://www.pipispy.com/) to get your API key and manage billing/recharge.
3. Set the environment variable: `PIPIADS_API_KEY`

## When to Use

- Find TikTok natural traffic videos tied to product interest
- Research organic product-picking signals and non-paid traction
- Look for strong play, like, and follower patterns in natural content

## When NOT to Use

- The user wants paid ad research across TikTok or Facebook
- The user wants TikTok Shop store analytics
- The user wants Facebook monitoring or Meta Ad Library data

## Core Tools

- `search_natural_videos` — Search TikTok natural traffic videos by plays, likes, followers, and keyword intent

## Recommended Workflow

1. Start with `search_natural_videos` using niche or product keywords.
2. Narrow by engagement signals such as plays, likes, and creator follower count.
3. Summarize repeated product themes and organic hooks.

## Capability Boundary

This skill is intentionally narrow. In the current server, the directly relevant tool is `search_natural_videos`. Do not present it as a full paid-ad or TikTok Shop analytics workflow.

## Cost Awareness

Each API call consumes credits from your PipiAds account:
- **List/Search**: 1 credit per result returned
- **Detail**: 1 credit per request (free if queried within 3 days when applicable)
