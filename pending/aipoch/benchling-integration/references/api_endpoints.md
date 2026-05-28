# Benchling REST API Reference

## Base URL

All API requests use the following base URL format:
```
https://{tenant}.benchling.com/api/v2
```

Replace `{tenant}` with your Benchling tenant name.

## Versioning

Current API version: `v2` (2025-10-07)

API version is specified in the URL path. Benchling maintains backward compatibility within major versions.

## Authentication

All requests require authentication via HTTP headers:

**API Key (Basic Auth):**
```bash
curl -X GET \
  https://your-tenant.benchling.com/api/v2/dna-sequences \
  -u "your_api_key:"
```

**OAuth Bearer Token:**
```bash
curl -X GET \
  https://your-tenant.benchling.com/api/v2/dna-sequences \
  -H "Authorization: Bearer your_access_token"
```

## Common Headers

```
Authorization: Bearer {token}
Content-Type: application/json
Accept: application/json
```

## Response Format

All responses follow a consistent JSON structure:

**Single Resource:**
```json
{
  "id": "seq_abc123",
  "name": "My Sequence",
  "bases": "ATCGATCG",
  ...
}
```

**List Response:**
```json
{
  "results": [
    {"id": "seq_1", "name": "Sequence 1"},
    {"id": "seq_2", "name": "Sequence 2"}
  ],
  "nextToken": "token_for_next_page"
}
```

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `pageSize`: Number of items per page (default: 50, max: 100)
- `nextToken`: Token from previous response to fetch next page

**Example:**
```bash
curl -X GET \
  "https://your-tenant.benchling.com/api/v2/dna-sequences?pageSize=50&nextToken=abc123"
```

## Error Responses

**Format:**
```json
{
  "error": {
    "type": "NotFoundError",
    "message": "DNA sequence not found",
    "userMessage": "The requested sequence does not exist or you don't have access"
  }
}
```

**Common Status Codes:**
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing or invalid credentials
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource does not exist
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Core Endpoints

### DNA Sequences

**List DNA sequences:**
```http
GET /api/v2/dna-sequences

Query Parameters:
- pageSize: integer (default: 50, max: 100)
- nextToken: string
- folderId: string
- schemaId: string
- name: string (filter by name)
- modifiedAt: string (ISO 8601 date)
```

**Get a DNA sequence:**
```http
GET /api/v2/dna-sequences/{sequenceId}
```

**Create a DNA sequence:**
```http
POST /api/v2/dna-sequences

Body:
{
  "name": "My Plasmid",
  "bases": "ATCGATCG",
  "isCircular": true,
  "folderId": "fld_abc123",
  "schemaId": "ts_abc123",
  "fields": {
    "gene_name": {"value": "GFP"},
    "resistance": {"value": "Kanamycin"}
  },
  "entityRegistryId": "src_abc123",  // Optional for registration
  "namingStrategy": "NEW_IDS"        // Optional for registration
}
```

**Update a DNA sequence:**
```http
PATCH /api/v2/dna-sequences/{sequenceId}

Body:
{
  "name": "Updated Plasmid",
  "fields": {
    "gene_name": {"value": "mCherry"}
  }
}
```

**Archive DNA sequences:**
```http
POST /api/v2/dna-sequences:archive

Body:
{
  "dnaSequenceIds": ["seq_abc123"],
  "reason": "Deprecated construct"
}
```

### RNA Sequences

**List RNA sequences:**
```http
GET /api/v2/rna-sequences
```

**Get an RNA sequence:**
```http
GET /api/v2/rna-sequences/{sequenceId}
```

**Create an RNA sequence:**
```http
POST /api/v2/rna-sequences

Body:
{
  "name": "gRNA-001",
  "bases": "AUCGAUCG",
  "folderId": "fld_abc123",
  "fields": {
    "target_gene": {"value": "TP53"}
  }
}
```

**Update an RNA sequence:**
```http
PATCH /api/v2/rna-sequences/{sequenceId}
```

