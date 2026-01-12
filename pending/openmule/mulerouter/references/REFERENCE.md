# MuleRouter API Reference

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MULEROUTER_SITE` | Yes | API site: `mulerouter` or `mulerun` |
| `MULEROUTER_API_KEY` | Yes | API key for authentication |

### .env File Example

```env
MULEROUTER_SITE=mulerun
MULEROUTER_API_KEY=your-api-key
```

## CLI Options

All model scripts support these options:

| Option | Description |
|--------|-------------|
| `--list-params` | Show available parameters and exit |
| `--json` | Output results as JSON |
| `--no-wait` | Return task ID immediately without polling |
| `--poll-interval N` | Polling interval in seconds (default: 5) |
| `--max-wait N` | Maximum wait time in seconds (default: 600) |
| `--quiet` | Suppress progress output |
| `--site SITE` | Override API site (mulerouter/mulerun) |
| `--api-key KEY` | Override API key |

## Task Workflow

All generation tasks are asynchronous:

1. **Create Task**: POST request returns a task ID
2. **Poll Status**: GET request checks task status (pending -> processing -> completed/failed)
3. **Get Results**: Completed tasks include URLs to generated images/videos

The scripts handle polling automatically. Use `--no-wait` for manual control.

## API Sites

| Site | Base URL | Notes |
|------|----------|-------|
| MuleRouter | `api.mulerouter.ai` | Full model catalog |
| MuleRun | `api.mulerun.com` | Full model catalog |

Both sites share the same API format. Model availability may differ between sites.

## Error Handling

Common error responses:

| Code | Meaning | Solution |
|------|---------|----------|
| 401 | Invalid API key | Check MULEROUTER_API_KEY |
| 400 | Invalid parameters | Run `--list-params` to see valid options |
| 429 | Rate limited | Wait and retry |
| 500 | Server error | Retry after a few seconds |

## Output Format

### JSON Output (--json)

```json
{
  "task_id": "2227246C-760C-4167-906C-DD727D7BBBEC",
  "status": "completed",
  "videos": ["https://..."],
  "images": ["https://..."]
}
```

### Default Output

```
Task ID: 2227246C-760C-4167-906C-DD727D7BBBEC
Status: completed
Result URLs:
  - https://...
```
