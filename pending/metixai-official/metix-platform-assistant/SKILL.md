---
name: metix-platform-assistant
description: Use when a task needs Metix AI data across more than one area (people, companies, or jobs) and you must decide which capability to call, in what order, and what it costs. Start here when the request is a goal rather than a single lookup.
---

# Metix AI platform assistant

Coordinates work across people, companies, and jobs. Use the focused skills for
a single dataset. Field names and prices come from the live contract and the
docs pages below, not from this file.

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

1. `GET /contract` (or MCP `metix_get_contract`). Build each `where` from
   `querySpecByEntity` for that dataset. The field lists are closed. Use the
   operators `fieldOperators` lists for each field: exact fields take `eq` or
   `in` with a whole value, and `match` is only for free-text fields.
2. Search returns IDs only. Detail returns records, up to 100 IDs at a time.
   Chain on IDs, not on names: ask for `company.id` in `_source` on a job
   detail call, and a profile's `experience.company.id` is the same kind of
   company token. Both resolve at `/entity/v1/companies/detail-by-id`.
3. On a 4xx, switch on `error_code`; `msg` says what to change. For the full
   explanation, fetch `docs_url` with `.md` added to the path:
   `https://platform.metix.ai/docs/reference/errors#query-refusals` becomes
   `https://platform.metix.ai/docs/reference/errors.md`, and `query-refusals`
   names the section to read.
4. If this file and the live contract disagree, the contract wins.

Typical cross-dataset sequence for "senior engineers at companies hiring for ML
platform roles": jobs query, job detail with `company.id` in `_source`, company
detail on those tokens, people query on those employers, profile detail on the
shortlist. Narrow before the last step; that is where API Credits concentrate.

## A first chain

A job's employer, by token rather than by name:

```bash
curl -s https://mira-api.metix.ai/entity/v1/jobs/detail-by-id \
  -H "Authorization: Bearer $METIX_KEY" -H "Content-Type: application/json" \
  -d '{"job_ids": ["<an id from /v1/jobs/query>"], "_source": ["title", "company.id"]}'

curl -s https://mira-api.metix.ai/entity/v1/companies/detail-by-id \
  -H "Authorization: Bearer $METIX_KEY" -H "Content-Type: application/json" \
  -d '{"company_ids": ["<company.id from the job record>"]}'
```

The three Query Spec search routes take `{"where": ..., "size": 25}`; the focused
skills show one for each dataset. `/v1/people-search` is the exception: it takes
`{"text": ..., "size": 25}` and refuses `where` outright, because it reads a
plain-language brief rather than a filter.

## Local rules

Every call reads `METIX_KEY` from the environment. If it is unset, stop and tell
the user to set it. Do not substitute another variable, and do not search the
machine for a lookalike key.

Never print the key, write it into a file, or include it in a summary.

Contact details are callable: `POST /v1/contact/unlock` takes people you have
already found and returns a personal email, a work email or a phone number.
Sequence it last, after search and detail have narrowed the list, because it
is charged per value returned rather than in result bands and is the most
expensive call on the API. `POST /v1/contact/probe` says who has one before
you buy, at search prices. Unlock takes at most 25 people and probe at most 50.
Unlock needs an account that has paid, an active plan or a purchased top-up;
signup API Credits are refused with a 403 that covers every kind, phone and email
alike. It also reserves the worst case before it looks anything up, the sum of
the requested rates times the number of people, so quote that figure and not
the expected spend. Both routes have MCP tools, `metix_probe_contacts` and
`metix_unlock_contacts`; unlock over MCP needs a connection granted the
`contact:unlock` scope, so a refusal there is about the grant, not the route.

This API retrieves data. It does not score or rank a person against a role.
Retrieve the records and reason over them; do not guess at a scoring path.

API Credits are charged in result bands. One ID per request is the expensive way to
walk a set; batch. The formulas live on `/docs/credits.md`. Check
`GET /auth/key/status` (free) before a run that will pull thousands of records.
