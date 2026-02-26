# Detailed Internationalization Workflow

Step-by-step guide for adding multi-language support to Next.js websites.

## Prerequisites

Before starting:
- [ ] Next.js project using `next-intl` for i18n
- [ ] Base English (`en.json`) translation files exist
- [ ] Project follows standard i18n structure:
  ```
  i18n/
  ├── messages/
  │   └── en.json
  ├── pages/
  │   └── landing/
  │       └── en.json
  ├── locale.ts
  └── request.ts
  ```

## Step-by-Step Workflow

### Step 1: Prepare Base Language Files

#### 1.1 Verify English files exist

```bash
# Navigate to project
cd /path/to/your/project

# Check base files
ls -la i18n/messages/en.json
ls -la i18n/pages/landing/en.json
```

#### 1.2 Review translation structure

Open `en.json` files and verify:
- All translation keys are present
- No placeholder or TODO values
- Structure is logical and organized

Example structure:
```json
{
  "nav": {
    "home": "Home",
    "about": "About",
    "contact": "Contact"
  },
  "hero": {
    "title": "Welcome to Our Site",
    "subtitle": "Your solution for..."
  },
  "metadata": {
    "title": "Site Title - SEO",
    "description": "Site description for SEO"
  }
}
```

#### 1.3 Document special requirements

Note any content that needs cultural adaptation:
- Dates and times (format varies by region)
- Currency (¥, $, €, etc.)
- Phone numbers
- Address formats
- Images with text (need separate versions)

### Step 2: Configure Languages to Add

#### 2.1 Determine target languages

Common target markets:
- **Primary**: English (en), Japanese (ja), Chinese (zh)
- **Secondary**: Korean (ko), Portuguese (pt), Spanish (es)
- **Extended**: German (de), French (fr), Italian (it), Russian (ru), Arabic (ar)

#### 2.2 Edit the script configuration

Open `scripts/i18n-add-languages.mjs`:

```javascript
// Configure languages to add
const languages = [
  'ja.json',    // Japanese
  'ko.json',    // Korean
  'zh.json',    // Simplified Chinese
  'zh-hk.json'  // Traditional Chinese (Hong Kong)
];

// Configure language names (for language switcher)
const languageNames = {
  ja: '日本語',
  ko: '한국어',
  zh: '中文',
  'zh-hk': '繁體中文'
};
```

#### 2.3 Verify target directories

Ensure `targetDirs` matches your project structure:

```javascript
const targetDirs = [
  'i18n/messages',
  'i18n/pages/landing'
];
```

Add more directories if your project has additional translation files:
```javascript
const targetDirs = [
  'i18n/messages',
  'i18n/pages/landing',
  'i18n/pages/about',     // If you have about page translations
  'i18n/pages/pricing'    // If you have pricing page translations
];
```

### Step 3: Run Language Addition Script

#### 3.1 Execute the script

```bash
node scripts/i18n-add-languages.mjs
```

Expected output:
```
🚀 开始添加多语言支持...
📋 需要添加的语言: ja.json, ko.json, zh.json, zh-hk.json

🔍 检查项目结构...
✅ 项目根目录: /path/to/project

📁 处理目录: /path/to/project/i18n/messages
✅ 已创建: /path/to/project/i18n/messages/ja.json
✅ 已创建: /path/to/project/i18n/messages/ko.json
✅ 已创建: /path/to/project/i18n/messages/zh.json
✅ 已创建: /path/to/project/i18n/messages/zh-hk.json

📁 处理目录: /path/to/project/i18n/pages/landing
✅ 已创建: /path/to/project/i18n/pages/landing/ja.json
...

📝 更新 locale.ts 文件...
✅ locale.ts 更新完成

📝 更新 request.ts 文件...
✅ request.ts 更新完成

📝 更新 sitemap.xml 文件...
✅ sitemap.xml 更新完成

✅ 多语言支持添加完成！
```

#### 3.2 Handle errors

**Error: "目录不存在"**
```bash
# Create missing directory
mkdir -p i18n/messages
mkdir -p i18n/pages/landing

# Ensure en.json exists
# Create or copy template file
```

**Error: "源文件不存在"**
```bash
# Create base en.json file
# Add basic structure
echo '{}' > i18n/messages/en.json
```

**Error: "项目根目录找不到 package.json"**
```bash
# Run from project root, not scripts directory
cd ..
node scripts/i18n-add-languages.mjs
```

### Step 4: Verify Configuration Updates

#### 4.1 Check locale.ts

```bash
cat i18n/locale.ts
```

Verify:
```typescript
export const locales = ["en", "ja", "ko", "zh", "zh-hk"];

export const localeNames: any = {
  en: "English",
  ja: "日本語",
  ko: "한국어",
  zh: "中文",
  "zh-hk": "繁體中文"
};
```

