# Sitemap and robots.txt: what each verdict actually proves

> Part of the ai-crawler-readiness skill. Back to https://visdenda.com/skills/ai-crawler-readiness/SKILL.md.
> Read this when the task matches: Read sitemap and robots results as two axes — structure and policy — and know which tool answers which.

## Three questions, one entry

- `visdenda_audit_site` with `focus=sitemap` — structure: XML validity, entry counts, the
  50,000-URL per-file limit and sitemap-index children. A normal page URL checks
  `/sitemap.xml` on its origin; a URL ending in `.xml` or `.xml.gz` is used as given.
- The same tool with `focus=robots` — syntax and the declared `Sitemap:` pointers. It
  does not judge per-bot access.
- `visdenda_check_crawler_access` — policy per bot: allow or blocked, the deciding rule
  and `crawl-delay`, from one fetch. With exactly one crawler, `probe: true` also fetches
  the page as that agent.

## Two axes, never one verdict

"robots.txt is valid" and "GPTBot is allowed" are different statements. A syntactically
perfect file that disallows an AI bot is correct syntax and a deliberate policy; report
both, then ask whether that policy is what the owner wants.

- A broken `Sitemap:` pointer is a robots defect even when the sitemap is valid at some
  other URL.
- A sitemap that parses is not an indexed sitemap. You proved structure, not Google's
  fetch, parse or selection. Do not upgrade the claim.
- `na` is not a pass. Say what was not applicable and why: no sitemap declared, no
  robots.txt, a non-XML response.
- If an index has more children than were checked, say so; a truncated check is not a
  clean result.
- `User-agent: *` with `Disallow: /` blocks search crawlers too. Do not report it as an
  "AI crawler problem" when it is a site-wide block.

## Report

Name the file or sitemap checked, the verdict, the exact failing directive or XML error,
and the one change. Re-run the same call after the fix; a different check is not
verification.
