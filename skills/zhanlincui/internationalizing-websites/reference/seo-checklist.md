# International SEO Checklist

Comprehensive checklist for optimizing multi-language websites for search engines.

## Pre-Launch Checklist

### URL Structure

- [ ] URL structure is consistent across all languages
- [ ] Language codes follow ISO 639-1 standard (e.g., `/ja`, `/zh`, `/ko`)
- [ ] URLs use language code, not country code (e.g., `/ja` not `/jp`)
- [ ] Default language decision made (root path vs `/en`)
- [ ] No duplicate content at different URLs

**Example structure**:
```
✅ https://example.com/           (English, default)
✅ https://example.com/ja          (Japanese)
✅ https://example.com/zh          (Chinese)

❌ https://example.com/japan       (use /ja)
❌ https://example.com/jp          (jp is country code)
```

### hreflang Implementation

- [ ] hreflang tags present on all pages
- [ ] All pages reference all language versions (including themselves)
- [ ] `x-default` specified (fallback language)
- [ ] Language codes are correct (not country codes)
- [ ] URLs in hreflang use absolute paths (not relative)
- [ ] HTTPS used consistently (not mixing http and https)
- [ ] www vs non-www consistent across all tags

**Validation**:
```bash
# Check hreflang in HTML
curl https://example.com/ | grep hreflang

# Check hreflang in sitemap
curl https://example.com/sitemap.xml | grep hreflang
```

### Sitemap Configuration

- [ ] Sitemap includes all language versions
- [ ] Each URL has hreflang annotations
- [ ] Sitemap submitted to Google Search Console
- [ ] Sitemap URL in robots.txt
- [ ] Sitemap updates when new languages added

**Sitemap structure**:
```xml
<url>
  <loc>https://example.com/</loc>
  <xhtml:link rel="alternate" hreflang="en" href="https://example.com/" />
  <xhtml:link rel="alternate" hreflang="ja" href="https://example.com/ja" />
  <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/" />
</url>
```

### HTML Language Attributes

- [ ] `<html lang="...">` attribute set correctly on each page
- [ ] Language attribute matches page content
- [ ] Attribute uses correct language code (e.g., `lang="ja"`)

**Example**:
```html
<!-- English page -->
<html lang="en">

<!-- Japanese page -->
<html lang="ja">

<!-- Chinese page -->
<html lang="zh">
```

### Meta Tags (Per Language)

- [ ] Each language has unique `<title>` tag (50-60 characters)
- [ ] Each language has unique `<meta description>` (150-160 characters)
- [ ] Keywords researched in target language (not just translated)
- [ ] Open Graph tags translated (`og:title`, `og:description`)
- [ ] Twitter Card tags translated
- [ ] Meta tags optimized for local search engines

**Example (Japanese)**:
```html
<title>PDFをMarkdownに変換 - 無料オンラインツール</title>
<meta name="description" content="PDF文書を簡単にMarkdown形式に変換できる無料ツール。画像、表、テキストを保持します。" />
```

### Content Quality

- [ ] Content translated by native speaker or reviewed by one
- [ ] Translation is culturally appropriate (not literal)
- [ ] No machine translation artifacts (awkward phrasing)
- [ ] Currency, dates, and numbers localized
- [ ] Images with text have localized versions
- [ ] Examples and case studies relevant to local market
- [ ] No "Lorem ipsum" or placeholder content

### Technical Configuration

- [ ] UTF-8 encoding set in HTML and HTTP headers
- [ ] Character sets render correctly for all languages
- [ ] Fonts support all character sets (Japanese, Chinese, Arabic, etc.)
- [ ] RTL (right-to-left) support if using Arabic or Hebrew
- [ ] Language switcher visible and functional
- [ ] Language preference saved (cookie or local storage)

### Navigation and UX

- [ ] Language switcher on every page
- [ ] Current language clearly indicated
- [ ] Clicking language link keeps user on equivalent page
- [ ] Navigation menu translated in each language
- [ ] Breadcrumbs translated
- [ ] Footer links translated
- [ ] 404 page exists in all languages

### Search Console Setup

- [ ] Google Search Console property created
- [ ] Sitemap submitted to Search Console
- [ ] International targeting set (if using generic domain)
- [ ] hreflang errors monitored
- [ ] Separate properties for each region (optional but recommended)

### Structured Data

- [ ] Schema.org markup added for each language
- [ ] `inLanguage` property set correctly
- [ ] Organization/WebSite schema translated
- [ ] LocalBusiness schema (if applicable) for each region
- [ ] Validated with Google Rich Results Test

**Example**:
```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "サイト名",
  "inLanguage": "ja",
  "url": "https://example.com/ja"
}
```

## Post-Launch Checklist

### Indexing Verification

