# agent-browser commands quick reference

## Core navigation and discovery

```bash
agent-browser open <url>
agent-browser wait --load networkidle
agent-browser snapshot -i
agent-browser snapshot -i -C
agent-browser snapshot -s "#main"
```

## Interaction

```bash
agent-browser click @e1
agent-browser fill @e2 "text"
agent-browser type @e2 "append text"
agent-browser select @e3 "Option"
agent-browser check @e4
agent-browser press Enter
```

## Verification and capture

```bash
agent-browser diff snapshot
agent-browser screenshot before.png
agent-browser diff screenshot --baseline before.png
agent-browser screenshot --annotate
agent-browser pdf output.pdf
```

## Session and utility

```bash
agent-browser --session task-a open https://example.com
agent-browser session list
agent-browser get text @e1
agent-browser get url
agent-browser close
```

## Security hardening

```bash
export AGENT_BROWSER_CONTENT_BOUNDARIES=1
export AGENT_BROWSER_MAX_OUTPUT=50000
export AGENT_BROWSER_ALLOWED_DOMAINS="example.com,*.example.com"
export AGENT_BROWSER_ACTION_POLICY=./policy.json
```

## Eval safety pattern

Prefer stdin for complex JavaScript:

```bash
agent-browser eval --stdin <<'EVALEOF'
JSON.stringify({ title: document.title, links: document.links.length })
EVALEOF
```
