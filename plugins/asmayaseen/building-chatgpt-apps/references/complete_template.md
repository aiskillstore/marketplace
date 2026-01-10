# Complete ChatGPT App Template

## Overview

A ready-to-use template incorporating all best practices learned from building ChatGPT Apps with widgets.

---

## Project Structure

```
my_chatgpt_app/
├── main.py              # FastMCP server with widgets
├── requirements.txt     # Dependencies
└── .env                 # Environment variables (optional)
```

---

## requirements.txt

```
mcp[cli]>=1.9.2
uvicorn>=0.32.0
httpx>=0.28.0
python-dotenv>=1.0.0
```

---

## main.py (Complete Server Template)

```python
"""
ChatGPT App MCP Server with Interactive Widgets

This template includes:
- Widget registry pattern for multiple widgets
- Action buttons using sendFollowUpMessage
- Proper response metadata structure
- Debug logging
"""

import mcp.types as types
from mcp.server.fastmcp import FastMCP

# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "My ChatGPT App"
SERVER_PORT = 8001
MIME_TYPE = "text/html+skybridge"

# ============================================================
# WIDGET DEFINITIONS
# ============================================================

# Main widget with action buttons
MAIN_WIDGET = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Widget</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 24px;
      color: #333;
    }
    .container {
      max-width: 600px;
      margin: 0 auto;
    }
    .card {
      background: rgba(255,255,255,0.98);
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    .header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 2px solid #f0f0f0;
    }
    .header-icon { font-size: 40px; }
    .header-title {
      font-size: 22px;
      font-weight: 600;
      color: #1a1a1a;
    }
    .header-subtitle {
      font-size: 14px;
      color: #666;
      margin-top: 4px;
    }
    .content {
      font-size: 16px;
      line-height: 1.7;
      color: #444;
      margin-bottom: 20px;
    }
    .content p { margin-bottom: 12px; }

    /* Action Buttons - The Pattern That Works */
    .action-buttons {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      padding-top: 16px;
      border-top: 1px solid #eee;
    }
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 12px 20px;
      border: none;
      border-radius: 10px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .btn-primary {
      background: #3b82f6;
      color: white;
    }
    .btn-primary:hover { background: #2563eb; }
    .btn-secondary {
      background: #27ae60;
      color: white;
    }
    .btn-secondary:hover { background: #219a52; }
    .btn-tertiary {
      background: #e67e22;
      color: white;
    }
    .btn-tertiary:hover { background: #d35400; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <div class="header">
        <div class="header-icon">ICON_PLACEHOLDER</div>
        <div>
          <div class="header-title">TITLE_PLACEHOLDER</div>
          <div class="header-subtitle">SUBTITLE_PLACEHOLDER</div>
        </div>
      </div>

      <div class="content">
        CONTENT_PLACEHOLDER
      </div>

      <!-- Action Buttons: Use sendFollowUpMessage for reliability -->
      <div class="action-buttons">
        <button class="btn btn-primary" id="action1Btn">
          ACTION1_ICON ACTION1_LABEL
        </button>
        <button class="btn btn-secondary" id="action2Btn">
          ACTION2_ICON ACTION2_LABEL
        </button>
        <button class="btn btn-tertiary" id="action3Btn">
          ACTION3_ICON ACTION3_LABEL
        </button>
      </div>
    </div>
  </div>

  <script>
    // ========================================
    // ACTION BUTTON HANDLERS
    // Uses sendFollowUpMessage for reliability
    // ========================================

    const actionButtons = {
      action1Btn: 'ACTION1_PROMPT',
      action2Btn: 'ACTION2_PROMPT',
      action3Btn: 'ACTION3_PROMPT'
    };

    Object.entries(actionButtons).forEach(([btnId, prompt]) => {
      document.getElementById(btnId)?.addEventListener('click', async () => {
        if (window.openai?.sendFollowUpMessage) {
          await window.openai.sendFollowUpMessage({ prompt });
        }
      });
    });

    // ========================================
    // OPTIONAL: For selection/data return
    // ========================================

    function sendSelection(action, data) {
      if (window.openai?.toolOutput) {
        window.openai.toolOutput({ action, ...data });
      }
    }

    // ========================================
    // OPTIONAL: For tool chaining
    // ========================================

    async function callTool(name, args) {
      if (window.openai?.callTool) {
        await window.openai.callTool({ name, arguments: args });
      }
    }
  </script>
</body>
</html>'''

# Widget registry - add more widgets here
WIDGETS = {
    "main": {
        "uri": "ui://widget/main.html",
        "html": MAIN_WIDGET,
        "title": "Main Widget",
    },
}

# ============================================================
# SERVER SETUP
# ============================================================

mcp = FastMCP(APP_NAME)


@mcp.resource(
    uri="ui://widget/{widget_name}.html",
    name="Widget Resource",
    mime_type=MIME_TYPE
)
def widget_resource(widget_name: str) -> str:
    """Serve widget HTML by name."""
    if widget_name in WIDGETS:
        return WIDGETS[widget_name]["html"]
    return WIDGETS["main"]["html"]


def _embedded_widget_resource(widget_id: str) -> types.EmbeddedResource:
    """Create embedded widget resource for tool response."""
    widget = WIDGETS[widget_id]
    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget["uri"],
            mimeType=MIME_TYPE,
            text=widget["html"],
            title=widget["title"],
        ),
    )


def listing_meta(widget_id: str = "main") -> dict:
    """Tool metadata for ChatGPT tool listing."""
    widget = WIDGETS[widget_id]
    return {
        "openai.com/widget": {
            "uri": widget["uri"],
            "title": widget["title"]
        }
    }


def response_meta(widget_id: str = "main") -> dict:
    """Response metadata with embedded widget."""
    return {
        "openai.com/widget": _embedded_widget_resource(widget_id)
    }


# ============================================================
# TOOLS
# ============================================================

@mcp.tool(
    annotations={
        "title": "My Tool",
        "readOnlyHint": True,
        "openWorldHint": False,
    },
    _meta=listing_meta(),
)
def my_tool() -> types.CallToolResult:
    """Description of what this tool does."""

    # Debug logging
    print("=== Tool Called ===")

    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text="Here's the widget content."
            )
        ],
        structuredContent={
            # Data available to the widget
            "status": "success",
            "data": {}
        },
        _meta=response_meta(),
    )


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn

    print(f"Starting {APP_NAME} on http://localhost:{SERVER_PORT}")
    print()
    print("Available tools:")
    print("  - my_tool: Description here")
    print()
    print("Connect via: https://your-tunnel.ngrok-free.app/mcp")

    uvicorn.run(
        "main:mcp.app",
        host="0.0.0.0",
        port=SERVER_PORT,
        reload=True
    )
```

