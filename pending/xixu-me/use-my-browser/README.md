# Use My Browser

**_[汉语](./README.zh.md)_**

`use-my-browser` is a browser automation strategy skill for agents that need to operate the user's current browser session, inspect pages, continue from DevTools context, debug dynamic apps, work with logged-in websites, and extract media from rendered pages; it also teaches the agent when a browser is actually needed and when to route the task through public-web tools, the live Chrome session, raw fetches, or a clean browser context.

> [!IMPORTANT]
> This skill is especially useful when browser automation is part of the job, but the agent still needs judgment about whether to use public-web tools, the live Chrome session, raw fetches, or a clean browser context.

## Why This Skill Exists

Web tasks often look like "just open the browser," but in practice they split into very different automation jobs: some need the user's logged-in Chrome session, some need DevTools inspection of the live DOM or network, some are safer in a clean browser context, and some do not need browser automation at all. This skill exists to help the agent handle browser-driven work deliberately: continue from the user's existing browser state when helpful, extract evidence from the page before guessing, and avoid unnecessary disruption while still choosing the right layer for the task.

## Capabilities

This skill helps an agent do the following:

| Capability                  | What It Means                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Smart Tool Routing          | The agent can choose between public web search, processed reads, raw fetches, shell-based fetches, and live browser tooling based on the task instead of forcing everything through one path.                   |
| Live Chrome Control         | The agent can attach to the user's current Chrome session when login state, cookies, current app context, or a selected DevTools target matters.                                                                |
| DevTools-Driven Interaction | The agent can inspect and operate on dynamic pages using DOM reads, clicks, form fills, uploads, console inspection, network inspection, performance tooling, and screenshots when needed.                      |
| DevTools Handoff            | If the user already selected an element in Elements or a request in Network, the agent can continue from that exact context instead of reproducing the issue from scratch.                                      |
| Evidence-First Inspection   | The agent prefers snapshots, DOM reads, console output, network requests, and direct extraction before falling back to screenshots or repetitive UI interaction.                                                |
| Media Extraction            | The agent can pull image or video URLs from the page directly, inspect media state, and use rendered screenshots only when pixel-level evidence is actually needed.                                             |
| Parallel Research           | For independent targets, the agent can batch public-web work and structure comparisons across multiple sites more efficiently, while avoiding parallel work that depends on one mutable page state.             |
| Isolated Browser Fallback   | When the task needs a clean browser context, or the live Chrome session is unavailable, the agent can switch to a separate automation browser instead of forcing everything through the user's current session. |
| Site Memory                 | The skill supports storing validated per-domain notes such as URL patterns, platform traits, extraction tactics, and known traps for reuse in later sessions.                                                   |
| Safe Escalation             | The agent can start with the cheapest path that might work, escalate only when needed, and avoid disturbing the user's live browser session unless the task truly requires it.                                  |

## Example Uses

Examples are easiest to understand when grouped by intent:

**Logged-in browser actions**

- "Post this video on YouTube and leave the last click to me."
- "Check this logged-in dashboard without making me sign in again."

**Website inspection and UX review**

- `Visit the page https://xi-xu.me and see how its UX design is`
- `Compare these public sources, cite them, and only use the browser if the static path fails`

**Social and dynamic site research**

- `Go to X.com and search for Xi Xu's account to see what he has recently posted`
- `Pull the real image or video source from this lazy-loaded page`

**DevTools handoff**

- `I already have the failing request selected in DevTools. Explain why it returns 403`
- `I clicked into the broken element in Elements. Figure out why the layout is wrong`

**Parallel comparison work**

- `Research the websites of these 5 projects simultaneously and provide a comparative summary`
- `Compare these three product pages and tell me how their onboarding flows differ`

## Installation

Install this skill with the `skills` CLI:

```bash
bunx skills add xixu-me/skills -s use-my-browser
```

If Bun is not available, use `npx`:

```bash
npx skills add xixu-me/skills -s use-my-browser
```

## Prerequisites

This skill works best when the agent can reuse your current Chrome session through Chrome DevTools MCP. For live browser automation, set up Chrome remote debugging first, then configure the MCP server to attach automatically to the running browser.

> [!IMPORTANT]
> Make sure Chrome is already running before you start. Otherwise, the agent may be unable to attach to your current browser session and may fall back to a separate isolated browser session instead.

