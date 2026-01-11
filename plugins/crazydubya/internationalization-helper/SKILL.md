---
name: internationalization-helper
description: Extracts hardcoded strings for i18n, manages translation files, and ensures locale coverage. Use when working with multi-language apps, translations, or user mentions i18n, localization, or languages.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Internationalization Helper

Helps manage internationalization (i18n) and localization (l10n) in multi-language applications.

## When to Use
- User requests i18n support
- Adding new languages
- Finding untranslated strings
- Managing translation files
- User mentions "translation", "i18n", "l10n", "locale"

## Instructions

### 1. Detect i18n Framework

**JavaScript/React:**
- react-i18next
- react-intl (FormatJS)
- i18next
- LinguiJS

**Vue:**
- vue-i18n

**Python:**
- gettext
- Django i18n
- Flask-Babel

**Ruby/Rails:**
- I18n gem (built-in)

Look for imports, config files, or translation directories.

### 2. Find Hardcoded Strings

Search for untranslated text:

```javascript
// Bad: Hardcoded
<button>Submit</button>
<p>Welcome, {user.name}!</p>

// Good: Translated
<button>{t('common.submit')}</button>
<p>{t('welcome.message', { name: user.name })}</p>
```

**Search patterns:**
- Strings in JSX/template tags
- Alert/error messages
- Form labels and placeholders
- Button text
- Validation messages

Exclude: code comments, console.log, test strings

### 3. Extract to Translation Files

**React-i18next format (JSON):**
```json
{
  "common": {
    "submit": "Submit",
    "cancel": "Cancel"
  },
  "welcome": {
    "message": "Welcome, {{name}}!"
  }
}
```

**Gettext format (.po):**
```po
msgid "submit_button"
msgstr "Submit"

msgid "welcome_message"
msgstr "Welcome, %(name)s!"
```

### 4. Organize Translation Keys

**Best practices:**
- Namespace by feature: `users.profile.title`
- Group common strings: `common.buttons.save`
- Describe context, not content: `errors.login.invalid` not `errors.wrong_password`
- Consistent naming convention

### 5. Check Translation Coverage

Compare locale files to find missing translations:

```
en.json: 150 keys
es.json: 142 keys (missing 8)
fr.json: 150 keys ✓

Missing in es.json:
- users.profile.bio
- settings.privacy.title
[...]
```

### 6. Handle Pluralization

Different languages have different plural rules:

```javascript
// react-i18next
t('items', { count: 0 })  // "0 items"
t('items', { count: 1 })  // "1 item"
t('items', { count: 5 })  // "5 items"

// Translation file
{
  "items_zero": "{{count}} items",
  "items_one": "{{count}} item",
  "items_other": "{{count}} items"
}
```

### 7. Date, Time, Number Formatting

Use locale-aware formatting:

```javascript
// Numbers
const price = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD'
}).format(29.99);

// Dates
const date = new Intl.DateTimeFormat('fr-FR').format(new Date());
```

### 8. RTL (Right-to-Left) Support

For Arabic, Hebrew:
- CSS: `direction: rtl;`
- HTML: `<html dir="rtl">`
- Logical properties: `margin-inline-start` instead of `margin-left`

### 9. Generate Translation Template

Create template for new locale:

```bash
# Copy keys from base language, empty values
cp locales/en.json locales/de.json
# Mark for translation
```

### 10. Best Practices

- Keep translations in separate files
- Use keys, not source text as keys
- Provide context to translators
- Test with long strings (German often longer)
- Use ICU MessageFormat for complex strings
- Avoid concatenating translated strings
- Extract all user-facing text

## Supporting Files
- `templates/i18n-config.js`: Configuration examples
- `templates/locale-file.json`: Translation file template
