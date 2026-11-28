# Page signals and changes over time

> Part of the ai-crawler-readiness skill. Back to https://visdenda.com/skills/ai-crawler-readiness/SKILL.md.
> Read this when the task matches: Choose between focused signals and a full scan, then prove whether a fix actually changed the verdict.

## Pick the cheap focus first

- `visdenda_audit_site` with `focus=signals` — one URL, five focused signals: canonical,
  noindex, meta preview, hreflang and structured data. One request, no report, no scan
  quota: use it for repeated checks while fixing something.
- The same tool with `focus=full` (the default) — 20+ checks in one pass, a grade, every
  failing/warning finding with its fix, and a seven-day report link. Pass `updateId` to
  attach one public radar update's checks. It consumes one of the three daily scans, so do
  not re-scan after a one-line change; re-check the specific signal instead.

## Compare, do not remember

- Every full audit returns a `scanId`. Pass `compareTo` with the previous id to get
  added, resolved and persisting findings plus the score delta. The baseline must be the
  same URL; expired or unknown ids return an error without consuming a scan.
- This is how you answer "did my fix work?" without an account. A lower score with fewer
  failures is possible: read the added and resolved lists, not only the number.

## Reading a signal

- A canonical pointing at another URL is not automatically wrong: consolidation is a
  legitimate choice. Say which URL wins and whether that matches intent.
- Noindex can arrive two ways: a meta-robots tag in the HTML, or an `X-Robots-Tag`
  response header. Both are checked here, and they can disagree across URLs; report which
  one you observed and on which URL, not just "noindex: yes".
- Hreflang tags alone do not prove a correct cluster; reciprocity and `x-default` matter.
- JSON-LD presence is not rich-result eligibility. Report the type found, not a promise.
- Findings filtered by `updateId` are a subset. No finding under a filter is not a clean
  site.

## Report

Page, signal, verdict, evidence, one change, and the exact call that would verify it.
Never turn "a check failed" into "traffic dropped".
