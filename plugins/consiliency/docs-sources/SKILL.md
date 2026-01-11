---
name: docs-sources
description: "Knowledge of documentation platforms and fetching strategies. Use when adding new documentation sources, determining fetch strategy for a docs site, detecting doc frameworks, or configuring the docs registry."
---

# Documentation Sources Skill

Understand documentation platforms and how to efficiently fetch content from each. Supports 20+ platforms and frameworks.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PREFER_LLMSTXT | true | Check for llms.txt before other strategies |
| PREFER_GITHUB | true | Prefer raw GitHub over web crawling |
| BROWSER_FALLBACK | true | Use browser automation when curl fails |
| DEFAULT_STRATEGY | web_crawl | Fallback when detection fails |

## Instructions

**MANDATORY** - Follow the Workflow steps below when adding or analyzing documentation sources.

- Always check for AI-native signals first (llms.txt)
- Prefer raw content over rendered HTML
- Use browser automation only when necessary

## Red Flags - STOP and Reconsider

If you're about to:
- Web crawl a site without checking for llms.txt first
- Use browser automation without trying curl first
- Add a source without detecting the documentation framework
- Skip GitHub raw access when repo is available

**STOP** -> Read the appropriate cookbook file -> Follow detection order -> Then proceed

## Quick Decision Tree

```
What documentation are you adding?
│
├─ Has /llms.txt? ──────────────────────► llmstxt-strategy.md
│
├─ GitHub repo available?
│   └─ Has docs.yml/mint.json/mkdocs.yml? ► github-strategy.md
│
├─ Has /openapi.json or /asyncapi.yaml? ─► openapi-strategy.md
│
├─ Has /sitemap.xml? ───────────────────► sitemap-strategy.md
│
├─ Curl returns <1KB? (JS-rendered) ────► browser-strategy.md
│
└─ Nothing else works? ─────────────────► sitemap-strategy.md (crawl mode)
```

## Workflow

1. [ ] Identify the documentation URL
2. [ ] **CHECKPOINT**: Check for AI-native signals (llms.txt, ai.txt)
3. [ ] Check if GitHub repo is available
4. [ ] Detect documentation framework from config files
5. [ ] Select appropriate strategy from cookbook
6. [ ] **CHECKPOINT**: Test fetch with curl before using browser
7. [ ] Configure registry entry with correct strategy
8. [ ] Validate fetch works correctly

## Strategy Priority Order

| Priority | Signal | Strategy | Cookbook |
|----------|--------|----------|----------|
| 1 | `/llms.txt` exists | `llmstxt` | `cookbook/llmstxt-strategy.md` |
| 2 | GitHub repo available | `github_raw` | `cookbook/github-strategy.md` |
| 3 | OpenAPI/AsyncAPI spec | `openapi` | `cookbook/openapi-strategy.md` |
| 4 | `/sitemap.xml` exists | `web_sitemap` | `cookbook/sitemap-strategy.md` |
| 5 | JS-rendered / curl fails | `browser_crawl` | `cookbook/browser-strategy.md` |
| 6 | Nothing else works | `web_crawl` | `cookbook/sitemap-strategy.md` |

## Cookbook

### llms.txt (AI-Native)
- IF: Site has `/llms.txt` or `/llms-full.txt`
- THEN: Read `cookbook/llmstxt-strategy.md`
- CHECK: `curl -sI {url}/llms.txt | head -1`

### GitHub Raw
- IF: GitHub repo is linked from docs site
- THEN: Read `cookbook/github-strategy.md`
- SUPPORTS: Fern, Docusaurus, MkDocs, Mintlify, Sphinx, Nextra, Starlight

### OpenAPI / AsyncAPI / GraphQL
- IF: Site has API spec (`/openapi.json`, `/asyncapi.yaml`, `/graphql`)
- THEN: Read `cookbook/openapi-strategy.md`

### Sitemap / Web Crawl
- IF: Site has `/sitemap.xml` or need to crawl
- THEN: Read `cookbook/sitemap-strategy.md`

