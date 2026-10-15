# Template: find loop shapes

Language-agnostic shapes for the discovery loop.
Adapt to the developer's language.

## Reconnaissance: site map

```bash
curl -sS -X POST https://api.gaffa.dev/v1/site/map \
  -H "X-API-Key: ${GAFFA_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: gaffa-skill/1.0" \
  -d '{ "url": "https://example.com" }'
```

The POST waits for the crawl and returns the links directly: `data.links` is the list of URLs and `data.link_count` their number.
It takes a root-level `max_cache_age` in seconds, like a browser request.
The path is singular `map`, not `maps`.
The map body takes no `proxy_location`, the crawl already goes out through residential proxies.

## Reconnaissance: broad markdown capture

```bash
curl -sS -X POST https://api.gaffa.dev/v1/browser/requests \
  -H "X-API-Key: ${GAFFA_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: gaffa-skill/1.0" \
  -d '{
    "url": "https://example.com",
    "proxy_location": "us",
    "max_cache_age": 0,
    "settings": {
      "time_limit": 60000,
      "record_request": true,
      "actions": [
        { "type": "generate_markdown" }
      ]
    }
  }'
```

The loop keeps `record_request: true` on its reconnaissance requests, drop it from the re-runnable script you hand back.
`proxy_location` stays in the re-runnable script, it is there to help the request succeed rather than for the reconnaissance.

## Targeted extraction with the parse_json action

Only reach for this once you have ruled out a deterministic path, per step 3 of the loop in SKILL.md.
LLM-backed extraction runs through the `parse_json` action, and there is no `/v1/schemas` action type.
Pass an inline `data_schema`, or reference a stored schema with `data_schema_id` after creating it via the `/v1/schemas` endpoint.

```bash
curl -sS -X POST https://api.gaffa.dev/v1/browser/requests \
  -H "X-API-Key: ${GAFFA_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: gaffa-skill/1.0" \
  -d '{
    "url": "https://example.com/leadership",
    "proxy_location": "us",
    "max_cache_age": 0,
    "settings": {
      "time_limit": 60000,
      "record_request": true,
      "actions": [
        {
          "type": "parse_json",
          "selector": "main",
          "data_schema": {
            "name": "leadership",
            "description": "Find the chief executive officer",
            "fields": [
              { "type": "string", "name": "ceo_name", "description": "the full name of the CEO" }
            ]
          }
        }
      ]
    }
  }'
```

The loop keeps `record_request: true` on this request too, drop it from the re-runnable script you hand back.
`proxy_location` stays, for the same reason as above.

`parse_json` is token-priced.
Gate it against the upper-bound estimate before firing.
Give it a `selector` for the region your recon identified, because `parse_json` over the full DOM of a large page can return `action_failed`.
If you do not yet know a good selector, your `generate_markdown` recon output often already contains the answer, so read that before spending another extraction request.

## Reasoning log

Append one entry per iteration to `./.gaffa-find-<timestamp>.log`.
One entry records the iteration number, the hypothesis, the request id, the candidate value, and the stop-condition decision.
Never write a key value into the log.

Write it safely.
The tempfile must live in the same directory as the final log so the rename is atomic on the same filesystem.
A tempfile in `/tmp` and a final log in the working directory are usually on different filesystems, which turns the rename into a non-atomic copy and defeats the crash-safety guarantee.

```bash
FINALLOG="./.gaffa-find-$(date +%Y%m%dT%H%M%S).log"
TMPLOG="${FINALLOG}.tmp"          # same directory as the final log, not /tmp

cat > "$TMPLOG" << 'EOF'
# gaffa-find reasoning log
... one entry per iteration ...
EOF

# redact only when the env value meets the entropy floor (16+ chars, a digit and a letter)
if [ "${#GAFFA_API_KEY}" -ge 16 ] && printf '%s' "$GAFFA_API_KEY" | grep -q '[0-9]' && printf '%s' "$GAFFA_API_KEY" | grep -q '[A-Za-z]'
then
  sed -i "s|${GAFFA_API_KEY}|<REDACTED>|g" "$TMPLOG"
fi

mv "$TMPLOG" "$FINALLOG"          # atomic rename within the same directory
```
