# Sources

Checked **as of 2026-11-05** unless a row says otherwise. Re-check before
relying on one for a decision; these pages change.

| Fact | Source | As of |
|---|---|---|
| AI Overviews and AI Mode: page must be indexed and eligible to show with a snippet; "no additional requirements"; no new machine-readable files, AI text files or markup needed; "no special schema.org structured data"; limits via nosnippet, data-nosnippet, max-snippet, noindex | https://developers.google.com/search/docs/appearance/ai-features | 2026-11-05 |
| Google's guide to optimizing for generative AI features (published 2026-05-15): Search ignores llms.txt and AI text files; no need to chunk content; structured data "isn't required for generative AI search"; Google can process JavaScript content if not blocked; pages made to manipulate AI responses violate the scaled content abuse policy; Generative AI performance report in Search Console | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (Markdown copy: same URL + `.md.txt`) | 2026-11-05 |
| llms.txt clarification (2026-06-15): files "aren't needed for Google Search (and won't negatively or positively impact your visibility or rankings)" | https://developers.google.com/search/updates | 2026-11-05 |
| FAQ rich result deprecated, not shown from 2026-05-07; docs removed 2026-06-15 | https://developers.google.com/search/updates | 2026-11-05 |
| HowTo rich results removed (mobile Aug 2023, desktop 2023-09-13); FAQ limited to authoritative government and health sites from Aug 2023 | https://developers.google.com/search/blog/2023/08/howto-faq-changes | 2026-11-05 |
| Structured data must represent visible page content; don't mark up content not visible to readers | https://developers.google.com/search/docs/appearance/structured-data/sd-policies | 2026-11-05 |
| Google processes structured data present in the rendered DOM; test with the Rich Results Test by URL | https://developers.google.com/search/docs/appearance/structured-data/generate-structured-data-with-javascript | 2026-11-05 |
| llms.txt: proposal by Jeremy Howard (first published 2024-09-03, v2 modified 2026-08-10); H1 is the only required section; makes no claim that search engines or AI products consume it | https://llmstxt.org/ | 2026-11-05 |
| Applebot "may render the content of your website within a browser" | https://support.apple.com/en-us/119829 | 2026-11-05 |
| OpenAI, Anthropic, Perplexity and Meta crawler pages don't mention llms.txt or JavaScript rendering | https://developers.openai.com/api/docs/bots, https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler, https://docs.perplexity.ai/guides/bots, https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/ | 2026-11-05 |

## Could not verify

- **Whether AI crawlers other than Googlebot and Applebot execute
  JavaScript.** Undocumented by the vendors; the skill treats JS-only facts
  as "at risk", not "invisible".
- **Whether any AI engine reads llms.txt in production.** No vendor page
  checked says it does; the skill reports presence only.
- **How non-Google engines use schema.org markup.** Undocumented.

## Ideas credited

- Noting that a plain fetch misses JavaScript-injected JSON-LD, so "no
  schema found" from `curl` is not a finding on its own:
  coreyhaines31/marketingskills `seo-audit` (MIT).
- Capped fix lists with explicit "not a problem" and "could not check"
  sections: autonnel `landing-page-conversion-audit` (Apache-2.0) and
  firecrawl `firecrawl-seo-audit` (ISC) use similar honesty sections.
- Reporting llms.txt presence with zero weight: agricidaniel/claude-seo
  (MIT).
