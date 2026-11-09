---
name: metix-people-search
description: Use when finding professional profiles on Metix AI by role, skills, employer, education, location, or seniority, when a profile search needs natural language, when retrieving the full profile records behind the ids, and when a search returns too many, too few, or the wrong people.
---

# Metix AI people search

Search returns `profile_ids`. Detail returns the records. Prefer the structured
Query Spec route: it is exact, repeatable, and has no base charge. Use natural
language only when the constraints resist being written as fields; it adds a
5 API Credit base. Field names, operators, and scopes come from the live contract
and the docs pages below, not from this file.

## Resources

```
API     https://mira-api.metix.ai
        GET /version            deployed version and contract hash (free)
        GET /contract           field names, operators, limits (free, no key needed)
        GET /auth/key/status    key state and remaining API Credits (free)
        GET /docs               tutorial catalog; add .md to any page for Markdown
        /mcp                    MCP endpoint, same key

Docs    https://mira-api.metix.ai/docs/api/people.md
        https://mira-api.metix.ai/docs/api/contact.md
        https://mira-api.metix.ai/docs/api/jobs.md
        https://mira-api.metix.ai/docs/api/companies.md
        https://mira-api.metix.ai/docs/api/query-spec.md
        https://mira-api.metix.ai/docs/reference/errors.md
        https://mira-api.metix.ai/docs/credits.md
        https://platform.metix.ai/llms.txt
```

The same pages are rendered for people at `https://platform.metix.ai/docs`.

## How to call

1. `GET /contract` (or MCP `metix_get_contract`). Build `where` only from
   `querySpecByEntity.profile`. The field list is closed; a name outside it is
   refused. Use the operators `fieldOperators` lists for each field: exact
   fields such as `experience.function`, `experience.seniority` or
   `location.country` take `eq` or `in` with a whole value from the people
   page, and `match` is only for free-text fields.
2. `POST /v1/people/query` for a structured tree, or `POST /v1/people-search`
   with `text` (not `query`) when the constraints will not sit on fields. Then
   `POST /entity/v1/profiles/detail-by-id` with up to 100 of those IDs. Search
   never returns records.
3. On a 4xx, switch on `error_code`; `msg` says what to change. For the full
   explanation, fetch `docs_url` with `.md` added to the path:
   `https://platform.metix.ai/docs/reference/errors#query-refusals` becomes
   `https://platform.metix.ai/docs/reference/errors.md`, and `query-refusals`
   names the section to read.
4. If this file and the live contract disagree, the contract wins.

## A first call

Search, then read the records. `location.country` is an exact field: it takes
the whole country name with `eq` or `in`, and refuses `match`.

```bash
curl -s https://mira-api.metix.ai/v1/people/query \
  -H "Authorization: Bearer $METIX_KEY" -H "Content-Type: application/json" \
  -d '{"where": {"all": [
        {"field": "current_title", "match": "data engineer"},
        {"field": "location.country", "eq": "United States"}]},
       "size": 25}'
# data.profile_ids, data.total, and data.next while more pages remain

curl -s https://mira-api.metix.ai/entity/v1/profiles/detail-by-id \
  -H "Authorization: Bearer $METIX_KEY" -H "Content-Type: application/json" \
  -d '{"profile_ids": ["<an id from data.profile_ids>"],
       "_source": ["profile_id", "full_name", "current_title", "location.country"]}'
```

For the next page, send `data.next` back as `after` with the same `where`.
`POST /v1/people-search` takes `text` and `size` only, and returns
`profile_ids` with no `total` and no `next`.

## Getting better results

Patterns that tend to help. Use whichever fit the request.

- **Put the requirements in `where`, and keep preferences out.** Every leaf has
  to hold, so a preference such as "ideally" or "a plus" written into the tree
  removes people the user may want. Search on what is required and weigh the
  preferences when reading the records. Alternatives ("Python or Java") are one
  `any`.
- **Write values the way records store them.** A country is its English name
  with `eq` (`"United States"`), a state its full name. Seniority fields take
  `eq` or `in` with labels from `closedValues`; they have no `gte`. "5+ years" is
  `total_experience_months` `gte` 60. `education.degree` is ordered, so `gte`
  works there.
- **Check which titles people use.** A title from a job description can be rare
  on profiles. Count a few spellings with `size: 1` and compare `total`, or read
  `current_title` on a few records.
- **Keep one job's conditions in one scope.** Conditions inside one
  `has_experience` match the same job; separate leaves can match different jobs.
- **Count before pulling records.** `size: 1` returns `total`, exact below
  100000, and an empty search is free. A very large total usually means a
  requirement is missing; a near-zero one usually means a spelling or value does
  not match what is stored.
- **With too few results, change one thing at a time**: another title first,
  then the least important requirement, then a wider location. Comparing the
  counts shows which condition was narrowing the search.
- **Read only what you need.** Name the fields in `_source` on detail.
  `headline`, `summary` and `experience.description` are left out of the
  default record and are there on request.

Backend engineers in the United States with five or more years, currently at a
financial services company, counted first:

```json
{"where": {"all": [
  {"field": "current_title", "match": "backend engineer"},
  {"field": "location.country", "eq": "United States"},
  {"field": "total_experience_months", "gte": 60},
  {"has_experience": {"all": [
    {"field": "experience.company.industry", "eq": "Financial Services"},
    {"field": "experience.is_current", "eq": true}]}}
]}, "size": 1}
```

## Local rules

Every call reads `METIX_KEY` from the environment. If it is unset, stop and tell
the user to set it. Do not substitute another variable, and do not search the
machine for a lookalike key.

Never print the key, write it into a file, or include it in a summary.

Contact details live on `POST /v1/contact/unlock`, for people you already
found. It is charged per value returned rather than in bands, at the largest
per-call rates on the API, so narrow the list first. `POST /v1/contact/probe`
reports who has a value before you buy and is priced like a search. Unlock
takes at most 25 people per call and probe at most 50, so split a longer list.
Unlock needs an account that has paid: an active plan or a purchased top-up.
Signup API Credits are refused with a 403, and that refusal covers every kind, so a
403 on an email unlock is about payment and never about phone. Unlock also
reserves the worst case up front, the sum of the requested rates times the
number of people, whatever the hit rate turns out to be, so tell the user that
figure before the call. Both routes have MCP tools, `metix_probe_contacts` and
`metix_unlock_contacts`, so an MCP session does not have to drop to raw HTTP for
them. Unlock over MCP needs a connection granted the `contact:unlock` scope.
Do not invent any other contact route.

API Credits are charged in result bands. One ID per request is the expensive way to
walk a set; batch. The formulas live on `/docs/credits.md`. Natural-language
people search keeps a 5 API Credit base even when it returns no IDs.
