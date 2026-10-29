---
name: upstash-ratelimit-js
description: Rate limiting for serverless and edge apps with the @upstash/ratelimit TypeScript/JavaScript SDK backed by Upstash Redis. Use when adding a rate limiter or throttling to an API route, Next.js middleware, Vercel Edge, Cloudflare Workers, or any HTTP endpoint; returning 429 Too Many Requests; choosing between fixed window, sliding window, and token bucket algorithms; limiting per user, IP, API key, or tenant with prefixes and custom keys; protecting login, signup, form, or AI endpoints from abuse, bots, and brute force; using deny lists, ephemeral caching, analytics, timeouts, and multi-region rate limits; or estimating the Redis command cost of rate limiting. Also use when the user says rate limit, rate-limiting, throttle, quota, request limits, or traffic protection.
license: MIT
metadata:
  author: Upstash
  homepage: https://upstash.com
---

# Rate Limit TS SDK

## Bundled docs and source

Before writing or debugging SDK code, check `node_modules/@upstash/ratelimit/docs/` for bundled docs and `node_modules/@upstash/ratelimit/src/` for readable TypeScript source. Read and search the relevant files when present; otherwise use the references in this skill.

## Quick Start
- Install the SDK and connect to Redis.
- Create a rate limiter and apply it to incoming operations.

Example:
```ts
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const redis = new Redis({ url: "<url>", token: "<token>" });
const limiter = new Ratelimit({ redis, limiter: Ratelimit.slidingWindow(5, "10s") });

const { success } = await limiter.limit("user-id");
if (!success) {
  // throttled
}
```

## Other Skill Files
- **algorithms.md**: Describes all available rate‑limiting algorithms and how they behave.
- **pricing-cost.md**: Explains pricing, Redis cost implications, and operational considerations.
- **features.md**: Lists SDK features such as prefixes, custom keys, and behavioral options.
- **methods-getting-started.md**: Full method reference for the SDK's API and getting started guide.
- **traffic-protection.md**: Guidance on applying rate limiting for traffic shaping, abuse prevention, and protection patterns.
