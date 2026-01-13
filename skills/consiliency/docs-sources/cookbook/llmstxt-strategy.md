# llms.txt Strategy

Fetch documentation from sites implementing the llms.txt standard - already optimized for LLMs.

## Overview

llms.txt is an emerging standard for AI-optimized documentation. Sites expose a single file with concise, LLM-friendly content.

**Spec**: https://llmstxt.org

## Detection

```bash
# Check if llms.txt exists
curl -sI "https://docs.viperjuice.dev/llms.txt" | head -1
# HTTP/2 200 = exists

# Check for extended version
curl -sI "https://docs.viperjuice.dev/llms-full.txt" | head -1
```

## File Types

| File | Content |
|------|---------|
| `/llms.txt` | Concise overview (~1-5k tokens) |
| `/llms-full.txt` | Complete documentation (if available) |

## Fetch Commands

```bash
# Basic fetch
curl -s "https://docs.viperjuice.dev/llms.txt"

# Full documentation (may not exist)
curl -s "https://docs.viperjuice.dev/llms-full.txt"

# Save to file
curl -s "https://docs.viperjuice.dev/llms.txt" -o docs-llms.txt
```

## Known Sites with llms.txt

| Site | URL |
|------|-----|
| Anthropic | https://docs.anthropic.com/llms.txt |
| Vercel AI SDK | https://sdk.vercel.ai/llms.txt |
| Tailwind CSS | https://tailwindcss.com/llms.txt |
| Next.js | https://nextjs.org/llms.txt |
| Prisma | https://prisma.io/llms.txt |

## Registry Configuration

```json
{
  "prisma": {
    "name": "Prisma",
    "strategy": "llmstxt",
    "paths": {
      "llms_txt": "https://prisma.io/llms.txt",
      "llms_full_txt": "https://prisma.io/llms-full.txt"
    }
  }
}
```

## Advantages

- Already optimized for LLM consumption
- Single file, no parsing needed
- Minimal tokens for maximum information
- No navigation extraction required

## Disadvantages

- Not widely adopted yet
- Content may be abbreviated
- No structured page-by-page organization

## Fallback

If llms.txt is insufficient:
1. Check for llms-full.txt
2. Fall back to GitHub raw strategy
3. Fall back to sitemap strategy
