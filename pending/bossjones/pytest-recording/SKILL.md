---
name: pytest-recording
description: Work with pytest-recording (VCR.py) for recording and replaying HTTP interactions in tests. Use when writing VCR tests, managing cassettes, configuring VCR options, filtering sensitive data, or debugging recorded HTTP responses.
---

# pytest-recording (VCR.py) Testing

## Overview

pytest-recording wraps VCR.py to record HTTP interactions as YAML cassettes, enabling deterministic tests without live API calls.

## Quick Reference

### Running Tests

```bash
# Run all tests (uses existing cassettes)
uv run pytest tests/

# Run a single test
uv run pytest tests/test_module.py::test_function

# Rewrite all cassettes with fresh responses
uv run pytest tests/ --vcr-record=rewrite

# Record only missing cassettes
uv run pytest tests/ --vcr-record=new_episodes

# Disable VCR (make live requests)
uv run pytest tests/ --disable-recording
```

### Recording Modes

| Mode | Flag | Behavior |
|------|------|----------|
| `none` | `--vcr-record=none` | Only replay, fail if no cassette |
| `once` | (default) | Record if no cassette exists |
| `new_episodes` | `--vcr-record=new_episodes` | Record new requests, keep existing |
| `all` | `--vcr-record=all` | Always record, overwrite existing |
| `rewrite` | `--vcr-record=rewrite` | Delete and re-record all cassettes |

### Writing VCR Tests

Basic test with VCR:

```python
import pytest

@pytest.mark.vcr()
def test_api_call():
    response = my_api_function()
    assert response.status_code == 200
```

Custom cassette name:

```python
@pytest.mark.vcr("custom_cassette_name.yaml")
def test_with_custom_cassette():
    pass
```

Multiple cassettes:

```python
@pytest.mark.vcr("cassette1.yaml", "cassette2.yaml")
def test_with_multiple_cassettes():
    pass
```

### VCR Configuration in conftest.py

The `vcr_config` fixture controls VCR behavior:

```python
@pytest.fixture(scope="module")
def vcr_config():
    return {
        # Filter sensitive headers from recordings
        "filter_headers": ["authorization", "api-key", "x-api-key"],

        # Filter query parameters
        "filter_query_parameters": ["key", "api_key", "token"],

        # Match requests by these criteria
        "match_on": ["method", "scheme", "host", "port", "path", "query"],

        # Ignore certain hosts (don't record)
        "ignore_hosts": ["localhost", "127.0.0.1"],

        # Record mode
        "record_mode": "once",
    }
```

### Filtering Sensitive Data

For LLM providers, filter authentication:

```python
@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            "authorization",      # OpenAI, Anthropic
            "api-key",            # Azure OpenAI
            "x-api-key",          # Anthropic
            "x-goog-api-key",     # Google AI
        ],
        "filter_query_parameters": ["key"],
    }
```

### Response Processing

Use `pytest_recording_configure` for advanced processing:

```python
def pytest_recording_configure(config, vcr):
    vcr.serializer = "yaml"
    vcr.decode_compressed_response = True

    # Sanitize response headers
    def sanitize_response(response):
        response['headers']['Set-Cookie'] = 'REDACTED'
        return response

    vcr.before_record_response = sanitize_response
```

### Cassette Location

Cassettes are stored in `tests/cassettes/` by default, organized by test module:

```
tests/
├── cassettes/
│   └── test_module/
│       └── test_function.yaml
└── test_module.py
```

## Debugging

### Cassette Not Found

If tests fail with "Can't find cassette":
1. Run with `--vcr-record=once` to create missing cassettes
2. Check cassette path matches test location
3. Verify cassette file exists and is valid YAML

### Request Mismatch

If VCR can't match requests:
1. Check `match_on` criteria in `vcr_config`
2. Compare request details in cassette vs actual request
3. Use `--vcr-record=new_episodes` to add missing interactions

### Stale Cassettes

When API responses change:
1. Delete specific cassette file and re-run test
2. Or use `--vcr-record=rewrite` to refresh all cassettes

### View Cassette Contents

```bash
# View a cassette file
cat tests/cassettes/test_module/test_function.yaml

# Search for specific content in cassettes
grep -r "error" tests/cassettes/
```

## Adding New LLM Providers

When adding a new provider:

1. Identify authentication headers (check provider docs)
2. Add headers to `filter_headers` in `vcr_config`
3. Add any query param auth to `filter_query_parameters`
4. Test with `--vcr-record=once` to create cassettes
5. Verify cassettes don't contain secrets

Common provider authentication:

| Provider | Headers to Filter |
|----------|-------------------|
| OpenAI | `authorization` |
| Anthropic | `x-api-key`, `authorization` |
| Azure OpenAI | `api-key` |
| Google AI | `x-goog-api-key` |
| Cohere | `authorization` |

## Best Practices

1. **Never commit secrets**: Always filter auth headers/params
2. **Use descriptive test names**: Cassette names derive from test names
3. **Keep cassettes small**: Mock only what you need to test
4. **Review cassettes in PRs**: Check for sensitive data leaks
5. **Regenerate periodically**: API responses may change over time
6. **Use scope appropriately**: `scope="module"` for shared fixtures