**Archive RNA sequences:**
```http
POST /api/v2/rna-sequences:archive
```

### Amino Acid Sequences

**List AA sequences:**
```http
GET /api/v2/aa-sequences
```

**Get an AA sequence:**
```http
GET /api/v2/aa-sequences/{sequenceId}
```

**Create an AA sequence:**
```http
POST /api/v2/aa-sequences

Body:
{
  "name": "GFP Protein",
  "aminoAcids": "MSKGEELFTGVVPILVELDGDVNGHKF",
  "folderId": "fld_abc123"
}
```

### Custom Entities

**List custom entities:**
```http
GET /api/v2/custom-entities

Query Parameters:
- schemaId: string (required to filter by type)
- pageSize: integer
- nextToken: string
```

**Get a custom entity:**
```http
GET /api/v2/custom-entities/{entityId}
```

**Create a custom entity:**
```http
POST /api/v2/custom-entities

Body:
{
  "name": "HEK293T-Clone5",
  "schemaId": "ts_cellline_abc",
  "folderId": "fld_abc123",
  "fields": {
    "passage_number": {"value": "15"},
    "mycoplasma_test": {"value": "Negative"}
  }
}
```

**Update a custom entity:**
```http
PATCH /api/v2/custom-entities/{entityId}

Body:
{
  "fields": {
    "passage_number": {"value": "16"}
  }
}
```

### Mixtures

**List mixtures:**
```http
GET /api/v2/mixtures
```

**Create a mixture:**
```http
POST /api/v2/mixtures

Body:
{
  "name": "LB-Amp Media",
  "folderId": "fld_abc123",
  "schemaId": "ts_mixture_abc",
  "ingredients": [
    {
      "componentEntityId": "ent_lb_base",
      "amount": {"value": "1000", "units": "mL"}
    },
    {
      "componentEntityId": "ent_ampicillin",
      "amount": {"value": "100", "units": "mg"}
    }
  ]
}
```

### Containers

**List containers:**
```http
GET /api/v2/containers

Query Parameters:
- parentStorageId: string (filter by location/box)
- schemaId: string
- barcode: string
```

**Get a container:**
```http
GET /api/v2/containers/{containerId}
```

**Create a container:**
```http
POST /api/v2/containers

Body:
{
  "name": "Sample-001",
  "schemaId": "cont_schema_abc",
  "barcode": "CONT001",
  "parentStorageId": "box_abc123",
  "fields": {
    "concentration": {"value": "100 ng/μL"},
    "volume": {"value": "50 μL"}
  }
}
```

**Update a container:**
```http
PATCH /api/v2/containers/{containerId}

Body:
{
  "fields": {
    "volume": {"value": "45 μL"}
  }
}
```

**Transfer containers:**
```http
POST /api/v2/containers:transfer

Body:
{
  "containerIds": ["cont_abc123"],
  "destinationStorageId": "box_xyz789"
}
```

**Check out containers:**
```http
POST /api/v2/containers:checkout

Body:
{
  "containerIds": ["cont_abc123"],
  "comment": "Taking to bench"
}
```

**Check in containers:**
```http
POST /api/v2/containers:checkin

Body:
{
  "containerIds": ["cont_abc123"],
  "locationId": "bench_loc_abc"
}
```

### Boxes

**List boxes:**
```http
GET /api/v2/boxes

Query Parameters:
- parentStorageId: string
- schemaId: string
```

**Get a box:**
```http
GET /api/v2/boxes/{boxId}
```

**Create a box:**
```http
POST /api/v2/boxes

Body:
{
  "name": "Freezer-A-Box-01",
  "schemaId": "box_schema_abc",
  "parentStorageId": "loc_freezer_a",
  "barcode": "BOX001"
}
```

### Locations

**List locations:**
```http
GET /api/v2/locations
```

**Get a location:**
```http
GET /api/v2/locations/{locationId}
```

