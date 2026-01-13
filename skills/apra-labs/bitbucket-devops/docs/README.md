# Bitbucket API Documentation

This directory contains local copies of Bitbucket Cloud API documentation to help with forming new REST API calls without needing internet access.

## Contents

### OpenAPI Specifications

Located in [`bitbucket-api/`](./bitbucket-api/):

- **bitbucket-cloud-api-v2.0-swagger.json** (888KB)
  Official Bitbucket Cloud API 2.0 specification in Swagger 2.0 format
  Source: https://api.bitbucket.org/swagger.json

- **bitbucket-cloud-api-openapi3.yml** (719KB)
  Community-maintained Bitbucket Cloud API specification in OpenAPI 3.0.1 format
  Source: https://github.com/tomasbjerre/bitbucket-cloud-java-rest-api

## Using the OpenAPI Specs

### Quick Reference

You can query the OpenAPI specs locally to find endpoints, parameters, and response schemas:

```bash
# Search for pipeline-related endpoints
grep -i "pipeline" bitbucket-api/bitbucket-cloud-api-v2.0-swagger.json | head -20

# Find all GET endpoints
jq '.paths | to_entries[] | select(.value.get) | .key' bitbucket-api/bitbucket-cloud-api-v2.0-swagger.json

# Get details for a specific endpoint
jq '.paths["/repositories/{workspace}/{repo_slug}/pipelines/"]' bitbucket-api/bitbucket-cloud-api-v2.0-swagger.json
```

### View in Tools

Load these specs in API documentation viewers:

1. **Swagger UI**: https://editor.swagger.io/
   - Upload `bitbucket-cloud-api-v2.0-swagger.json`

2. **Redoc**: https://redocly.github.io/redoc/
   - Load either spec file

3. **VSCode Extensions**:
   - [OpenAPI (Swagger) Editor](https://marketplace.visualstudio.com/items?itemName=42Crunch.vscode-openapi)
   - [Swagger Viewer](https://marketplace.visualstudio.com/items?itemName=Arjun.swagger-viewer)

## Key API Endpoints

### Pipelines API

Base: `https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pipelines`

- `GET /pipelines/` - List pipeline runs (supports filtering, sorting)
- `GET /pipelines/{pipeline_uuid}` - Get pipeline details
- `POST /pipelines/` - Trigger a new pipeline run
- `POST /pipelines/{pipeline_uuid}/stopPipeline` - Stop a running pipeline
- `GET /pipelines/{pipeline_uuid}/steps/` - List pipeline steps
- `GET /pipelines/{pipeline_uuid}/steps/{step_uuid}` - Get step details
- `GET /pipelines/{pipeline_uuid}/steps/{step_uuid}/log` - Get step logs

### Common Query Parameters

- `pagelen` - Number of results per page (default: 10, max: 100)
- `page` - Page number (default: 1)
- `q` - Query filter (e.g., `state.name="FAILED"`)
- `sort` - Sort field (prefix with `-` for descending, e.g., `-created_on`)

## Authentication

All requests require authentication via one of:

1. **App Password** (recommended for scripts):
   ```bash
   curl -u "username:app_password" https://api.bitbucket.org/2.0/...
   ```

2. **OAuth 2.0 Token**:
   ```bash
   curl -H "Authorization: Bearer {token}" https://api.bitbucket.org/2.0/...
   ```

Get your app password: https://bitbucket.org/account/settings/app-passwords/

## Official Documentation Links

- **REST API Overview**: https://developer.atlassian.com/cloud/bitbucket/rest/
- **Pipelines API**: https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pipelines/
- **Pull Requests API**: https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pullrequests/
- **Filtering & Sorting**: https://developer.atlassian.com/cloud/bitbucket/rest/intro/#filtering

## Examples

### List Recent Failed Pipelines

```bash
curl -u "$BB_USERNAME:$BB_APP_PASSWORD" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pipelines/?sort=-created_on&q=state.result.name=%22FAILED%22&pagelen=5"
```

### Get Pipeline Step Logs

```bash
curl -u "$BB_USERNAME:$BB_APP_PASSWORD" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pipelines/{pipeline_uuid}/steps/{step_uuid}/log"
```

### Trigger Pipeline on Branch

```bash
curl -X POST -u "$BB_USERNAME:$BB_APP_PASSWORD" \
  -H "Content-Type: application/json" \
  -d '{
    "target": {
      "ref_type": "branch",
      "type": "pipeline_ref_target",
      "ref_name": "main"
    }
  }' \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pipelines/"
```

## Updates

To update the API specifications:

```bash
cd docs/bitbucket-api

# Update Swagger 2.0 spec
curl -s https://api.bitbucket.org/swagger.json -o bitbucket-cloud-api-v2.0-swagger.json

# Update OpenAPI 3.0 spec
curl -s https://raw.githubusercontent.com/tomasbjerre/bitbucket-cloud-java-rest-api/master/openapi.yml -o bitbucket-cloud-api-openapi3.yml
```

---

**Note**: These specs are provided for offline reference. Always consult the official Atlassian documentation for the most up-to-date information.
