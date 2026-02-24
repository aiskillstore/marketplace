---
name: google-official-seo-guide
description: Official Google SEO guide covering search optimization, best practices, Search Console, crawling, indexing, and improving website search visibility based on official Google documentation
---

# Google Official SEO Guide

Comprehensive assistance with Google Search optimization, SEO best practices, and search visibility improvements based on official Google documentation.

## When to Use This Skill

This skill should be triggered when users ask about:

### SEO & Search Optimization
- Improving website ranking in Google Search
- Implementing SEO best practices
- Optimizing meta tags, titles, and descriptions
- Fixing crawling or indexing issues
- Understanding how Google Search works

### Structured Data & Rich Results
- Adding VideoObject, BroadcastEvent, or Clip structured data
- Implementing schema.org markup for rich results
- Creating sitemaps and robots.txt files
- Setting up breadcrumb navigation
- Configuring hreflang for multi-language sites

### Technical SEO
- Mobile-first indexing optimization
- JavaScript SEO and rendering issues
- Managing duplicate content with canonical tags
- Configuring robots meta tags
- URL structure and internal linking

### Search Console & Monitoring
- Using Google Search Console reports
- Debugging search visibility issues
- Monitoring crawl errors and indexing status
- Analyzing search performance metrics

### Content & Links
- Writing effective anchor text
- Internal and external linking strategies
- Avoiding spam policies violations
- Managing site migrations and redirects

## Key Concepts

### The Three Stages of Google Search
1. **Crawling**: Googlebot discovers and fetches pages from the web
2. **Indexing**: Google analyzes page content and stores it in the index
3. **Serving**: Google returns relevant results for user queries

### Important SEO Principles
- **Mobile-First Indexing**: Google primarily uses the mobile version of content for indexing and ranking
- **Canonical URLs**: Specify the preferred version of duplicate or similar pages
- **Structured Data**: Use schema.org markup to help Google understand your content
- **Search Essentials**: Technical, content, and spam requirements for Google Search eligibility

### Common Structured Data Types
- **VideoObject**: For video content and features
- **BroadcastEvent**: For livestream videos (LIVE badge)
- **Clip**: For video key moments/timestamps
- **SeekToAction**: For auto-detected key moments in videos

## Quick Reference

### Example 1: Basic VideoObject Structured Data

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Video title",
  "description": "Video description",
  "thumbnailUrl": [
    "https://example.com/photos/1x1/photo.jpg",
    "https://example.com/photos/4x3/photo.jpg",
    "https://example.com/photos/16x9/photo.jpg"
  ],
  "uploadDate": "2024-03-31T08:00:00+08:00",
  "duration": "PT1M54S",
  "contentUrl": "https://example.com/video.mp4",
  "embedUrl": "https://example.com/embed/123"
}
```

**Use this for**: Adding basic video metadata to help Google understand and display your videos in search results.

---

### Example 2: LIVE Badge with BroadcastEvent

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Livestream title",
  "uploadDate": "2024-10-27T14:00:00+00:00",
  "publication": {
    "@type": "BroadcastEvent",
    "isLiveBroadcast": true,
    "startDate": "2024-10-27T14:00:00+00:00",
    "endDate": "2024-10-27T14:37:14+00:00"
  }
}
```

**Use this for**: Enabling the LIVE badge on livestream videos in Google Search results.

---

### Example 3: Video Key Moments with Clip

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Cat video",
  "hasPart": [
    {
      "@type": "Clip",
      "name": "Cat jumps",
      "startOffset": 30,
      "endOffset": 45,
      "url": "https://example.com/video?t=30"
    },
    {
      "@type": "Clip",
      "name": "Cat misses the fence",
      "startOffset": 111,
      "endOffset": 150,
      "url": "https://example.com/video?t=111"
    }
  ]
}
```

**Use this for**: Manually specifying important timestamps/chapters in your video for the key moments feature.

---

### Example 4: Good Anchor Text Practices

```html
<!-- Bad: Too generic -->
<a href="https://example.com">Click here</a> to learn more.

<!-- Better: Descriptive and contextual -->
For a full list of cheese available for purchase, see the
<a href="https://example.com">list of cheese types</a>.

<!-- Bad: Too many adjacent links -->
I've written about cheese
<a href="/page1">so</a>
<a href="/page2">many</a>
<a href="/page3">times</a>.

<!-- Better: Spaced out with context -->
I've written about cheese so many times this year:
the <a href="/blue-cheese">controversy over blue cheese</a>,
the <a href="/oldest-brie">world's oldest brie</a>, and
<a href="/boy-and-cheese">A Boy and His Cheese</a>.
```

**Use this for**: Creating effective internal and external links that help both users and Google understand your content.

---

### Example 5: Crawlable Links

```html
<!-- Recommended: Google can crawl these -->
<a href="https://example.com">Link text</a>
<a href="/products/category/shoes">Link text</a>
<a href="./products/category/shoes">Link text</a>