- [ ] All language versions indexed by Google
- [ ] Check: `site:example.com/ja` in Google
- [ ] No `noindex` tags accidentally left on pages
- [ ] robots.txt not blocking language directories
- [ ] Sitemap shows as "Success" in Search Console

### Performance Monitoring

- [ ] Google Analytics tracks each language separately
- [ ] Set up Analytics views for each language
- [ ] Monitor bounce rate by language
- [ ] Track conversions by language
- [ ] Set up Search Console Performance reports by language

### hreflang Validation

- [ ] No hreflang errors in Search Console
- [ ] "Internationalization" report shows no issues
- [ ] All pages have return tags
- [ ] No conflicting hreflang declarations

**Common errors to fix**:
- "No return tags" - Reciprocal hreflang missing
- "Incorrect language codes" - Using wrong codes
- "Missing self-reference" - Page doesn't reference itself

### Search Appearance

- [ ] Correct language version appears in search results
- [ ] Check from different countries (use VPN or Google's geo-targeting)
- [ ] Meta descriptions display correctly (not truncated)
- [ ] Titles not cut off (respect character limits)

### Content Completeness

- [ ] All pages translated (no English-only pages)
- [ ] Images localized where needed
- [ ] Videos have subtitles in each language (if applicable)
- [ ] PDFs or downloads available in each language
- [ ] Legal pages translated (Terms, Privacy Policy)

## Ongoing Maintenance

### Regular Checks

**Weekly**:
- [ ] Monitor Search Console for new hreflang errors
- [ ] Check Analytics for traffic by language
- [ ] Review crawl errors by language

**Monthly**:
- [ ] Review keyword rankings by language
- [ ] Analyze user behavior by language (bounce rate, time on site)
- [ ] Check for new competitors in each market
- [ ] Update content based on performance

**Quarterly**:
- [ ] Review and update translations based on user feedback
- [ ] A/B test translations if conversion rates differ
- [ ] Analyze which languages drive most value
- [ ] Consider adding new languages based on demand

### Content Updates

When adding new content:
- [ ] Create in all languages simultaneously
- [ ] Update sitemap with new pages
- [ ] Add hreflang tags to new pages
- [ ] Verify all language versions linked correctly
- [ ] Submit updated sitemap to Search Console

### New Language Additions

When expanding to new languages:
- [ ] Research keywords in new language
- [ ] Create content strategy for new market
- [ ] Get professional translation or native speaker review
- [ ] Update `i18n/locale.ts` configuration
- [ ] Update all hreflang tags across site
- [ ] Update sitemap
- [ ] Create Search Console property for new language
- [ ] Monitor indexing and performance

## Common Pitfalls to Avoid

### Auto-Redirects

❌ **Don't do this**:
```javascript
// Bad: Auto-redirect based on IP
if (userCountry === 'JP') {
  redirect('/ja');
}
```

**Why**: Prevents search engines from crawling all versions.

✅ **Do this instead**:
```javascript
// Good: Suggest language, don't force
if (userCountry === 'JP' && currentLang === 'en') {
  showLanguageSuggestion('ja');
}
```

### Duplicate Content

❌ **Don't**:
- Serve same content on multiple URLs without hreflang
- Mix languages on same page
- Use automatic translation without review

✅ **Do**:
- Use hreflang for language variants
- Keep each page in one language (except brand names)
- Review all translations for quality

### Poor URL Structure

❌ **Don't**:
```
example.com/?lang=ja        (Parameters)
ja.example.com              (Subdomains without geo-targeting)
example.jp                  (Multiple domains)
```

✅ **Do**:
```
example.com/ja              (Subdirectories - best for most cases)
```

### Language Detection

❌ **Don't**:
- Use IP address as only signal
- Force redirect without user control
- Hide language selector

✅ **Do**:
- Respect `Accept-Language` header as suggestion
- Allow user to override
- Make language selector always visible

## Testing Procedures

### Manual Testing

**For each language**:

1. **Visit homepage**:
   - URL is correct (e.g., `/ja`)
   - Content in correct language
   - Language switcher shows current language
   - Meta tags in correct language (view source)

2. **Navigate site**:
   - All pages render correctly
   - Links work
   - Forms submit correctly
   - Search works in that language

3. **Check hreflang**:
   - View page source
   - Find `<link rel="alternate" hreflang=...`
   - Verify all languages listed
   - Verify current page references itself

4. **Test language switcher**:
   - Click each language
   - Verify URL changes
   - Verify content updates
   - Verify you stay on equivalent page

### Automated Testing

```bash
#!/bin/bash
# Quick validation script

SITE="https://example.com"
LANGUAGES=("ja" "zh" "ko")

echo "Testing $SITE"

# Check each language is accessible
for lang in "${LANGUAGES[@]}"; do
  HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}" "$SITE/$lang")
  if [ $HTTP_CODE -eq 200 ]; then
    echo "✅ /$lang is accessible"
  else
    echo "❌ /$lang returned $HTTP_CODE"
  fi
done

# Check sitemap includes all languages
echo "Checking sitemap..."
curl -s "$SITE/sitemap.xml" | grep -q "hreflang=\"ja\"" && echo "✅ Japanese in sitemap" || echo "❌ Japanese missing"
curl -s "$SITE/sitemap.xml" | grep -q "hreflang=\"zh\"" && echo "✅ Chinese in sitemap" || echo "❌ Chinese missing"
curl -s "$SITE/sitemap.xml" | grep -q "hreflang=\"ko\"" && echo "✅ Korean in sitemap" || echo "❌ Korean missing"

echo "Done!"
```

### Search Console Validation

After deployment:

1. **Submit sitemap** (if not auto-detected)
2. **Wait 2-3 days** for initial crawl
3. **Check Coverage report**:
   - Valid pages should include all languages
   - No "Excluded" or "Error" pages
4. **Check International Targeting**:
   - No hreflang errors
   - All languages listed

### Google Search Test

```
# Search for your site in different languages
site:example.com/ja keyword
site:example.com/zh keyword
site:example.com/ko keyword

# Should show pages in respective languages
```

## Performance Optimization

### Loading Speed

- [ ] Each language loads in < 3 seconds
- [ ] Images optimized (WebP format)
- [ ] Fonts subset for each language (Japanese, Chinese need specific fonts)
- [ ] JavaScript bundles split by language (lazy load)
- [ ] CSS optimized (remove unused styles)

### Core Web Vitals

**Per language**:
- [ ] LCP < 2.5s
- [ ] FCP < 1.8s
- [ ] CLS < 0.1
- [ ] TBT < 200ms

Test with: https://pagespeed.web.dev/

### Font Optimization

For Asian languages (Japanese, Chinese, Korean):

```css
/* Subset font to needed characters */
@font-face {
  font-family: 'NotoSansJP';
  src: url('/fonts/NotoSansJP-subset.woff2');
  /* Only include common characters, not all 2000+ kanji */
  unicode-range: U+3000-303F, U+3040-309F, U+30A0-30FF;
}
```

## Analytics and Reporting

### Key Metrics by Language

Track separately:
- **Traffic**: Sessions, users, pageviews
- **Engagement**: Bounce rate, pages/session, avg. session duration
- **Conversions**: Goal completions, conversion rate
- **Revenue**: If e-commerce

### Google Analytics Setup

**Create views**:
- All Languages (master view)
- English
- Japanese
- Chinese
- Korean

**Set up goals per language**:
- Signups
- Downloads
- Purchases
- Contact forms

**Track language switching**:
```javascript
// Track when user changes language
gtag('event', 'language_change', {
  'from_language': 'en',
  'to_language': 'ja'
});
```

## Troubleshooting

### Issue: Wrong language in search results

**Check**:
1. hreflang tags correct?
2. Content actually in target language?
3. `<html lang="...">` attribute correct?
4. Meta tags in target language?

### Issue: Low rankings in non-English markets

**Possible causes**:
1. Keywords not researched in target language
2. Content is too literal translation
3. Not enough local backlinks
4. Missing local cultural context

**Solutions**:
1. Research keywords with local tools (not just translate)
2. Hire native speaker to review
3. Get links from local websites
4. Add local examples and case studies

### Issue: High bounce rate for specific language

**Investigate**:
1. Translation quality (ask native speaker)
2. Cultural relevance (local examples?)
3. Page load speed (especially for Asian languages with custom fonts)
4. Mobile experience (many Asian markets are mobile-first)

## Tools and Resources

### hreflang Validation
- Google Search Console
- Aleyda Solis's hreflang Generator
- Merkle's hreflang Tag Testing Tool

### Keyword Research
- Google Trends (by country)
- Google Keyword Planner (by language/location)
- Ahrefs (multi-language support)
- SEMrush (multi-language support)

### Translation
- DeepL (high quality for European languages)
- Google Translate (broad coverage, lower quality)
- Gengo (professional translation service)
- Smartling (enterprise translation platform)

### Analytics
- Google Analytics
- Google Search Console
- Plausible (privacy-friendly alternative)

### Testing
- Google Rich Results Test (for structured data)
- PageSpeed Insights (per URL)
- Screaming Frog (crawl each language version)

## References

- [Google International SEO Guide](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)
- [hreflang specification](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Moz International SEO](https://moz.com/learn/seo/international-seo)
- [Ahrefs International SEO Guide](https://ahrefs.com/blog/international-seo/)
