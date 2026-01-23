# Recipe System Guide

Recipes are reusable automation workflows that can be created, stored, and executed with parameter substitution.

## Recipe Structure

```json
{
  "name": "recipe-name",
  "description": "What this recipe does",
  "version": "1.0.0",
  "parameters": {
    "param_name": {
      "type": "string",
      "required": true,
      "default": "optional default value",
      "description": "What this parameter is for"
    }
  },
  "browsers": ["auto", "chrome", "firefox", "edge"],
  "steps": []
}
```

## Step Structure

```json
{
  "name": "step-name",
  "action": "tool_name",
  "arguments": {
    "arg1": "value",
    "arg2": "${parameter_name}"
  },
  "continue_on_error": false,
  "retry_count": 3,
  "retry_delay_ms": 1000,
  "condition": "javascript expression",
  "session_id": "optional",
  "browser": "optional browser override"
}
```

### Step Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Human-readable step name |
| `action` | Yes | MCP tool name to execute |
| `arguments` | Yes | Arguments for the tool |
| `continue_on_error` | No | Continue if step fails (default: false) |
| `retry_count` | No | Number of retries on failure |
| `retry_delay_ms` | No | Delay between retries |
| `condition` | No | JavaScript condition to evaluate |
| `session_id` | No | Override session for this step |
| `browser` | No | Override browser for this step |

## Parameter Substitution

Use `${param_name}` syntax in arguments to substitute values:

```json
{
  "action": "send_keys",
  "arguments": {
    "selector": "#email",
    "text": "${email_address}"
  }
}
```

## Example Recipes

### Login Workflow

```json
{
  "name": "login-workflow",
  "description": "Automates login to a website",
  "version": "1.0.0",
  "parameters": {
    "url": {
      "type": "string",
      "required": true,
      "description": "Login page URL"
    },
    "username": {
      "type": "string",
      "required": true
    },
    "password": {
      "type": "string",
      "required": true
    }
  },
  "browsers": ["auto"],
  "steps": [
    {
      "name": "navigate-to-login",
      "action": "navigate",
      "arguments": {"url": "${url}"}
    },
    {
      "name": "wait-for-form",
      "action": "wait_for_element",
      "arguments": {
        "selector": "form",
        "timeout_ms": 5000
      }
    },
    {
      "name": "enter-username",
      "action": "send_keys",
      "arguments": {
        "selector": "input[name='username'], input[type='email'], #username, #email",
        "text": "${username}"
      }
    },
    {
      "name": "enter-password",
      "action": "send_keys",
      "arguments": {
        "selector": "input[type='password'], #password",
        "text": "${password}"
      }
    },
    {
      "name": "submit-form",
      "action": "click",
      "arguments": {
        "selector": "button[type='submit'], input[type='submit'], .login-button"
      }
    },
    {
      "name": "wait-for-redirect",
      "action": "wait_for_element",
      "arguments": {
        "selector": ".dashboard, .home, .welcome",
        "timeout_ms": 10000
      },
      "continue_on_error": true
    }
  ]
}
```

### Web Scraping Template

```json
{
  "name": "scrape-list",
  "description": "Scrapes a list of items from a page",
  "version": "1.0.0",
  "parameters": {
    "url": {
      "type": "string",
      "required": true
    },
    "item_selector": {
      "type": "string",
      "required": true,
      "description": "CSS selector for list items"
    }
  },
  "browsers": ["chrome"],
  "steps": [
    {
      "name": "load-page",
      "action": "navigate",
      "arguments": {"url": "${url}"}
    },
    {
      "name": "wait-for-content",
      "action": "wait_for_element",
      "arguments": {
        "selector": "${item_selector}",
        "timeout_ms": 10000
      }
    },
    {
      "name": "scroll-to-load-all",
      "action": "execute_script",
      "arguments": {
        "script": "window.scrollTo(0, document.body.scrollHeight); return true;"
      }
    },
    {
      "name": "find-all-items",
      "action": "find_elements",
      "arguments": {
        "selector": "${item_selector}"
      }
    },
    {
      "name": "extract-data",
      "action": "execute_script",
      "arguments": {
        "script": "return Array.from(document.querySelectorAll('${item_selector}')).map(el => ({text: el.textContent, href: el.href || null}))"
      }
    }
  ]
}
```

### Performance Audit

```json
{
  "name": "performance-audit",
  "description": "Run performance audit on a URL",
  "version": "1.0.0",
  "parameters": {
    "url": {
      "type": "string",
      "required": true
    }
  },
  "browsers": ["chrome"],
  "steps": [
    {
      "name": "navigate",
      "action": "navigate",
      "arguments": {"url": "${url}"}
    },
    {
      "name": "wait-for-load",
      "action": "wait_for_element",
      "arguments": {
        "selector": "body",
        "timeout_ms": 30000
      }
    },
    {
      "name": "get-metrics",
      "action": "get_performance_metrics",
      "arguments": {}
    },
    {
      "name": "check-memory",
      "action": "monitor_memory_usage",
      "arguments": {}
    },
    {
      "name": "get-errors",
      "action": "get_console_logs",
      "arguments": {"level": "error"}
    },
    {
      "name": "screenshot",
      "action": "screenshot",
      "arguments": {
        "path": "/tmp/audit-${url}.png"
      }
    }
  ]
}
```

### Multi-Browser Testing

```json
{
  "name": "cross-browser-test",
  "description": "Test page rendering across browsers",
  "version": "1.0.0",
  "parameters": {
    "url": {
      "type": "string",
      "required": true
    }
  },
  "browsers": ["chrome", "firefox"],
  "steps": [
    {
      "name": "load-in-chrome",
      "action": "navigate",
      "arguments": {"url": "${url}"},
      "browser": "chrome"
    },
    {
      "name": "screenshot-chrome",
      "action": "screenshot",
      "arguments": {"path": "/tmp/chrome-screenshot.png"},
      "browser": "chrome"
    },
    {
      "name": "load-in-firefox",
      "action": "navigate",
      "arguments": {"url": "${url}"},
      "browser": "firefox"
    },
    {
      "name": "screenshot-firefox",
      "action": "screenshot",
      "arguments": {"path": "/tmp/firefox-screenshot.png"},
      "browser": "firefox"
    }
  ]
}
```

## Best Practices

### 1. Use Descriptive Names
Give recipes and steps clear, descriptive names that explain their purpose.

### 2. Add Wait Steps
Always add `wait_for_element` steps before interacting with dynamic content.

### 3. Handle Errors Gracefully
Use `continue_on_error` for non-critical steps and `retry_count` for flaky operations.

### 4. Parameterize Everything
Make recipes reusable by parameterizing URLs, selectors, and input values.

### 5. Document Parameters
Add descriptions to all parameters explaining what they're for.

### 6. Version Your Recipes
Increment the version number when making changes to track recipe evolution.

### 7. Test Across Browsers
Use the `browsers` field to specify which browsers the recipe is compatible with.

## Execution

Execute recipes using the `execute_recipe` tool:

```json
{
  "name": "login-workflow",
  "parameters": {
    "url": "https://myapp.com/login",
    "username": "testuser",
    "password": "testpass123"
  },
  "session_id": "chrome_test"
}
```

The recipe executor will:
1. Validate all required parameters are provided
2. Substitute parameters in step arguments
3. Execute each step in order
4. Handle retries and error conditions
5. Return results from all steps
