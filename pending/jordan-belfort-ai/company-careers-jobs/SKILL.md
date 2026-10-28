---
name: company-careers-jobs
description: "Get the open jobs of specific companies straight from the employer's own applicant tracking system (Workday, Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Recruitee, Personio), looked up by company name, domain or careers-page URL, in one uniform schema, with a monitor mode that returns only newly posted jobs. Routes to jordan-belfort/ats-jobs-api and jordan-belfort/workday-jobs-scraper (1,447 Workday companies by name). Use when someone asks what NVIDIA, Stripe or Notion is hiring for, open roles at a list of companies, new postings since yesterday, hiring signals for sales or recruiting, a Workday, Greenhouse, Lever or Personio jobs API, or to track a company's careers page. Not for market-wide job search on LinkedIn or Indeed. $0.001 per job returned."
author: Jordan Belfort
author_url: https://apify.com/jordan-belfort
metadata:
  category: data-extraction
  openclaw:
    requires:
      bins: [apify]
    primaryEnv: APIFY_TOKEN
    envVars:
      - name: APIFY_TOKEN
        required: false
        description: Apify API token for the pay-per-job Actors ($0.001 per job). Not needed after `apify login`.
  keywords: "company jobs, careers page, ats, workday, greenhouse, lever, ashby, workable, smartrecruiters, recruitee, personio, hiring signals, job monitor, new jobs"
---

# Company Careers Jobs: open jobs from the employer's own ATS

Open jobs for named companies, read from the job feed the company's applicant tracking system (ATS) publishes for its careers page. One row per job, same fields whatever the ATS.

Author: [Jordan Belfort](https://apify.com/jordan-belfort). Routed Actors are built and priced by the author.

## Example prompts

Prompts this skill handles:

- "What is NVIDIA hiring for in Germany? Engineering roles only."
- "Here are 40 company names. Give me their open sales roles that were posted in the last 14 days."
- "Set up a daily watch on Stripe, Notion and Spotify careers pages and send me only the jobs that are new."

Out of scope (the boundary):

- "Find Python jobs in Berlin across the whole market" or anything on LinkedIn or Indeed. This skill needs companies to look up; market-wide search needs a job-board scraper instead.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console -> Settings -> Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Get the companies.** A list of names, domains or careers-page URLs. A careers URL is exact and skips guessing; a name or domain is matched by trying the company's slug on the supported ATSs. If the user has no list, say so: this skill looks companies up, it does not search the whole market.
2. **Pick the Actor** (table below). Default to `jordan-belfort/ats-jobs-api`. Use `jordan-belfort/workday-jobs-scraper` only when every company is a Workday employer.
3. **Build the input** from the user's filters (`titleKeywords`, `locationKeywords`, `remoteOnly`, `postedWithinDays`). Filters run before billing, so jobs they drop are free. Set `maxJobsPerCompany` (for example 50) on a first run, see cost below.
4. **Estimate cost, then run.** Price is $0.001 per job returned; one large Workday employer can return up to 2,000 jobs, about $2. Confirm with the user above a few dollars (see `references/gotchas.md`).
5. **Deliver.** Report how many jobs came back and from how many companies, name the companies that were not found (those rows have an `error` field and cost nothing), and link the dataset. Check the `company` field on name matches: a name can resolve to a different company's board.

For monitoring, set `onlyNewJobs: true` and give each watch list its own `monitorName`. The first run returns every current job (the memory starts empty); later runs return only jobs not seen before. Schedule the run daily with an [Apify schedule](https://docs.apify.com/platform/schedules).

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Jobs at named companies on any of 8 ATSs, by name, domain or URL | `jordan-belfort/ats-jobs-api` | community | Mixed company lists; Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Recruitee, Personio; Workday by name |
| Jobs at Workday employers only | `jordan-belfort/workday-jobs-scraper` | community | Large employers on `*.myworkdayjobs.com`; name lookup with "did you mean" hints |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party). Both Actors are community Actors by the skill's author.

Full table and input fields: [references/actor-index.md](references/actor-index.md).

## Calling Actors: choose your interface

### Option A: Apify CLI (recommended for portability)

    apify actors call "jordan-belfort/ats-jobs-api" \
      -i '{"companies": ["NVIDIA", "https://boards.greenhouse.io/stripe", "notion.so"], "titleKeywords": ["engineer"], "locationKeywords": ["remote", "germany"], "maxJobsPerCompany": 50}' \
      --json \
      --user-agent clawhub/company-careers-jobs \
      2>/dev/null

Daily watch (only new jobs):

    apify actors call "jordan-belfort/ats-jobs-api" \
      -i '{"companies": ["Stripe", "Notion", "Spotify"], "onlyNewJobs": true, "monitorName": "my-watch"}' \
      --json \
      --user-agent clawhub/company-careers-jobs \
      2>/dev/null

Other useful commands:

    # Fetch the input schema
    apify actors info "jordan-belfort/ats-jobs-api" --input --json \
      --user-agent clawhub/company-careers-jobs 2>/dev/null

    # Fetch results of a run
    apify datasets get-items DATASET_ID --format json \
      --user-agent clawhub/company-careers-jobs 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>, documented at <https://docs.apify.com/platform/integrations/mcp>. Per the Actor READMEs, the Actors can be added as tools with `https://mcp.apify.com/?tools=jordan-belfort/ats-jobs-api` and `https://mcp.apify.com/?tools=jordan-belfort/workday-jobs-scraper`.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- A company comes back as one row with `error` and nothing else: no public board was found for that name. Ask for the careers-page URL and retry; such rows are free.
- A company is missing from the output with no `error` row: its board was found, but no job passed the filters. Rerun it without `titleKeywords` or `locationKeywords` to confirm.
- A Workday company is not found by name in `ats-jobs-api`: its Workday board is only matched by exact name or tenant id from the built-in directory. Try `jordan-belfort/workday-jobs-scraper` (it returns a "did you mean" list) or paste the careers URL, for example `https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite`.
- Wrong company returned for a short name: two companies can share a slug. Check the `company` and `boardSlug` fields, or pass the careers-page URL.
- Fewer jobs than the careers page claims: Workday serves at most 2,000 postings per site, so bigger employers return their newest 2,000.
- Employers on iCIMS, Taleo, SuccessFactors or other ATSs are not covered. Say so instead of guessing.
- For cost guardrails and details, see [references/gotchas.md](references/gotchas.md).
