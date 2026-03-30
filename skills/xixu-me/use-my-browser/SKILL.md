---
name: use-my-browser
description: Use when the user wants browser automation, page inspection, or web research and you need to choose between public-web tools, the live browser session, or a separate browser context, especially for signed-in, dynamic, social, or DevTools-driven pages.
compatibility: Environment with chrome-devtools, web, playwright, shell_command, and multi_tool_use.parallel available.
---

# Use My Browser

This is the main browser automation strategy skill for nontrivial web work. It teaches the agent when to stay on public-web tools, when to use the live browser session, and when to fall back to a separate browser or raw-fetch path.

Despite the name, it covers more than "use my current browser." It also teaches a broader browsing philosophy: define the goal first, choose the right network layer, treat results as evidence, prefer primary sources over recycled summaries, and keep live-session work minimally intrusive.

## When to Use

Use this skill when any of these are true:

- The user wants public-web research, source verification, or page inspection and the choice of tool matters.
- The task depends on the user's current sign-in state or cookies.
- The user already has the relevant page, element, or failing request open in Chrome DevTools.
- The target is a social platform, anti-bot-heavy site, or other dynamic page where static fetches are likely to miss the real content.
- The target page is dynamic, authenticated, or difficult to inspect with search and raw fetch alone.
- The task needs the current DOM, console, network activity, performance data, file upload, or rendered media from the live browser session.
- The user wants the agent to take over a debugging flow they already started manually in Chrome.

Do not use this skill when:

- The task is purely local and does not involve the web at all.
- A separate clean browser context is safer than touching the live browsing session.
- The user explicitly asks not to use their live browser session.

## Preflight

Before choosing a browsing layer:

- If the task is public and citation-heavy, start with `web`.
- If the task needs the live browser session, confirm the Chrome DevTools connection is usable before depending on it.
- If a domain note exists under `references/site-patterns/`, read it before browsing that site.
- Use [`references/session-playbook.md`](./references/session-playbook.md) for live-browser-session fallback and recovery rules.

## First Principles

### 1. Define success before choosing tools

Start with the outcome, not the tool. Clarify what would count as done:

- What information or action does the user actually need?
- Does the task require the user's current browser state?
- Is the answer expected to be citation-heavy, interaction-heavy, or debugging-heavy?

### 2. Start with the cheapest layer that can plausibly succeed

Use the lowest-cost layer that can still reach the goal:

- public-web tools for discovery, citations, and normal page reads
- processed or raw reads when you need cheaper content extraction or source-level response data
- browser tools when the task depends on live state, interaction, or rendered evidence

Use [`references/tool-matrix.md`](./references/tool-matrix.md) for the detailed routing rules.

### 3. Treat every result as evidence

Do not repeat the same failed tactic blindly. Each step should update the plan:

- Search results may show the target is public, missing, or hidden behind login.
- A snapshot may reveal the data is already in the DOM and does not need OCR.
- A missing DOM node may mean the site is lazy-loaded, virtualized, gated by interaction, or simply on the wrong page.
- A platform saying "not found" may reflect an access path problem rather than a true absence.

### 4. Preserve the user's session

The live browser session is valuable. Use it carefully:

- Prefer the already connected Chrome DevTools session when the task depends on current state.
- Avoid closing or hijacking tabs you did not open.
- Prefer your own tab for exploration unless the point of the task is the already selected page, element, or request.
- Leave the session cleaner than you found it.

### 5. Search helps you find sources, not prove claims

Search engines and aggregators are discovery tools. When the task is about truth or verification:

- Use search to locate the likely source
- Read the source directly before making a strong claim
- Prefer official docs, official pages, raw announcements, and original content over repeated summaries

### 6. Prefer site-native URLs and complete parameters

If a site already exposes a link in the DOM, prefer that full URL over a hand-constructed guess. Query parameters, tokens, and generated paths often carry real session or routing context.

## Session Boundaries and Safety

The official Chrome DevTools MCP docs matter here:

- Live-session access can expose all open windows in the selected Chrome profile.
- `--autoConnect` is the safe modern pattern for sharing a real Chrome session with an MCP client.
- `--browser-url` is a fallback for explicit remote-debug-port setups, but it should not be recommended against the user's normal browsing profile.
- A manual remote debugging port on a default profile is riskier than the normal live browser session flow because any local app can connect while the port is open.

Treat these as background rules:

- Prefer the current DevTools connection if it already exists.
- Mention `--autoConnect` and `--browser-url` only as configuration context or troubleshooting guidance.
- Do not steer the user toward remote-debug-port workflows unless the current environment genuinely needs that fallback.

## Core Workflow

### Goal-first browsing loop

1. Define the success condition.
2. Choose the cheapest promising layer.
3. Inspect the result for evidence.
4. Escalate only when the current layer cannot reach the goal.
5. Stop when the goal is met, not when every possible path has been explored.

