# Structured data: what to check and what to say (as of 2026-11-05)

## Google's position, in its own words

- Google's AI features page: "There's also no special schema.org structured
  data that you need to add" to appear in AI Overviews or AI Mode.
- Google's generative AI optimization guide (May 2026): structured data
  "isn't required for generative AI search".

So structured data is worth having for what it already does (rich results
that still exist, consistent machine-readable facts), not as an AI-citation
lever. Don't claim otherwise. Other engines don't document how they use it.

## Rich result status that trips up popular advice

| Markup | Status in Google Search | Source |
|---|---|---|
| `FAQPage` | Not shown since 2026-05-07; documentation removed 2026-06-15. Before that (Aug 2023) limited to well-known government and health sites | Search Central updates log |
| `HowTo` | Removed on desktop 2023-09-13 (mobile earlier); documentation removed | Search Central blog, Aug 2023 (updated Sept 2023) |

FAQ *content* on a page can still help readers and give any engine a direct
answer. The finding is only "don't add FAQPage markup expecting a rich
result".

## What to look for

| Page | Useful types | Check |
|---|---|---|
| Homepage or about | `Organization` (or `LocalBusiness`) with `name`, `url`, `logo`, `sameAs` links to real profiles, `description` | Name and description match the visible page and every other place the name appears |
| Product or pricing | `SoftwareApplication`, `Product` or `Service`; `offers` with `price` and `priceCurrency` only if the price is shown on the page | Price matches the visible price exactly |
| Blog posts, guides | `Article` or `BlogPosting` with `headline`, `author`, `datePublished`, `dateModified` | Dates match the visible dates and sitemap |
| Any page | `BreadcrumbList` | Matches the visible breadcrumb |

Common defects worth a fix:

- JSON that doesn't parse (a trailing comma kills the whole block).
- Markup describing things not on the page (reviews, ratings, prices).
  Google's structured data policies require markup to reflect visible
  content.
- Two `Organization` blocks with different names or logos (often a theme
  plus a plugin).
- `sameAs` pointing at dead or unrelated profiles.
- Markup present only after JavaScript runs (see checks.md); emit it in the
  server response where the stack allows.

## Minimal examples (adapt; don't paste values that aren't true)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Example Co",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "description": "Example Co makes invoicing software for freelance designers.",
  "sameAs": ["https://www.linkedin.com/company/example-co", "https://github.com/example-co"]
}
</script>
```

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Example Invoicing",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": { "@type": "Offer", "price": "12.00", "priceCurrency": "USD" }
}
</script>
```

Validate changes with https://validator.schema.org/ (syntax and vocabulary)
and Google's Rich Results Test for types Google still supports.
