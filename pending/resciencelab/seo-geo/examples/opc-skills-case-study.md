# Case Study: OPC Skills Website SEO/GEO Optimization

Real-world example of applying SEO and GEO optimization to opc.dev.

---

## Background

**Website:** opc.dev  
**Product:** AI Agent Skills for Solopreneurs  
**Platforms:** Claude Code, Cursor, Codex, Factory Droid, OpenCode  
**Date:** January 2026

### Initial Status

| Metric | Status |
|--------|--------|
| Google Indexed | ❌ No |
| Bing Indexed | ❌ No |
| Schema Markup | ❌ None |
| FAQ Section | ❌ None |
| Meta Tags | ⚠️ Basic |
| AI Bot Access | ⚠️ Not configured |

---

## Problem Analysis

### 1. Keyword Conflict

The term "OPC" has different meanings in different markets:

| Market | "OPC" Meaning |
|--------|--------------|
| English (Industrial) | OPC UA - Industrial automation protocol |
| Chinese | 一人公司 (One Person Company) |
| Solopreneur | One Person Company (intended meaning) |

**Decision:** Focus on long-tail keywords for English market:
- "AI agent skills for solopreneurs"
- "Claude Code skills"
- "indie hacker tools"

### 2. Missing Schema Markup

No structured data meant:
- No rich results in Google
- Poor AI visibility
- No FAQ display

### 3. No GEO Optimization

Content lacked:
- Statistics and data points
- Expert citations
- FAQ format
- Answer-first structure

---

## Implementation

### Phase 1: Meta Tags Optimization

**Before:**
```html
<title>OPC Skills</title>
<meta name="description" content="Skills for one person companies">
```

**After:**
```html
<title>OPC Skills - AI Agent Skills for Solopreneurs & Indie Hackers | Claude Code, Cursor, Codex</title>
<meta name="description" content="10+ AI agent skills for solopreneurs. Domain hunting, social media research, logo creation. Works with Claude Code, Cursor, Codex, Factory Droid. One-click install, 100% open source.">
```

**Keywords targeted:**
- solopreneur (high intent, low competition)
- indie hacker (community term)
- Claude Code skills (specific platform)
- AI agent skills (emerging category)

### Phase 2: Schema Markup Implementation

Added comprehensive JSON-LD:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebPage",
      "name": "OPC Skills - AI Agent Skills for Solopreneurs",
      "description": "10+ agent skills for Claude Code, Cursor, Codex...",
      "dateModified": "2026-01-20",
      "speakable": {
        "@type": "SpeakableSpecification",
        "cssSelector": ["h1", ".hero-description", ".faq-answer"]
      }
    },
    {
      "@type": "SoftwareApplication",
      "name": "OPC Skills",
      "applicationCategory": "DeveloperApplication",
      "operatingSystem": "Cross-platform",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      }
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is OPC Skills?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "OPC Skills is a collection of 10+ AI agent skills..."
          }
        }
        // 12 total FAQ items
      ]
    }
  ]
}
```

### Phase 3: GEO Optimization (Princeton Methods)

#### Statistics Addition (+37%)

**Before:**
```
"Skills for one person companies"
```

**After:**
```
"10+ Skills | 5 Platforms | One-Click Install | 100% Open Source"
```

#### FAQ Section (+40% AI Visibility)

Added 12 FAQ questions targeting high-search queries:

1. What is OPC Skills?
2. What platforms does OPC Skills support?
3. How do I install OPC Skills?
4. Is OPC Skills free?
5. What skills are included in OPC Skills?
6. How does the domain-hunter skill work?
7. Can I use OPC Skills with Claude Code?
8. What is the twitter skill used for?
9. How do I create a logo with OPC Skills?
10. Is OPC Skills open source?
11. How do I contribute to OPC Skills?
12. What is a solopreneur?

#### Authoritative Tone (+25%)

**Before:**
```
"Some tools for solo workers"
```

**After:**
```
"AI Agent Skills for Solopreneurs - The definitive skill library for 
one-person companies. Trusted by indie hackers worldwide."
```

#### Citations (+40%)

Added references to:
- Anthropic (Claude Code official documentation)
- Industry statistics on solopreneur growth
- Sam Altman's "billion-dollar one-person company" prediction

### Phase 4: AI Bot Configuration

Updated robots.txt considerations:

```
# Allow AI bots for GEO visibility
User-agent: GPTBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /
```

### Phase 5: Hero Section Rewrite

**Before:**
```
OPC Skills
Skills for OPCs
```

**After:**
```
AI Agent Skills for Solopreneurs

