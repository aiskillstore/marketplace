# Language and Locale Codes Reference

Complete reference for language and regional codes used in i18n.

## Language Codes (ISO 639-1)

Two-letter codes for languages.

### Ben's Primary Markets

| Code | Language | Native Name | Market |
|------|----------|-------------|--------|
| `en` | English | English | 🇺🇸 Primary - Global |
| `ja` | Japanese | 日本語 | 🇯🇵 High-value - Japan |
| `zh` | Chinese (Simplified) | 中文 | 🇨🇳 Domestic - China |

### Extended Asian Markets

| Code | Language | Native Name | Market |
|------|----------|-------------|--------|
| `ko` | Korean | 한국어 | 🇰🇷 South Korea |
| `zh-hk` | Chinese (Traditional) | 繁體中文 | 🇭🇰 Hong Kong |
| `zh-tw` | Chinese (Traditional) | 繁體中文 | 🇹🇼 Taiwan |
| `vi` | Vietnamese | Tiếng Việt | 🇻🇳 Vietnam |
| `th` | Thai | ไทย | 🇹🇭 Thailand |
| `id` | Indonesian | Bahasa Indonesia | 🇮🇩 Indonesia |
| `hi` | Hindi | हिन्दी | 🇮🇳 India |

### European Markets

| Code | Language | Native Name | Market |
|------|----------|-------------|--------|
| `de` | German | Deutsch | 🇩🇪 Germany |
| `fr` | French | Français | 🇫🇷 France |
| `es` | Spanish | Español | 🇪🇸 Spain |
| `it` | Italian | Italiano | 🇮🇹 Italy |
| `pt` | Portuguese | Português | 🇵🇹 Portugal |
| `ru` | Russian | Русский | 🇷🇺 Russia |
| `pl` | Polish | Polski | 🇵🇱 Poland |
| `nl` | Dutch | Nederlands | 🇳🇱 Netherlands |
| `sv` | Swedish | Svenska | 🇸🇪 Sweden |
| `tr` | Turkish | Türkçe | 🇹🇷 Turkey |

### Other Markets

| Code | Language | Native Name | Market |
|------|----------|-------------|--------|
| `ar` | Arabic | العربية | 🇸🇦 Middle East |
| `pt-br` | Portuguese (Brazil) | Português | 🇧🇷 Brazil |
| `es-mx` | Spanish (Mexico) | Español | 🇲🇽 Mexico |
| `fr-ca` | French (Canada) | Français | 🇨🇦 Canada |

## Regional Variants

### When to Use Regional Codes

Use language + region (e.g., `pt-BR`) when:
- **Content differs by region**: Pricing, products, legal requirements
- **Cultural differences**: Different cultural references or examples
- **Dialect differences**: Spanish (Spain) vs Spanish (Mexico)

Use language only (e.g., `pt`) when:
- **Content is same**: No regional differences
- **Starting out**: Limited resources for multiple variants
- **Testing**: Validate market before creating regional variants

### Chinese Variants

| Code | Script | Region | Notes |
|------|--------|--------|-------|
| `zh` or `zh-CN` | Simplified | Mainland China | Most common, largest market |
| `zh-HK` | Traditional | Hong Kong | Different from Taiwan Traditional |
| `zh-TW` | Traditional | Taiwan | Different from Hong Kong Traditional |
| `zh-SG` | Simplified | Singapore | Usually same as `zh-CN` |

**Recommendation for Ben**:
- Start with `zh` (Simplified) for mainland China
- Add `zh-hk` if targeting Hong Kong specifically
- Same content can work for both if no regional differences

### Portuguese Variants

| Code | Region | Differences |
|------|--------|-------------|
| `pt` or `pt-PT` | Portugal | European Portuguese, formal tone |
| `pt-BR` | Brazil | Brazilian Portuguese, different vocabulary and grammar |

**Note**: Brazilian and European Portuguese are quite different. If targeting Brazil, use `pt-BR`.

### Spanish Variants

| Code | Region | Differences |
|------|--------|-------------|
| `es` or `es-ES` | Spain | European Spanish, "vosotros" form |
| `es-MX` | Mexico | Mexican Spanish, largest Spanish-speaking market |
| `es-AR` | Argentina | Argentine Spanish, "vos" form |
| `es-CO` | Colombia | Colombian Spanish |

**Recommendation**:
- Start with `es` (general Spanish) or `es-MX` (Mexican) for Latin America
- Add `es-ES` if targeting Spain specifically

### English Variants

| Code | Region | Differences |
|------|--------|-------------|
| `en` or `en-US` | United States | American spelling (color, organize) |
| `en-GB` | United Kingdom | British spelling (colour, organise) |
| `en-AU` | Australia | Australian English |
| `en-CA` | Canada | Canadian English |

**Recommendation for Ben**:
- Use `en` (US English) as default - largest market
- Add `en-GB` only if specifically targeting UK market

## Next.js Locale Configuration

### In `i18n/locale.ts`

```typescript
// Basic configuration
export const locales = ["en", "ja", "zh", "ko"];

// With regional variants
export const locales = [
  "en",
  "ja",
  "zh", "zh-hk",
  "ko",
  "pt", "pt-br",
  "es", "es-mx"
];

// Display names
export const localeNames: any = {
  en: "English",
  ja: "日本語",
  zh: "中文",
  "zh-hk": "繁體中文",
  ko: "한국어"
};
```

### URL Structure

**Recommended structure**:
```
https://example.com/          → English (default)
https://example.com/ja        → Japanese
https://example.com/zh        → Chinese (Simplified)
https://example.com/zh-hk     → Chinese (Traditional, Hong Kong)
https://example.com/ko        → Korean
```

