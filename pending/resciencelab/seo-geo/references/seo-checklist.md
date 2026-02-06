# SEO/GEO Audit Checklist

Complete checklist for auditing and optimizing websites for both traditional SEO and GEO (AI search visibility).

## Priority Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **P0** | Critical | Must fix immediately - blocks indexing or causes major issues |
| **P1** | Important | Should fix soon - significant impact on rankings |
| **P2** | Recommended | Nice to have - improves visibility and user experience |

---

## Technical SEO

### P0 - Critical

- [ ] **P0** `robots.txt` allows important pages
- [ ] **P0** Site is accessible (no 5xx errors)
- [ ] **P0** HTTPS enabled (valid SSL certificate)
- [ ] **P0** Mobile-responsive design
- [ ] **P0** No critical pages blocked by `noindex`
- [ ] **P0** Site is indexed in Google (check: `site:domain.com`)

### P1 - Important

- [ ] **P1** `robots.txt` allows AI bots (GPTBot, PerplexityBot, ClaudeBot)
- [ ] **P1** XML sitemap exists and is submitted
- [ ] **P1** Site is indexed in Bing (for Copilot visibility)
- [ ] **P1** Canonical tags properly implemented
- [ ] **P1** No duplicate content issues
- [ ] **P1** Page load time < 3 seconds
- [ ] **P1** LCP (Largest Contentful Paint) < 2.5s

### P2 - Recommended

- [ ] **P2** FID (First Input Delay) < 100ms
- [ ] **P2** CLS (Cumulative Layout Shift) < 0.1
- [ ] **P2** Images optimized (WebP format, lazy loading)
- [ ] **P2** CSS/JS minified
- [ ] **P2** GZIP/Brotli compression enabled
- [ ] **P2** CDN configured
- [ ] **P2** Mobile-friendly test passed
- [ ] **P2** No mixed content warnings
- [ ] **P2** Secure headers configured

---

## On-Page SEO

### P0 - Critical

- [ ] **P0** Unique `<title>` tag exists (50-60 characters)
- [ ] **P0** Title contains primary keyword
- [ ] **P0** Unique `<meta description>` exists (150-160 characters)
- [ ] **P0** Single H1 tag per page
- [ ] **P0** H1 contains primary keyword

### P1 - Important

- [ ] **P1** Description is compelling and includes keyword
- [ ] **P1** `<meta name="robots">` correctly set
- [ ] **P1** Logical heading hierarchy (H1 > H2 > H3)
- [ ] **P1** All images have `alt` attributes
- [ ] **P1** Internal links to related content
- [ ] **P1** No broken links (404s)
- [ ] **P1** Anchor text is descriptive

### P2 - Recommended

- [ ] **P2** `og:title` set
- [ ] **P2** `og:description` set
- [ ] **P2** `og:image` set (1200x630px recommended)
- [ ] **P2** `og:url` set (canonical URL)
- [ ] **P2** `og:type` set (website/article)
- [ ] **P2** `twitter:card` set (summary_large_image)
- [ ] **P2** `twitter:title` set
- [ ] **P2** `twitter:description` set
- [ ] **P2** `twitter:image` set
- [ ] **P2** Paragraphs are short (2-3 sentences)
- [ ] **P2** Bullet points used for lists
- [ ] **P2** Tables used for comparisons
- [ ] **P2** Alt text includes keywords where natural
- [ ] **P2** Image file names are descriptive
- [ ] **P2** External links have `rel="noopener noreferrer"`

---

## Schema Markup (Structured Data)

### P1 - Important

- [ ] **P1** Organization schema on homepage
- [ ] **P1** WebPage schema on all pages
- [ ] **P1** Article schema on blog posts
- [ ] **P1** Schema passes Google Rich Results Test
- [ ] **P1** No errors in Search Console "Enhancements"

### P2 - Recommended - GEO Enhanced

- [ ] **P2** FAQPage schema on FAQ sections (+40% AI visibility)
- [ ] **P2** BreadcrumbList schema for navigation
- [ ] **P2** SpeakableSpecification for voice search
- [ ] **P2** datePublished and dateModified included
- [ ] **P2** Author information with credentials
- [ ] **P2** Publisher information with logo
- [ ] **P2** Schema passes Schema.org Validator

