# OpenAPI / AsyncAPI / GraphQL Strategy

Fetch structured API documentation from specification files.

## Overview

API specs provide machine-readable documentation for REST, async, and GraphQL APIs. They contain endpoints, parameters, schemas, and descriptions.

## Detection

```bash
# OpenAPI / Swagger
curl -sI "https://api.viperjuice.dev/openapi.json"
curl -sI "https://api.viperjuice.dev/swagger.json"
curl -sI "https://api.viperjuice.dev/api-docs"

# AsyncAPI
curl -sI "https://docs.viperjuice.dev/asyncapi.yaml"
curl -sI "https://docs.viperjuice.dev/asyncapi.json"

# GraphQL
curl -sI "https://api.viperjuice.dev/graphql"
curl -sI "https://docs.viperjuice.dev/schema.graphql"
```

## OpenAPI Fetch

```bash
# JSON spec
curl -s "https://api.viperjuice.dev/openapi.json" | jq '.'

# YAML spec
curl -s "https://api.viperjuice.dev/openapi.yaml"

# From GitHub
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/openapi/spec.json"
```

### Key Fields

| Field | Description |
|-------|-------------|
| `info` | API title, version, description |
| `paths` | Endpoint definitions |
| `components.schemas` | Data models |
| `security` | Authentication methods |

## AsyncAPI Fetch

```bash
# Fetch spec
curl -s "https://docs.viperjuice.dev/asyncapi.yaml"

# From GitHub
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/asyncapi.yaml"
```

### Key Fields

| Field | Description |
|-------|-------------|
| `info` | API metadata |
| `channels` | Event channels/topics |
| `components.messages` | Message definitions |
| `components.schemas` | Data schemas |

## GraphQL Schema Fetch

```bash
# Static schema file
curl -s "https://docs.viperjuice.dev/schema.graphql"

# Introspection query
curl -X POST "https://api.viperjuice.dev/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name description fields { name description } } } }"}'
```

## Registry Configuration

### OpenAPI

```json
{
  "stripe-api": {
    "name": "Stripe API",
    "strategy": "openapi",
    "paths": {
      "spec_url": "https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json",
      "homepage": "https://stripe.com/docs/api"
    }
  }
}
```

### AsyncAPI

```json
{
  "kafka-events": {
    "name": "Kafka Event Schema",
    "strategy": "asyncapi",
    "paths": {
      "spec_url": "https://raw.githubusercontent.com/org/repo/main/asyncapi.yaml",
      "homepage": "https://docs.viperjuice.dev/events"
    }
  }
}
```

### GraphQL

```json
{
  "github-graphql": {
    "name": "GitHub GraphQL API",
    "strategy": "graphql_schema",
    "paths": {
      "endpoint": "https://api.github.com/graphql",
      "schema_url": "https://docs.github.com/public/schema.docs.graphql",
      "homepage": "https://docs.github.com/graphql"
    }
  }
}
```

## Advantages

- Machine-readable and structured
- Self-documenting API details
- Includes schemas and types
- Can generate client code

## Disadvantages

- Only covers API, not conceptual docs
- May require auth for introspection
- Large specs can be verbose
- Doesn't include tutorials/guides

## Combining with Other Strategies

API specs usually complement conceptual docs:

```json
{
  "example-api": {
    "name": "Example API",
    "strategy": "github_raw",
    "api_spec": {
      "strategy": "openapi",
      "url": "https://api.viperjuice.dev/openapi.json"
    }
  }
}
```
