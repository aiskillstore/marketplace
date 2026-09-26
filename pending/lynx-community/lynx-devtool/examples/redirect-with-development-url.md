# Redirect with Development URL

Reload the page with URL from dev-server.

```bash
agent-lynx list-sessions
# Find the sessionId to be redirected
agent-lynx cdp --session <sessionId> -m Page.reload '{"url": "http://<host>:<port>/path/to/template.js"}'
```

> Note that the `url` in `list-sessions` would not change after `Page.reload`.
