# Patchright Scripts

## Core Server Scripts

- **server.py** - Background server that maintains persistent browser session
- **executor.py** - One-shot command executor (non-persistent session)

## Google Search Utilities

### Main Script
- **google_search.py** - Complete Google search automation script
  ```bash
  python google_search.py "<search_query>" [max_results]
  # Example: python google_search.py "2026年Go语言展望" 20
  ```

### Utility Scripts

#### google_extract_results.py
Extracts search results from the currently open Google search page.
```bash
# First, navigate to a Google search page manually or via scripts
python google_extract_results.py
```

#### google_debug.py
Debug utility to analyze Google search page structure when extraction fails.
```bash
# First, navigate to a Google search page
python google_debug.py
```

## Server Mode Usage

### Start Server
```bash
python server.py start &
```

### Check Status
```bash
python server.py status
```

### Call Tools
```bash
# Format: python server.py call '<json>'
python server.py call '{"tool": "launch", "args": {"headless": false}}'
python server.py call '{"tool": "navigate", "args": {"url": "https://www.google.com"}}'
python server.py call '{"tool": "screenshot", "args": {"path": "screenshot.png"}}'
python server.py call '{"tool": "evaluate", "args": {"script": "document.title"}}'
```

### Stop Server
```bash
python server.py stop
```

## Available Tools

| Tool | Description | Args |
|------|-------------|------|
| launch | Start browser | headless: bool (default: false) |
| close | Close browser | - |
| navigate | Go to URL | url: string (required) |
| screenshot | Save to file | path: string, full_page: bool |
| click | Click element | selector: string (required) |
| type | Type text | selector: string, text: string |
| get_text | Get element text | selector: string |
| evaluate | Execute JavaScript | script: string (required) |
| get_url | Get current URL | - |
| get_title | Get page title | - |

## Adding Custom Tools

To add a new tool to `server.py`:

1. Add the async method:
```python
async def my_tool(self, param):
    if not self.page:
        return {"status": "error", "message": "No page open"}
    # Your logic here
    return {"status": "success", "result": ...}
```

2. Add to handlers dictionary:
```python
handlers = {
    # ... existing handlers ...
    "my_tool": lambda: self.my_tool(args["param"]),
}
```

3. Restart server for changes to take effect.
