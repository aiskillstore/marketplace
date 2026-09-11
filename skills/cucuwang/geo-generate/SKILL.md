---
name: geo-generate
description: Use when previewing optional llms.txt proposal files, candidate JSON-LD, or crawler-control suggestions for a website build
---

# GEO Generate — Optional Discovery Artifacts

Generate reviewable candidate artifacts. These files do not guarantee crawling, indexing, search features, visibility, or citation.

## Workflow

1. Identify an authorized static build directory.
2. Preview without writing:

   ```bash
   npx geoptimize generate <directory> --dry-run
   ```

3. Review every output:
   - `llms.txt` and `llms-full.txt` are experiments based on a proposal.
   - Candidate `Article` or `BreadcrumbList` JSON-LD must match visible content.
   - Crawler rules have service-specific meanings; an allow rule is not an outcome guarantee.
4. Write only after the user approves the exact directory:

   ```bash
   npx geoptimize generate <directory>
   ```

## Boundaries

- Never overwrite an existing artifact without confirmation and a recoverable copy.
- Never infer `FAQPage` from question headings.
- Never add `<link rel="llms-txt">` as if it were a standardized discovery mechanism.
- Never auto-apply `robots.txt` suggestions.
- Validate structured data against current primary documentation before deployment.