**Create a location:**
```http
POST /api/v2/locations

Body:
{
  "name": "Freezer A - Shelf 2",
  "parentStorageId": "loc_freezer_a",
  "barcode": "LOC-A-S2"
}
```

### Plates

**List plates:**
```http
GET /api/v2/plates
```

**Get a plate:**
```http
GET /api/v2/plates/{plateId}
```

**Create a plate:**
```http
POST /api/v2/plates

Body:
{
  "name": "PCR-Plate-001",
  "schemaId": "plate_schema_abc",
  "barcode": "PLATE001",
  "wells": [
    {"position": "A1", "entityId": "ent_abc"},
    {"position": "A2", "entityId": "ent_xyz"}
  ]
}
```

### Notebook Entries

**List entries:**
```http
GET /api/v2/entries

Query Parameters:
- folderId: string
- schemaId: string
- modifiedAt: string
```

**Get an entry:**
```http
GET /api/v2/entries/{entryId}
```

**Create an entry:**
```http
POST /api/v2/entries

Body:
{
  "name": "Experiment 2025-10-20",
  "folderId": "fld_abc123",
  "schemaId": "entry_schema_abc",
  "fields": {
    "objective": {"value": "Test gene expression"},
    "date": {"value": "2025-10-20"}
  }
}
```

**Update an entry:**
```http
PATCH /api/v2/entries/{entryId}

Body:
{
  "fields": {
    "results": {"value": "Successful expression"}
  }
}
```

### Workflow Tasks

**List workflow tasks:**
```http
GET /api/v2/tasks

Query Parameters:
- workflowId: string
- statusIds: string[] (comma-separated)
- assigneeId: string
```

**Get a task:**
```http
GET /api/v2/tasks/{taskId}
```

**Create a task:**
```http
POST /api/v2/tasks

Body:
{
  "name": "PCR Amplification",
  "workflowId": "wf_abc123",
  "assigneeId": "user_abc123",
  "schemaId": "task_schema_abc",
  "fields": {
    "template": {"value": "seq_abc123"},
    "priority": {"value": "High"}
  }
}
```

**Update a task:**
```http
PATCH /api/v2/tasks/{taskId}

Body:
{
  "statusId": "status_complete_abc",
  "fields": {
    "completion_date": {"value": "2025-10-20"}
  }
}
```

### Folders

**List folders:**
```http
GET /api/v2/folders

Query Parameters:
- projectId: string
- parentFolderId: string
```

**Get a folder:**
```http
GET /api/v2/folders/{folderId}
```

**Create a folder:**
```http
POST /api/v2/folders

Body:
{
  "name": "2025 Experiments",
  "parentFolderId": "fld_parent_abc",
  "projectId": "proj_abc123"
}
```

### Projects

**List projects:**
```http
GET /api/v2/projects
```

**Get a project:**
```http
GET /api/v2/projects/{projectId}
```

### Users

**Get current user:**
```http
GET /api/v2/users/me
```

**List users:**
```http
GET /api/v2/users
```

**Get a user:**
```http
GET /api/v2/users/{userId}
```

### Teams

**List teams:**
```http
GET /api/v2/teams
```

**Get a team:**
```http
GET /api/v2/teams/{teamId}
```

### Schemas

**List schemas:**
```http
GET /api/v2/schemas

Query Parameters:
- entityType: string (e.g., "dna_sequence", "custom_entity")
```

**Get a schema:**
```http
GET /api/v2/schemas/{schemaId}
```

### Registries

**List registries:**
```http
GET /api/v2/registries
```

**Get a registry:**
```http
GET /api/v2/registries/{registryId}
```

## Bulk Operations

### Bulk Archive

**Archive multiple entities:**
```http
POST /api/v2/{entity-type}:archive

Body:
{
  "{entity}Ids": ["id1", "id2", "id3"],
  "reason": "Cleanup"
}
```

### Bulk Transfer

