# Browser Automation Tools Reference

Complete documentation for all 45 MCP tools provided by rust-browser-mcp.

## Navigation Tools

### navigate
Navigate to a URL in the browser.
```json
{
  "url": "https://example.com",
  "session_id": "optional_session_id"
}
```

### back
Navigate back in browser history.
```json
{
  "session_id": "optional_session_id"
}
```

### forward
Navigate forward in browser history.
```json
{
  "session_id": "optional_session_id"
}
```

### refresh
Reload the current page.
```json
{
  "session_id": "optional_session_id"
}
```

## Element Interaction Tools

### find_element
Find a single element on the page.
```json
{
  "selector": "CSS selector or XPath",
  "by": "css" | "xpath" | "id" | "name" | "tag" | "class",
  "session_id": "optional_session_id"
}
```

### find_elements
Find multiple elements matching a selector.
```json
{
  "selector": "CSS selector or XPath",
  "by": "css" | "xpath" | "id" | "name" | "tag" | "class",
  "session_id": "optional_session_id"
}
```

### click
Click on an element.
```json
{
  "selector": "button.submit",
  "by": "css",
  "session_id": "optional_session_id"
}
```

### send_keys
Type text into an input element.
```json
{
  "selector": "#email",
  "text": "user@example.com",
  "by": "css",
  "session_id": "optional_session_id"
}
```

### hover
Hover over an element.
```json
{
  "selector": ".dropdown-trigger",
  "by": "css",
  "session_id": "optional_session_id"
}
```

### scroll_to_element
Scroll until an element is visible.
```json
{
  "selector": "#footer",
  "by": "css",
  "session_id": "optional_session_id"
}
```

### wait_for_element
Wait for an element to appear on the page.
```json
{
  "selector": ".loading-complete",
  "by": "css",
  "timeout_ms": 5000,
  "session_id": "optional_session_id"
}
```

## Form Tools

### fill_and_submit_form
Fill a form and submit it.
```json
{
  "form_selector": "form#login",
  "fields": {
    "#username": "myuser",
    "#password": "mypass"
  },
  "submit_selector": "button[type='submit']",
  "session_id": "optional_session_id"
}
```

### login_form
Specialized login form handler.
```json
{
  "username_selector": "#email",
  "password_selector": "#password",
  "username": "user@example.com",
  "password": "secretpassword",
  "submit_selector": "button.login",
  "session_id": "optional_session_id"
}
```

## Information Extraction Tools

### get_title
Get the page title.
```json
{
  "session_id": "optional_session_id"
}
```

### get_text
Get text content from an element.
```json
{
  "selector": ".article-content",
  "by": "css",
  "session_id": "optional_session_id"
}
```

### get_attribute
Get an attribute value from an element.
```json
{
  "selector": "a.download",
  "attribute": "href",
  "by": "css",
  "session_id": "optional_session_id"
}
```

### get_property
Get a DOM property from an element.
```json
{
  "selector": "#checkbox",
  "property": "checked",
  "by": "css",
  "session_id": "optional_session_id"
}
```

### get_page_source
Get the full HTML source of the page.
```json
{
  "session_id": "optional_session_id"
}
```

### get_current_url
Get the current page URL.
```json
{
  "session_id": "optional_session_id"
}
```

### get_page_load_status
Check if the page has finished loading.
```json
{
  "session_id": "optional_session_id"
}
```

## Visual Tools

### screenshot
Take a screenshot of the current page.
```json
{
  "path": "/tmp/screenshot.png",
  "full_page": false,
  "session_id": "optional_session_id"
}
```

### resize_window
Resize the browser window.
```json
{
  "width": 1920,
  "height": 1080,
  "session_id": "optional_session_id"
}
```

## JavaScript Execution

### execute_script
Execute JavaScript in the browser context.
```json
{
  "script": "return document.querySelectorAll('.item').length;",
  "args": [],
  "session_id": "optional_session_id"
}
```

## Performance Monitoring Tools

### get_performance_metrics
Get detailed page performance metrics.
```json
{
  "session_id": "optional_session_id"
}
```
Returns: Navigation timing, resource timing, first paint, DOM content loaded, etc.

### monitor_memory_usage
Monitor JavaScript heap memory usage.
```json
{
  "session_id": "optional_session_id"
}
```
Returns: Used heap size, total heap size, heap limit.

### get_console_logs
Retrieve browser console logs.
```json
{
  "level": "all" | "error" | "warning" | "info" | "log",
  "session_id": "optional_session_id"
}
```

### run_performance_test
Run automated performance analysis.
```json
{
  "url": "https://example.com",
  "iterations": 3,
  "session_id": "optional_session_id"
}
```
Returns: Average load times, performance score, recommendations.

### monitor_resource_usage
Monitor ongoing resource usage.
```json
{
  "duration_ms": 5000,
  "session_id": "optional_session_id"
}
```
Returns: Network requests, FPS, CPU usage estimates.

## Driver Management Tools

### start_driver
Start a WebDriver process.
```json
{
  "browser": "chrome" | "firefox" | "edge",
  "headless": true
}
```

### stop_driver
Stop a specific WebDriver process.
```json
{
  "browser": "chrome" | "firefox" | "edge"
}
```

### stop_all_drivers
Stop all running WebDriver processes.
```json
{}
```

### list_managed_drivers
List all managed driver processes.
```json
{}
```
Returns: Running drivers with PIDs and health status.

### get_healthy_endpoints
Get list of healthy WebDriver endpoints.
```json
{}
```

### refresh_driver_health
Force a health check on all drivers.
```json
{}
```

### force_cleanup_orphaned_processes
Clean up any orphaned driver processes.
```json
{}
```

## Recipe Tools

### create_recipe
Create a reusable automation recipe.
```json
{
  "name": "login-workflow",
  "description": "Automates login process",
  "version": "1.0.0",
  "parameters": {
    "username": {"type": "string", "required": true},
    "password": {"type": "string", "required": true}
  },
  "browsers": ["chrome", "firefox"],
  "steps": [
    {
      "name": "navigate-to-login",
      "action": "navigate",
      "arguments": {"url": "https://example.com/login"}
    },
    {
      "name": "fill-username",
      "action": "send_keys",
      "arguments": {"selector": "#username", "text": "${username}"}
    },
    {
      "name": "fill-password",
      "action": "send_keys",
      "arguments": {"selector": "#password", "text": "${password}"}
    },
    {
      "name": "submit",
      "action": "click",
      "arguments": {"selector": "button[type='submit']"}
    }
  ]
}
```

### execute_recipe
Execute a saved recipe.
```json
{
  "name": "login-workflow",
  "parameters": {
    "username": "myuser",
    "password": "mypass"
  },
  "session_id": "optional_session_id"
}
```

### list_recipes
List all available recipes.
```json
{}
```

### delete_recipe
Delete a saved recipe.
```json
{
  "name": "recipe-name"
}
```

## Session ID Conventions

Session IDs can include browser prefixes to route to specific browsers:
- `chrome_*` - Routes to Chrome
- `firefox_*` - Routes to Firefox
- `edge_*` - Routes to Edge

Examples:
- `chrome_user1` - Chrome session for user 1
- `firefox_testing` - Firefox session for testing
- `main` - Uses default/preferred browser