### Browser Automation
- IF: Curl fails (JS-rendered, blocked, <1KB response)
- THEN: Read `cookbook/browser-strategy.md`
- ALSO: See `browser-discovery` skill for IDE browser tools

## Quick Detection Commands

```bash
# Check for llms.txt
curl -sI "https://docs.viperjuice.dev/llms.txt" | head -1

# Check for sitemap
curl -sI "https://docs.viperjuice.dev/sitemap.xml" | head -1

# Check for OpenAPI
curl -sI "https://api.viperjuice.dev/openapi.json" | head -1

# Test curl response size (detect JS-rendered)
curl -s "https://docs.viperjuice.dev" | wc -c
# If < 1000 bytes, likely JS-rendered -> use browser
```

## Framework Detection

| Framework | Config File | Typical Location |
|-----------|-------------|------------------|
| Fern | `docs.yml` | `fern/docs.yml` |
| Docusaurus | `docusaurus.config.js` | repo root |
| MkDocs | `mkdocs.yml` | repo root |
| Mintlify | `mint.json` | repo root |
| Sphinx | `conf.py` | `docs/conf.py` |
| Nextra | `_meta.json` | `pages/_meta.json` |
| Starlight | `astro.config.mjs` | repo root |
| Antora | `antora.yml` | repo root |
| GitBook | `SUMMARY.md` | repo root |

See `reference/framework-detection.md` for detailed patterns.

## Registry Configuration

See `reference/registry-examples.md` for configuration templates.

Basic structure:
```json
{
  "source-id": {
    "name": "Display Name",
    "strategy": "strategy_name",
    "paths": {
      "homepage": "https://..."
    }
  }
}
```

## Auto-Discovery from Manifests

When used with the `library-detection` skill, automatically suggest documentation sources based on detected dependencies.

### Workflow

1. Receive stack info from `library-detection` skill
2. Map each framework/library to known documentation sources
3. Check if source already exists in `ai-docs/libraries/_registry.json`
4. Suggest `/ai-dev-kit:docs-add` commands for missing sources

### Library-to-Docs Mapping

| Library | Documentation URL | Strategy |
|---------|-------------------|----------|
| react | https://react.dev | llmstxt |
| next | https://nextjs.org/docs | github_raw |
| vue | https://vuejs.org/guide | github_raw |
| nuxt | https://nuxt.com/docs | github_raw |
| svelte | https://svelte.dev/docs | github_raw |
| fastapi | https://fastapi.tiangolo.com | github_raw |
| django | https://docs.djangoproject.com | web_sitemap |
| flask | https://flask.palletsprojects.com | web_sitemap |
| express | https://expressjs.com | web_sitemap |
| prisma | https://www.prisma.io/docs | llmstxt |
| drizzle | https://orm.drizzle.team/docs | github_raw |
| vitest | https://vitest.dev | github_raw |
| playwright | https://playwright.dev/docs | github_raw |
| tailwindcss | https://tailwindcss.com/docs | llmstxt |
| trpc | https://trpc.io/docs | github_raw |
| zod | https://zod.dev | llmstxt |

### Auto-Discovery Command

When `/ai-dev-kit:quickstart-codebase` or manual request:

```bash
# Get detected frameworks
FRAMEWORKS=$(library-detection --output json | jq -r '.frameworks[].name')

# For each framework, check if docs exist
for fw in $FRAMEWORKS; do
  if ! grep -q "\"$fw\"" ai-docs/libraries/_registry.json; then
    echo "Missing docs for: $fw"
    echo "Suggest: /ai-dev-kit:docs-add <url> $fw"
  fi
done
```

### Output

Returns list of:
```json
{
  "already_tracked": ["react", "typescript"],
  "missing": [
    {"library": "fastapi", "url": "https://fastapi.tiangolo.com", "command": "/ai-dev-kit:docs-add https://fastapi.tiangolo.com fastapi"}
  ],
  "unknown": ["custom-internal-lib"]
}
```

## Output

After adding a source, verify:
1. Pages are discovered correctly
2. Content is fetched without errors
3. Registry entry is valid JSON
