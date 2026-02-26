# hreflang Implementation Guide

Complete guide to implementing hreflang tags for international SEO.

## What is hreflang?

hreflang is an HTML attribute that tells search engines which language and regional version of a page to serve to users.

**Purpose**:
- Prevents duplicate content penalties
- Serves correct language to users
- Improves international SEO

**Format**:
```html
<link rel="alternate" hreflang="language-region" href="URL" />
```

## Basic Implementation

### Single Language Implementation

For a website with English and Japanese:

```html
<!-- On English page: https://example.com/ -->
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

```html
<!-- On Japanese page: https://example.com/ja -->
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

**Key points**:
- Every page must reference all language versions (including itself)
- `x-default` specifies the fallback for unlisted languages
- Tags must be identical on all language versions

### Multi-Language Implementation

For English, Japanese, Chinese, Korean:

```html
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
<link rel="alternate" hreflang="zh" href="https://example.com/zh" />
<link rel="alternate" hreflang="ko" href="https://example.com/ko" />
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

## Regional Variants

### Language + Region Codes

Format: `language-region` (e.g., `zh-CN`, `pt-BR`)

**Examples**:
```html
<!-- Simplified Chinese (China) -->
<link rel="alternate" hreflang="zh-CN" href="https://example.com/zh-cn" />

<!-- Traditional Chinese (Hong Kong) -->
<link rel="alternate" hreflang="zh-HK" href="https://example.com/zh-hk" />

<!-- Traditional Chinese (Taiwan) -->
<link rel="alternate" hreflang="zh-TW" href="https://example.com/zh-tw" />

<!-- Portuguese (Portugal) -->
<link rel="alternate" hreflang="pt-PT" href="https://example.com/pt-pt" />

<!-- Portuguese (Brazil) -->
<link rel="alternate" hreflang="pt-BR" href="https://example.com/pt-br" />

<!-- Spanish (Spain) -->
<link rel="alternate" hreflang="es-ES" href="https://example.com/es-es" />

<!-- Spanish (Mexico) -->
<link rel="alternate" hreflang="es-MX" href="https://example.com/es-mx" />
```

### When to Use Regional Variants

Use regional variants when:
- Content differs significantly by region (pricing, products, legal)
- Cultural differences require separate versions
- Targeting specific markets (e.g., Spanish-speaking countries)

Use language-only codes when:
- Content is same for all regions
- Starting with basic i18n
- Limited resources for maintaining multiple versions

## Implementation Methods

### Method 1: HTML Tags (Recommended for small sites)

Add in `<head>` section of every page:

```html
<head>
  <link rel="alternate" hreflang="en" href="https://example.com/" />
  <link rel="alternate" hreflang="ja" href="https://example.com/ja" />
  <link rel="alternate" hreflang="x-default" href="https://example.com/" />
</head>
```

**Pros**:
- Easy to implement
- Immediate validation in browser
- Visible in page source

**Cons**:
- Increases page size
- Must update all pages when adding languages

### Method 2: XML Sitemap (Recommended for large sites)

Add hreflang in `sitemap.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://example.com/</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://example.com/" />
    <xhtml:link rel="alternate" hreflang="ja" href="https://example.com/ja" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/" />
  </url>
  <url>
    <loc>https://example.com/ja</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://example.com/" />
    <xhtml:link rel="alternate" hreflang="ja" href="https://example.com/ja" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/" />
  </url>
</urlset>
```

**Pros**:
- Doesn't increase page size
- Easier to manage for large sites
- Centralized configuration

**Cons**:
- Not visible in page source (harder to debug)
- Requires sitemap submission to search engines

### Method 3: HTTP Headers (Rare)

For non-HTML content (PDFs, etc.):

```
Link: <https://example.com/>; rel="alternate"; hreflang="en",
      <https://example.com/ja>; rel="alternate"; hreflang="ja",
      <https://example.com/>; rel="alternate"; hreflang="x-default"
```

## Common Patterns for Ben's Sites

### Pattern 1: English + Japanese + Chinese

```html
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
<link rel="alternate" hreflang="zh" href="https://example.com/zh" />
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

### Pattern 2: English + Asian Markets

```html
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
<link rel="alternate" hreflang="ko" href="https://example.com/ko" />
<link rel="alternate" hreflang="zh" href="https://example.com/zh" />
<link rel="alternate" hreflang="zh-HK" href="https://example.com/zh-hk" />
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

### Pattern 3: Global Coverage

```html
<!-- Primary markets -->
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
<link rel="alternate" hreflang="zh" href="https://example.com/zh" />

<!-- European markets -->
<link rel="alternate" hreflang="de" href="https://example.com/de" />
<link rel="alternate" hreflang="es" href="https://example.com/es" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr" />
<link rel="alternate" hreflang="it" href="https://example.com/it" />
<link rel="alternate" hreflang="pt" href="https://example.com/pt" />

<!-- Other markets -->
<link rel="alternate" hreflang="ar" href="https://example.com/ar" />
<link rel="alternate" hreflang="ru" href="https://example.com/ru" />

<!-- Default -->
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

## The x-default Tag

### Purpose

`x-default` specifies which version to show users whose language isn't listed.

