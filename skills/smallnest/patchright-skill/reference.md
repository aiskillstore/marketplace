# Patchright Skill Reference

## Google Search Processing (Special Case)

### Overview
This skill can be used to automate Google searches and extract search results using the Patchright browser automation library.

### Key Learnings from Google Search Implementation

#### 1. Server Mode Requirement
The skill uses a **server mode** (`scripts/server.py`) that maintains a persistent browser session across multiple commands. This is essential for complex workflows like Google searches that require multiple steps.

```bash
# Start server (required first step)
python scripts/server.py start &

# Check status
python scripts/server.py status

# Stop server when done
python scripts/server.py stop
```

#### 2. Adding Custom Tools
The default server implementation may not include all needed tools. You can add custom tools by modifying `scripts/server.py`:

**Example: Adding an `evaluate` tool for JavaScript execution**

```python
async def evaluate(self, script):
    if not self.page:
        return {"status": "error", "message": "No page open"}
    result = await self.page.evaluate(script)
    return {"status": "success", "result": result}

# Add to handlers dictionary
handlers = {
    # ... existing handlers ...
    "evaluate": lambda: self.evaluate(args["script"]),
}
```

#### 3. Google Search Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Cookie consent page | Navigate directly to search results URL with encoded query |
| Dynamic content loading | Scroll and wait before extracting results |
| Limited results per page | Navigate to next page for more results |
| Complex DOM structure | Use multiple selector strategies |

#### 4. URL Encoding for Chinese Search Terms
When searching with Chinese characters, use URL encoding:

```python
from urllib.parse import quote
search_url = f"https://www.google.com/search?q={quote('2026年Go语言展望')}"
```

#### 5. DOM Selectors for Google Search Results
Google's page structure uses specific selectors:

```javascript
// Main search result containers
document.querySelectorAll("div[data-hveid]")
document.querySelectorAll(".g")
document.querySelectorAll(".MjjYud")

// Title elements
document.querySelectorAll("h3")

// Description elements
document.querySelector(".VwiC3b")
document.querySelector(".st")
document.querySelector(".ITZIwc")
```

### Complete Google Search Workflow

```bash
# 1. Start the server
python scripts/server.py start &
sleep 2

# 2. Launch browser
python scripts/server.py call '{"tool": "launch", "args": {"headless": false}}'

# 3. Navigate directly to search results (bypasses consent page)
python scripts/server.py call '{"tool": "navigate", "args": {"url": "https://www.google.com/search?q=<encoded_query>"}}'

# 4. Scroll to load all results
python scripts/server.py call '{"tool": "evaluate", "args": {"script": "window.scrollTo(0, document.body.scrollHeight);"}}'

# 5. Extract results using JavaScript
python scripts/server.py call '{"tool": "evaluate", "args": {"script": "<extraction_script>"}}'

# 6. Navigate to next page if needed
python scripts/server.py call '{"tool": "evaluate", "args": {"script": "document.querySelector(\"#pnnext\").click();"}}'
```

### JavaScript Extraction Script Template

```javascript
(function() {
  const results = [];
  const h3Elements = document.querySelectorAll("h3");
  const seen = new Set();

  h3Elements.forEach((h3, index) => {
    if (index >= 20) return; // Limit to 20 results

    let parent = h3.closest("div[data-hveid]") || h3.closest("div.g") || h3.parentElement;

    if (parent) {
      const a = parent.querySelector("a");
      const link = a ? a.href : "";

      let description = "";
      const descSelectors = [".VwiC3b", ".st", ".ITZIwc"];
      for (const sel of descSelectors) {
        const descEl = parent.querySelector(sel);
        if (descEl) {
          description = descEl.textContent.trim().substring(0, 200);
          break;
        }
      }

      const key = link || h3.textContent.trim();
      if (!seen.has(key) && h3.textContent.trim() && link) {
        seen.add(key);
        results.push({
          rank: results.length + 1,
          title: h3.textContent.trim(),
          link: link,
          description: description
        });
      }
    }
  });

  return results;
})();
```

### Important Notes

1. **Shell Escaping**: When passing JavaScript to server.py via command line, be careful with quotes and special characters. It's often better to create a Python script file.

2. **Session Persistence**: The server mode maintains the browser session, so you don't need to relaunch the browser for each command.

3. **Server Restart**: After modifying `server.py` (like adding new tools), you must restart the server:
   ```bash
   python scripts/server.py stop
   python scripts/server.py start &
   ```

4. **Screenshot Debugging**: Use screenshots to verify page state when extraction fails:
   ```bash
   python scripts/server.py call '{"tool": "screenshot", "args": {"path": "/tmp/debug.png"}}'
   ```

5. **Multi-Page Result Numbering**: When combining results from multiple pages, the JavaScript extraction script resets the rank counter for each page. You must renumber the results after combining:
   ```python
   # Renumber results sequentially after combining pages
   for i, result in enumerate(results):
       result["rank"] = i + 1
   ```

6. **Using the Ready-Made Script**: The easiest way to perform Google searches is using `scripts/google_search.py`:
   ```bash
   python scripts/google_search.py "<search_query>" [max_results]
   # Example: python scripts/google_search.py "2026年Go语言展望" 20
   ```

### Available Tools

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