The skill library for one-person companies. 
Install once, use everywhere.

10+ Skills | 5 Platforms | One-Click Install | 100% Open Source
```

---

## Results

### Technical Improvements

| Metric | Before | After |
|--------|--------|-------|
| Meta Title | "OPC Skills" | Full keyword-rich title |
| Meta Description | 20 chars | 155 chars |
| Schema Types | 0 | 4 (WebPage, Software, FAQ, Org) |
| FAQ Items | 0 | 12 |
| Statistics | 0 | 4 key metrics |

### SEO Improvements

| Factor | Before | After |
|--------|--------|-------|
| Title keyword match | ❌ | ✅ |
| Description keyword match | ❌ | ✅ |
| Structured data | ❌ | ✅ |
| Rich results eligible | ❌ | ✅ |

### GEO Improvements

| Princeton Method | Applied | Expected Boost |
|-----------------|---------|----------------|
| Cite Sources | ✅ | +40% |
| Statistics | ✅ | +37% |
| FAQ Schema | ✅ | +40% |
| Authoritative Tone | ✅ | +25% |
| Easy Language | ✅ | +20% |

**Estimated total GEO visibility boost: 40-60%**

---

## Lessons Learned

### 1. Keyword Research is Critical

The "OPC" keyword conflict could have hurt visibility. Long-tail keywords solved this:
- "solopreneur tools" > "OPC tools"
- "Claude Code skills" > "AI skills"

### 2. FAQPage Schema is High-Impact

Adding 12 FAQ items with proper schema:
- Enables rich results
- Provides AI-extractable content
- Targets specific search queries

### 3. Statistics Make Content Quotable

"10+ Skills | 5 Platforms | One-Click Install | 100% Open Source"

These specific numbers are:
- Easy for AI to extract
- Memorable for users
- Differentiated from competitors

### 4. Answer-First Structure

Each FAQ answer starts with a direct answer:
- "OPC Skills is a collection of..." (not "Well, it depends...")
- This matches AI response patterns

---

## Next Steps

### Short-term (1 month)

- [ ] Submit sitemap to Google Search Console
- [ ] Submit to Bing Webmaster Tools
- [ ] Monitor indexing progress
- [ ] Track FAQ rich results

### Medium-term (3 months)

- [ ] Monitor AI citation rate
- [ ] A/B test different FAQ questions
- [ ] Build backlinks from dev communities
- [ ] Create content for Reddit/HN

### Long-term (6 months)

- [ ] Establish "OPC Skills = Solopreneur tools" brand
- [ ] Rank for "Claude Code skills" in AI search
- [ ] Get cited in AI responses about solopreneur tools

---

## Replication Guide

To replicate this optimization for your own site:

1. **Audit current state** using seo-geo skill checklist
2. **Research keywords** - find long-tail opportunities
3. **Write meta tags** - include primary keyword in title/description
4. **Add Schema markup** - start with FAQPage and WebPage
5. **Apply Princeton methods** - statistics, citations, structure
6. **Configure AI bot access** - robots.txt
7. **Validate schema** - Google Rich Results Test
8. **Submit to search engines** - Search Console, Bing Webmaster
9. **Monitor and iterate** - track visibility, adjust content

---

## Files Changed

| File | Changes |
|------|---------|
| `website/worker.js` | Meta tags, Schema, Hero section, FAQ section, Stats bar |
| `README.md` | Badges, navigation links, updated tagline |
| `docs/MARKETING_SPEC.md` | Comprehensive marketing plan (new) |
