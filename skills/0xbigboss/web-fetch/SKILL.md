---
name: web-fetch
description: Fetches web content as clean markdown by preferring markdown-native responses and falling back to selector-based HTML extraction. Use for documentation, articles, and reference pages at http/https URLs.
---

# Web Content Fetching

Fetch web content in this order:
1. Prefer markdown-native endpoints (`content-type: text/markdown`)
2. Use selector-based HTML extraction for known sites
3. Use the bundled Bun fallback script when selectors fail

## Prerequisites

Verify required tools before extracting:

```bash
command -v curl >/dev/null || echo "curl is required"
command -v html2markdown >/dev/null || echo "html2markdown is required for HTML extraction"
command -v bun >/dev/null || echo "bun is required for fetch.ts fallback"
```

Install Bun dependencies for the bundled script:

```bash
cd ~/.claude/skills/web-fetch && bun install
```

## Default Workflow

Use this as the default flow for any URL:

```bash
URL="<url>"
CONTENT_TYPE="$(curl -sIL "$URL" | awk -F': ' 'tolower($1)=="content-type"{print tolower($2)}' | tr -d '\r' | tail -1)"

if echo "$CONTENT_TYPE" | grep -q "markdown"; then
  curl -sL "$URL"
else
  curl -sL "$URL" \
    | html2markdown \
        --include-selector "article,main,[role=main]" \
        --exclude-selector "nav,header,footer,script,style"
fi
```

## Known Site Selectors

| Site | Include Selector | Exclude Selector |
|------|------------------|------------------|
| platform.claude.com | `#content-container` | - |
| docs.anthropic.com | `#content-container` | - |
| developer.mozilla.org | `article` | - |
| github.com (docs) | `article` | `nav,.sidebar` |
| Generic | `article,main,[role=main]` | `nav,header,footer,script,style` |

Example:

```bash
curl -sL "<url>" \
  | html2markdown \
      --include-selector "#content-container" \
      --exclude-selector "nav,header,footer"
```

## Finding the Right Selector

When a site isn't in the patterns list:

```bash
# Check what content containers exist
curl -s "<url>" | grep -o '<article[^>]*>\|<main[^>]*>\|id="[^"]*content[^"]*"' | head -10

# Test a selector
curl -sL "<url>" | html2markdown --include-selector "<selector>" | head -30

# Check line count
curl -sL "<url>" | html2markdown --include-selector "<selector>" | wc -l
```

## Universal Fallback Script

When selectors produce poor output, run the bundled parser:

```bash
bun ~/.claude/skills/web-fetch/fetch.ts "<url>"
```

If already in the skill directory:

```bash
bun fetch.ts "<url>"
```

## Options Reference

```bash
--include-selector "CSS"  # Keep only matching elements
--exclude-selector "CSS"  # Remove matching elements
--domain "https://..."    # Convert relative links to absolute
```

## Troubleshooting

**Empty output with selectors**: The page might be markdown-native. Check headers first:

```bash
curl -sIL "<url>" | grep -i '^content-type:'
```

**Wrong content selected**: The site may have multiple article/main regions:

```bash
curl -s "<url>" | grep -o '<article[^>]*>'
```

**`html2markdown` not found**: Install it, then retry selector-based extraction.

**`bun` or script deps missing**: Run `cd ~/.claude/skills/web-fetch && bun install`.

**Missing code blocks**: Check if the site uses non-standard code formatting.

**Client-rendered content**: If HTML only has "Loading..." placeholders, the content is JS-rendered. Neither curl nor the Bun script can extract it; use browser-based tools.
