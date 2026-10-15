# Template: async request plus poll

The pattern to reach for by default.
With `"async": true` in the body, `POST /v1/browser/requests` returns an id immediately.
Without it the request runs synchronously and the POST blocks until the result is ready.
Poll `GET /v1/browser/requests/{id}` until `state` is terminal.

Language-agnostic shape shown with curl.
Adapt to the developer's language and HTTP library.
Keep `time_limit` explicit and read the key from the environment.

## Submit

```bash
curl -sS -X POST https://api.gaffa.dev/v1/browser/requests \
  -H "X-API-Key: ${GAFFA_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: gaffa-skill/1.0" \
  -d '{
    "url": "https://example.com",
    "proxy_location": "us",
    "async": true,
    "max_cache_age": 0,
    "settings": {
      "time_limit": 60000,
      "actions": [
        { "type": "capture_screenshot" }
      ]
    }
  }'
```

The response is wrapped in a top-level `data` object, so the id is at `data.id`.
The 60000 ms above (60 seconds) matches the default, set it anyway so the value is visible and intentional.
If you omit `time_limit` it defaults to 60000 ms on every plan, it does not grow with the plan.
Set it explicitly and raise it toward your plan max if the job needs longer (Pay As You Go and Starter 1 min, Startup 2 min, Growth 5 min async).
A value above the cap is rejected with a 400 `time_limit_too_long` before the request runs.

## Poll

```bash
curl -sS https://api.gaffa.dev/v1/browser/requests/REQUEST_ID \
  -H "X-API-Key: ${GAFFA_API_KEY}"
```

Poll on an interval until the request is terminal.
The parameters page documents `pending` while the request runs and `completed` once it is finished, the API reference filter also names `failed` and `queued`.
A failed request comes back `completed` with `data.error` set, so treat `completed` with an empty `data.error` as success, and `failed` or any non-empty `data.error` as failure.
Keep polling on any other state rather than hard-coding the in-progress names, so a name you did not anticipate is not misread as a failure.
Always bound the loop with a deadline so it cannot spin forever, for example `time_limit` plus a margin for queueing and network.
On reaching the deadline, stop and report a timeout rather than continuing to poll.
A finished run carries `data.actions` (each action result is in `data.actions[].output`, a storage URL by default or the content itself with `output_type: "inline"`) plus `data.credit_usage`, `data.from_cache`, `data.started_at`, `data.completed_at`, `data.running_time`, and `data.page_load_time`.
A failed run carries `data.error` and `data.error_reason`.
If you set `record_request: true`, the response also carries `data.video`.

## Notes

- `record_request: true` lets `/gaffa-debug` inspect what happened later, within the plan-tiered retention window (7 days / 30 days / 3 months).
  It costs extra, so set it while exploring or debugging, not in shipped code.
- `proxy_location` is set to `us`, so the request goes out from a residential IP in that country instead of the datacenter IP it uses when the field is unset.
  Another supported location (`ie`, `sg`, `fr`) changes the country, and proxy bandwidth is billed.
- `max_cache_age` is a root-level field, not under `settings`, and is in seconds.
  It defaults to 0, so the cross-user cache is only used when you set it.
- Never place the key in the URL or query string.
  It belongs only in the `X-API-Key` header.
