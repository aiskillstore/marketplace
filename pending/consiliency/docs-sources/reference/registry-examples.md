# Registry Configuration Examples

Complete examples for configuring documentation sources in the registry.

## Basic Structure

```json
{
  "source-id": {
    "name": "Display Name",
    "description": "Brief description",
    "homepage": "https://docs.viperjuice.dev",
    "strategy": "strategy_name",
    "priority": "high|medium|low",
    ...strategy-specific-config
  }
}
```

## llms.txt Source

```json
{
  "prisma": {
    "name": "Prisma",
    "description": "Type-safe database ORM",
    "homepage": "https://www.prisma.io/docs",
    "strategy": "llmstxt",
    "priority": "high",
    "paths": {
      "llms_txt": "https://prisma.io/llms.txt",
      "llms_full_txt": "https://prisma.io/llms-full.txt"
    }
  }
}
```

## GitHub / Fern Source

```json
{
  "baml": {
    "name": "BAML",
    "description": "Structured LLM outputs with type safety",
    "homepage": "https://docs.boundaryml.com",
    "strategy": "github_raw",
    "priority": "high",
    "github": {
      "owner": "BoundaryML",
      "repo": "baml",
      "branch": "canary",
      "docs_path": "fern",
      "nav_config": "fern/docs.yml"
    }
  }
}
```

## GitHub / Docusaurus Source

```json
{
  "react": {
    "name": "React",
    "description": "JavaScript library for building user interfaces",
    "homepage": "https://react.dev",
    "strategy": "docusaurus",
    "priority": "high",
    "github": {
      "owner": "facebook",
      "repo": "react",
      "branch": "main",
      "docs_path": "docs",
      "nav_config": "sidebars.js"
    }
  }
}
```

## GitHub / MkDocs Source

```json
{
  "fastapi": {
    "name": "FastAPI",
    "description": "Modern Python web framework",
    "homepage": "https://fastapi.tiangolo.com",
    "strategy": "github_raw",
    "priority": "medium",
    "github": {
      "owner": "tiangolo",
      "repo": "fastapi",
      "branch": "master",
      "docs_path": "docs",
      "nav_config": "mkdocs.yml"
    }
  }
}
```

## GitHub / Mintlify Source

```json
{
  "resend": {
    "name": "Resend",
    "description": "Email API for developers",
    "homepage": "https://resend.com/docs",
    "strategy": "mintlify",
    "priority": "medium",
    "github": {
      "owner": "resendlabs",
      "repo": "resend-docs",
      "branch": "main",
      "nav_config": "mint.json"
    }
  }
}
```

## GitHub / Sphinx Source

```json
{
  "python-docs": {
    "name": "Python Documentation",
    "description": "Official Python language docs",
    "homepage": "https://docs.python.org",
    "strategy": "sphinx",
    "priority": "high",
    "github": {
      "owner": "python",
      "repo": "cpython",
      "branch": "main",
      "docs_path": "Doc",
      "nav_config": "Doc/conf.py"
    }
  }
}
```

## GitHub / Nextra Source

```json
{
  "swr-docs": {
    "name": "SWR Documentation",
    "description": "React Hooks for data fetching",
    "homepage": "https://swr.vercel.app",
    "strategy": "nextra",
    "priority": "medium",
    "github": {
      "owner": "vercel",
      "repo": "swr-site",
      "branch": "main",
      "docs_path": "pages",
      "nav_config": "pages/_meta.json"
    }
  }
}
```

## GitHub / Starlight Source

```json
{
  "astro-docs": {
    "name": "Astro Documentation",
    "description": "All-in-one web framework",
    "homepage": "https://docs.astro.build",
    "strategy": "starlight",
    "priority": "medium",
    "github": {
      "owner": "withastro",
      "repo": "docs",
      "branch": "main",
      "docs_path": "src/content/docs",
      "nav_config": "astro.config.mjs"
    }
  }
}
```

## OpenAPI Source

```json
{
  "stripe-api": {
    "name": "Stripe API",
    "description": "Payment processing API",
    "homepage": "https://stripe.com/docs/api",
    "strategy": "openapi",
    "priority": "high",
    "paths": {
      "spec_url": "https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json"
    }
  }
}
```

## AsyncAPI Source

```json
{
  "kafka-events": {
    "name": "Kafka Event Schema",
    "description": "Event-driven API documentation",
    "homepage": "https://docs.viperjuice.dev/events",
    "strategy": "asyncapi",
    "priority": "medium",
    "paths": {
      "spec_url": "https://raw.githubusercontent.com/org/repo/main/asyncapi.yaml"
    }
  }
}
```

## GraphQL Source

```json
{
  "github-graphql": {
    "name": "GitHub GraphQL API",
    "description": "GitHub's GraphQL API schema",
    "homepage": "https://docs.github.com/graphql",
    "strategy": "graphql_schema",
    "priority": "high",
    "paths": {
      "endpoint": "https://api.github.com/graphql",
      "schema_url": "https://docs.github.com/public/schema.docs.graphql"
    }
  }
}
```

## Web Sitemap Source

```json
{
  "example-docs": {
    "name": "Example Documentation",
    "description": "Example project docs",
    "homepage": "https://docs.viperjuice.dev",
    "strategy": "web_sitemap",
    "priority": "low",
    "paths": {
      "sitemap": "https://docs.viperjuice.dev/sitemap.xml"
    },
    "filters": {
      "include_patterns": ["/docs/", "/guide/"],
      "exclude_patterns": ["/blog/", "/changelog/"]
    }
  }
}
```

## Browser Crawl Source (JS-Rendered)

```json
{
  "antigravity-ide": {
    "name": "Google Antigravity",
    "description": "AI-powered IDE documentation",
    "homepage": "https://antigravity.google",
    "strategy": "browser_crawl",
    "priority": "high",
    "browser": {
      "nav_selector": "nav.sidebar",
      "content_selector": "main",
      "wait_for": "nav",
      "js_required": true
    },
    "sections": {
      "getting-started": {
        "path_pattern": "get-started",
        "priority": "core"
      },
      "agent": {
        "path_pattern": "agent",
        "priority": "core"
      }
    }
  }
}
```

## Priority Levels

| Priority | Description | Update Frequency |
|----------|-------------|------------------|
| `high` | Critical dependencies | Daily check |
| `medium` | Regular dependencies | Weekly check |
| `low` | Reference only | Monthly check |

## Sections Configuration

For organizing large doc sources:

```json
{
  "sections": {
    "section-id": {
      "path_pattern": "regex-or-path",
      "priority": "core|important|reference",
      "keywords": ["keyword1", "keyword2"]
    }
  }
}
```
