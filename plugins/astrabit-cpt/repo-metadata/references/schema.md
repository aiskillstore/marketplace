# Catalog Info Schema Reference

Complete schema reference for `catalog-info.yaml`.

## Root Structure

```yaml
apiVersion: astrabit.io/v1
kind: Component
metadata: {...}
spec: {...}
```

## metadata Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique component identifier (lowercase, hyphens) |
| `description` | string | No | Human-readable description |
| `tags` | string[] | No | Search and grouping tags |

### Naming Conventions

- Use lowercase with hyphens: `user-service`, `order-processor`
- Prefix team/domain if needed: `trading-order-service`
- Avoid underscores: use `api-gateway` not `api_gateway`

## spec Section

### Service Classification

| Field | Type | Required | Values |
|-------|------|----------|--------|
| `type` | string | Yes | `service`, `gateway`, `worker`, `library`, `frontend`, `database` |
| `category` | string | No | `backend`, `frontend`, `infrastructure`, `platform`, `shared` |
| `domain` | string | No | Business domain: `trading`, `user`, `platform` |
| `owner` | string | No | Team: `platform-team`, `trading-team` |
| `lifecycle` | string | No | `experimental`, `production`, `deprecated` |

### Type Values

| Type | Description | Typical Characteristics |
|------|-------------|-------------------------|
| `service` | Business logic microservice | Provides APIs, may consume events |
| `gateway` | API Gateway / Proxy | Has routes with `forwardsTo`, minimal logic |
| `worker` | Background processor | Only `eventConsumers`, no HTTP routes |
| `library` | Shared code/package | No dependencies, provides SDK/API |
| `frontend` | Web/app UI | Build artifacts, no backend |
| `database` | Database | Schema/migrations, no app code |

### Dependencies

```yaml
dependsOn:
  - component: service-name
    type: service
  - component: database-name
    type: database
  - component: cache-name
    type: cache
```

| Dependency `type` values |
|--------------------------|
| `service` |
| `database` |
| `cache` |
| `message-queue` |
| `library` |

### APIs

```yaml
# APIs this component provides
providesApis:
  - name: Human Readable Name
    type: REST
    definition: ./openapi.yaml

# APIs this component consumes
consumesApis:
  - name: API Name
    providedBy: service-name
```

| API `type` values |
|-------------------|
| `REST` |
| `GraphQL` |
| `gRPC` |
| `SDK` |
| `WebSocket` |

### Events

```yaml
# Events this component produces
eventProducers:
  - name: event-stream-name
    type: kafka
    topic: topic.name
    schema: avro

# Events this component consumes
eventConsumers:
  - name: event-stream-name
    type: kafka
    topic: topic.name
    group: consumer-group-name
```

| Event `type` values |
|---------------------|
| `kafka` |
| `rabbitmq` |
| `redis` |
| `sqs` |
| `pubsub` |

| Event `schema` values |
|----------------------|
| `avro` |
| `json` |
| `protobuf` |
| `none` |

### Routes (Gateway/Service)

```yaml
routes:
  - path: /api/users/*
    methods: [GET, POST, PUT, DELETE]
    handler: this                    # handled by this service
  - path: /api/auth/*
    methods: [POST]
    forwardsTo: auth-service         # proxied to another service
```

| Field | Description |
|-------|-------------|
| `path` | Route pattern (use `*` as wildcard) |
| `methods` | HTTP methods (array) |
| `handler` | Use `this` if handled locally |
| `forwardsTo` | Component name if proxied |

### Infrastructure

```yaml
runtime: nodejs     # nodejs, python, go, java, rust
framework: nestjs   # nestjs, fastapi, spring, echo, etc.
```

| Runtime values | Framework values (examples) |
|----------------|----------------------------|
| `nodejs` | `nestjs`, `express`, `fastify` |
| `python` | `fastapi`, `flask`, `django` |
| `go` | `echo`, `gin`, `fiber` |
| `java` | `spring`, `micronaut`, `quarkus` |
| `rust` | `actix`, `rocket` |
