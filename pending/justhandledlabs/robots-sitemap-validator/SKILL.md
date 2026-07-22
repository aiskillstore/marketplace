---
name: robots-sitemap-validator
description: Check robots.txt and sitemap.xml for crawl-blocking mistakes. Use when the user says "check my robots.txt", "validate my sitemap", or "is my site crawlable".
metadata:
  author: JustHandled Labs
  version: 1.0.0
  price: $0
  credits: 0
  triggers:
    - check my robots.txt
    - validate my sitemap
    - is my site crawlable
---

# Robots Sitemap Validator

Detect common local robots.txt and sitemap.xml mistakes that can hurt crawling. This detector does not fetch, submit, or change live sites.

## Workflow

1. Run scripts/scan_robots_sitemap.py with a folder, files, or --stdin.
2. Review findings by rule id, severity, file, and line.
3. Treat missing sibling sitemap files as review flags when robots.txt references them.

## Guardrails

- Read local files or stdin only.
- Do not fetch live URLs or submit sitemaps.
- Do not modify robots.txt or sitemap files.

## Verification

Run tests/test_robots_sitemap.py. Risky fixture must produce findings and clean fixture must produce zero findings.

## Commercial Terms

Price: $0 / 0 credits. Free commercial use for personal or internal team workflows. Do not resell or redistribute the package as-is.
