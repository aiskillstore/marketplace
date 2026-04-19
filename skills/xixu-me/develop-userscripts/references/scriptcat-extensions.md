# ScriptCat Extensions

Distilled from the current ScriptCat developer docs:

- <https://docs.scriptcat.org/docs/dev/background/>
- <https://docs.scriptcat.org/docs/dev/config/>
- <https://docs.scriptcat.org/docs/dev/subscribe/>
- <https://docs.scriptcat.org/docs/dev/cloudcat/>
- <https://docs.scriptcat.org/docs/use/open-dev/>

Use this reference when the task goes beyond a normal portable userscript.

## `@background`

- ScriptCat background scripts are ScriptCat-specific and run in a sandbox without DOM access.
- Use them for persistent workers, manager-managed state, and tasks that should continue after script enablement or browser start.
- Background logs show up in ScriptCat's run log via `GM_log`.

## `@crontab`

- Cron scripts are a form of background script for repeated scheduled work.
- Only the first `@crontab` entry in a script is effective.
- Prefer the standard 5-field cron form. ScriptCat also supports a 6-field seconds form, but its own docs discourage it.
- ScriptCat adds `once` and `once(expr)` to prevent repeated execution inside the same time period.
- Keep single-run time plus retry delay below the cron interval or runs can overlap.

## Async Completion and `CATRetryError`

- If a ScriptCat background or cron script does asynchronous work, return a `Promise`.
- Resolve or reject only after the real work is finished. Once you settle the promise, ScriptCat considers the run complete and later GM operations may no longer take effect.
- To request retry, reject with `new CATRetryError(message, seconds)`.
- ScriptCat documents a minimum retry delay of 5 seconds.

## Debugging Background Scripts

- The editor can debug background scripts, but ScriptCat documents that value sync and registered menu commands do not behave like the real runtime there.
- For real-environment debugging, enable browser support for userscripts first, then open the extension's `background.html` page from the extension settings.
- On Manifest V3 browsers, ScriptCat may require `Allow User Scripts` or browser developer mode, depending on browser version and engine.

## `==UserConfig==`

- Place the `==UserConfig==` block after `==UserScript==`.
- The config block uses YAML, not JavaScript object syntax.
- ScriptCat exposes values through storage keys shaped like `group.key`, which you read with `GM_getValue`.

## Minimal `==UserConfig==` Example

```javascript
// ==UserScript==
// @name         Configurable Script
// @namespace    https://example.com/
// @version      0.1.0
// @match        https://example.com/*
// ==/UserScript==

/* ==UserConfig==
settings:
  apiToken:
    title: API Token
    type: text
    password: true
    default: ""
  enabled:
    title: Enabled
    type: checkbox
    default: true
==/UserConfig== */

const enabled = GM_getValue("settings.enabled", true);
```

## `==UserSubscribe==`

- Subscription packages must start with `==UserSubscribe==`, not `==UserScript==`.
- ScriptCat recommends the `.user.sub.js` suffix for installation links and requires HTTPS.
- Subscription install asks for confirmation once, then later updates are silent unless the declared `connect` permission changes.
- A subscription can install multiple scripts through repeated `@scriptUrl` entries.
- Subscription-level `@connect` overrides the child scripts' own `connect` metadata.
- `@version` is the cleanest update signal. If omitted, ScriptCat falls back to content-change detection for the subscription file itself.

## CloudCat Caveats

- CloudCat is described as a FaaS-style path for cloud execution and is still documented as under development.
- Uploading to cloud changes the meaning of `once` in cron expressions by collapsing it to the earliest matching time in the larger period.
- Cloud execution only supports a reduced API set. ScriptCat currently documents `GM_xmlhttpRequest`, `GM_notification`, `GM_log`, and `GM_getValue`, with `GM_getValue` limited to exported values.
- Use `@exportValue` and `@exportCookie` to describe which state or cookies move to the cloud runtime.
- ScriptCat documents local export as a zip plus Node.js runner and Tencent Cloud as a hosted target.
