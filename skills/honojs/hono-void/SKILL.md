---
name: hono-void
description: Use when checking or testing a Void app with Hono CLI — pages, page actions, and API routes. TRIGGER when package.json depends on 'void', the project has void.config.ts, or the user mentions Void. Void is a framework built on Hono.
---

# Hono Void Skill

[Void](https://void.cloud) builds a Hono app from file-based routes, so there is no entry file and the code does not import `hono`. Verify changes with [Hono CLI](https://github.com/honojs/cli), not with a browser, curl, or a dev server. It runs the app through Vite with no flag and no file argument:

```bash
npm install -D @hono/cli@next
npx hono --help
npx hono routes --exclude /__void   # hide Void's internal routes
npx hono request /
```

For a flow (create, then read), use one `npx hono batch -` call with `expect` on every step. Send `x-voidpages: true` so a page answers with JSON instead of the full HTML. A page action returns 200 even when it fails, so assert on the body (`body` in `expect` is a deep partial match):

```bash
npx hono batch - <<'EOF'
{"method":"POST","path":"/","headers":{"x-voidpages":"true"},"body":{"shop":""},"expect":{"status":200,"body":{"errors":{"shop":"Enter a shop name"}}}}
{"method":"POST","path":"/","headers":{"x-voidpages":"true"},"body":{"shop":"Hono Ramen"},"expect":{"status":200}}
EOF
```

A create that redirects shows its `location`; follow it with `"save":{"next":"header:location"}` and then `"path":"{{next}}"`. An array in `expect` must match the whole array, so check one item of a list by reading the response, not with `expect`. The path, fields, and messages above are an example. Check yours with `npx hono routes` and one request first.

## Checking the page in a browser

HTTP requests do not run the page's JavaScript, so they miss client-side bugs: a form that keeps its values after a submit, or a redirect that lands on the wrong URL. Check those with `npx hono browse`. It loads the page in happy-dom, runs its JavaScript, and fills and clicks in order. Install happy-dom first:

```bash
npm install -D happy-dom
npx hono browse / --fill "Shop name=Hono Ramen" --click 'button[type=submit]'
```

`--fill` takes a field's name, label text, or placeholder (the keys in `forms` of the output), or a CSS selector. The output has the final `url`, the visible `text`, the `forms` values, and `console` errors. happy-dom has no layout or CSS.

## Checking a Void app

- `pages/**` return HTML. Send the header `x-voidpages: true` to get the page data as JSON: `{ component, props, errors, head, ... }`.
- Page actions are POST/PUT/PATCH/DELETE to the page URL. A named action has a `?name` suffix, e.g. `POST /ramen/1?delete`.
- A validation failure in a page action returns 200, not 422, with the messages in `body.errors` (`{ field: message }`). A success has no `errors`.
- A foreign `Origin` header gets 403. Omit `Origin` or use the app's own origin.
- `npx void db seed --yes` resets the local DB between runs.

For Void itself (routing, pages, the Void CLI), read Void's docs in `node_modules/void/docs/`.
