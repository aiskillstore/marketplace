# Network Debugging Patterns

## Symptoms
- 4xx/5xx errors
- Requests stuck in pending
- Data missing or stale
- CORS failures

## Evidence to gather
- Request URL, method, headers
- Response status, payload, timing
- Console error messages

## Typical fixes
- Correct endpoint or base URL
- Fix auth headers/token
- Update payload shape
- Add caching headers or retries