### Default live browser session workflow

When a task depends on the user's current browser session:

1. Inspect available pages with `list_pages`.
2. Reuse the selected page if the user's active context is the task.
3. Otherwise open or select a dedicated page before exploring.
4. Use `take_snapshot` before screenshots whenever structured page data might be enough.
5. Use `evaluate_script`, network tools, console tools, and performance tools as the primary evidence sources.
6. Use screenshots only when the visual state itself matters or the DOM does not expose enough information.

Read [`references/browser-recipes.md`](./references/browser-recipes.md) for concrete tool mappings and equivalent browser operations.

## Chrome DevTools Handoff Patterns

### Continue from a selected element

If the user already selected something in the Elements panel:

- `take_snapshot` can surface the current selection context.
- `evaluate_script` is usually the next best tool for reading computed values, attributes, state, or nearby DOM.
- Use `click`, `fill`, `hover`, and related tools only after confirming the current structure.

### Continue from a selected network request

If the user already highlighted a failing request in the Network panel:

- Call `get_network_request` without a `reqid` first.
- Inspect request and response bodies, headers, status, timing, and failure shape before looking for broader patterns.
- Use `list_network_requests` only when you need surrounding context or need to compare multiple requests.

### Continue from an active debugging page

If the user is already on the problem page:

- Start from that page instead of opening a parallel isolated copy.
- Preserve the state they already set up unless the user asks for a fresh reproduction.
- If you need a second tab for safe experimentation, create one yourself and keep the original page intact.

## Extraction and Interaction Rules

Read [`references/session-playbook.md`](./references/session-playbook.md) for the detailed patterns. The short version:

- Prefer DOM and network evidence over OCR.
- Prefer `take_snapshot` over `take_screenshot` for interaction planning.
- Prefer `evaluate_script` when the data likely exists but is not visible.
- Switch between direct extraction and GUI-style interaction based on what the site actually responds to.
- Treat screenshots, reconstructed URLs, and "not found" pages as things to verify, not things to trust immediately.

## Public Web vs Live Session

This skill should not collapse into "always use the browser."

- Public-web tasks still belong to this skill when the main question is "which layer should I use first?"
- Start with public-web tools for citation-heavy work and escalate only when the cheaper path cannot reach the goal.
- Use [`references/tool-matrix.md`](./references/tool-matrix.md) for the routing decision and [`references/browser-recipes.md`](./references/browser-recipes.md) for the concrete operations.

## Parallel Research Policy

For multiple independent public research targets:

- Batch `web.search_query` requests in one call when possible.
- Batch `web.open` calls when reading several sources.
- Use `multi_tool_use.parallel` for independent shell or local-doc reads, not for browser steps that depend on the same selected page state.
- Use [`references/session-playbook.md`](./references/session-playbook.md) for the rules on when agent-level parallelism is worth it and how to frame it safely.

## Red Flags

Stop and change approach if you notice any of these:

- You are about to use the live browser session for a task that only needs public citations.
- You are about to close, reload, or navigate a page the user may still be using.
- You reached for screenshots before checking whether the DOM or network already contains the answer.
- You are ignoring a currently selected DevTools request or element and starting from scratch.
- You are hand-constructing site URLs even though the page already exposes the real link with parameters.
- You are treating a platform "not found" message as definitive before checking whether the access path itself is wrong.
- You are about to recommend remote debugging on the user's normal browsing profile.
- You are using Playwright by habit even though the goal depends on the user's current signed-in Chrome state.

## Examples

**Use this skill**

- "I already have the failing request selected in DevTools. Explain why it returns 403."
- "Check this dashboard in my logged-in browser without making me sign in again."
- "I clicked into the broken component in Elements. Figure out why the layout is wrong."
- "Pull the real image or video source from this lazy-loaded page."
- "Read this public doc and tell me the structured metadata without opening a browser if a fetch is enough."
- "Compare these three public sources, cite them, and only touch the browser if the static path fails."
- "Go through this social site and find the real content even if search results and direct fetches are weak."

**Do not use this skill**

- "Rename these local files and update the import paths."
- "Refactor this parser and run the unit tests."
- "Open a clean browser and test the unauthenticated signup flow."

## Reference Files

- [`references/tool-matrix.md`](./references/tool-matrix.md): choose between `web`, `chrome-devtools`, `playwright`, and raw-fetch paths.
- [`references/session-playbook.md`](./references/session-playbook.md): tab hygiene, DOM/media extraction, login handling, and fallback tactics.
- [`references/browser-recipes.md`](./references/browser-recipes.md): concrete browser operations for tab control, extraction, interaction, and audits.
- [`references/site-patterns/README.md`](./references/site-patterns/README.md): format for validated domain-specific notes.
