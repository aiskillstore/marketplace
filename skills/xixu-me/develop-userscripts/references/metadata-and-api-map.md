# Metadata and API Map

Distilled from the current Tampermonkey documentation and ScriptCat developer docs:

- <https://www.tampermonkey.net/documentation.php>
- <https://docs.scriptcat.org/docs/dev/api/>

Use this reference to choose metadata and high-value APIs without copying the full upstream docs into the skill.

## Portable Defaults

- Start ordinary page scripts with `==UserScript==`, `@name`, `@namespace`, `@version`, and at least one `@match`.
- Prefer `@match` for normal site targeting. Reach for `@include` only when you really need broader pattern matching.
- Keep `@grant` minimal and explicit. If you use `GM_*`, list the exact APIs.
- Add explicit `@connect` hosts for every domain touched by `GM_xmlhttpRequest` or `GM_cookie`.
- Use `@run-at` only when timing matters. Do not add it by habit.
- Keep update metadata simple: `@version` first, then `@updateURL`, `@downloadURL`, or `@supportURL` if the distribution model actually needs them.

## Metadata Decisions

| Key                                           | Use it for                      | Practical rule                                                                         |
| --------------------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------- |
| `@match`                                      | page targeting                  | Default choice for normal host and path matching                                       |
| `@include` / `@exclude`                       | legacy or broader pattern cases | Use sparingly when `@match` is not expressive enough                                   |
| `@grant`                                      | privileged APIs                 | Declare only what the script uses so permissions stay readable                         |
| `@connect`                                    | request and cookie hosts        | Prefer explicit hosts first; avoid `*` unless the use case truly requires it           |
| `@run-at`                                     | injection timing                | Add it only when `document-start`, `document-end`, or `document-idle` changes behavior |
| `@sandbox`                                    | Tampermonkey injection context  | Use only when page-context versus isolated-context behavior matters                    |
| `@updateURL` / `@downloadURL` / `@supportURL` | update and support surfaces     | Keep them aligned with the actual release channel                                      |

## Minimal Portable Template

```javascript
// ==UserScript==
// @name         Example Foreground Script
// @namespace    https://example.com/
// @version      0.1.0
// @match        https://app.example.com/*
// @grant        GM_addStyle
// @grant        GM_xmlhttpRequest
// @connect      api.example.com
// @run-at       document-idle
// ==/UserScript==

GM_addStyle(".userscript-ready { outline: 2px solid #0a7; }");

GM_xmlhttpRequest({
  method: "GET",
  url: "https://api.example.com/status",
  onload: (response) => console.log(response.responseText),
});
```

## High-Value APIs

### Storage

- `GM_getValue`, `GM_setValue`, `GM_deleteValue`, and listeners are the first choice for script state.
- In ScriptCat, `GM_setValue(name, undefined)` deletes the key instead of storing `undefined`.
- In ScriptCat, data operations are asynchronous under the hood. If the page may close immediately after a write, prefer the `GM.*` promise form and await completion.

### Menu Commands

- `GM_registerMenuCommand` is useful for manual actions and diagnostics.
- ScriptCat adds menu-specific options such as `autoClose`, `nested`, and `individual`.
- Prefer stable IDs when you need to update or unregister the same command later.

### Notifications

- Use `GM_notification` for visible status, retries, or action prompts.
- ScriptCat extends notification behavior with progress, buttons, and update or close helpers.
- Treat those extra helpers as ScriptCat-specific, not portable Tampermonkey behavior.

### Clipboard

- `GM_setClipboard` is the safer default over raw page clipboard tricks.
- ScriptCat does not support the Tampermonkey callback shape here, so write code that does not depend on it.

### Tabs and Resources

- `GM_openInTab` is the normal path for opening related pages.
- In ScriptCat, prefer the `active` option and avoid old `loadInBackground` semantics unless you are explicitly matching Tampermonkey behavior.
- `GM_getResourceText` and `GM_getResourceURL` are better than ad hoc fetches for packaged resources.

### `GM_xmlhttpRequest`

- Use it when same-origin fetch is blocked, cookies need manager support, or CSP interferes with ordinary requests.
- Treat `@connect` as required design input, not an afterthought.
- ScriptCat supports `text`, `arraybuffer`, `blob`, `json`, `document`, and `stream` response types, but documents partial feature differences and Firefox cookie caveats.
- ScriptCat also documents support for special headers such as `user-agent`, `origin`, `referer`, `cookie`, and `host`.

## Compatibility Notes

- ScriptCat documents only a subset of Tampermonkey APIs and marks its extensions with `*`.
- `GM_info.runAt` is not currently supported in ScriptCat, and `GM_info.sandboxMode` is currently only documented as `raw`.
- Tampermonkey `@sandbox` is a high-leverage knob for page-context behavior. Do not assume ScriptCat gives you the same control surface.
- Keep ordinary page scripts portable first. Move into ScriptCat-only runtime features only when the task needs background execution, cron, config blocks, or subscription packaging.
