# Gotchas: apify-company-careers-jobs

Cost guardrails, error recovery and pitfalls for `jordan-belfort/ats-jobs-api` and `jordan-belfort/workday-jobs-scraper`.

## Cost guardrails

Both Actors are pay per event: $0.001 per job returned, per their READMEs. Not charged: run start, jobs dropped by your filters, companies that were not found, and (monitor mode) jobs you have already seen.

| Run | Rough cost |
|-----|-----------|
| 100 jobs | around $0.10 |
| One large Workday employer, newest 2,000 jobs | around $2 |
| 50 companies, no filters | depends on the boards; a first run with `maxJobsPerCompany` set gives a real number |

### Confirmation thresholds (suggested)

- Estimated cost above $5: warn the user.
- Estimated cost above $20: require explicit confirmation before running.
- Always present cost as a rough estimate.
- Set `maxJobsPerCompany` on a first run. Through the API its default is 0 (no cap).

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Row with `error`: "No job board with open jobs found for ..." | Name or domain matched no board on the supported ATSs | Paste the careers-page URL |
| Row with `error`: "'X' is not in the Workday company directory. Did you mean ..." | `workday-jobs-scraper` does not know that name | Use a suggestion, or paste the careers URL |
| Right company, zero jobs | Board exists but has no open jobs, or filters dropped everything | Loosen `titleKeywords` / `locationKeywords` |
| Wrong company's jobs | Two companies share a slug | Check `company` and `boardSlug`; pass the careers URL |
| Monitor run returns nothing | Nothing new since the last run with the same `monitorName` | Expected; a new `monitorName` returns everything again |

## Actor-specific notes

### `jordan-belfort/ats-jobs-api`

- A bare name or domain is checked against the built-in Workday directory first (exact name or tenant id only); if it matches, the Workday board is used and the other ATSs are not tried. If `atsSystems` is set, this Workday-by-name lookup is skipped.
- Otherwise it tries the company's slug on the seven non-Workday systems and keeps boards whose company name matches the slug.
- Workday companies outside the directory need the careers URL.
- Lever boards are read from the US API and the EU API.
- Salary fields are filled only where the ATS publishes them.

### `jordan-belfort/workday-jobs-scraper`

- Workday serves at most 2,000 postings per site; bigger employers return their newest 2,000.
- Workday's list only says "Posted 30+ Days Ago" for older jobs; the exact date comes from the job's detail page, which is fetched only for jobs that pass your filters.
- It reads the careers site's public JSON, at most 4 requests at a time per site, and only where the site's robots.txt allows it.