**Alternative structure** (with `/en/`):
```
https://example.com/en        → English
https://example.com/ja        → Japanese
https://example.com/zh        → Chinese
```

**Recommendation**: Use first structure (English at root) for better SEO and simpler URLs.

## Naming Conventions

### File Names

Use lowercase with hyphens for multi-part codes:

```
en.json         ✅ Correct
ja.json         ✅ Correct
zh.json         ✅ Correct
zh-hk.json      ✅ Correct (lowercase, hyphen)
pt-br.json      ✅ Correct (lowercase, hyphen)

zh_hk.json      ❌ Wrong (underscore)
ZH-HK.json      ❌ Wrong (uppercase)
zhHK.json       ❌ Wrong (camelCase)
```

### Directory Structure

```
i18n/
├── messages/
│   ├── en.json
│   ├── ja.json
│   ├── zh.json
│   ├── zh-hk.json
│   └── ko.json
├── pages/
│   └── landing/
│       ├── en.json
│       ├── ja.json
│       ├── zh.json
│       ├── zh-hk.json
│       └── ko.json
├── locale.ts
└── request.ts
```

## Language Direction

### Left-to-Right (LTR)

Most languages:
```
en, ja, zh, ko, de, fr, es, it, pt, ru, etc.
```

### Right-to-Left (RTL)

Requires special handling:
```
ar, he, fa, ur
```

**For RTL languages**, you need to:
1. Set `dir="rtl"` on `<html>` tag
2. Use CSS logical properties (`inline-start` instead of `left`)
3. Mirror layouts and icons
4. Test thoroughly

**Example**:
```typescript
// In app/[locale]/layout.tsx
const direction = locale === 'ar' ? 'rtl' : 'ltr';

return (
  <html lang={locale} dir={direction}>
    ...
  </html>
);
```

## Character Sets and Encoding

Always use UTF-8 encoding for all files.

### Character Ranges

| Language | Characters | Notes |
|----------|------------|-------|
| English | A-Z, a-z | ASCII compatible |
| Japanese | Hiragana, Katakana, Kanji | ~2,000 common kanji |
| Chinese | Simplified: ~3,500 common | Traditional: ~4,800 common |
| Korean | Hangul | ~11,000 possible syllables |
| Arabic | Arabic script | Includes diacritics |
| Russian | Cyrillic | 33 letters |
| Thai | Thai script | 44 consonants, 15 vowels |

### Font Considerations

Ensure your web fonts support the character sets you need:

```css
/* Example for multi-language support */
@font-face {
  font-family: 'NotoSans';
  src: url('/fonts/NotoSans-Regular.woff2');
  /* Noto Sans has excellent multi-language support */
}

/* Japanese-specific font */
@font-face {
  font-family: 'NotoSansJP';
  src: url('/fonts/NotoSansJP-Regular.woff2');
  unicode-range: U+3000-9FFF; /* Japanese characters */
}
```

## Special Cases

### Language Code Mappings

Some systems use different codes. Handle mapping in `i18n/request.ts`:

```typescript
// Map common variants
if (["zh-CN", "zh-cn"].includes(locale)) {
  locale = "zh";
}

if (["zh-HK", "zh-hk"].includes(locale)) {
  locale = "zh-hk";
}

if (["pt-BR", "pt-br"].includes(locale)) {
  locale = "pt-br";
}
```

### Browser Language Detection

Browsers send `Accept-Language` header:
```
Accept-Language: en-US,en;q=0.9,ja;q=0.8
```

**Parsing**:
- `en-US` - First preference (US English)
- `en;q=0.9` - Second preference (general English, quality 0.9)
- `ja;q=0.8` - Third preference (Japanese, quality 0.8)

**Matching logic**:
1. Try exact match (`en-US`)
2. Try language match (`en`)
3. Fall back to default (`en` or `x-default`)

## Testing Different Locales

### Browser Testing

**Chrome DevTools**:
1. Open DevTools (F12)
2. Settings > Preferences > Languages
3. Add and reorder languages
4. Reload page

**Firefox**:
1. Settings > General > Language
2. Choose language
3. Reload page

### Curl Testing

```bash
# Test with specific language
curl -H "Accept-Language: ja" https://example.com/

# Test with regional variant
curl -H "Accept-Language: zh-HK" https://example.com/
```

### URL Testing

```bash
# Test direct URL access
curl https://example.com/ja
curl https://example.com/zh
curl https://example.com/ko
```

## Market Prioritization for Ben

Based on SaaS tool market size and Ben's expertise:

### Tier 1 (Essential)
- 🇺🇸 English (`en`) - Largest market, Ben's primary language
- 🇯🇵 Japanese (`ja`) - High-value market, strong SaaS adoption
- 🇨🇳 Chinese (`zh`) - Large market, domestic advantage

### Tier 2 (High Value)
- 🇰🇷 Korean (`ko`) - Strong tech market
- 🇩🇪 German (`de`) - European tech hub
- 🇫🇷 French (`fr`) - Large European market
- 🇪🇸 Spanish (`es`) - Latin America + Spain

### Tier 3 (Expansion)
- 🇵🇹 Portuguese (`pt-br`) - Brazilian market
- 🇮🇹 Italian (`it`) - European market
- 🇷🇺 Russian (`ru`) - Eastern Europe
- 🇮🇩 Indonesian (`id`) - Southeast Asia

**Recommendation**:
1. Start with Tier 1 (en, ja, zh)
2. Add Tier 2 based on traffic data
3. Consider Tier 3 if demand exists

## References

- [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
- [ISO 3166-1 Country Codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
- [IETF Language Tags](https://www.ietf.org/rfc/bcp/bcp47.txt)
- [Unicode CLDR](http://cldr.unicode.org/)
- [MDN: lang attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/lang)