---

## Development Workflow

### 1. Start Server

```bash
cd my_chatgpt_app
python main.py
```

### 2. Start ngrok Tunnel

```bash
ngrok http 8001
# Note the https URL
```

### 3. Register in ChatGPT

1. Go to https://chatgpt.com/apps
2. Click Settings (gear icon)
3. Enable **Developer mode**
4. Click **Create app**
5. Fill in:
   - **Name**: Your App Name
   - **MCP Server URL**: `https://abc123.ngrok-free.app/mcp`
   - **Authentication**: No Auth
6. Click **Create**

### 4. Test

1. Start new conversation
2. Type `@YourAppName`
3. Invoke your tool

---

## Customization Checklist

Replace these placeholders in the template:

| Placeholder | Replace With |
|-------------|--------------|
| `APP_NAME` | Your app name |
| `ICON_PLACEHOLDER` | Emoji (e.g., `📚`, `🎮`, `📊`) |
| `TITLE_PLACEHOLDER` | Widget title |
| `SUBTITLE_PLACEHOLDER` | Subtitle or description |
| `CONTENT_PLACEHOLDER` | Main content HTML |
| `ACTION1_ICON/LABEL/PROMPT` | First action button |
| `ACTION2_ICON/LABEL/PROMPT` | Second action button |
| `ACTION3_ICON/LABEL/PROMPT` | Third action button |

---

## Widget Cache Reset

If changes don't appear:

```bash
# 1. Kill everything
lsof -ti:8001 | xargs kill -9
pkill ngrok

# 2. Start fresh
ngrok http 8001
python main.py

# 3. Delete old app in ChatGPT Settings
# 4. Create new app with new ngrok URL
# 5. Test in new conversation
```

---

## Key Learnings Applied

1. **Action Buttons**: Use `sendFollowUpMessage` instead of complex onclick handlers
2. **MIME Type**: Must be `text/html+skybridge`
3. **Response Meta**: Always include `_meta["openai.com/widget"]`
4. **Widget Caching**: Delete and recreate app to see changes
5. **API Checks**: Always use optional chaining (`window.openai?.method`)
6. **Inline Styles**: All CSS must be in `<style>` tags, not external files