# Gotchas

Common pitfalls and failure modes discovered through real-world usage.

## Chrome Automation

### form_fill_and_submit Silently Fails
NotebookLM is an Angular app with no `<form>` element. The `form_fill_and_submit` MCP tool appears to work but nothing actually submits. Use `javascript_tool` to fill the textarea value + `computer(key Enter)` to submit.

### Synthetic KeyboardEvent Doesn't Trigger Submit
`dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter'}))` creates a JavaScript-level event that Angular's zone.js doesn't intercept as a real user action. Only `computer` tool's `key` action generates a Chrome DevTools Protocol `Input.dispatchKeyEvent` — a real OS-level keyboard event that Angular recognizes.

### String Escaping for javascript_tool
User input embedded in JavaScript strings must be escaped: `\` → `\\`, `"` → `\"`, newline → `\n`, carriage return → `\r`. Always use double quotes. Unescaped quotes break JS execution silently — no error, just no output.

### Max Input Character Limit
NotebookLM has a server-side character limit of approximately 45,000–50,000 characters. There is **no client-side enforcement** — the textarea has no `maxLength` attribute, no character counter, and the submit button stays enabled regardless of input length. Testing confirmed: 10k, 20k, 30k, 40k, and 45k characters all returned responses successfully, while 50k characters caused a silent timeout with no response. The skill pre-validates question length (`max_query_length` in config, default 40,000) and the agent reports textarea fill status. If the agent returns an empty response (backend timeout), the skill blocks coverage analysis to prevent a follow-up loop that would multiply the wait time.

### Extension Service Worker Goes Idle
Chrome Manifest V3 extensions have a service worker that idles after ~30 seconds of inactivity. MCP tool calls then fail with `"Receiving end does not exist"`. This maps to the `CHROME_NOT_CONNECTED` error — user needs to reconnect the extension via the side panel.

### Page Load Timing
NotebookLM loads content asynchronously via Angular. The 5-second delay in metadata extraction (STEP 2) is necessary for the framework to render. Without it, DOM selectors return null even though the page appears loaded.

### Clear History Selectors Are Fragile
The clear history button is found via `aria-label` patterns (`clear`, `reset`). Google can change these labels in any NotebookLM update. If clearing fails, it's usually because the selectors no longer match — not a Chrome connection issue.

## Architecture

### Skill Cannot Use Chrome MCP Tools
The notebooklm-manager skill has `allowed-tools: Read, Write, Edit, Agent, AskUserQuestion`. Chrome MCP tools are only available to the chrome-mcp-query agent. If the skill tries to call them, it will error. If the agent fails, the skill should report the error — not try Chrome tools itself.

### Data Path Must Be Resolved First
The data directory path is written by the PreToolUse hook when Claude first reads `data-path`. If the hook hasn't fired (e.g., hook not loaded), the file won't exist. Error message should tell the user to restart the session.

### Smart Add Triggers Coverage Reminder
The PostToolUse hook fires on all chrome-mcp-query Task completions, including Smart Add metadata queries. The hook skips Smart Add queries to avoid unnecessary coverage analysis prompts.

## Coverage Analysis

### NotebookLM Answers First Topic Only
Multi-topic questions frequently get partial answers. NotebookLM tends to deeply address the first topic and briefly mention or skip later topics. Coverage analysis catches this — it's not over-engineering, it's addressing a real and frequent failure mode.

### Follow-up Tab Reuse
Follow-up queries reuse the existing Chrome tab (same URL match in STEP 1). No new tab creation needed. This makes follow-ups cheap and fast.
