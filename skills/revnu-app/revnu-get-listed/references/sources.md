# Sources (as of 2026-11-05)

Platform and policy statements in this skill, with their primary sources.
Fetched on 2026-11-05 unless marked. Re-check before quoting.

## How AI answers pick pages

| Statement | Source |
|---|---|
| Google AI Overviews and AI Mode may use "query fan-out" (several related searches) and draw on pages eligible for Search with a snippet; no special files or markup are needed; inclusion isn't guaranteed | https://developers.google.com/search/docs/appearance/ai-features |
| Microsoft Copilot Chat turns a prompt into a short search query sent to the Bing search service and composes the answer from the results | https://learn.microsoft.com/en-us/copilot/plan/privacy-and-protections , https://learn.microsoft.com/en-us/microsoft-365/copilot/enterprise-data-protection (via search results) |
| Bing Webmaster Tools' AI Performance report (public preview, 2026-02-10) counts citations of a site's pages in Microsoft Copilot, Bing AI summaries and some partner integrations | https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview |
| OpenAI API web search tool returns `url_citation` annotations; the docs don't say it matches ChatGPT's consumer search | https://developers.openai.com/api/docs/guides/tools-web-search |
| Gemini API Grounding with Google Search returns URL citations and the queries it ran | https://aistudio.google.com/docs/google-search |
| ChatGPT search uses third-party search providers plus partner content | OpenAI Help Center https://help.openai.com/en/articles/9237897 . **Unverified directly:** HTTP 403 to our fetcher; content seen only in search snippets. SKILL.md doesn't rely on it. |

Not claimed: that any listing type gets cited by any engine at a known rate.
The skill measures that per category instead (Steps 1-2).

## Links and payment

| Statement | Source |
|---|---|
| Buying or selling links that pass ranking credit (money, goods, services, or a free product in exchange for a link) is link spam; paid links are fine with `rel="sponsored"` or `rel="nofollow"` | Google spam policies: https://developers.google.com/search/docs/essentials/spam-policies ; qualifying outbound links: https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links |

## Reviews and disclosure (US)

| Statement | Source |
|---|---|
| FTC rule (16 CFR Part 465, in force 2024-10-21) bans fake reviews, incentives conditioned on positive or negative sentiment, undisclosed insider reviews by officers and managers, company-controlled "independent" review sites, and review suppression | FTC final rule press release https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials ; Federal Register https://www.federalregister.gov/documents/2024/08/22/2024-18519 (via search results) |
| Generalized requests to all purchasers are allowed; incentives not tied to sentiment aren't banned by the rule; asking only happy customers could still violate the FTC Act; insider reviews need clear disclosure in the review itself | FTC Q&A: https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers |
| Employees and co-owners endorsing their company's products, including on forums and review sites, must disclose the relationship; a profile listing the employer isn't enough | FTC Endorsement Guides FAQ: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking |

Outside the US, local consumer-protection rules apply; this skill doesn't
summarize them.

## Communities

| Statement | Source |
|---|---|
| Reddit: participate authentically, no spam or content manipulation (Rule 2); don't mislead others or impersonate an entity (Rule 5); follow each community's rules | https://redditinc.com/policies/reddit-rules (fetched with curl; the WebFetch tool was blocked) |
| Hacker News: don't use HN primarily for promotion; don't solicit upvotes, comments or submissions | https://news.ycombinator.com/newsguidelines.html |
| Wikipedia: owners, employees and paid editors are strongly discouraged from editing articles about their company; use disclosed talk-page edit requests | https://en.wikipedia.org/wiki/Wikipedia:Conflict_of_interest |

## Lists and directories

| Statement | Source |
|---|---|
| Example of list gates: the main sindresorhus/awesome index requires lists to be at least 30 days old, rejects fully AI-generated PRs and asks contributors to review other open PRs | https://github.com/sindresorhus/awesome/blob/main/pull_request_template.md |
| G2: free to claim a profile; claims reviewed in 1-3 business days; B2C and alpha/beta products aren't accepted; vendors can't edit reviews | https://sell.g2.com/claim-your-profile , https://documentation.g2.com/help/docs/finding-or-listing-a-product-on-g2 (via search results) |

Gates on other lists (star minimums, "no SaaS", "no AI-submitted PRs") vary and
change; the skill reads each list's CONTRIBUTING and PR template at run time
instead of hard-coding them.

## Credits

- Corey Haines' `directory-submissions` skill (coreyhaines31/marketingskills,
  MIT) covers directory launches, positioning per directory type and checking
  live backlinks. This skill takes a different starting point (pages actually
  cited for the buyer's questions, read rules first) and its own wording.
