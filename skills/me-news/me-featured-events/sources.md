# ME Featured Events Sources

Only use the following ME News read-only API endpoints:

| Purpose | Endpoint |
|---|---|
| Filter options | `https://api.me.news/skill/events/options` |
| Upcoming events | `https://api.me.news/skill/events/upcoming` |
| Newly added events | `https://api.me.news/skill/events/changes` |

Rules:

- Prefer an available HTTP/Web Fetch tool; otherwise use `curl -fsS --max-time 30`.
- URL-encode query parameters.
- Do not replace a failed endpoint with public web search.
- Treat HTTP errors, invalid JSON, or a top-level `code` other than `200` as failure.
- Never update the local cursor after a failed request.
