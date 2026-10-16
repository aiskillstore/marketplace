# Template: re-run with capture for triage

When the original request had no recording, or you need fresh page state to compare against, recommend a re-run with recording plus DOM and screenshot captures.
The video lets a human review what happened.
The DOM and screenshot let an agent inspect page state directly.

The re-run defaults to OFF.
Get explicit developer confirmation and show the credit estimate first.
The cost counts against `CREDITS_PER_INVOCATION`.

```bash
curl -sS -X POST https://api.gaffa.dev/v1/browser/requests \
  -H "X-API-Key: ${GAFFA_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: gaffa-skill/1.0" \
  -d '{
    "url": "URL_FROM_FAILING_REQUEST",
    "proxy_location": "us",
    "max_cache_age": 0,
    "settings": {
      "time_limit": 60000,
      "record_request": true,
      "actions": [
        { "type": "capture_dom" },
        { "type": "capture_screenshot" }
      ]
    }
  }'
```

Append the original failing action after the captures when you want to reproduce the failure with full evidence.
Keep the original request's `proxy_location` when it had one, `us` is the fallback when it did not.
Keep `max_cache_age: 0` so the re-run reflects live page state rather than a cache hit.
