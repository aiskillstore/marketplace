---
name: repo-metadata
description: This skill should be used when the user asks to "generate repository metadata", "create catalog-info.yaml", "add repo metadata", "document repository structure", or mentions generating structured metadata for service catalog or architecture documentation.
version: 1.0.0
---

# Repository Metadata

Generate structured `catalog-info.yaml` metadata for repositories using industry-standard conventions (based on Backstage catalog format). This metadata enables cross-repository architecture analysis and service catalog functionality.

## Purpose

Create and maintain `catalog-info.yaml` files that describe a repository's role in the broader architecture. This metadata feeds into architectural views, dependency graphs, and service groupings across the entire organization.

## When to Use

Trigger this skill when:
- User asks to "generate repo metadata" or "create catalog-info.yaml"
- User wants to document a repository for a service catalog
- User needs to prepare a repository for cross-repo architecture analysis
- User mentions "service catalog" or "component metadata"

## Metadata Schema

The `catalog-info.yaml` file follows Backstage conventions with Astrabit-specific extensions:

```yaml
apiVersion: astrabit.io/v1
kind: Component
metadata:
  name: service-name          # Required: Unique identifier
  description: Brief description
  tags:
    - backend
    - user-management
spec:
  # Service Classification
  type: service               # Required: service, gateway, worker, library, frontend, database
  category: backend           # Broader category
  domain: trading             # Business domain
  owner: platform-team        # Team responsible

  # Dependencies (Upstream)
  dependsOn:
    - component: auth-service
      type: service
    - component: user-db
      type: database

  # APIs Provided
  providesApis:
    - name: User API
      type: REST
      definition: ./openapi.yaml

  # APIs Consumed
  consumesApis:
    - name: Auth API
      providedBy: auth-service

  # Events Produced
  eventProducers:
    - name: user-events
      type: kafka
      topic: user.created
      schema: avro

  # Events Consumed
  eventConsumers:
    - name: order-events
      type: kafka
      topic: order.placed
      group: user-service-group

  # HTTP Routes (for gateways/services)
  routes:
    - path: /api/users/*
      methods: [GET, POST, PUT, DELETE]
      handler: this
    - path: /api/auth/*
      methods: [POST]
      forwardsTo: auth-service

  # Infrastructure
  runtime: nodejs             # nodejs, python, go, java, etc.
  framework: nestjs           # nestjs, fastapi, spring, etc.
```

## Generation Workflow

### Phase 1: Analyze Repository

Gather information about the repository:

1. **Use existing analysis scripts:**
   ```bash
   python skills/repo-docs/scripts/analyze-repo-structure.py /path/to/repo
   python skills/repo-docs/scripts/find-integration-points.py /path/to/repo
   ```

2. **Read existing documentation:**
   - Check for `INTEGRATIONS.md` - contains upstream/downstream relationships
   - Check for `ARCHITECTURE.md` - contains service role and dependencies
   - Check for `README.md` - contains basic description and tech stack

3. **Detect from code:**
   - Language from file extensions and package files
   - Framework from dependencies
   - Integration points from import patterns

### Phase 2: Generate Metadata

Based on analysis, generate `catalog-info.yaml` with detected values:

| Field | Detection Method |
|-------|------------------|
| `name` | Repo name or `package.json` `name` field |
| `description` | README title/description or generated from code |
| `type` | Inferred from code patterns (gateway has routes, worker has consumers only) |
| `runtime` | From package files (`package.json`, `pyproject.toml`, `go.mod`) |
| `framework` | From dependencies (`nestjs`, `fastapi`, `spring-boot`, etc.) |
| `dependsOn` | From integration point scanning |
| `eventProducers` | From `kafka.producer` or similar patterns |
| `eventConsumers` | From `@KafkaListener`, `@EventListener`, or similar patterns |
| `routes` | From `@Controller`, `@GetMapping`, router definitions |

### Phase 3: Present and Refine

Present the generated metadata to the user in a table format:

```markdown
Generated catalog-info.yaml:

| Field | Value | Source |
|-------|-------|--------|
| name | user-service | repo name |
| type | service | detected: has routes and consumers |
| runtime | nodejs | package.json |
| framework | nestjs | dependencies |
| domain | unknown | ❌ needs input |
| owner | unknown | ❌ needs input |
| dependsOn | auth-service, user-db | integration scan |
```

Prompt user to review and fill in missing fields (marked with ❌).

### Phase 4: Write Metadata File

Write `catalog-info.yaml` to the repository root.

### Phase 5: Update Related Documentation

Offer to update related docs to reference the new metadata file:
- Add link to `catalog-info.yaml` in `README.md`
- Update `INTEGRATIONS.md` to be consistent with metadata

## Service Type Detection

| Type | Indicators |
|------|------------|
| **gateway** | Has `routes` with `forwardsTo`, handles external requests, minimal business logic |
| **service** | Has both `providesApis` and `consumesApis`, business logic |
| **worker** | Only `eventConsumers`, no HTTP routes, background processing |
| **library** | No APIs consumed, only provides, shared utilities |
| **frontend** | `type: frontend` in package.json, has build artifacts |
| **database** | Contains migrations, schemas, no application code |

## Script Usage

Use `scripts/generate-metadata.py` to automate metadata generation:

```bash
# Generate from current directory
python skills/repo-metadata/scripts/generate-metadata.py

# Generate from specific repo
python skills/repo-metadata/scripts/generate-metadata.py /path/to/repo

# Output as JSON for inspection
python skills/repo-metadata/scripts/generate-metadata.py --format json
```

The script:
1. Runs repo structure analysis
2. Scans for integration points
3. Reads existing docs
4. Outputs `catalog-info.yaml` content

## Additional Resources

### Reference Files

- **`references/schema.md`** - Complete catalog-info.yaml schema reference
- **`references/detection-patterns.md`** - Patterns for detecting service characteristics

### Example Templates

- **`examples/catalog-info-template.yaml`** - Full template with all fields
- **`examples/catalog-info-gateway.yaml`** - Example gateway service
- **`examples/catalog-info-worker.yaml`** - Example worker service
- **`examples/catalog-info-library.yaml`** - Example shared library

## Quality Checklist

Before finalizing metadata, verify:

- [ ] `name` is unique across the organization
- [ ] `type` correctly classifies the service
- [ ] `domain` and `owner` are filled (not auto-detected)
- [ ] `dependsOn` lists all upstream dependencies
- [ ] `eventProducers` and `eventConsumers` are complete
- [ ] Routes are documented if this is a gateway/service
- [ ] File is valid YAML
- [ ] File is at repository root (`catalog-info.yaml`)
