# Actor index: apify-company-careers-jobs

Routing table for the two Actors this skill uses. Both are community Actors built and priced by the skill's author (Jordan Belfort). Source: the Actors' READMEs, input schemas and code.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Workday, Greenhouse, Lever (US and EU), Ashby, Workable, SmartRecruiters, Recruitee, Personio | Jobs at named companies, from the company's own ATS feed | `jordan-belfort/ats-jobs-api` | community | $0.001 per job returned (event `job`). Name, domain or careers URL in. `atsSystems` limits name/domain detection. |
| Workday (`*.myworkdayjobs.com`, `myworkdaysite.com`) | Jobs at large employers on Workday | `jordan-belfort/workday-jobs-scraper` | community | $0.001 per job returned. 1,447 companies by name, others by careers URL. |

## Input fields (both Actors)

| Field | What it does |
|-------|--------------|
| `companies` (required) | Careers page URLs, domains or company names |
| `titleKeywords` | Keep jobs whose title contains any of these (case-insensitive) |
| `locationKeywords` | Keep jobs whose location or country contains any of these |
| `remoteOnly` | Only jobs marked remote, or whose location says Remote |
| `postedWithinDays` | Only jobs published in the last N days (0 = all; jobs without a date are kept, except Workday jobs known to be 30+ days old) |
| `onlyNewJobs` | Monitor mode: skip job ids returned by earlier runs |
| `monitorName` | Separate memory per watch list (default `default`) |
| `includeDescription` | Full description as HTML and text (default on) |
| `maxJobsPerCompany` | Cap per company after filters (0 = no cap) |
| `atsSystems` | `ats-jobs-api` only: restrict detection to some of greenhouse, lever, ashby, workable, smartrecruiters, recruitee, personio |

## Output (one row per job)

`company`, `ats`, `boardSlug`, `jobId`, `title`, `department`, `team`, `location`, `allLocations`, `country`, `remote`, `workplaceType`, `employmentType`, `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryInterval`, `salaryText`, `url`, `applyUrl`, `publishedAt`, `updatedAt`, `descriptionText`, `descriptionHtml`, `input`, `scrapedAt`. Fields an ATS does not publish are `null`. A company that cannot be found gives one row with `input` and `error`. Run statistics are in the `STATS` record of the run's key-value store.

## Picking between the two

- Mixed list, or unsure which ATS a company uses: `ats-jobs-api`.
- Only Workday employers: either works. `workday-jobs-scraper` adds "did you mean" suggestions for unknown names, and its monitor memory is a separate store (`workday-jobs-seen`, versus `ats-jobs-seen`).
