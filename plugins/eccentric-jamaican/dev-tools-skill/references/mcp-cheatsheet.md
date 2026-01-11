# MCP DevTools Cheatsheet

## Page control
- `list_pages` -> see open tabs/pages
- `select_page` -> pick target page
- `navigate_page` -> go to URL / reload
- `resize_page` -> set viewport size
- `emulate` -> CPU/network throttling or geolocation

## Observation
- `take_snapshot` -> a11y tree text (primary for DOM checks)
- `take_screenshot` -> visual reference
- `evaluate_script` -> read DOM/JS state (avoid mutations unless needed)

## Interaction
- `click`, `hover`, `press_key` -> reproduce issues
- `fill`, `fill_form` -> input values (confirm before submit)
- `handle_dialog` -> accept/dismiss browser dialogs

## Console
- `list_console_messages` -> list logs/errors
- `get_console_message` -> details for a specific message

## Network
- `list_network_requests` -> list requests
- `get_network_request` -> request details

## Performance
- `performance_start_trace` -> begin tracing
- `performance_stop_trace` -> end trace
- `performance_analyze_insight` -> top CWV insights