<!-- Not recommended: May not be crawled -->
<a routerLink="products/category">Link text</a>
<a onclick="goto('https://example.com')">Link text</a>
<span href="https://example.com">Link text</span>
```

**Use this for**: Ensuring your links are discoverable and crawlable by Googlebot.

---

### Example 6: Mobile and Desktop hreflang for Separate URLs

```html
<!-- Mobile version (https://m.example.com/) -->
<link rel="canonical" href="https://example.com/">
<link rel="alternate" hreflang="es" href="https://m.example.com/es/">
<link rel="alternate" hreflang="fr" href="https://m.example.com/fr/">

<!-- Desktop version (https://example.com/) -->
<link rel="canonical" href="https://example.com/">
<link rel="alternate" media="only screen and (max-width: 640px)"
      href="https://m.example.com/">
<link rel="alternate" hreflang="es" href="https://example.com/es/">
<link rel="alternate" hreflang="fr" href="https://example.com/fr/">
```

**Use this for**: Properly configuring separate mobile URLs (m-dot sites) with internationalization support.

---

### Example 7: robots meta tags

```html
<!-- Don't index this page -->
<meta name="robots" content="noindex">

<!-- Don't follow links on this page -->
<meta name="robots" content="nofollow">

<!-- Don't index and don't follow -->
<meta name="robots" content="noindex, nofollow">

<!-- Don't show snippet in search results -->
<meta name="robots" content="nosnippet">
```

**Use this for**: Controlling how Google crawls and indexes specific pages.

---

### Example 8: InteractionStatistic for Video Views

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Video title",
  "interactionStatistic": {
    "@type": "InteractionCounter",
    "interactionType": { "@type": "WatchAction" },
    "userInteractionCount": 12345
  }
}
```

**Use this for**: Displaying the number of views/watches for your video content.

---

### Example 9: External Links with Attribution

```html
<!-- Citing sources with proper attribution -->
<p>
According to a recent study from Swiss researchers,
Emmental cheese wheels exposed to music had a milder flavor,
with the full findings available in
<a href="https://example.com/cheese-study">
  Cheese in Surround Sound—a culinary art experiment
</a>.
</p>

<!-- Use nofollow when you don't trust the source -->
<a href="https://untrusted-site.com" rel="nofollow">
  Untrusted content
</a>

<!-- Sponsored links must be marked -->
<a href="https://partner-site.com" rel="sponsored">
  Partner content
</a>
```

**Use this for**: Properly linking to external sources while maintaining SEO best practices.

---

### Example 10: Mobile-First Indexing Checklist

```html
<!-- Ensure same robots meta tags on mobile and desktop -->
<meta name="robots" content="index, follow">

<!-- Use same structured data on both versions -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Example Corp"
}
</script>

<!-- Ensure images have proper alt text on mobile -->
<img src="product.jpg" alt="Blue ceramic vase, 12 inches tall">

<!-- Use same title and meta description -->
<title>Product Name - Category | Site Name</title>
<meta name="description" content="High-quality product description">
```

**Use this for**: Ensuring your mobile site is properly optimized for Google's mobile-first indexing.

## Reference Files

This skill includes comprehensive documentation organized into the following categories:

### apis.md (1 page)
**Content**: Getting started with Google Search Console, monitoring tools, and APIs.

**Key Topics**:
- Setting up Search Console
- Reports for SEO specialists and marketers
- Reports for web developers
- Managing site performance

**When to use**: Setting up monitoring, accessing Search Console features, understanding available reports.

---

### appearance.md (58 pages)
**Content**: Visual elements and rich results in Google Search.

**Key Topics**:
- Visual Elements Gallery (text results, rich results, images, videos)
- Attribution elements (favicon, site name, breadcrumbs)
- Structured data features
- Search result optimization
- Title links and snippets

**When to use**: Optimizing how your content appears in search results, implementing rich results, understanding search UI elements.

---

### crawling.md
**Content**: How Google discovers, crawls, and accesses web content.

**Key Topics**:
- Googlebot behavior and user agents
- Crawl budget and optimization
- robots.txt configuration
- Managing crawl rate
- Handling special file types

**When to use**: Debugging crawling issues, optimizing crawl efficiency, controlling what Google crawls.

---

### fundamentals.md
**Content**: Core concepts and essential SEO knowledge.

**Key Topics**:
- How Google Search works (crawling, indexing, serving)
- SEO starter guide
- Search Essentials
- Creating helpful content
- Site organization and URL structure

**When to use**: Learning SEO basics, understanding Google Search fundamentals, starting a new project.

---

### guides.md
**Content**: Detailed how-to guides for specific SEO tasks.

**Key Topics**:
- Link best practices
- Mobile-first indexing
- Internationalization
- Site migrations
- Duplicate content management
- JavaScript SEO

**When to use**: Implementing specific SEO features, solving technical SEO challenges, following best practices.

---

### indexing.md
**Content**: How Google indexes content and troubleshooting indexing issues.

**Key Topics**:
- Canonical URLs
- Meta tags (robots, noindex, etc.)
- Sitemaps
- Status codes and redirects
- Removing content from Google

**When to use**: Fixing indexing problems, managing duplicate content, controlling what gets indexed.

---

### other.md
**Content**: Additional topics and specialized information.

**Key Topics**:
- Google Search policies
- Spam prevention
- Algorithm updates
- Advanced features

**When to use**: Understanding policies, avoiding penalties, staying current with Google changes.

---

### specialty.md
**Content**: Structured data and specialized search features.

**Key Topics**:
- VideoObject structured data
- BroadcastEvent (LIVE badge)
- Clip and SeekToAction (key moments)
- Other schema.org types
- Rich result guidelines
- Troubleshooting structured data

**When to use**: Implementing video features, adding structured data, enabling rich results, debugging markup errors.

## Working with This Skill

### For Beginners

Start with **fundamentals.md** to understand:
- How Google Search works (crawling → indexing → serving)
- Basic SEO principles
- Search Essentials requirements

Then review **guides.md** for practical implementation:
- Creating good anchor text
- Mobile optimization
- Basic structured data

**Pro tip**: Use the Quick Reference examples above as templates for common tasks.

---

### For SEO Specialists & Marketers

Focus on these areas:
1. **appearance.md**: Optimize how your content displays in search results
2. **guides.md**: Implement link strategies, mobile optimization, internationalization
3. **indexing.md**: Manage canonical URLs, sitemaps, and content removal
4. **apis.md**: Monitor performance with Search Console

**Common workflows**:
- **Site audit**: Check crawling.md + indexing.md
- **Rich results**: Use specialty.md for structured data
- **International expansion**: Follow guides.md hreflang patterns
- **Link building**: Apply guides.md anchor text best practices

---

### For Web Developers

Priority reading:
1. **fundamentals.md**: Understand the technical foundation
2. **crawling.md**: Optimize Googlebot access and crawl efficiency
3. **indexing.md**: Implement proper meta tags and redirects
4. **specialty.md**: Add structured data for rich features

**Common tasks**:
- **JavaScript apps**: See guides.md JavaScript SEO section
- **Video content**: Use specialty.md VideoObject examples
- **Site migration**: Follow guides.md migration patterns
- **Debugging**: Use indexing.md for troubleshooting

---

### For Advanced Users

Explore specialized topics:
- **Structured data mastery**: Deep dive into specialty.md
- **Crawl optimization**: Advanced techniques in crawling.md
- **Policy compliance**: Review other.md spam policies
- **International SEO**: Complex hreflang setups in guides.md

**Advanced patterns**:
- Multi-region sites with separate mobile URLs
- Dynamic structured data with JavaScript
- Large-scale site migrations
- Custom crawl budget management

## Common Pitfalls to Avoid

### Spam Policy Violations
- ❌ Keyword stuffing in content or meta tags
- ❌ Hidden text or links
- ❌ Buying/selling links for ranking
- ❌ Cloaking (showing different content to Google vs users)
- ✅ See **other.md** for complete spam policies

### Mobile-First Indexing Issues
- ❌ Different content on mobile vs desktop
- ❌ Blocking resources on mobile
- ❌ Missing structured data on mobile
- ✅ See **guides.md** mobile-first section

### Structured Data Mistakes
- ❌ Using unsupported formats or properties
- ❌ Missing required fields
- ❌ Different URLs in mobile vs desktop markup
- ✅ Validate with Rich Results Test tool

### Link Problems
- ❌ Generic anchor text ("click here")
- ❌ Non-crawlable JavaScript links
- ❌ Too many links chained together
- ✅ See **guides.md** link best practices

## Tips & Best Practices

### SEO Fundamentals
1. Create unique, descriptive titles and meta descriptions for each page
2. Use meaningful heading structure (H1, H2, H3)
3. Optimize images with descriptive alt text
4. Ensure fast page load times (especially on mobile)
5. Build a logical site structure with clear navigation

### Technical SEO
1. Submit and maintain an XML sitemap
2. Use robots.txt appropriately (crawl control, not indexing control)
3. Implement canonical tags for duplicate content
4. Use HTTPS for security
5. Ensure mobile-friendliness (responsive design recommended)

### Content Strategy
1. Focus on creating helpful, people-first content
2. Match user intent with your content
3. Keep content fresh and up-to-date
4. Use natural language, avoid keyword stuffing
5. Build internal links with descriptive anchor text

### Monitoring & Maintenance
1. Set up Search Console and verify ownership
2. Monitor crawl errors and indexing issues regularly
3. Track search performance metrics
4. Test structured data with validation tools
5. Stay informed about Google Search updates

## Resources

### Official Tools
- **Google Search Console**: Monitor and optimize search presence
- **Rich Results Test**: Validate structured data markup
- **Mobile-Friendly Test**: Check mobile optimization
- **Page Speed Insights**: Analyze performance

### Documentation Links
- Most documentation preserves links to official Google resources
- Use reference files for detailed explanations and examples
- Code examples include proper syntax highlighting

## Notes

- This skill was automatically generated from official Google Search documentation
- Reference files preserve structure and examples from source docs
- Quick reference patterns are extracted from real-world usage examples
- All examples follow Google's official guidelines and best practices

## Updating

To refresh this skill with updated documentation:
1. Re-run the documentation scraper with the same configuration
2. The skill will be rebuilt with the latest official information
3. Check for new features, deprecated patterns, or policy changes
