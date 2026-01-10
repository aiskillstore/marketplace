# Debugging ChatGPT Apps

## Overview

This guide covers common issues when developing ChatGPT Apps with widgets and how to resolve them.

---

## Server-Side Debugging

### Enable Debug Logging

Add logging to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

@mcp.tool(_meta=listing_meta())
def my_tool() -> types.CallToolResult:
    print("=== Tool Called ===")
    print(f"Widget HTML length: {len(MY_WIDGET)}")
    print(f"Widget starts with: {MY_WIDGET[:100]}")

    result = types.CallToolResult(
        content=[types.TextContent(type="text", text="Done")],
        _meta=response_meta(),
    )
    print(f"Response meta keys: {result._meta.keys()}")
    return result
```

### Check Server Logs

Watch for these request types:

```
Processing request of type ListToolsRequest    # Tool discovery
Processing request of type ReadResourceRequest # Widget HTML fetch
Processing request of type CallToolRequest     # Tool execution
```

### Verify Server Accessibility

```bash
# Test local server
curl http://localhost:8001

# Test ngrok tunnel
curl https://your-url.ngrok-free.app/mcp
```

---

## Widget Caching Issues

### Symptoms

- Old widget displays instead of updated version
- Changes to HTML not reflected
- Server logs show correct content but browser shows old

### Root Cause

ChatGPT aggressively caches widgets. Once a widget is loaded, it may persist even after server changes.

### Solution: Complete Reset

1. **Delete the app** in ChatGPT Settings > Apps
2. **Kill the server** completely
3. **Kill ngrok** and start new tunnel (new URL)
4. **Create new app** with new ngrok URL
5. **Test in new conversation**

```bash
# Kill everything
lsof -ti:8001 | xargs kill -9
pkill ngrok

# Start fresh
ngrok http 8001
python main.py
```

### Prevention

- Use unique URIs during development: `ui://widget/v2/my-widget.html`
- Test significant changes with fresh app registration

---

## Widget Not Rendering

### Check 1: MIME Type

```python
# Must be exactly this
mimeType="text/html+skybridge"
```

### Check 2: Response Metadata

```python
# Must include this structure
_meta={
    "openai.com/widget": types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri="ui://widget/...",
            mimeType="text/html+skybridge",
            text=HTML_STRING,
            title="...",
        ),
    )
}
```

### Check 3: HTML Structure

```html
<!-- Must be valid HTML5 -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  ...
</head>
<body>
  ...
</body>
</html>
```

### Check 4: Server Receiving Requests

Look for in server logs:
```
Processing request of type CallToolRequest
```

If missing, the tool isn't being called.

---

## Widget Shows "Loading..."

### Causes

1. HTML not delivered
2. JavaScript error in widget
3. Network timeout

### Debug Steps

1. Add visible marker to widget:
   ```html
   <div style="background:red;color:white;padding:20px;">
     WIDGET LOADED
   </div>
   ```

2. Check server logs for `CallToolRequest`

3. Simplify widget to minimal HTML:
   ```html
   <!DOCTYPE html>
   <html>
   <body>
     <h1>Test</h1>
   </body>
   </html>
   ```

---

## window.openai Not Available

### In Browser (Expected)

`window.openai` is only available inside ChatGPT's iframe. It won't work in standalone browser testing.

### Add Fallback for Local Testing

```javascript
// Mock for local development
if (!window.openai) {
  console.log('Running outside ChatGPT, mocking window.openai');
  window.openai = {
    toolOutput: (data) => {
      console.log('Mock toolOutput:', JSON.stringify(data, null, 2));
    },
    sendFollowUpMessage: (data) => {
      console.log('Mock sendFollowUpMessage:', JSON.stringify(data, null, 2));
    },
    callTool: (data) => {
      console.log('Mock callTool:', JSON.stringify(data, null, 2));
    }
  };
}
```

### Defensive Code Pattern

```javascript
function sendAction(action, data) {
  if (window.openai && window.openai.toolOutput) {
    window.openai.toolOutput({ action, ...data });
  } else {
    console.warn('window.openai not available');
  }
}
```

---

## Buttons Not Responding to Clicks

### Symptoms

- Clicking widget buttons does nothing
- No console errors visible
- Buttons appear but aren't interactive
- onclick handlers never fire

### Root Cause

ChatGPT renders widgets in a sandboxed iframe. Buttons may render as **static UI elements** rather than interactive JavaScript buttons. This is a known limitation of the widget environment.

### Solution 1: Use sendFollowUpMessage (Recommended)

Replace complex button handlers with `sendFollowUpMessage`:

