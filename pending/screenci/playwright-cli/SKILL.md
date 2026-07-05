---
name: playwright-cli
description: Automate browser interactions, test web pages and work with Playwright tests.
allowed-tools:
  - Bash(playwright-cli:*)
  - Bash(npx:*)
  - Bash(npm:*)
---

<!--
  Adapted from the "playwright-cli" skill in the Microsoft Playwright CLI project
  (https://github.com/microsoft/playwright-cli), Copyright (c) Microsoft Corporation,
  licensed under the Apache License, Version 2.0. Modified by ScreenCI.
  Full license and attribution: see THIRD_PARTY_NOTICES.md and
  licenses/microsoft-playwright-cli-APACHE-2.0.txt in the screenci package.
-->

# Browser Automation with playwright-cli

Use `playwright-cli` to inspect a live page and discover the real flow, stable
selectors, and cookie/consent steps before authoring a ScreenCI `.screenci.ts`
script. It drives a real browser from the CLI: navigate, snapshot, click, type.

## When Inspecting Pages For ScreenCI

- After the first navigation and snapshot, check whether a cookie consent or
  cookie policy banner appeared.
- Identify the exact accept action the video script should use inside its initial
  `hide()` block, preferably a stable locator such as
  `getByRole('button', { name: /accept|accept all|allow all|agree|ok/i })`.
- If multiple consent actions exist, prefer the clear accept/allow action over a
  dismiss-only or settings action.
- Report that cookie-consent click as part of the hidden initial setup, not as a
  visible demo step.

## Quick start

```bash
# open new browser
playwright-cli open
# navigate to a page
playwright-cli goto https://playwright.dev
# interact with the page using refs from the snapshot
playwright-cli click e15
playwright-cli type "page.click"
playwright-cli press Enter
# close the browser
playwright-cli close
```

## Core commands

```bash
playwright-cli open
# open and navigate right away
playwright-cli open https://example.com/
playwright-cli goto https://playwright.dev
playwright-cli type "search query"
playwright-cli click e3
playwright-cli dblclick e7
# --submit presses Enter after filling the element
playwright-cli fill e5 "user@example.com" --submit
playwright-cli hover e4
playwright-cli select e9 "option-value"
playwright-cli check e12
playwright-cli uncheck e12
playwright-cli snapshot
playwright-cli eval "document.title"
playwright-cli eval "el => el.textContent" e5
# get an attribute not visible in the snapshot
playwright-cli eval "el => el.getAttribute('data-testid')" e5
playwright-cli close
```

### Navigation

```bash
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
playwright-cli press Enter
playwright-cli press ArrowDown
```

## Snapshots

After each command, playwright-cli provides a snapshot of the current browser state.

```bash
> playwright-cli goto https://example.com
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
[Snapshot](.playwright-cli/page-2026-02-14T19-22-42-679Z.yml)
```

You can also take a snapshot on demand. Options can be combined.

```bash
# default - save to a file with timestamp-based name
playwright-cli snapshot

# snapshot an element instead of the whole page
playwright-cli snapshot "#main"

# limit snapshot depth for efficiency
playwright-cli snapshot --depth=4
playwright-cli snapshot e34
```

The global `--raw` option strips page status and generated code, returning only
the result value. Use it to pipe output into other tools.

```bash
playwright-cli --raw snapshot > before.yml
playwright-cli click e5
playwright-cli --raw snapshot > after.yml
diff before.yml after.yml
```

## Targeting elements

By default, use refs from the snapshot to interact with page elements.

```bash
# get snapshot with refs
playwright-cli snapshot

# interact using a ref
playwright-cli click e15
```

You can also use css selectors or Playwright locators.

```bash
# css selector
playwright-cli click "#main > button.submit"

# role locator
playwright-cli click "getByRole('button', { name: 'Submit' })"

# test id
playwright-cli click "getByTestId('submit-button')"
```

## Browser Sessions

```bash
# create a named browser session
playwright-cli -s=mysession open example.com
playwright-cli -s=mysession click e6
playwright-cli -s=mysession close

playwright-cli list
# close all browsers
playwright-cli close-all
```

## Installation

If global `playwright-cli` is not available, try a local version:

```bash
npx --no-install playwright-cli --version
```

Otherwise install it globally:

```bash
npm install -g @playwright/cli@latest
```

## Example: Form submission

```bash
playwright-cli open https://example.com/form
playwright-cli snapshot
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot
playwright-cli close
```

</content>
