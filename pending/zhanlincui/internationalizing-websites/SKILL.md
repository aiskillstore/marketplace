---
name: Internationalizing Websites
description: Adds multi-language support to Next.js websites with proper SEO configuration including hreflang tags, localized sitemaps, and language-specific content. Use when adding new languages, setting up i18n, optimizing for international SEO, or when user mentions localization, translation, multi-language, or specific languages like Japanese, Korean, Chinese.
---

# Internationalizing Websites

Complete workflow for adding multi-language support to Next.js websites with SEO best practices.

## When to use this Skill

- Adding new language versions to existing website
- Setting up i18n (internationalization) for new website
- Configuring SEO for multiple languages
- User mentions: "add language", "translation", "localization", "hreflang", "multi-language"

## Supported Languages

Common target markets:
- 🇺🇸 English (en) - Global market
- 🇯🇵 Japanese (ja) - Asian market
- 🇨🇳 Chinese (zh) - Chinese market

Extended support available for:
- Korean (ko), Portuguese (pt), Spanish (es), French (fr), German (de)
- Arabic (ar), Vietnamese (vi), Hindi (hi), Indonesian (id), Thai (th)
- Traditional Chinese (zh-hk), Italian (it), Russian (ru)

## Internationalization Workflow

Copy this checklist and track your progress:

```
i18n Progress:
- [ ] Step 1: Prepare base language files
- [ ] Step 2: Add new language files
- [ ] Step 3: Update configuration files
- [ ] Step 4: Add translations
- [ ] Step 5: Configure SEO elements
- [ ] Step 6: Validate and test
```

### Step 1: Prepare base language files

Ensure English (`en.json`) files exist as templates:

**Required directories**:
- `i18n/messages/en.json` - Main translations
- `i18n/pages/landing/en.json` - Landing page translations

**Verify structure**:
```bash
# Check if base files exist
ls i18n/messages/en.json
ls i18n/pages/landing/en.json
```

If missing, create them with complete translation keys for your website.

### Step 2: Add new language files

Run the language addition script:

```bash
node scripts/i18n-add-languages.mjs
```

**What this script does**:
- Copies `en.json` to all target language files
- Updates `i18n/locale.ts` with new locales
- Updates `i18n/request.ts` with language mappings
- Updates `public/sitemap.xml` with new language URLs

**Script configuration** (in `i18n-add-languages.mjs`):
- `languages` array - List of languages to add
- `languageNames` object - Language display names
- `targetDirs` array - Directories containing translation files

See [WORKFLOW.md](WORKFLOW.md) for detailed step-by-step guide.

### Step 3: Verify configuration updates

**Check `i18n/locale.ts`**:
```typescript
export const locales = ["en", "ja", "zh", "ko", ...];

export const localeNames: any = {
  en: "English",
  ja: "日本語",
  zh: "中文",
  ko: "한국어",
  ...
};
```

**Check `i18n/request.ts`**:
- Language code mappings configured
- `zh-CN` → `zh`, `zh-HK` → `zh-hk` mappings present

**Check `public/sitemap.xml`**:
- All language versions listed
- `hreflang` tags present for each URL

### Step 4: Add translations

**Option A: Using AI translation** (faster but needs review):
```bash
# Add structured data and pricing translations
node scripts/i18n-add-schema.js
```

Configure translations in the script's `translations` object.

**Option B: Manual translation** (recommended for quality):

Edit each language file with proper translations:
```bash
# Open language file
code i18n/messages/ja.json
```

**Translation best practices**:
- Use native speakers when possible
- Maintain SEO keywords in target language
- Adapt content to local culture, don't just translate
- Keep formatting consistent (placeholders, variables)

See [reference/locale-codes.md](reference/locale-codes.md) for language code reference.

### Step 5: Configure SEO elements

**hreflang tags** - Automatic via sitemap, but verify:

See [reference/hreflang-guide.md](reference/hreflang-guide.md) for complete guide.

