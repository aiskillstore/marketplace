# Steel Browser Commands Reference

Use this reference when you need command-level patterns for navigation, interaction, extraction, and debugging.

## Navigation

```bash
steel browser open <url>
steel browser back
steel browser forward
steel browser reload
steel browser close
steel browser connect 9222
```

## Snapshot and element discovery

```bash
steel browser snapshot
steel browser snapshot -i
steel browser snapshot -c
steel browser snapshot -d 3
steel browser snapshot -s "#main"
```

## Interactions with element refs

```bash
steel browser click @e1
steel browser click @e1 --new-tab
steel browser dblclick @e1
steel browser focus @e1
steel browser fill @e2 "text"
steel browser type @e2 "text"
steel browser press Enter
steel browser press Control+a
steel browser keydown Shift
steel browser keyup Shift
steel browser hover @e1
steel browser check @e1
steel browser uncheck @e1
steel browser select @e1 "value"
steel browser select @e1 "a" "b"
steel browser scroll down 500
steel browser scrollintoview @e1
steel browser drag @e1 @e2
steel browser upload @e1 ./file.pdf
```

## Semantic locator alternatives

```bash
steel browser find role button click --name "Submit"
steel browser find text "Sign In" click
steel browser find text "Sign In" click --exact
steel browser find label "Email" fill "user@test.com"
steel browser find placeholder "Search" type "query"
steel browser find alt "Logo" click
steel browser find title "Close" click
steel browser find testid "submit-btn" click
steel browser find first ".item" click
steel browser find last ".item" click
steel browser find nth 2 "a" hover
```

## Information extraction

```bash
steel browser get text @e1
steel browser get html @e1
steel browser get value @e1
steel browser get attr @e1 href
steel browser get title
steel browser get url
steel browser get count ".item"
steel browser get box @e1
steel browser get styles @e1
```

There is no top-level `steel browser extract` command.
Use `steel browser get ...`, `steel browser snapshot`, and `steel browser find ...`.

## State checks

```bash
steel browser is visible @e1
steel browser is enabled @e1
steel browser is checked @e1
```

## Waiting and synchronization

```bash
steel browser wait @e1
steel browser wait 2000
steel browser wait --text "Success"
steel browser wait --url "**/dashboard"
steel browser wait --load networkidle
steel browser wait --fn "window.ready"
```

## Screenshots, PDFs, and recording

```bash
steel browser screenshot
steel browser screenshot ./page.png
steel browser screenshot --full
steel browser pdf ./output.pdf
steel browser record start ./demo.webm
steel browser record stop
steel browser record restart ./take2.webm
```

Use a positional file path for screenshot output.
Do not use `-o`/`--output` with `steel browser screenshot`.

## Browser settings

```bash
steel browser set viewport 1920 1080
steel browser set device "iPhone 14"
steel browser set geo 37.7749 -122.4194
steel browser set offline on
steel browser set headers '{"X-Key":"v"}'
steel browser set credentials user pass
steel browser set media dark
steel browser set media light reduced-motion
```

## Cookies and storage

```bash
steel browser cookies
steel browser cookies set name value
steel browser cookies clear
steel browser storage local
steel browser storage local key
steel browser storage local set k v
steel browser storage local clear
```

## Network controls

```bash
steel browser network route <url>
steel browser network route <url> --abort
steel browser network route <url> --body '{}'
steel browser network unroute [url]
steel browser network requests
steel browser network requests --filter api
```

## Tabs, windows, frames, and dialogs

```bash
steel browser tab
steel browser tab new [url]
steel browser tab 2
steel browser tab close
steel browser tab close 2
steel browser window new
steel browser frame "#iframe"
steel browser frame main
steel browser dialog accept [text]
steel browser dialog dismiss
```

## JavaScript evaluation

```bash
steel browser eval "document.title"
steel browser eval -b "<base64-script>"
steel browser eval --stdin
```

Prefer `-b` or `--stdin` when script complexity makes shell escaping brittle.

## Session and global options

```bash
steel browser --session <name> ...
steel browser --json ...
steel browser --headed ...
steel browser --full ...
steel browser --cdp <port-or-url> ...
steel browser --proxy <url> ...
steel browser --proxy-bypass <hosts> ...
steel browser --headers <json> ...
steel browser --ignore-https-errors ...
steel browser --help
steel browser --version
steel browser <command> --help
```

## Debugging quick set

```bash
steel browser --headed open example.com
steel browser --cdp 9222 snapshot
steel browser console
steel browser console --clear
steel browser errors
steel browser errors --clear
steel browser highlight @e1
```

## CAPTCHA control

```bash
steel browser start --session <name> --session-solve-captcha
steel browser start --session <name> --stealth
steel browser captcha status
steel browser captcha status --wait
steel browser captcha status --wait --timeout 120000
steel browser captcha status --raw
steel browser captcha solve --session <name>
steel browser captcha solve --session <name> --page-id <id> --task-id <id>
steel browser screenshot /tmp/captcha-progress.png --session <name>
```