```javascript
// Instead of complex onclick handlers
document.getElementById('myBtn')?.addEventListener('click', async () => {
  if (window.openai?.sendFollowUpMessage) {
    await window.openai.sendFollowUpMessage({
      prompt: 'Do the action I want'
    });
  }
});
```

### Solution 2: Simplify Button Logic

Remove complex JavaScript and use simple data return:

```javascript
// Simple pattern that works
document.querySelectorAll('.chapter-item').forEach(item => {
  item.addEventListener('click', () => {
    if (window.openai?.toolOutput) {
      window.openai.toolOutput({
        action: 'select',
        id: item.dataset.id
      });
    }
  });
});
```

### What NOT to Do

Avoid these patterns which may not work:

```javascript
// ❌ Selection API - may not work
const selection = window.getSelection();

// ❌ Complex multi-step interactions
async function complexFlow() {
  await step1();
  await step2();
  await step3();
}

// ❌ Inline onclick with complex logic
<button onclick="complexFunction(arg1, arg2, arg3)">

// ❌ Event delegation on document
document.addEventListener('click', handler);
```

### Recommended Button Pattern

```html
<div class="action-buttons">
  <button class="btn" id="actionBtn">📝 Do Action</button>
</div>

<script>
document.getElementById('actionBtn')?.addEventListener('click', async () => {
  if (window.openai?.sendFollowUpMessage) {
    await window.openai.sendFollowUpMessage({
      prompt: 'Perform this specific action'
    });
  }
});
</script>
```

### Testing Button Interactivity

1. Add a visible indicator when button is clicked:
   ```javascript
   btn.addEventListener('click', () => {
     btn.textContent = '✓ Clicked!';
     btn.style.background = 'green';
   });
   ```

2. If indicator shows but `sendFollowUpMessage` doesn't work, check:
   - Is `window.openai` defined?
   - Is `sendFollowUpMessage` a function?

3. If indicator doesn't show, buttons aren't receiving clicks - simplify or use alternative UI

---

## ngrok Issues

### ERR_NGROK_108: Session Limit

Free ngrok allows only 1 agent session.

```bash
# Kill existing ngrok
pkill ngrok

# Start new one
ngrok http 8001
```

### Tunnel Not Working

1. Check ngrok is running: `curl http://localhost:4040/api/tunnels`
2. Verify port matches server: ngrok 8001 = server 8001
3. Test tunnel URL in browser

### ngrok URL Changed

After restarting ngrok, update the app:
1. Go to ChatGPT Settings > Apps
2. Find your app
3. Update MCP Server URL
4. Or delete and recreate app

---

## Tool Not in @mentions

### Check 1: Server Connected

1. Start server: `python main.py`
2. Start ngrok: `ngrok http 8001`
3. Verify server logs show requests when creating app

### Check 2: App Registered

1. Go to ChatGPT Settings
2. Check Developer mode is ON
3. Check your app appears in the list

### Check 3: MCP URL Correct

The URL should end with `/mcp`:
```
https://abc123.ngrok-free.app/mcp
```

### Check 4: ListToolsRequest

Server logs should show:
```
Processing request of type ListToolsRequest
```

If missing, ChatGPT isn't discovering your tools.

---

## Debug Checklist

When something isn't working, check in order:

1. **Server running?**
   ```bash
   curl http://localhost:8001
   ```

2. **ngrok running?**
   ```bash
   curl http://localhost:4040/api/tunnels
   ```

3. **App registered?**
   - ChatGPT Settings > Apps > Your app exists

4. **MCP URL correct?**
   - Ends with `/mcp`
   - Matches current ngrok URL

5. **Tool discovered?**
   - Type `@` in ChatGPT
   - Your app should appear

6. **Tool called?**
   - Server logs show `CallToolRequest`

7. **Widget delivered?**
   - Response includes `_meta["openai.com/widget"]`
   - MIME type is `text/html+skybridge`

8. **Widget renders?**
   - Try minimal HTML first
   - Check for JavaScript errors
   - Try fresh app registration

---

## Quick Reset Script

```bash
#!/bin/bash
# reset-chatgpt-app.sh

echo "Killing existing processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null
pkill ngrok 2>/dev/null

sleep 2

echo "Starting ngrok..."
ngrok http 8001 &
sleep 3

echo "Starting server..."
python main.py &

echo ""
echo "=== RESET COMPLETE ==="
echo "1. Get new ngrok URL from http://localhost:4040"
echo "2. Delete old app in ChatGPT Settings"
echo "3. Create new app with new ngrok URL"
echo "4. Test in new conversation"
```