---

## GEO Optimization (AI Search)

### P1 - Important - Princeton GEO Methods

- [ ] **P1** Content includes authoritative citations (+40%)
- [ ] **P1** Statistics and data points included (+37%)
- [ ] **P1** Expert quotes with attribution (+30%)
- [ ] **P1** NO keyword stuffing (causes -10%)

### P2 - Recommended - GEO Enhancement

- [ ] **P2** Authoritative, confident tone (+25%)
- [ ] **P2** Content is accessible/easy to understand (+20%)
- [ ] **P2** Appropriate technical terminology (+18%)
- [ ] **P2** Diverse vocabulary throughout (+15%)
- [ ] **P2** High fluency and readability (+15-30%)

### Content Structure for AI

- [ ] "Answer-first" format (direct answer at top)
- [ ] Clear, extractable paragraphs
- [ ] FAQ format for common questions
- [ ] Tables for comparison data
- [ ] Lists for step-by-step processes

### AI Bot Access

- [ ] GPTBot allowed in robots.txt
- [ ] PerplexityBot allowed in robots.txt
- [ ] ClaudeBot allowed in robots.txt
- [ ] Anthropic-ai allowed in robots.txt
- [ ] Bingbot allowed in robots.txt

---

## Off-Page SEO

### Backlinks

- [ ] Quality backlinks from relevant sites
- [ ] Diverse referring domains
- [ ] No toxic/spammy backlinks
- [ ] Brand mentions (even without links)

### E-E-A-T Signals

- [ ] Author bios with credentials
- [ ] About page with company info
- [ ] Contact information visible
- [ ] Privacy policy and terms
- [ ] Trust badges/certifications if applicable
- [ ] Customer reviews/testimonials

### Social Presence

- [ ] Active social media profiles
- [ ] Links to social profiles on website
- [ ] Social sharing buttons on content
- [ ] Consistent branding across platforms

---

## Content Strategy

### Content Audit

- [ ] All pages have unique, valuable content
- [ ] No thin content (< 300 words for main pages)
- [ ] Content matches search intent
- [ ] Content is up-to-date (within 30 days for news/tech)
- [ ] Content provides unique value vs competitors

### Keyword Strategy

- [ ] Primary keyword identified for each page
- [ ] Secondary keywords mapped
- [ ] Long-tail keywords targeted
- [ ] No keyword cannibalization
- [ ] Keywords match user intent

---

## Monitoring & Analytics

### Setup

- [ ] Google Analytics installed
- [ ] Google Search Console connected
- [ ] Bing Webmaster Tools connected
- [ ] Sitemap submitted to both

### Regular Checks

- [ ] Weekly: Check Search Console for errors
- [ ] Weekly: Review Core Web Vitals
- [ ] Monthly: Analyze organic traffic trends
- [ ] Monthly: Review top performing pages
- [ ] Quarterly: Full SEO audit

---

## Quick Audit Commands

```bash
# Check meta tags
curl -sL "https://example.com" | grep -E "<title>|<meta"

# Check robots.txt
curl -s "https://example.com/robots.txt"

# Check sitemap
curl -s "https://example.com/sitemap.xml" | head -30

# Check page speed (using PageSpeed Insights API)
# Requires API key
curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://example.com&strategy=mobile"

# Check if indexed in Google
# Manual check: https://www.google.com/search?q=site:example.com

# Validate schema
# Open: https://search.google.com/test/rich-results?url=https://example.com
```

---

## Priority Matrix

| Priority | Task | Impact |
|----------|------|--------|
| **Critical** | Fix crawl errors | Blocks indexing |
| **Critical** | HTTPS enabled | Trust + ranking |
| **High** | Core Web Vitals | UX + ranking |
| **High** | Mobile-friendly | 60%+ traffic |
| **High** | FAQPage schema | +40% AI visibility |
| **Medium** | Meta descriptions | CTR improvement |
| **Medium** | Internal linking | Authority distribution |
| **Low** | Social meta tags | Share appearance |
