---
name: metix-job-search
description: Use when analysing active job postings on Metix AI (hiring demand by role, function, company, location, salary, or seniority) and when retrieving full posting records.
---

# Metix AI job search

Search returns `job_ids`. Detail returns the postings. Field names, operators,
and salary rules come from the live contract and the docs pages below, not from
this file.

## Resources

```
API     https://mira-api.metix.ai
        GET /version            deployed version and contract hash (free)
        GET /contract           field names, operators, limits (free, no key needed)
        GET /auth/key/status    key state and remaining API Credits (free)
        GET /docs               tutorial catalog; add .md to any page for Markdown
        /mcp                    MCP endpoint, same key

Docs    https://mira-api.metix.ai/docs/api/jobs.md
        https://mira-api.metix.ai/docs/api/people.md
        https://mira-api.metix.ai/docs/api/contact.md
        https://mira-api.metix.ai/docs/api/companies.md
        https://mira-api.metix.ai/docs/api/query-spec.md
        https://mira-api.metix.ai/docs/reference/errors.md
        https://mira-api.metix.ai/docs/credits.md
        https://platform.metix.ai/llms.txt
```

The same pages are rendered for people at `https://platform.metix.ai/docs`.

## How to call

1. `GET /contract` (or MCP `metix_get_contract`). Build `where` only from
   `querySpecByEntity.job`. The field list is closed; a name outside it is
   refused. Use the operators `fieldOperators` lists for each field: exact
   fields such as `salary.currency` or `salary.period` take `eq` or `in`, and
   `match` is only for free-text fields such as `title`. A salary comparison
   (`gte`, `gt`, `lte` or `lt` on `salary.annual_min` or `salary.annual_max`)
   needs `salary.currency` with `eq` or `in` in the same `all`.
2. `POST /v1/jobs/query` returns `job_ids`, and a `next` cursor to send back as
   `after` when there are more. `POST /entity/v1/jobs/detail-by-id` with up to
   100 of those IDs returns the postings. Search never returns records.
3. On a 4xx, switch on `error_code`; `msg` says what to change. For the full
   explanation, fetch `docs_url` with `.md` added to the path:
   `https://platform.metix.ai/docs/reference/errors#query-refusals` becomes
   `https://platform.metix.ai/docs/reference/errors.md`, and `query-refusals`
   names the section to read.
4. If this file and the live contract disagree, the contract wins.

To reach the employer, add `company.id` to `_source` on the detail call and send
it to `/entity/v1/companies/detail-by-id`. `_source` returns exactly the fields
you list, so list the others you need as well. Do not search for the employer by
name.

## A first call

```bash
curl -s https://mira-api.metix.ai/v1/jobs/query \
  -H "Authorization: Bearer $METIX_KEY" -H "Content-Type: application/json" \
  -d '{"where": {"all": [
        {"field": "title", "match": "data engineer"},
        {"field": "posted_date", "gte": "now-30d"}]},
       "size": 25}'
# data.job_ids, data.total, and data.next while more pages remain

curl -s https://mira-api.metix.ai/entity/v1/jobs/detail-by-id \
  -H "Authorization: Bearer $METIX_KEY" -H "Content-Type: application/json" \
  -d '{"job_ids": ["<an id from data.job_ids>"],
       "_source": ["id", "title", "posted_date", "company.id", "company.name"]}'
```

For the next page, send `data.next` back as `after` with the same `where`.

## Local rules

Every call reads `METIX_KEY` from the environment. If it is unset, stop and tell
the user to set it. Do not substitute another variable, and do not search the
machine for a lookalike key.

Never print the key, write it into a file, or include it in a summary.

Contact details are a people capability: `POST /v1/contact/unlock`, through
`metix-people-search`. If a user asks for an email or a phone number, send
them there rather than inventing a route here.

API Credits are charged in result bands. One ID per request is the expensive way to
walk a set; batch. The formulas live on `/docs/credits.md`.
