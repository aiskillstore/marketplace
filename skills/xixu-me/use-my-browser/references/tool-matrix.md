# Tool Matrix

Use this table when deciding whether a task should stay on public-web tools, switch into the live browser session, or use a separate automation browser.

| Situation                                                                        | Primary tool                                              | Why                                                                           | Avoid                                                           |
| -------------------------------------------------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Public discovery, recent info, citation-backed answers                           | `web.search_query` plus `web.open`                        | Fast source discovery, easy citations, no browser intrusion                   | Attaching to the browser session just to read public pages      |
| Known public page where rendered state is not important                          | `web.open` or `web.find`                                  | Cheapest read path                                                            | Launching browser tools before proving they are needed          |
| Known article, doc, or PDF where a cheaper processed read is enough              | `web.open` or a markdown mirror such as Jina Reader       | Good for content-first pages and lower token use                              | Jumping straight to a browser for article-shaped pages          |
| Need raw HTML, headers, JSON-LD, or source metadata                              | `shell_command` with a native fetch tool                  | Preserves the original response shape                                         | Treating a processed read as if it were source HTML             |
| Task depends on current sign-in state, cookies, or app context                   | `chrome-devtools`                                         | Reuses the live browser session                                               | Playwright unless the user wants a separate clean state         |
| User already selected an element in Elements                                     | `chrome-devtools.take_snapshot` then `evaluate_script`    | Continues from the existing debugging context                                 | Recreating the page in a new browser by default                 |
| User already selected a request in Network                                       | `chrome-devtools.get_network_request`                     | Reads the current request directly                                            | Listing every request before checking the selected one          |
| Dynamic SPA, lazy loading, console errors, network timing, performance, uploads  | `chrome-devtools`                                         | Best coverage for live DOM, network, and performance evidence                 | Raw fetches that miss app state                                 |
| Social platform or anti-bot-heavy site where static fetches are weak             | `chrome-devtools`                                         | Lets the agent work through the real rendered page and session context        | Assuming search results or static fetches reflect the real page |
| Need a separate clean browser context or reproducible isolated automation        | `playwright`                                              | Best for isolated automation flows                                            | Reusing the live session when state isolation is the goal       |
| Need a downloadable public asset after discovering the real URL in-page          | `shell_command` with a native fetch tool                  | Better than screenshotting a file that is directly fetchable                  | Using screenshots for raw-fetch problems                        |
| Need to inspect or compare several public sources                                | Batched `web` calls                                       | Parallel and citation-friendly                                                | Serial browser attachment for each source                       |
| Need several independent local-doc or shell reads                                | `multi_tool_use.parallel`                                 | Parallelizes developer-tool reads cleanly                                     | Using it for `web` operations or dependent browser actions      |
| User explicitly asks for parallel agent work across independent browsing targets | Goal-driven delegated workers plus isolated page contexts | Keeps independent targets separated without disturbing one mutable page state | Splitting work that depends on one mutable page state           |

## Decision Rules

### Start with `web` when

- The answer should cite public sources.
- The page is not user-specific.
- Search quality is more important than interaction.
- The task can be solved from docs, blogs, release notes, or public pages.
- The first problem is source discovery, not page interaction.

### Start with a processed read when

- The URL is known and the page is mostly article, documentation, or PDF content.
- You want the page text, not its raw HTML.
- Token efficiency matters and the page structure is not highly interactive.

### Start with `chrome-devtools` when

- The task depends on the user's current Chrome state.
- The relevant element or request is already selected in DevTools.
- The target is behind login or requires a current app session.
- You need DOM, console, network, performance, upload, or rendered media from the real page.
- The site is dynamic enough that static fetches are unreliable.

### Start with `playwright` when

- The user wants a clean, separate browser context.
- The task is a browser automation workflow that should not touch the live session.
- The environment does not have the needed Chrome DevTools session attached.

### Start with a raw fetch when

- You need HTML source, response headers, or direct file downloads.
- Browser rendering is not the interesting part.
- The task is about response bodies rather than in-page behavior.
- You already discovered the exact asset or page URL and need its source form.

## Escalation Order

When the first layer fails, escalate thoughtfully:

1. `web`
2. processed read
3. raw fetch
4. `chrome-devtools`
5. `playwright`

This is not a rigid ladder. If the task is obviously logged-in or DevTools-driven from the start, begin with `chrome-devtools`.

## Notes

- `web` already supports batching multiple search or open requests in a single call.
- `multi_tool_use.parallel` is only for developer tools, not the `web` namespace.
- Do not use the live browser session when a public, lower-risk layer is already enough.
- Prefer site-generated URLs over hand-constructed guesses when a page exposes the real link.
