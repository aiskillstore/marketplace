# Browser Recipes

This file lists the concrete browser operations and their closest tool equivalents.

## Processed Read and Raw Fetch Layers

These two layers sit before full browser attachment when the task does not yet need live browser state.

### Processed read

Use a processed read when:

- the URL is already known
- the page is mostly article, documentation, or PDF content
- you need the page text more than the original response shape

Preferred options:

- `web.open` for the standard processed page
- an external markdown mirror only when token savings matter and fidelity is still acceptable for the task

### Raw fetch

Use a raw fetch when:

- you need source HTML, headers, JSON-LD, or a direct asset
- the distinction between rendered text and original response data matters

Preferred options:

- `shell_command` with a native fetch tool such as `Invoke-WebRequest` or `curl.exe`
- save large responses to a file when inline output would be noisy

## Page and Tab Control

| Goal                           | Equivalent tool or action                 |
| ------------------------------ | ----------------------------------------- |
| List open tabs                 | `chrome-devtools.list_pages`              |
| Create a new tab               | `chrome-devtools.new_page`                |
| Switch to an existing tab      | `chrome-devtools.select_page`             |
| Close your own tab             | `chrome-devtools.close_page`              |
| Go to a URL in the current tab | `chrome-devtools.navigate_page`           |
| Go back                        | `chrome-devtools.navigate_page` with back |

## Inspect and Extract

| Goal                                    | Equivalent tool or action                             |
| --------------------------------------- | ----------------------------------------------------- |
| Run arbitrary page script               | `chrome-devtools.evaluate_script`                     |
| Read the accessible page structure      | `chrome-devtools.take_snapshot`                       |
| Get rendered image state                | `chrome-devtools.take_screenshot`                     |
| Inspect the selected request in Network | `chrome-devtools.get_network_request` without `reqid` |
| Inspect broader traffic                 | `chrome-devtools.list_network_requests`               |
| Inspect console output                  | `chrome-devtools.list_console_messages`               |

## Interaction

| Goal                  | Equivalent tool or action             |
| --------------------- | ------------------------------------- |
| Click an element      | `chrome-devtools.click`               |
| Hover an element      | `chrome-devtools.hover`               |
| Fill an input         | `chrome-devtools.fill` or `fill_form` |
| Upload files          | `chrome-devtools.upload_file`         |
| Drag and drop         | `chrome-devtools.drag`                |
| Keyboard-only actions | `chrome-devtools.press_key`           |

## Scroll and Wait Patterns

There is no dedicated `scroll` endpoint in the Chrome DevTools toolset. Use one of these:

- `evaluate_script(() => window.scrollBy(0, 1200))`
- `evaluate_script(() => window.scrollTo(0, document.body.scrollHeight))`
- `press_key("PageDown")` when a keyboard-style interaction is more realistic

After scrolling or a major interaction:

- use `wait_for` if you know the next text or state to wait on
- otherwise re-run `take_snapshot`

## Performance, Memory, and Audits

| Goal                                      | Equivalent tool or action                     |
| ----------------------------------------- | --------------------------------------------- |
| Start a performance trace                 | `chrome-devtools.performance_start_trace`     |
| Stop and save trace                       | `chrome-devtools.performance_stop_trace`      |
| Analyze a highlighted performance insight | `chrome-devtools.performance_analyze_insight` |
| Capture a memory snapshot                 | `chrome-devtools.take_memory_snapshot`        |
| Run a Lighthouse audit                    | `chrome-devtools.lighthouse_audit`            |

## When to Switch to Playwright

Switch to Playwright when:

- The task wants a clean browser context
- The live Chrome session is unavailable and cannot be attached
- The work is browser automation, not reuse of the current signed-in session

Playwright is a fallback, not an equivalent replacement for the user's current browser session or state.