#### 4.2 Check request.ts

```bash
cat i18n/request.ts
```

Verify language mapping logic:
```typescript
// Language code mappings
if (["zh-CN"].includes(locale)) {
  locale = "zh";
}

if (["zh-HK", "zh-hk"].includes(locale)) {
  locale = "zh-hk";
}
```

#### 4.3 Check sitemap.xml

```bash
cat public/sitemap.xml
```

Verify hreflang tags for each language:
```xml
<url>
  <loc>https://example.com/</loc>
  <lastmod>2025-06-15T10:00:00+00:00</lastmod>
  <xhtml:link rel="alternate" hreflang="en" href="https://example.com/"/>
  <xhtml:link rel="alternate" hreflang="ja" href="https://example.com/ja"/>
  <xhtml:link rel="alternate" hreflang="zh" href="https://example.com/zh"/>
  <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/"/>
</url>
```

### Step 5: Add Translations

#### 5.1 Choose translation method

**Method A: AI Translation (faster)**

Use `i18n-add-schema.js` for structured data:

1. Configure translations in script:
```javascript
const translations = {
  ja: {
    schema: {
      webApp: {
        name: "アプリ名",
        description: "アプリの説明",
        features: ["機能1", "機能2"]
      }
    }
  },
  zh: {
    schema: {
      webApp: {
        name: "应用名称",
        description: "应用描述",
        features: ["功能1", "功能2"]
      }
    }
  }
};
```

2. Run script:
```bash
node scripts/i18n-add-schema.js
```

**Method B: Manual Translation (recommended)**

1. Open language file:
```bash
code i18n/messages/ja.json
```

2. Replace English with translated text:
```json
{
  "nav": {
    "home": "ホーム",
    "about": "会社概要",
    "contact": "お問い合わせ"
  }
}
```

3. Repeat for each language

**Method C: Professional Translation Service**

1. Export English files
2. Send to translation service (Gengo, Smartling, etc.)
3. Import translated files
4. Review and adjust

#### 5.2 Translation quality checklist

For each language:
- [ ] All keys translated (no English remaining)
- [ ] Special characters render correctly
- [ ] Grammar and spelling checked
- [ ] Cultural adaptation applied (not just literal translation)
- [ ] SEO keywords researched and included
- [ ] Formatting maintained (HTML tags, variables)
- [ ] Links updated to language-specific URLs

#### 5.3 Handle special content types

**Dates**:
```json
{
  "en": "January 1, 2025",
  "ja": "2025年1月1日",
  "zh": "2025年1月1日"
}
```

**Currency**:
```json
{
  "en": "$99.99",
  "ja": "¥12,000",
  "zh": "¥699"
}
```

**Names and titles**:
- Keep brand names in original form
- Translate descriptive titles
- Consider local naming conventions

### Step 6: Configure SEO Elements

#### 6.1 Update meta tags in translations

Each language file should include:
```json
{
  "metadata": {
    "title": "Page Title | Brand",
    "description": "Page description for search engines (150-160 chars)",
    "keywords": "keyword1, keyword2, keyword3"
  }
}
```