In Chrome (>=144), navigate to `chrome://inspect/#remote-debugging` to enable remote debugging.

![Screenshot showing how to enable remote debugging in Chrome](https://developer.chrome.com/static/blog/chrome-devtools-mcp-debug-your-browser-session/image/chrome-remote-debugging.png)

To connect the Chrome DevTools MCP server to the running Chrome instance, use the `--autoConnect` command line argument in the MCP server configuration.

You can run it with either Bun or npm:

```bash
bunx chrome-devtools-mcp@latest --autoConnect --no-usage-statistics
```

```bash
npx chrome-devtools-mcp@latest --autoConnect --no-usage-statistics
```

Many agent runtimes use a JSON-style MCP configuration like this:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "bunx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--autoConnect",
        "--no-usage-statistics"
      ]
    }
  }
}
```

For Codex, the MCP configuration can look like this:

```toml
[mcp_servers.chrome-devtools]
command = "bunx"
args = ["chrome-devtools-mcp@latest", "--autoConnect", "--no-usage-statistics"]
```

## Strategy Model

This skill is not just a bundle of browser tricks. It teaches a browsing strategy.

### 1. Define success before choosing tools

The agent starts with the goal, not the tool. It first determines whether the task is citation-heavy, interaction-heavy, debugging-heavy, or dependent on the user's current browser state.

### 2. Start with the cheapest layer that can succeed

The default routing model is:

1. public web search and page reads
2. processed content reads
3. raw fetches for source HTML, headers, or direct assets
4. live Chrome DevTools session
5. clean browser automation

This is an escalation model, not a rigid ladder. If the task obviously depends on the current signed-in browser state, the agent should start with the live session.

### 3. Treat each result as evidence

Each step should update the plan. Search results, snapshots, requests, console logs, and screenshots are evidence, not ceremony. The skill encourages agents to stop repeating failed tactics and to switch layers when the current one is no longer informative.

### 4. Preserve the user's browser session

When using the live browser:

- reuse the current page only when its state is actually the point of the task
- otherwise open or use a dedicated working tab
- avoid closing, reloading, or hijacking tabs the user may still care about
- prefer structured extraction over intrusive interaction

### 5. Prefer primary sources over recycled summaries

Search is for discovery. Verification should come from primary sources, official docs, direct pages, raw responses, and live-session evidence where needed.

## How The Skill Implements This

The skill is split into a main policy file and a small set of focused references:

- [`SKILL.md`](./SKILL.md): the main decision model, safety rules, escalation logic, and examples
- [`references/tool-matrix.md`](./references/tool-matrix.md): routing rules for choosing between public web, raw fetches, live browser tooling, and clean browser contexts
- [`references/session-playbook.md`](./references/session-playbook.md): session hygiene, login handling, DOM-first extraction, and live-session fallback patterns
- [`references/browser-recipes.md`](./references/browser-recipes.md): concrete browser operations and tool mappings
- [`references/site-patterns/README.md`](./references/site-patterns/README.md): how to store validated site-specific notes without turning guesses into policy

Together, these files form the skill's "scheduling strategy" layer:

- what to try first
- when to escalate
- when to switch modes
- how to keep independent research tasks separate
- how to avoid unnecessary browser intrusion

## When To Use It

Use this skill when:

- the user wants web research, page inspection, or browser interaction and tool choice matters
- the task depends on the current browser session, cookies, or sign-in state
- the user already has the relevant page, DevTools element, or network request open
- the target is a dynamic or anti-bot-heavy site where static fetches are unreliable
- the task needs DOM, console, network, performance, or rendered-state evidence
- you need a deliberate approach to comparing several websites or public sources

## When Not To Use It

Do not use this skill when:

- the task is purely local and does not involve the web
- a normal public-web read is already enough and no browser decision is needed
- the user explicitly does not want their live browser session touched
- the job is purely isolated automation and does not benefit from the live-session routing model

## What Makes It Different

Most browser-oriented skills focus on how to drive a browser. This one focuses on when, why, and at what layer to do that.

That makes it a better fit for agents that need judgment, not just clicks.

## References

- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Let your Coding Agent debug your browser session with Chrome DevTools MCP](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)

## Inspiration

- [Web Access](https://github.com/eze-is/web-access)