**Transfer multiple containers:**
```http
POST /api/v2/containers:bulk-transfer

Body:
{
  "transfers": [
    {"containerId": "cont_1", "destinationId": "box_a"},
    {"containerId": "cont_2", "destinationId": "box_b"}
  ]
}
```

## Asynchronous Operations

Some operations return a task ID for asynchronous processing:

**Response:**
```json
{
  "taskId": "task_abc123"
}
```

**Check task status:**
```http
GET /api/v2/tasks/{taskId}

Response:
{
  "id": "task_abc123",
  "status": "RUNNING", // or "SUCCEEDED", "FAILED"
  "message": "Processing...",
  "response": {...}  // Available when status is SUCCEEDED
}
```

## Field Value Formats

Custom schema fields use specific formats:

**Simple Values:**
```json
{
  "field_name": {
    "value": "Field Value"
  }
}
```

**Dropdowns:**
```json
{
  "dropdown_field": {
    "value": "Option1"  // Must match exact option name
  }
}
```

**Dates:**
```json
{
  "date_field": {
    "value": "2025-10-20"  // Format: YYYY-MM-DD
  }
}
```

**Entity Links:**
```json
{
  "entity_link_field": {
    "value": "seq_abc123"  // Entity ID
  }
}
```

**Numeric:**
```json
{
  "numeric_field": {
    "value": "123.45"  // String representation
  }
}
```

## Rate Limiting

**Limits:**
- Default: 100 requests per 10 seconds per user/app
- Rate limit headers included in response:
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

**Handling 429 Responses:**
```json
{
  "error": {
    "type": "RateLimitError",
    "message": "Rate limit exceeded",
    "retryAfter": 5  // Seconds to wait
  }
}
```

## Filtering and Search

**Common Query Parameters:**
- `name`: Partial name match
- `modifiedAt`: ISO 8601 datetime
- `createdAt`: ISO 8601 datetime
- `schemaId`: Filter by schema
- `folderId`: Filter by folder
- `archived`: Boolean (include archived items)

**Example:**
```bash
curl -X GET \
  "https://tenant.benchling.com/api/v2/dna-sequences?name=plasmid&folderId=fld_abc&archived=false"
```

## Best Practices

### Request Efficiency

1. **Use Appropriate Page Sizes:**
   - Default: 50 items
   - Max: 100 items
   - Adjust based on needs

2. **Filter Server-Side:**
   - Use query parameters instead of client-side filtering
   - Reduces data transfer and processing overhead

3. **Bulk Operations:**
   - Use bulk endpoints whenever possible
   - Archive/Transfer multiple items in one request

### Error Handling

```javascript
// Error handling example
async function fetchSequence(id) {
  try {
    const response = await fetch(
      `https://tenant.benchling.com/api/v2/dna-sequences/${id}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      }
    );

    if (!response.ok) {
      if (response.status === 429) {
        // Rate limit - exponential backoff retry
        const retryAfter = response.headers.get('Retry-After');
        await sleep(retryAfter * 1000);
        return fetchSequence(id);
      } else if (response.status === 404) {
        return null;  // Not found
      } else {
        throw new Error(`API error: ${response.status}`);
      }
    }

    return await response.json();
  } catch (error) {
    console.error('Request failed:', error);
    throw error;
  }
}
```

### Pagination Loop

```javascript
async function getAllSequences() {
  let allSequences = [];
  let nextToken = null;

  do {
    const url = new URL('https://tenant.benchling.com/api/v2/dna-sequences');
    if (nextToken) {
      url.searchParams.set('nextToken', nextToken);
    }
    url.searchParams.set('pageSize', '100');

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json'
      }
    });

    const data = await response.json();
    allSequences = allSequences.concat(data.results);
    nextToken = data.nextToken;
  } while (nextToken);

  return allSequences;
}
```

## Resources

- **API Documentation:** https://benchling.com/api/reference
- **Interactive API Explorer:** https://your-tenant.benchling.com/api/reference (Requires authentication)
- **Changelog:** https://docs.benchling.com/changelog
