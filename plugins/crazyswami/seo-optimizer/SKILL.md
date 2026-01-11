---
name: seo-optimizer
description: Audit and optimize WordPress SEO (Yoast/Rank Math) - checks focus keywords, meta descriptions, featured images. Uses Unsplash API for missing images. Run on all pages/posts to identify and fix SEO issues.
allowed-tools: Read, Write, Edit, Bash, Task, WebFetch, WebSearch
---

# SEO Optimizer Skill

Comprehensive SEO audit and optimization for WordPress sites using Yoast SEO or Rank Math.

## What This Skill Does

1. **Audit all pages/posts** for SEO completeness
2. **Check focus keywords** - ensures each page has one set
3. **Validate meta descriptions** - confirms focus keyword appears in description
4. **Verify featured images** - checks if present and properly named
5. **Auto-fix issues** using Unsplash API for missing images
6. **Generate reports** with actionable recommendations

## SEO Rules Enforced

### Focus Keyword Rules
- Every page/post MUST have a focus keyword
- Focus keyword should be 1-3 words, relevant to content
- Focus keyword MUST appear in meta description at least once

### Meta Description Rules
- Must be 120-160 characters (optimal for SERPs)
- Must contain the focus keyword
- Should be compelling and include a call to action
- Must be unique per page

### Featured Image Rules
- Every page/post MUST have a featured image
- Image ALT text should contain the focus keyword
- Image title should BE the focus keyword
- Image should be relevant to page content

## Usage

Ask Claude to run SEO audit:
- "Run SEO audit on all pages"
- "Check SEO for the portfolio page"
- "Fix missing featured images across the site"
- "Optimize meta descriptions for all pages"

## Technical Details

### Yoast SEO Meta Keys
```
_yoast_wpseo_focuskw      - Focus keyword
_yoast_wpseo_metadesc     - Meta description
_yoast_wpseo_title        - SEO title
_thumbnail_id             - Featured image ID
```

### Rank Math Meta Keys
```
rank_math_focus_keyword   - Focus keyword
rank_math_description     - Meta description
rank_math_title           - SEO title
_thumbnail_id             - Featured image ID
```

### REST API Endpoints
```
GET  /wp-json/wp/v2/pages         - List all pages
GET  /wp-json/wp/v2/posts         - List all posts
GET  /wp-json/yoast/v1/get_head   - Get Yoast SEO data for URL
POST /wp-json/wp/v2/media         - Upload image
POST /wp-json/wp/v2/pages/{id}    - Update page (featured_media)
```

### Database Direct Access (if API limited)
```sql
-- Get Yoast focus keyword
SELECT meta_value FROM wp_postmeta
WHERE post_id = {id} AND meta_key = '_yoast_wpseo_focuskw';

-- Update meta description
UPDATE wp_postmeta SET meta_value = '{desc}'
WHERE post_id = {id} AND meta_key = '_yoast_wpseo_metadesc';
```

## Workflow

### 1. Audit Phase (Parallel Haiku Agents)
- Agent 1: Audit Home + About pages
- Agent 2: Audit Portfolio + Contact pages
- Agent 3: Audit Legal pages (Privacy, Terms)
- Agent 4: Audit all Property posts

### 2. Report Generation
```json
{
  "page": "About",
  "url": "/about/",
  "focus_keyword": {
    "status": "ok|missing|weak",
    "value": "real estate development",
    "in_title": true,
    "in_description": true
  },
  "meta_description": {
    "status": "ok|missing|too_short|too_long|missing_keyword",
    "length": 156,
    "value": "..."
  },
  "featured_image": {
    "status": "ok|missing|wrong_alt",
    "id": 123,
    "alt": "...",
    "title": "..."
  },
  "recommendations": [
    "Add focus keyword to meta description",
    "Update featured image ALT text"
  ]
}
```

### 3. Fix Phase
- Use Unsplash API to find relevant images
- Upload to WordPress media library
- Set as featured image with correct ALT/title
- Update meta descriptions to include focus keyword

## Unsplash Integration

Uses the Unsplash MCP server configured at `/root/.claude/.mcp.json`:
- Search for images matching focus keyword
- Download high-quality image
- Upload to WordPress
- Set proper metadata

## Example Audit Output

```
SEO AUDIT REPORT - CSR Development
===================================

Page: About
-----------
Focus Keyword: real estate Miami ✓
Meta Description: "CSR Real Estate builds legacy..." (156 chars) ✓
  - Contains focus keyword: YES ✓
Featured Image: team-photo.jpg ✓
  - ALT text: "CSR team" ⚠ (should contain focus keyword)
  - Title: "team-photo" ⚠ (should be focus keyword)
Score: 80/100

Recommendations:
1. Update image ALT to "real estate Miami team"
2. Update image title to "real estate Miami"

Page: Portfolio
---------------
Focus Keyword: MISSING ✗
Meta Description: MISSING ✗
Featured Image: MISSING ✗
Score: 0/100

Recommendations:
1. Add focus keyword: "Miami properties" or "real estate portfolio"
2. Add meta description with focus keyword
3. Add featured image from Unsplash (search: Miami real estate)
```

## Sources

- [Yoast REST API Documentation](https://developer.yoast.com/customization/apis/rest-api/)
- [Yoast Meta Description API](https://developer.yoast.com/features/seo-tags/descriptions/api/)
- [Rank Math API Manager Plugin](https://github.com/Devora-AS/rank-math-api-manager)
- [WordPress REST API Featured Images](https://rudrastyh.com/wordpress/rest-api-get-featured-image-url.html)
