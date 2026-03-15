# Advanced Azure Quota Commands

Reference for less commonly used Azure quota CLI commands for tracking quota requests and operations.

## az quota request status list

Get current quota requests for a one-year period. Use oData filter to select requests.

**Syntax**:
```bash
az quota request status list --scope SCOPE [--filter FILTER] [--max-items N] [--next-token TOKEN] [--skip-token TOKEN] [--top N]
```

**Required**:
- `--scope` - Target Azure resource URI

**Optional**:
- `--filter` - Filter by requestSubmitTime (ge/le/eq), provisioningState (eq), resourceName (eq)
- `--max-items` - Total items to return
- `--next-token` - Pagination token from previous response
- `--skip-token` - Skip token for next page
- `--top` - Number of records to return

**Examples**:
```bash
# List compute quota requests
az quota request status list --scope /subscriptions/{id}/providers/Microsoft.Compute/locations/eastus

# List network quota requests
az quota request status list --scope /subscriptions/{id}/providers/Microsoft.Network/locations/eastus
```

## az quota request status show

Get quota request details and status by request ID. The ID is returned from `az quota update` PUT operation.

**Syntax**:
```bash
az quota request status show --id REQUEST_ID --scope SCOPE
```

**Required**:
- `--id` - Quota request ID
- `--scope` - Target Azure resource URI

**Example**:
```bash
az quota request status show \
  --id 2B5C8515-37D8-4B6A-879B-CD641A2CF605 \
  --scope /subscriptions/{id}/providers/Microsoft.Compute/locations/eastus
```

## az quota operation list

List all operations supported by Microsoft.Quota resource provider.

**Syntax**:
```bash
az quota operation list
```

**Examples**:
```bash
# List all operations
az quota operation list

# Table format
az quota operation list --output table
```