### Best Practices

**Option 1: Primary language (Recommended)**
```html
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

**Option 2: Language selector page**
```html
<link rel="alternate" hreflang="x-default" href="https://example.com/language-selector" />
```

**When to use which**:
- Use Option 1 if you have a clear primary market
- Use Option 2 if you want users to actively choose their language

**For Ben's sites**: Use English as `x-default` since English is the primary market.

## Common Mistakes

### Mistake 1: Missing Self-Reference

❌ **Wrong**:
```html
<!-- On English page -->
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
<!-- Missing self-reference! -->
```

✅ **Correct**:
```html
<!-- On English page -->
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
```

### Mistake 2: Inconsistent URLs

❌ **Wrong**:
```html
<!-- Some pages use https, some use http -->
<link rel="alternate" hreflang="en" href="http://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
```

✅ **Correct**:
```html
<!-- All use https -->
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
```

### Mistake 3: Incorrect Language Codes

❌ **Wrong**:
```html
<link rel="alternate" hreflang="jp" href="https://example.com/ja" />  <!-- jp is country code -->
<link rel="alternate" hreflang="cn" href="https://example.com/zh" />  <!-- cn is country code -->
```

✅ **Correct**:
```html
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />  <!-- ja is language code -->
<link rel="alternate" hreflang="zh" href="https://example.com/zh" />  <!-- zh is language code -->
```

### Mistake 4: Non-Equivalent Content

❌ **Wrong**:
```html
<!-- English page: Product overview -->
<link rel="alternate" hreflang="ja" href="https://example.com/ja/pricing" />  <!-- Japanese page: Pricing -->
```

✅ **Correct**:
```html
<!-- English page: Product overview -->
<link rel="alternate" hreflang="ja" href="https://example.com/ja/" />  <!-- Japanese page: Product overview -->
```

**Rule**: Only link to equivalent content in other languages.

### Mistake 5: Missing x-default

❌ **Wrong**:
```html
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
<!-- No x-default! -->
```

✅ **Correct**:
```html
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

## Validation

### Google Search Console

1. Go to Google Search Console
2. Navigate to: **Enhancements > International Targeting**
3. Check for hreflang errors:
   - "No return tags"
   - "Incorrect language codes"
   - "Conflicting hreflang tags"

### Online Validators

**hreflang Tags Testing Tool**:
- URL: https://www.aleydasolis.com/english/international-seo-tools/hreflang-tags-generator/
- Paste your URL
- View hreflang tags found
- Check for errors

**Merkle's hreflang Tag Testing Tool**:
- URL: https://technicalseo.com/tools/hreflang/
- Comprehensive validation
- Shows all errors and warnings

### Manual Validation

```bash
# Check hreflang in sitemap
curl https://your-site.com/sitemap.xml | grep hreflang

# Check hreflang in HTML
curl https://your-site.com/ | grep hreflang

# Verify all language URLs are accessible
curl -I https://your-site.com/ja
curl -I https://your-site.com/zh
curl -I https://your-site.com/ko
```

## Monitoring

### Track in Google Search Console

After implementation:
1. Submit sitemap to Search Console
2. Wait 1-2 weeks for indexing
3. Check: **Performance > Search Results**
4. Filter by country/language
5. Monitor impressions and clicks by language

### Analytics Setup

Configure Google Analytics:
1. Create separate views for each language
2. Set up language-specific goals
3. Monitor conversion rates by language
4. A/B test translations if needed

## Troubleshooting

### Issue: Google showing wrong language

**Possible causes**:
1. hreflang tags not implemented correctly
2. Missing self-references
3. Inconsistent URLs (http vs https)
4. Wrong language codes

**Solution**:
1. Validate hreflang using Google Search Console
2. Check all pages have identical hreflang sets
3. Verify language codes are correct
4. Wait 1-2 weeks for re-crawl

### Issue: hreflang errors in Search Console

**Common errors**:

1. **"No return tags"**
   - English page links to Japanese page
   - But Japanese page doesn't link back to English page
   - **Fix**: Ensure all pages have complete hreflang sets

2. **"Incorrect language codes"**
   - Using wrong codes (e.g., "jp" instead of "ja")
   - **Fix**: Use ISO 639-1 language codes

3. **"Conflicting hreflang tags"**
   - Different hreflang in HTML vs sitemap
   - **Fix**: Remove one method or ensure they match

## Next-Specific Implementation

### Using next-intl

The `i18n-add-languages.mjs` script automatically configures hreflang in sitemap.xml.

**Manual configuration** (if needed):

In `app/[locale]/layout.tsx`:
```typescript
export async function generateMetadata({ params: { locale } }: Props) {
  const languages = {
    en: 'https://example.com/',
    ja: 'https://example.com/ja',
    zh: 'https://example.com/zh'
  };

  return {
    alternates: {
      canonical: languages[locale],
      languages: languages
    }
  };
}
```

This generates hreflang tags automatically for each page.

## References

- [Google's hreflang specification](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Moz's hreflang guide](https://moz.com/learn/seo/hreflang-tag)
- [ISO 639-1 language codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
- [ISO 3166-1 country codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