**SEO translation tips**:
- Research keywords in target language (don't just translate English keywords)
- Use local search trends (Google Trends, Ahrefs)
- Match local search intent
- Respect character limits (may differ in Asian languages)

#### 6.2 Verify hreflang implementation

Check page source in browser:
```html
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="ja" href="https://example.com/ja" />
<link rel="alternate" hreflang="zh" href="https://example.com/zh" />
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

**Common hreflang mistakes**:
- ❌ Missing `x-default` (fallback for unlisted languages)
- ❌ Self-referential hreflang (every page must reference itself)
- ❌ Inconsistent URLs (https vs http, www vs non-www)
- ❌ Wrong language codes (use ISO 639-1)

#### 6.3 Update structured data

Add localized structured data for each language:

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Site Name",
  "inLanguage": "ja",
  "url": "https://example.com/ja"
}
```

Use `i18n-add-schema.js` script or add manually to each page.

### Step 7: Testing and Validation

#### 7.1 Build test

```bash
npm run build
```

Expected: No errors, all pages compile successfully.

**If build fails**:
- Check for JSON syntax errors (missing commas, brackets)
- Verify all referenced translation keys exist
- Check for special characters that need escaping

#### 7.2 Development testing

```bash
npm run dev
```

Test each language version:

1. **Language switcher**:
   - Visit `http://localhost:3000/`
   - Click language switcher
   - Verify all languages listed
   - Click each language, verify URL changes and content updates

2. **URL routing**:
   - Visit `http://localhost:3000/ja`
   - Verify Japanese content displays
   - Repeat for all languages

3. **Content rendering**:
   - Check all pages in each language
   - Verify no untranslated text
   - Check special characters (日本語, 中文, العربية)
   - Test all interactive elements (forms, buttons)

#### 7.3 Production testing (after deployment)

1. **Validate hreflang**:
   - Use Google Search Console > Internationalization
   - Or use: https://validator.schema.org/

2. **Test geo-targeting**:
   - Use VPN to test from target countries
   - Verify correct language version served
   - Check that auto-detection works (if enabled)

3. **Crawlability test**:
   - Use Screaming Frog or similar tool
   - Verify all language versions crawlable
   - Check for redirect loops

#### 7.4 SEO validation

See [reference/seo-checklist.md](reference/seo-checklist.md) for complete checklist.

**Quick checks**:
```bash
# Check sitemap includes all languages
curl https://your-site.com/sitemap.xml | grep hreflang

# Verify each language URL is accessible
curl -I https://your-site.com/ja
curl -I https://your-site.com/zh
curl -I https://your-site.com/ko
```

## Troubleshooting

### Build Errors

**Error: "Cannot find translation key"**

Cause: Referenced key doesn't exist in language file.

Solution:
```bash
# Find missing key in English file
grep -r "missing.key" i18n/messages/en.json

# Add to all language files
# Or remove reference if not needed
```

**Error: "JSON parse error"**

Cause: Syntax error in JSON file.

Solution:
```bash
# Use JSON validator
cat i18n/messages/ja.json | jq .

# Or use VS Code's JSON validation
code i18n/messages/ja.json
```

### Runtime Errors

**Error: Translations not loading**

Cause: Locale configuration issue.

Solution:
1. Check `i18n/locale.ts` includes the locale
2. Verify `i18n/request.ts` loads the correct file
3. Clear Next.js cache: `rm -rf .next`
4. Rebuild: `npm run build`

**Error: Language switcher not working**

Cause: Routing configuration issue.

Solution:
1. Verify language switcher component uses correct locale codes
2. Check next-intl navigation configuration
3. Test with direct URL navigation first

### SEO Issues

**Issue: Google not indexing language versions**

Causes and solutions:
1. **Missing hreflang**: Verify sitemap.xml includes all versions
2. **robots.txt blocking**: Check robots.txt doesn't block language paths
3. **Canonical issues**: Ensure each language has correct canonical URL
4. **Duplicate content**: Verify hreflang properly configured

**Issue: Wrong language showing in search results**

Cause: hreflang configuration error.

Solution:
1. Validate hreflang tags using Google Search Console
2. Ensure language codes are correct (ISO 639-1)
3. Check `x-default` points to primary language
4. Verify each page has self-referential hreflang

## Best Practices

### Do's ✅

- ✅ Research keywords in target language before translating
- ✅ Use native speakers for review (even if AI translated)
- ✅ Test with users from target market
- ✅ Keep URL structure consistent across languages
- ✅ Translate meta tags and structured data
- ✅ Use hreflang tags correctly
- ✅ Create separate Search Console properties for each region

### Don'ts ❌

- ❌ Auto-redirect based on IP address (prevents search engines from crawling all versions)
- ❌ Use machine translation without human review
- ❌ Duplicate content across languages without proper hreflang
- ❌ Mix languages on same page (except for brand names)
- ❌ Forget to translate images with text
- ❌ Use cookies to remember language preference (blocks search engines)
- ❌ Serve different content for same URL based on user agent

## Performance Optimization

### Reduce i18n bundle size

```javascript
// In next.config.mjs
const nextConfig = {
  i18n: {
    localeDetection: false  // Disable if not needed
  }
};
```

### Lazy load translations

Only load translations for current page:
```typescript
// Use next-intl's namespaces feature
const t = useTranslations('HomePage');  // Only loads HomePage translations
```

### Cache translations

Configure appropriate cache headers for translation files:
```javascript
// In next.config.mjs
const nextConfig = {
  async headers() {
    return [
      {
        source: '/locales/:locale/:namespace',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          }
        ]
      }
    ];
  }
};
```

## Maintenance

### Adding new content

When adding new pages or features:
1. Add English translations first
2. Run `i18n-add-languages.mjs` to copy structure
3. Add translations for all languages
4. Update sitemap.xml
5. Test all language versions

### Updating translations

```bash
# Find all occurrences of a translation key
grep -r "hero.title" i18n/

# Update in all language files
# Test that changes render correctly
```

### Removing languages

1. Delete language files from `i18n/` directories
2. Remove from `i18n/locale.ts` locales array
3. Remove from `i18n/request.ts` mappings
4. Update `public/sitemap.xml`
5. Rebuild project
