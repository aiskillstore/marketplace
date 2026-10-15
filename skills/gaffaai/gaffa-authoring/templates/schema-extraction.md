# Template: structured extraction (/v1/schemas and inline parse_json)

`/v1/schemas` stores a reusable structured-extraction shape that a browser request references by `data_schema_id`.
The endpoint is reached with a normal API key.
The extraction cost comes from the token-priced `parse_json` action that uses the schema, so warn the developer that the per-call cost is token-based rather than deterministic.

Two-step flow.
Create or update a schema, then reference it from a browser request.
Confirm the exact request and response shape against the live docs before emitting final code, because the schema body format can change.

## Create a schema

```bash
curl -sS -X POST https://api.gaffa.dev/v1/schemas \
  -H "X-API-Key: ${GAFFA_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: gaffa-skill/1.0" \
  -d '{
    "name": "product",
    "description": "Extract product details",
    "fields": [
      { "type": "string", "name": "title", "description": "the product title" },
      { "type": "string", "name": "price", "description": "the listed price" }
    ]
  }'
```

A schema is a structured object: a `name`, a `description`, and a `fields` array where each field has `type`, `name`, and `description`.
The response carries the schema id.
Use `PUT /v1/schemas/{id}` to update, `GET /v1/schemas` to list, and `DELETE /v1/schemas/{id}` to remove.
Update and delete both take the id in the path.
Confirm the exact create body against the live docs before relying on it, because the schema body format can change.

## Alternative: parse_json inline

For one-off extraction without a stored schema, the `parse_json` action runs inside a browser request.
It is token-priced, so flag the cost as token-based rather than deterministic.

```bash
curl -sS -X POST https://api.gaffa.dev/v1/browser/requests \
  -H "X-API-Key: ${GAFFA_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: gaffa-skill/1.0" \
  -d '{
    "url": "https://example.com",
    "proxy_location": "us",
    "max_cache_age": 0,
    "settings": {
      "time_limit": 60000,
      "actions": [
        {
          "type": "parse_json",
          "data_schema": {
            "name": "product",
            "description": "Extract the product title and price",
            "fields": [
              { "type": "string", "name": "title", "description": "the product title" },
              { "type": "string", "name": "price", "description": "the listed price" }
            ]
          }
        }
      ]
    }
  }'
```

`parse_json` is driven by `data_schema` (inline) or `data_schema_id` (a saved schema).
The `data_schema` is a structured object with `name`, `description`, and a `fields` array of `{type, name, description}`.
A flat object like `{"title":"string"}` is rejected and the action fails.
There is no free-form `prompt` parameter.
An optional `instruction` parameter sits alongside `data_schema` for extra parsing guidance.
See `references/actions.md` for the full parameter list, and "Choosing an extraction action" in `SKILL.md` for whether `parse_json` is the right action here at all.
