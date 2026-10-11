---
name: ball-ranks
description: Get published Ball Ranks fantasy basketball and football rankings and player projections through its read-only MCP server or REST API. Use for draft boards, player comparisons, and football weekly start/sit questions grounded in Ball Ranks data.
---

# Ball Ranks

Use Ball Ranks rankings and projections to answer fantasy basketball (NBA) and football (NFL) questions with current published numbers and a source link.

## Connect

Prefer the Ball Ranks MCP tools when connected. The Streamable HTTP server is `https://ballranks.com/api/mcp`. Use a standard MCP client to initialize the connection and discover its tools; plain GET requests do not call MCP tools.

If MCP is unavailable, make read-only REST requests to `https://ballranks.com`. Consult the live [OpenAPI schema](https://ballranks.com/openapi.json) for full field definitions and [developer documentation](https://ballranks.com/developers) for current access limits.

Anonymous access uses Model Zero (`model=v0`, the default). If the user supplies a Ball Ranks API key, send `Authorization: Bearer <key>` on requests to Ball Ranks only. Keys come from [Account](https://ballranks.com/account); keep them out of URLs, logs, answers, and committed files. Model One (`model=v1`) requires a key belonging to a Premium account. Use it only when requested and authorized.

## Choose the request

| Need | MCP tool | REST GET path |
| --- | --- | --- |
| Season board, either sport | `get_season_rankings` | `/api/v1/rankings/season` |
| One player's season rank | `get_player_rankings` | `/api/v1/players/{player}/rankings` |
| One player's projection | `get_player_projections` | `/api/v1/players/{player}/projections` |
| Football weekly position board | `get_week_rankings` | `/api/v1/rankings/weekly` |

- Set `sport` to `basketball` or `football`. Use the user's sport; clarify if it is ambiguous.
- Omit `season` for the current published season. Explicit season requests must match a currently published season.
- Football uses `scoring_format=standard`, `half_ppr`, or `ppr` (default). Ask for the scoring format when a comparison depends on it; otherwise identify the PPR default in the answer.
- Basketball season rankings use nine-category per-game scoring. Omit `scoring_format`. Read the returned scoring and mode before comparing ranks.
- Weekly scopes apply to football. Weekly boards require `week` (1–18) and accept `position`: `QB`, `RB`, `WR`, `TE`, `K`, or `DST` (default `RB`). Specify the relevant position explicitly.
- Player projections default to `scope=season`; football weekly projections need `scope=weekly` and `week`.
- Use a known Ball Ranks player ID or slug. In MCP pass it as `player`; in REST URL-encode it in the path. Board results can supply player IDs and, when present, slugs.
- Lists accept `limit` (1–100, default 50) and `offset` (0–10,000, default 0). Fetch the smallest useful page; paginate only when the task needs more results.

## Examples

For a basketball draft board, call `get_season_rankings` with:

```json
{"sport":"basketball","model":"v0","limit":10}
```

Equivalent REST request:

```sh
curl --get 'https://ballranks.com/api/v1/rankings/season' \
  --data-urlencode 'sport=basketball' --data-urlencode 'limit=10'
```

For a week 4 half-PPR wide receiver comparison, call `get_week_rankings` with:

```json
{"sport":"football","week":4,"position":"WR","scoring_format":"half_ppr","model":"v0","limit":20}
```

For one player's season numbers, call `get_player_projections` with:

```json
{"sport":"basketball","player":"victor-wembanyama","scope":"season","model":"v0"}
```

For a football player's weekly projection, use a known ID or slug from the returned season board with `sport=football`, `scope=weekly`, `week`, and the user's `scoring_format`.

## Use the response

MCP results include structured data and a JSON text representation; REST returns JSON. Check MCP `isError` as well as transport status before using a result.

Report the returned rank, projected points or basketball stat projection relevant to the question. Keep overall season rank, position rank, and weekly rank distinct; lower ranks are better. Compare players within the same sport, model, season, scope, and football scoring format.

Cite the returned `sourceUrl`. Identify Model Zero or Model One from `meta.model`; include the season and week where applicable. Use `meta.generatedAt` or `meta.updatedAt` to explain freshness when relevant. Treat `meta.modelDataVersion` as a version identifier, and keep null values distinct from zero. Rankings and projections support advice; label your own recommendation or calculation clearly.

## Limits and errors

Current documented allowances: anonymous access 10 requests/day per originating IP; Free keys 8/minute and 80/day; Premium keys 60/minute and 1,000/day. REST and MCP share access limits. An additional IP guard applies before authentication. Prefer one ranking board over repeated player lookups when it answers the task.

| Response | Action |
| --- | --- |
| `400 invalid_request` | Correct fields using the live schema. |
| `401 unauthorized` | Ask the user to replace or revoke an invalid key; never expose it. |
| `403 premium_required` | Explain the account requirement; use Model Zero only if the user accepts it. |
| `404 not_found` or unavailable published data | Verify player identity or requested week once; say when no data is returned. |
| `422 unsupported_combination` | Correct sport, scoring, scope, or season; explain supported choices. |
| `429` | Honor `Retry-After` and `X-RateLimit-Remaining`; stop repeated calls when the daily quota is reached. |
| `503` | Respect `Retry-After` and report temporary unavailability; retry only if appropriate to the user's task. |

MCP can return tool errors inside a successful transport response, and rate-limit failures in a JSON-RPC error envelope. Read those errors rather than inventing rankings or projections.
