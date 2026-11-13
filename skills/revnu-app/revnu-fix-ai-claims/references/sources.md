# Sources (as of 2026-11-05)

Each platform statement in this skill, with the primary source it rests on.
All fetched on 2026-11-05 unless marked. Re-check before quoting; these pages
change.

## How engines find pages

| Statement | Source |
|---|---|
| Google AI Overviews and AI Mode have no extra requirements beyond being indexed and eligible for a snippet; no special AI text files or markup are needed; they may use "query fan-out" across subtopics; inclusion is never guaranteed | Google Search Central, "AI features and your website": https://developers.google.com/search/docs/appearance/ai-features |
| `OAI-SearchBot` controls appearing in ChatGPT search answers; `GPTBot` is for training; `ChatGPT-User` is user-triggered and not used for search eligibility; robots.txt changes take about 24 hours for search | OpenAI, "Overview of OpenAI crawlers": https://developers.openai.com/api/docs/bots |
| ChatGPT search uses third-party search providers and partner content; publisher feedback address `publishers-feedback@openai.com`; `utm_source=chatgpt.com` on referrals | OpenAI Help Center, "Publishers and Developers FAQ" https://help.openai.com/en/articles/12627856 and "Searching the web with ChatGPT" https://help.openai.com/en/articles/9237897. **Unverified directly:** both returned HTTP 403 to our fetcher on 2026-11-05; the content comes from search-engine snippets of those pages. Not stated as fact in SKILL.md for that reason. |
| `PerplexityBot` surfaces sites in Perplexity search and isn't used for foundation-model training; `Perplexity-User` handles user-requested fetches and generally ignores robots.txt | Perplexity, "Perplexity Crawlers": https://docs.perplexity.ai/guides/bots |
| Bing Webmaster Tools "AI Performance" (public preview since 2026-02-10) shows citations of your pages in Microsoft Copilot, Bing AI summaries and some partner integrations, with sampled grounding queries | Bing Webmaster Blog: https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview |

## Collecting answers by API

| Statement | Source |
|---|---|
| OpenAI API web search tool returns `url_citation` annotations with URL and title; the docs don't say it matches ChatGPT's consumer search | https://developers.openai.com/api/docs/guides/tools-web-search |
| Gemini API Grounding with Google Search returns URL citations for the grounded spans and the queries it ran | https://aistudio.google.com/docs/google-search (redirected from ai.google.dev/gemini-api/docs/google-search) |
| Perplexity offers an API (Sonar) that returns cited answers | https://docs.perplexity.ai/getting-started/overview (index page only checked for HTTP 200) |

## Fixing own pages

| Statement | Source |
|---|---|
| Organization structured data helps Google disambiguate the organization and pick the logo; no properties are required; place it on the home or about page; `sameAs`, `alternateName`, `legalName`, `foundingDate` etc. are recommended | https://developers.google.com/search/docs/appearance/structured-data/organization |
| Google processes structured data present in the rendered DOM, including JSON-LD added by JavaScript (with caveats for Product markup) | https://developers.google.com/search/docs/appearance/structured-data/generate-structured-data-with-javascript |
| Recrawl: URL Inspection for a few URLs (quota applies) or a sitemap; crawling can take a few days to a few weeks; no guarantee | https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl |
| Redirects and canonicals for retired or duplicate pages | https://developers.google.com/search/docs/crawling-indexing/301-redirects , https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls |
| IndexNow notifies participating engines (Bing, Yandex, Naver, Seznam, Yep, Amazon) of added, changed or deleted URLs; no guarantee of indexing | https://www.indexnow.org/faq |

Not claimed anywhere in this skill: that any AI crawler other than Google
renders JavaScript (not documented in the sources above), and that llms.txt
affects citations (Google's AI features page says such files aren't needed).

## Profiles

| Statement | Source |
|---|---|
| G2 profiles are free to claim; vendors edit description, pricing and screenshots, request changes for locked fields, and can't edit reviews; names should match the website | https://sell.g2.com/claim-your-profile , https://documentation.g2.com/docs/product-information (via search results; product-information page reported as updated in late Oct 2026) |
| Google Business Profile owners edit their info; Google reviews changes before they go live; others can suggest edits | https://support.google.com/business/answer/3039617 |
| Knowledge panels can be claimed by the entity; corrections go through Feedback with links; anyone can send feedback, verified users get priority | https://support.google.com/knowledgepanel/answer/7534902 |

## Third-party and community rules

| Statement | Source |
|---|---|
| Wikipedia: people with a conflict of interest (owners, employees, paid editors) are strongly discouraged from editing affected articles; disclose and use talk-page edit requests (`{{edit COI}}`); editors may decline | https://en.wikipedia.org/wiki/Wikipedia:Conflict_of_interest , https://en.wikipedia.org/wiki/Wikipedia:Edit_requests |
| Wikidata: creating items about yourself or your organization is strongly discouraged (an essay; Wikidata has no adopted COI policy); notability needs independent reliable sources; on existing items, correct clear factual errors and request other changes | https://www.wikidata.org/wiki/Wikidata:Self-promotion |
| Reddit: participate authentically, no spam or content manipulation; don't mislead others or impersonate an entity | Reddit Rules 2 and 5: https://redditinc.com/policies/reddit-rules |
| FTC: employees and co-owners must disclose the relationship when endorsing their company's products, including on forums and review sites | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking |

## Credits

- Splitting answers into single claims and tracing each to its source page is
  an idea also found in Corey Haines' `ai-seo` skill (answer accuracy
  reference, MIT), which credits Profound's research. This skill uses its own
  categories, wording and steps.
