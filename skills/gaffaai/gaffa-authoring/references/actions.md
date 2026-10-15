# gaffa action parameter catalog

Per-action parameters, fetched from the live gaffa docs.
Read this on demand when you need a specific action's parameters.
When in doubt, re-confirm against the live docs (`getPage` on the action's page under `/docs/features/browser-requests/actions/`, or the HTTP fallback), because the docs can change.

## Universal parameters (every action)

- `type` (string, required): the action type identifier, for example `capture_dom`.
- `continue_on_fail` (boolean, optional): continue the run if this action fails.
  Default `false`.
- `custom_id` (string, optional): a custom action identifier, echoed back on the matching action in the response.
  Default `null`.

Actions run in the order they are submitted.

## Selectors

Every `selector` parameter below runs through Playwright's selector engine, not plain CSS.
All standard CSS works, and so do Playwright's extensions, text selectors such as `:has-text('foo')` and `:text('foo')`, `:visible`, and XPath.
Pseudo-elements such as `::before` cannot be targeted, there is no real element to return.
Elements inside same-origin iframes are reached with a plain selector, no frame targeting needed.
Cross-origin iframes are currently out of reach, a selector cannot match inside them.
Full reference: `/docs/features/browser-requests/selectors`.

## Actions without outputs

### click
- `selector` (string, required): selector for the element to click.
- `timeout` (integer, optional): max wait for the element.
  Default 5000 ms.

Click waits up to its timeout for the element, so no `wait` before it.
Prefer stable selectors (`id`, `data-testid`, `aria-label`) over generated class names or positional ones.
Set `continue_on_fail: true` on clicks for cookie banners and pop-ups that may not appear.
After a click that loads new content, `wait` for that content before capturing.

### scroll
- `percentage` (integer, required): the position to scroll to, not a distance, so 50 is halfway down and 100 the bottom.
  Default 100.
  Scrolling only goes down, so emit 0 to 100.
- `wait_time` (integer, optional): after the scroll, keep watching the page and keep scrolling as loading content grows it.
  Default 0.
- `max_scroll_time` (integer, optional): max scroll duration.
  Default 20000 ms.
- `scroll_speed` (string, optional): one of `slow`, `medium`, `instant`.
  Default `medium`.
- `interval` (integer, optional): pause between scroll events in ms. Default 0.
- `timeout` (integer, optional): wait for a scrollable element.
  Default 0.
- `selector` (string, optional): element to scroll.
  Defaults to the page body.

For infinite scroll, set `wait_time` so the scroll follows the growing page, and cap it with `max_scroll_time`.
Match `scroll_speed` to the site: `instant` when nothing throttles, `slow` when fast scrolling gets throttled, and `instant` with a large `interval` when the limits are strict.
Hitting `max_scroll_time` stops the scroll without failing, later actions still run.
Scroll a modal or side panel by passing its `selector`, scrolling the body will not move it.
If rows vanish while scrolling past them, put `block_dom_removals` before the scroll.
There is no scrolling back up, so order the actions to need one downward pass only.

### select
- `selector` (string, required): selector for the `<select>` element.
- `values` (array, required): the options to choose, one object per option with `value` or `label`.
  `value` matches the option's HTML `value` attribute, `label` matches its visible text and is only used when `value` is absent or empty.
  When both are set, `value` is used and `label` is ignored.
- `timeout` (integer, optional): max wait for the element.
  Default 5000 ms.

Only a native `<select>` works, a custom dropdown built from `div` or `input[role='combobox']` takes a `click`.
Target the `<select>` itself, not a wrapper.
For a multi-select, every item in `values` is applied to the same `<select>`.
An item that matches no option is skipped, the action succeeds when at least one item matched and fails only when none did.
The browser does not update the `selected` attribute, so `capture_dom` and `capture_element` look unchanged after a successful select, confirm with `capture_screenshot`.
If the dropdown loads after the page, `wait` for it first.

### type
- `selector` (string, required): input field selector.
- `text` (string, required): text to enter.
- The docs currently list no `timeout` for this action.
  If the form renders late, `wait` for the field first.

Typing does not submit, follow with a `click` on the submit button and a `wait` for what comes next.
Target the input element itself, not its wrapper.
Inside attribute selectors use single quotes (`input[name='email']`) so the selector needs no escaping in the JSON string.
One `type` action per field, checkboxes, radios and custom dropdowns take a `click`, a native `<select>` takes `select`.
Close a cookie banner or modal with a `click` first, an overlay blocks the field even when the selector is right.

### wait
- `time` (integer, optional): milliseconds to wait.
- `selector` (string, optional): selector to wait for.
- `timeout` (integer, optional): max wait for the selector.
  Default 5000 ms.

Prefer a `selector` wait over a fixed `time`, it moves on as soon as the element appears.
Never set both, `time` silently wins and the selector is ignored.
No `wait` is needed before `click`, `capture_element`, or `parse_table`, they wait for their own selector.
Set `continue_on_fail: true` when the awaited element may never appear.

### block_dom_removals
- No parameters beyond the universal ones are documented.

Run it first, it only protects what happens after it and cannot restore what the page already removed.
It stays in force for the rest of the request.
The usual shape is `block_dom_removals`, then `scroll`, then the capture.

## Actions with outputs

### capture_cookies
- No parameters beyond the universal ones are documented.

Place it after the actions that set the cookies, so a login flow ends `type`, `click`, `wait`, then `capture_cookies`.
It returns cookie names and values only, no domain, expiry or flags.
Cookies cannot be replayed into another request, every browser request starts a fresh session.
Treat the output as credentials.

### capture_dom
- No parameters beyond the universal ones are documented.

Do not send the output to an LLM, `generate_simplified_dom` and `generate_markdown` carry nearly the same information in far fewer tokens.
There is no `selector` here, capturing part of the page means `capture_element`.
If content is missing from the capture, the page was not done loading, `wait` for a selector of the expected content first.

### capture_screenshot
- `size` (string, optional): one of `view`, `fullscreen`.
  Default `view`.

`view` captures the visible viewport, `fullscreen` the whole page.
On pages that lazy-load images, scroll to 100 with a `wait_time` first or they come out blank.
There is no single-element screenshot, use `capture_element` for the HTML or scroll the element into view.

### capture_snapshot
- No parameters beyond the universal ones are documented.

The saved file has JavaScript switched off, so open tabs and expand sections with `click` and `wait` before capturing.
Reach for it when the page will be read or searched later, `capture_screenshot` only shows it, `print` makes a paper-style PDF.

### capture_element
- `selector` (string, required): selector for the target element.
- `timeout` (integer, optional): max wait for the element.
  Default 5000 ms.

It waits for its selector up to the timeout, so no `wait` before it, and a generous timeout does not slow a successful run.
Only the first match is captured, target a shared container to get more than one element.
Prefer it over `capture_dom` when you know where the content lives.

### download_file
- `timeout` (integer, optional): max download wait.
  Default 5000 ms.

Only the documented file types download: .pdf, .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg, .tiff, .tif, .img.
Each action returns the most recent download and consumes it, so emit one `download_file` per expected file, each with a `custom_id`.
Never emit more `download_file` actions than there are files, the extra ones wait out their timeout and fail.
The stored file keeps its original name.
The default 5000 ms suits small images, documents want more, the docs suggest 20000 ms as a starting point.
A file behind a link is a `click` first, then the download.

### generate_markdown
- `selector` (string, optional): selector for a specific element.
- `output_type` (string, optional): one of `file`, `inline`.
  Default `file`.

The default choice for LLM-bound page content, and `output_type: "inline"` returns it in the response, which suits agents and short pages.
Pass a `selector` such as `main` or `article` to skip navigation and footers.
Tables survive as Markdown tables, but code that processes a table wants `parse_table` instead.

### generate_simplified_dom
- No parameters beyond the universal ones are documented.

The selector-discovery step: run it, read the stable ids and classes, then write the other actions' selectors from what is there.
Query strings are stripped from links, use `capture_dom` when URL parameters matter.

### print
- `size` (string, optional): paper size, `A4` is the only accepted value at the moment.
  Default `A4`.
- `margin` (integer, optional): margin in pixels.
  Default 20.
- `orientation` (string, optional): one of `portrait`, `landscape`.
  Default `portrait`.

The PDF follows the site's print styles, so it can differ from the screen, `capture_screenshot` with `size: "fullscreen"` keeps the screen look.
Wide content such as tables wants `landscape`, edge-to-edge designs want `margin: 0`.
A page that already is a PDF wants `download_file`, not `print`.

### parse_json
Token-priced, so surface cost as token-based, not deterministic.
The documented rate for `gpt-4o-mini` is 1 credit per 20,000 input tokens and 1 credit per 10,000 output tokens, re-check the live docs before quoting it.
- `data_schema_id` (string, required if `data_schema` is absent): a saved schema identifier.
- `data_schema` (json, required if `data_schema_id` is absent): an inline schema definition.
  It is a structured object with `name`, `description`, and a `fields` array where each field has `type`, `name`, and `description`.
  The documented field types are `string`, `integer`, `decimal`, `double`, `boolean`, `datetime`, `object`, and `array`, where `object` and `array` take nested `fields`.
  A flat object such as `{"title":"string"}` is rejected and the action fails.
- `instruction` (string, optional): additional parsing instructions.
  This is a sibling parameter of `parse_json`, not a field inside `data_schema`.
- `model` (string, optional): the parsing model.
  Defaults to `gpt-4o-mini`, which is also the only accepted value at the moment.
- `input_token_cap` (integer, optional): max source tokens, longer input is cut off at the cap.
  Default 1000000.
- `selector` (string, optional): selector for a content subset.
- `output_type` (string, optional): one of `file`, `inline`.
  Default `file`.
- `max_pages` (integer, optional): PDF page limit.
  Default: no limit.

Write field descriptions as instructions, the expected format and what to do when the value is missing, not as labels.
A list of items is an `array` field with nested `fields` describing the item shape.
It reads online PDFs too, with `max_pages` capping what is sent to the model.

Compute a deterministic field in the script, not in the schema.
A value that follows a fixed rule from text already on the page (a word-contains flag, a first word, an arithmetic result) belongs in your code, because the extraction will sometimes let the page's subject override the rule.
Verified on the gaffa.dev blog: asking `parse_json` to flag which post titles contain "gaffa" marked every post true on roughly one run in five, likely because the blog is about gaffa, even where the title did not contain the word.
When such a field has to stay in the schema, word it as a literal character check and name the trap, that the site and topic are irrelevant and what the usual answer is.

### parse_table
- `selector` (string, required): selector identifying the table.
- `timeout` (integer, optional): max wait for the table.
  Default 5000 ms.

Headers become the property names, lowercased, and characters other than letters and numbers become underscores, so `Ticket Price (£)` comes back as `ticket_price_`, check the keys before mapping them.
Every value comes back as a string, convert numbers and dates on your side.
Only real `<table>` markup parses, a div grid takes `parse_json` or `capture_element`.
If the table lazy-loads rows, scroll and wait first so the rows exist when it runs.
There is no merged-cell handling, take `capture_dom` plus your own parser for those.

## Flow actions

### loop
Repeats its nested actions in order, so pagination or repeated interaction fits in one request.
Marked as beta in the August 2026 changelog.
- `actions` (action[], required): the actions each iteration runs, any type except another `loop`.
- `iterations` (integer, optional): fixed number of iterations, 1 to 100.
- `max_iterations` (integer, optional): upper bound on iterations when the count is open.
  Default 10, range 1 to 1000.
  With both set, the lower value wins.
- `timeout` (integer, optional): max duration of the whole loop, all iterations together, not each one.
  Default 20000 ms.
- `stop_on_fail` (boolean, optional): end the loop when a nested action fails.
  Default `true`.
  A nested action with `continue_on_fail: true` does not end it.

The basic pagination shape is capture first, then the click to the next page, so the last page is still captured and the click failing on it is what ends the loop.
Size `timeout` for the whole loop, the 20 second default rarely covers many pages.
A loop that hits its timeout fails with `action_timed_out`, and the finished iterations keep their outputs.
The response lists every iteration's nested entries in execution order under the loop entry's `actions` array, with `iterations` on the loop entry, so give the nested actions `custom_id`s to tell them apart.
Dismiss cookie banners before the loop with a `continue_on_fail: true` click, and `wait` for the pagination control before the loop starts.
Set `continue_on_fail: true` on the loop itself when actions follow it, otherwise an early exit cancels them with `action_cancelled`.

## Notes on parse_json

There is no free-form `prompt` parameter.
Extraction is driven by `data_schema` or `data_schema_id`, with `instruction` as an optional refinement.
Do not emit a `prompt` field for `parse_json`.

Verified behavior: running `parse_json` over the full DOM of a large, content-rich page (for example a Wikipedia article) returns `data.error: action_failed` with no `output`, even with a valid `data_schema`.
Narrow the input to fix it: pass a `selector` for the region that holds the data (cheaper, around 2 credits in testing), or set `input_token_cap` (worked but cost more, around 4 credits).
Small pages extract fine without either.

## When to use parse_json

The rule for choosing between `parse_json` and a deterministic path lives in "Choosing an extraction action" in `SKILL.md`, because the choice has to be made before you get here.
If you are reading this page to look up `parse_json` parameters and have not weighed a deterministic path yet, go back and do that first.
