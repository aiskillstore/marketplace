---
name: metix-company-search
description: Use when building organization lists on Metix AI or retrieving company records for account research, market mapping, funding and headcount filters, or connecting company data to people and job signals.
---

# Metix AI company search

Search returns `company_ids`. Detail returns the records. Field names, operators,
and enumerations come from the live contract and the docs pages below, not from
this file.

## Resources

```
API     https://mira-api.metix.ai
        GET /version            deployed version and contract hash (free)
        GET /contract           field names, operators, limits (free, no key needed)
        GET /auth/key/status    key state and remaining API Credits (free)
        GET /docs               tutorial catalog; add .md to any page for Markdown
        /mcp                    MCP endpoint, same key

Docs    https://mira-api.metix.ai/docs/api/companies.md
        https://mira-api.metix.ai/docs/api/jobs.md
        https://mira-api.metix.ai/docs/api/people.md
        https://mira-api.metix.ai/docs/api/contact.md
        https://mira-api.metix.ai/docs/api/query-spec.md
        https://mira-api.metix.ai/docs/reference/errors.md
        https://mira-api.metix.ai/docs/credits.md
        https://platform.metix.ai/llms.txt
```

The same pages are rendered for people at `https://platform.metix.ai/docs`.

## How to call

1. `GET /contract` (or MCP `metix_get_contract`). Build `where` only from
   `querySpecByEntity.company`. The field list is closed; a name outside it is
   refused. Use the operators `fieldOperators` lists for each field: exact
   fields such as `type` take `eq` or `in` with a value from the companies
   page, ordered fields such as `size` also take `gte`, `gt`, `lte` and `lt` by
   position in their value list, and `match` is only for free-text fields such
   as `industry`.
2. `POST /v1/companies/query`, then `POST /entity/v1/companies/detail-by-id`
   with up to 100 of those IDs. Search never returns records.
3. On a 4xx, switch on `error_code`; `msg` says what to change. For the full
   explanation, fetch `docs_url` with `.md` added to the path:
   `https://platform.metix.ai/docs/reference/errors#query-refusals` becomes
   `https://platform.metix.ai/docs/reference/errors.md`, and `query-refusals`
   names the section to read.
4. If this file and the live contract disagree, the contract wins.

## A first call

```bash
curl -s https://mira-api.metix.ai/v1/companies/query \
  -H "Authorization: Bearer $METIX_KEY" -H "Content-Type: application/json" \
  -d '{"where": {"all": [
        {"field": "industry", "match": "biotechnology"},
        {"field": "size", "gte": "51-200"}]},
       "size": 25}'
# data.company_ids, data.total, and data.next while more pages remain

curl -s https://mira-api.metix.ai/entity/v1/companies/detail-by-id \
  -H "Authorization: Bearer $METIX_KEY" -H "Content-Type: application/json" \
  -d '{"company_ids": ["<an id from data.company_ids>"],
       "_source": ["id", "name", "industry", "size", "headquarters.country"]}'
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