**Localized meta tags** - Translate in each language file:
```json
{
  "metadata": {
    "title": "Your Site Title",
    "description": "Your SEO description"
  }
}
```

**URL structure** - Verify correct format:
- English: `https://example.com/` or `https://example.com/en/`
- Japanese: `https://example.com/ja/`
- Chinese: `https://example.com/zh/`

### Step 6: Validate and test

**Build the project**:
```bash
npm run build
```

**CRITICAL: Fix any errors before proceeding.**

**Manual testing**:
1. **Language switcher**:
   - Visit each language version
   - Verify language switcher shows all languages
   - Click each language link, verify correct page loads

2. **Content display**:
   - Check all pages render correctly in each language
   - Verify no untranslated text (check for English in non-English pages)
   - Test special characters display correctly (Japanese, Chinese, Arabic)

3. **SEO elements**:
   - Inspect `<html lang="...">` attribute matches page language
   - Verify `<link rel="alternate" hreflang="...">` tags present
   - Check meta tags are in correct language

**Automated validation**:
```bash
# Check sitemap
curl https://your-site.com/sitemap.xml | grep hreflang

# Validate hreflang (use online tool)
# Google Search Console > Internationalization > hreflang
```

**SEO checklist** - See [reference/seo-checklist.md](reference/seo-checklist.md).

**If validation fails**:
- Review error messages carefully
- Check configuration files for typos
- Verify language codes are correct
- Return to Step 3 and fix issues

**Only proceed when all validations pass.**

## Important Notes

### Language Code Standards

Use ISO 639-1 (two-letter codes) with optional regional variants:
- `en` - English
- `ja` - Japanese
- `zh` - Simplified Chinese
- `zh-hk` - Traditional Chinese (Hong Kong)
- `pt` - Portuguese
- `pt-br` - Brazilian Portuguese

See [reference/locale-codes.md](reference/locale-codes.md) for complete list.

### SEO Implications

**Correct i18n improves SEO by**:
- Targeting users in their native language
- Avoiding duplicate content penalties
- Helping search engines serve correct language version

**Common SEO mistakes to avoid**:
- ❌ Auto-redirect based on IP (prevents search engines from crawling all versions)
- ❌ Missing hreflang tags (causes duplicate content issues)
- ❌ Inconsistent URL structure across languages
- ❌ Untranslated meta tags

### Translation Quality

**AI translation vs Human translation**:
- ✅ AI: Fast, cost-effective, good for initial draft
- ⚠️ AI: May miss cultural nuances, needs review
- ✅ Human: Better quality, cultural adaptation
- ⚠️ Human: Slower, more expensive

**Recommended approach**:
1. Use AI to generate initial translations
2. Have native speaker review and refine
3. Test with target market users
4. Iterate based on feedback

### Next.js i18n Routing

The system uses `next-intl` for routing:
- Automatic locale detection from URL
- Language switcher component
- Localized navigation

Configuration in `i18n/locale.ts` and `i18n/request.ts`.

## Post-Internationalization Tasks

After adding languages:

1. **Submit updated sitemap to Google Search Console**
2. **Create separate Search Console properties** for each language/region
3. **Monitor international organic traffic** in Analytics
4. **A/B test translations** if conversion rates differ by language
5. **Set up alerts** for international crawl errors

## Script Locations

All i18n scripts are in the `scripts/` directory:
- `i18n-add-languages.mjs` - Add new language files
- `i18n-add-schema.js` - Add structured data translations

## Reference Materials

- [WORKFLOW.md](WORKFLOW.md) - Detailed step-by-step workflow
- [reference/hreflang-guide.md](reference/hreflang-guide.md) - hreflang implementation guide
- [reference/locale-codes.md](reference/locale-codes.md) - Language codes reference
- [reference/seo-checklist.md](reference/seo-checklist.md) - International SEO checklist

For troubleshooting, see [WORKFLOW.md](WORKFLOW.md) troubleshooting section.
