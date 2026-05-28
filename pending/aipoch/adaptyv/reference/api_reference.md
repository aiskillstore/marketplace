# Adaptyv API Reference

## Base URL

```
https://kq5jp7qj7wdqklhsxmovkzn4l40obksv.lambda-url.eu-central-1.on.aws
```

## Authentication

All API requests require Bearer token authentication in the request header:

```
Authorization: Bearer YOUR_API_KEY
```

Get API access:
1. Contact support@adaptyvbio.com
2. Request API access during alpha/beta
3. Receive your personal access token

Securely store your API key:
- Use environment variables: `ADAPTYV_API_KEY`
- Never commit API keys to version control
- Use `.env` files with `.gitignore` for local development

## Endpoints

### Experiments

#### Create Experiment

Submit protein sequences for experimental testing.

**Endpoint:** `POST /experiments`

**Request Body:**
```json
{
  "sequences": ">protein1\nMKVLWALLGLLGAA...\n>protein2\nMATGVLWALLG...",
  "experiment_type": "binding|expression|thermostability|enzyme_activity",
  "target_id": "optional_target_identifier",
  "webhook_url": "https://your-webhook.com/callback",
  "metadata": {
    "project": "optional_project_name",
    "notes": "optional_notes"
  }
}
```

**Sequence Format:**
- FASTA format with headers
- Supports multiple sequences
- Standard amino acid codes

**Response:**
```json
{
  "experiment_id": "exp_abc123xyz",
  "status": "submitted",
  "created_at": "2025-11-24T10:00:00Z",
  "estimated_completion": "2025-12-15T10:00:00Z"
}
```

#### Get Experiment Status

Check the current status of an experiment.

**Endpoint:** `GET /experiments/{experiment_id}`

**Response:**
```json
{
  "experiment_id": "exp_abc123xyz",
  "status": "submitted|processing|completed|failed",
  "created_at": "2025-11-24T10:00:00Z",
  "updated_at": "2025-11-25T14:30:00Z",
  "progress": {
    "stage": "sequencing|expression|assay|analysis",
    "percentage": 45
  }
}
```

**Status Values:**
- `submitted` - Experiment received and queued
- `processing` - Active testing in progress
- `completed` - Results available for download
- `failed` - Experiment encountered an error

#### List Experiments

Retrieve all experiments for the organization.

**Endpoint:** `GET /experiments`

**Query Parameters:**
- `status` - Filter by status (optional)
- `limit` - Results per page (default: 50)
- `offset` - Pagination offset (default: 0)

**Response:**
```json
{
  "experiments": [
    {
      "experiment_id": "exp_abc123xyz",
      "status": "completed",
      "experiment_type": "binding",
      "created_at": "2025-11-24T10:00:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

### Results

#### Get Experiment Results

Download results from completed experiments.

**Endpoint:** `GET /experiments/{experiment_id}/results`

**Response:**
```json
{
  "experiment_id": "exp_abc123xyz",
  "results": [
    {
      "sequence_id": "protein1",
      "measurements": {
        "kd": 1.2e-9,
        "kon": 1.5e5,
        "koff": 1.8e-4
      },
      "quality_metrics": {
        "confidence": "high",
        "r_squared": 0.98
      }
    }
  ],
  "download_urls": {
    "raw_data": "https://...",
    "analysis_package": "https://...",
    "report": "https://..."
  }
}
```

### Targets

#### Search Target Catalog

Search the ACROBiosystems antigen catalog.

**Endpoint:** `GET /targets`

**Query Parameters:**
- `search` - Search term (protein name, UniProt ID, etc.)
- `species` - Filter by species
- `category` - Filter by category

**Response:**
```json
{
  "targets": [
    {
      "target_id": "tgt_12345",
      "name": "Human PD-L1",
      "species": "Homo sapiens",
      "uniprot_id": "Q9NZQ7",
      "availability": "in_stock|custom_order",
      "price_usd": 450
    }
  ]
}
```

#### Request Custom Target

Request antigens not included in the standard catalog.

**Endpoint:** `POST /targets/request`

**Request Body:**
```json
{
  "target_name": "Custom target name",
  "uniprot_id": "optional_uniprot_id",
  "species": "species_name",
  "notes": "Additional requirements"
}
```

### Organization

#### Get Credit Balance

Check your organization's credit balance and usage.

**Endpoint:** `GET /organization/credits`

**Response:**
```json
{
  "balance": 10000,
  "currency": "USD",
  "usage_this_month": 2500,
  "experiments_remaining": 22
}
```

## Webhooks

Configure Webhook URLs to receive notifications when experiments are completed.

**Webhook Payload:**
```json
{
  "event": "experiment.completed",
  "experiment_id": "exp_abc123xyz",
  "status": "completed",
  "timestamp": "2025-12-15T10:00:00Z",
  "results_url": "/experiments/exp_abc123xyz/results"
}
```

**Webhook Events:**
- `experiment.submitted` - Experiment received
- `experiment.started` - Processing started
- `experiment.completed` - Results available
- `experiment.failed` - Error occurred

**Security:**
- Verify Webhook signatures (details provided during onboarding)
- Use HTTPS endpoints only
- Respond with 200 OK to confirm receipt

## Error Handling

**Error Response Format:**
```json
{
  "error": {
    "code": "invalid_sequence",
    "message": "Sequence contains invalid amino acid codes",
    "details": {
      "sequence_id": "protein1",
      "position": 45,
      "character": "X"
    }
  }
}
```

**Common Error Codes:**
- `authentication_failed` - API key invalid or missing
- `invalid_sequence` - Malformed FASTA format or invalid amino acids
- `insufficient_credits` - Insufficient experiment credits
- `target_not_found` - Specified target ID does not exist
- `rate_limit_exceeded` - Request frequency exceeded limit
- `experiment_not_found` - Invalid experiment ID
- `internal_error` - Internal server error

## Rate Limiting

- 100 requests per minute per API key
- 1000 experiments per day per organization
- Bulk submission is encouraged for large-scale testing

When rate limits are triggered, the response includes:
```
HTTP 429 Too Many Requests
Retry-After: 60
```

## Best Practices

1. **Use Webhooks** for long-running experiments instead of polling.
2. **Batch sequences** when submitting multiple variants.
3. **Cache results** to avoid redundant API calls.
4. Implement **retry logic** with exponential backoff.
5. **Monitor credit usage** to avoid experiment failures.
6. **Validate sequences** locally before submission.
7. **Use descriptive metadata** for better experiment tracking.

## API Versioning

The API is currently in alpha/beta. Breaking changes may occur, but will be:
- Notified to registered users via email
- Documented in the changelog
- Provided with migration guides

The current version is reflected in the response header:
```
X-API-Version: alpha-2025-11
```

## Support

For API issues or questions:
- Email: support@adaptyvbio.com
- Documentation updates: https://docs.adaptyvbio.com
- Please provide experiment ID and request details when reporting bugs.
