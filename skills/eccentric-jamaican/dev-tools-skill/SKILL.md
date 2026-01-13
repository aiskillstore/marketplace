---
name: dev-tools-skill
description: Use when the user says "use the DevTools skill" or when they need help debugging a web app with Chrome DevTools MCP (UI bugs, incorrect behavior, console errors, network/API failures, or performance/lag), especially if the user seems inexperienced and needs guided, step-by-step diagnosis.
---

# Dev Tools Skill

## Overview
Use the Chrome DevTools MCP server to diagnose and fix frontend issues by observing the live page, gathering evidence (console, network, performance), and proposing targeted code changes.

## Quick Start
1. Confirm the user wants DevTools used (or they already asked).
2. Open the target page, then take an a11y snapshot.
3. Triage via console + network + quick DOM inspection.
4. Choose the appropriate workflow below and follow it end-to-end.
5. Summarize findings + propose the smallest safe fix.

## Workflow Decision Tree
- **UI/interaction bug** (layout, hover/click, missing text): use *UI/Interaction Workflow*.
- **Performance/lag** (slow load, jank, long TTI): use *Performance Workflow*.
- **API/network issue** (failed fetch, wrong data): use *Network Workflow*.
- **Runtime error** (crash, blank screen, stack trace): use *Console/Error Workflow*.

## Core Workflows

### 1) Triage (always first)
- Capture state: `list_pages` → `select_page` → `take_snapshot`.
- Scan for visible errors (missing sections, broken layout) in snapshot text.
- Check console messages (`list_console_messages`, then `get_console_message` for details).
- Check network requests (`list_network_requests`, then `get_network_request` for errors/slow calls).
- Form a hypothesis and select a workflow below.

### 2) UI/Interaction Workflow
- Use `take_snapshot` to locate the target element; if unclear, `take_screenshot`.
- Inspect element text/attributes via `evaluate_script` (read-only DOM queries).
- Reproduce the issue with `click`, `hover`, or `press_key`.
- If layout is involved, measure box sizes/positions via `evaluate_script`.
- Propose minimal CSS/JS fixes; if unsure, ask 1 targeted question.

### 3) Performance Workflow
- Run a trace: `performance_start_trace` (reload=true) → reproduce → `performance_stop_trace`.
- Identify top issue via `performance_analyze_insight`.
- Correlate with network timings and large asset loads.
- Recommend fixes: reduce bundle size, defer non-critical JS, optimize images, avoid layout thrash.

### 4) Network Workflow
- List requests and find failures/slow endpoints.
- Open failing request details (`get_network_request`), capture status, timing, payload.
- Cross-check console for CORS or runtime fetch errors.
- Suggest fixes: endpoint URL, headers/auth, payload shape, caching, retries.

### 5) Console/Error Workflow
- Read console errors and stack traces in full.
- Identify the first failing module/function; map to code location if possible.
- Confirm if error is user-triggered vs load-time.
- Suggest smallest code change + safe rollback steps.

## UX & Safety Rules
- Explain actions in plain language; assume the user is less experienced.
- Avoid submitting forms or destructive actions without explicit user confirmation.
- Keep fixes minimal and reversible; call out any risk.

## References
- See `references/mcp-cheatsheet.md` for MCP command usage.
- See `references/debug-workflows.md` for detailed steps and examples.
- See `references/performance.md` for perf triage patterns.
- See `references/network.md` for network debugging patterns.
- See `references/ui-debug.md` for DOM/layout debugging tips.
