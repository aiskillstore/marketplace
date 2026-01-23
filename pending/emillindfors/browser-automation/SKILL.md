---
name: browser-automation
description: Enterprise-grade browser automation using WebDriver protocol. Use when the user needs to automate web browsers, perform web scraping, test web applications, fill forms, take screenshots, monitor performance, or execute multi-step browser workflows. Supports Chrome, Firefox, and Edge with connection pooling and health management.
allowed-tools: "Read,Bash,Write"
version: "1.0.0"
---

# Browser Automation Skill

This skill provides guidance for using the rust-browser-mcp server to automate web browsers through the WebDriver protocol. It enables enterprise-grade browser control with performance monitoring, multi-session support, and health management.

## Overview

The rust-browser-mcp server provides 45+ MCP tools for browser automation:

### Core Automation Tools (25)
- **Navigation**: `navigate`, `back`, `forward`, `refresh`
- **Element Interaction**: `click`, `send_keys`, `hover`, `find_element`, `find_elements`
- **Information Extraction**: `get_title`, `get_text`, `get_attribute`, `get_property`, `get_page_source`
- **Advanced**: `fill_and_submit_form`, `login_form`, `scroll_to_element`, `wait_for_element`
- **JavaScript**: `execute_script`
- **Visual**: `screenshot`, `resize_window`, `get_current_url`, `get_page_load_status`

### Performance Monitoring Tools (5)
- `get_performance_metrics` - Page load times, resource timing, navigation data
- `monitor_memory_usage` - Heap monitoring, memory leak detection
- `get_console_logs` - Error detection, log filtering
- `run_performance_test` - Automated performance analysis
- `monitor_resource_usage` - Network, FPS, CPU tracking

### Driver Management Tools (7)
- `start_driver`, `stop_driver`, `stop_all_drivers`
- `list_managed_drivers`
- `get_healthy_endpoints`, `refresh_driver_health`
- `force_cleanup_orphaned_processes`

### Recipe System (4)
- `create_recipe` - Create reusable automation workflows
- `execute_recipe` - Run a saved recipe
- `list_recipes` - List all available recipes
- `delete_recipe` - Remove a recipe

## Setup Instructions

### Prerequisites
Ensure you have at least one WebDriver installed:
- **Chrome**: ChromeDriver (must match Chrome version)
- **Firefox**: GeckoDriver
- **Edge**: MSEdgeDriver

### Configuration for Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "browser": {
      "command": "/path/to/rust-browser-mcp",
      "args": ["--transport", "stdio", "--browser", "chrome"]
    }
  }
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBDRIVER_ENDPOINT` | `auto` | WebDriver URL or "auto" for auto-discovery |
| `WEBDRIVER_HEADLESS` | `true` | Run browsers in headless mode |
| `WEBDRIVER_PREFERRED_DRIVER` | - | Preferred browser: chrome, firefox, edge |
| `WEBDRIVER_CONCURRENT_DRIVERS` | `firefox,chrome` | Browsers to start concurrently |
| `WEBDRIVER_POOL_ENABLED` | `true` | Enable connection pooling |
| `WEBDRIVER_POOL_MAX_CONNECTIONS` | `3` | Max connections per driver type |

## Usage Patterns

### Basic Navigation
```
1. Use `navigate` with URL to load a page
2. Use `wait_for_element` to ensure page loads
3. Use `get_title` or `get_text` to verify content
```

### Form Filling
```
1. Navigate to the form page
2. Use `find_element` with CSS selector to locate fields
3. Use `send_keys` to input values
4. Use `click` on submit button, or use `fill_and_submit_form` for convenience
```

### Web Scraping
```
1. Navigate to target page
2. Use `find_elements` to get multiple matching elements
3. Use `get_text` or `get_attribute` to extract data
4. Use `execute_script` for complex DOM traversal
```

### Performance Testing
```
1. Navigate to page under test
2. Use `run_performance_test` for automated analysis
3. Use `get_performance_metrics` for detailed timing data
4. Use `monitor_memory_usage` to detect leaks
5. Use `get_console_logs` to capture errors
```

### Multi-Step Workflows with Recipes
```
1. Define a recipe with `create_recipe` including steps array
2. Each step specifies: action (tool name), arguments, optional retry logic
3. Execute with `execute_recipe` and parameters
4. Recipes support conditions and browser-specific variants
```

## Session Management

### Browser-Specific Sessions
Use session IDs prefixed with browser name for explicit browser control:
- `chrome_session1` - Uses Chrome
- `firefox_work` - Uses Firefox
- `edge_testing` - Uses Edge

### Multi-Session Support
You can run multiple browser sessions concurrently by using different session IDs:
```
Session: chrome_user1 -> Opens first Chrome tab
Session: chrome_user2 -> Opens second Chrome tab
Session: firefox_admin -> Opens Firefox for different workflow
```

## Best Practices

### Error Handling
1. Always use `wait_for_element` before interacting with dynamic content
2. Check `get_page_load_status` for slow-loading pages
3. Use `get_console_logs` to debug JavaScript errors

### Performance
1. Enable connection pooling (default) for better resource usage
2. Reuse session IDs when possible
3. Use headless mode for faster execution

### Security
1. Never store credentials in recipes
2. Use environment variables for sensitive data
3. Clear sessions after authentication workflows

## Troubleshooting

### Driver Not Starting
- Verify WebDriver is installed and in PATH
- Check browser version matches driver version
- Use `list_managed_drivers` to see status

### Element Not Found
- Use browser DevTools to verify selector
- Wait for page load with `wait_for_element`
- Try different selector strategies (CSS, XPath)

### Performance Issues
- Check `monitor_memory_usage` for leaks
- Use `get_console_logs` for JavaScript errors
- Consider reducing concurrent sessions

## Reference Files

See companion files for detailed information:
- `reference/tools.md` - Complete tool documentation
- `reference/recipes.md` - Recipe system guide
- `examples/` - Example automation scripts
