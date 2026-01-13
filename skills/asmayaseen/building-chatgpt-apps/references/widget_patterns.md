# Widget Patterns for ChatGPT Apps

## Overview

ChatGPT Apps use HTML widgets embedded in iframes to render rich UI. Widgets communicate with ChatGPT via `window.openai.toolOutput`.

---

## Basic Widget Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Widget Title</title>
  <style>
    /* All CSS must be inline */
  </style>
</head>
<body>
  <!-- Widget content -->
  <script>
    // Widget logic
  </script>
</body>
</html>
```

---

## Communication with ChatGPT

The `window.openai` object provides three main APIs for widget communication:

### 1. sendFollowUpMessage (Best for Action Buttons)

Triggers a follow-up message in the conversation:

```javascript
// Send a follow-up prompt to ChatGPT
async function suggestAction(prompt) {
  if (window.openai?.sendFollowUpMessage) {
    await window.openai.sendFollowUpMessage({ prompt });
  }
}

// Example usage
suggestAction('Summarize this chapter');
suggestAction('Explain the key concepts');
suggestAction('Give me a quiz on this material');
```

**Best for**: Action buttons, suggested next steps, navigation prompts.

### 2. toolOutput (For Data Return)

Sends structured data back to ChatGPT:

```javascript
function sendToChatGPT(action, data) {
  if (window.openai?.toolOutput) {
    window.openai.toolOutput({
      action: action,
      ...data
    });
  }
}

// Example usage
sendToChatGPT('chapter_selected', { chapter: 1 });
sendToChatGPT('search_query', { query: 'hello world' });
```

**Best for**: Selections, form submissions, returning user choices.

### 3. callTool (For Tool Chaining)

Calls another MCP tool directly:

```javascript
async function callMCPTool(toolName, args) {
  if (window.openai?.callTool) {
    await window.openai.callTool({
      name: toolName,
      arguments: args
    });
  }
}

// Example usage
callMCPTool('read-chapter', { chapter: 2 });
```

**Best for**: Navigation between content, multi-step workflows.

### Common Actions for toolOutput

| Action | Description | Data |
|--------|-------------|------|
| `item_selected` | User selected an item | `{ id, name }` |
| `button_clicked` | Button was clicked | `{ buttonId }` |
| `form_submitted` | Form was submitted | `{ formData }` |
| `navigation` | User navigated | `{ target }` |

---

## Action Button Patterns (Recommended)

**Critical**: Widget buttons may not respond to clicks in some ChatGPT environments. Use `sendFollowUpMessage` for reliable action buttons.

### Simple Action Buttons

```html
<div class="action-buttons">
  <button class="btn btn-primary" id="summarizeBtn">
    📝 Summarize
  </button>
  <button class="btn btn-secondary" id="explainBtn">
    💡 Explain
  </button>
  <button class="btn btn-secondary" id="quizBtn">
    ❓ Quiz Me
  </button>
</div>

<script>
// Action button handlers using sendFollowUpMessage
const actions = {
  summarizeBtn: 'Summarize this content for me',
  explainBtn: 'Explain the key concepts in simple terms',
  quizBtn: 'Create a short quiz to test my understanding'
};

Object.entries(actions).forEach(([btnId, prompt]) => {
  document.getElementById(btnId)?.addEventListener('click', async () => {
    if (window.openai?.sendFollowUpMessage) {
      await window.openai.sendFollowUpMessage({ prompt });
    }
  });
});
</script>
```

### Action Button Styles

```css
.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #27ae60;
  color: white;
}

.btn-secondary:hover {
  background: #219a52;
}
```

---

## Styling Best Practices

### Responsive Container

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.5;
  color: #333;
  background: #f5f5f5;
  min-height: 100vh;
  padding: 16px;
}

.container {
  max-width: 600px;
  margin: 0 auto;
}
```

### Card Component

```css
.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 16px;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1a1a1a;
}

.card-content {
  color: #666;
}
```

### Interactive Elements

```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #0066cc;
  color: white;
}

.btn-primary:hover {
  background: #0052a3;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #e5e5e5;
  color: #333;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s;
}

.list-item:hover {
  background: #f9f9f9;
}

.list-item:last-child {
  border-bottom: none;
}
```

---

## Complete Widget Examples

### Table of Contents Widget

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 24px;
    }
    .book-card {
      background: white;
      border-radius: 16px;
      padding: 24px;
      max-width: 500px;
      margin: 0 auto;
      box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    .book-header {
      display: flex;
      gap: 16px;
      margin-bottom: 20px;
    }
    .book-cover {
      font-size: 48px;
    }
    .book-info h1 {
      font-size: 20px;
      color: #1a1a1a;
    }
    .book-info p {
      color: #666;
      font-size: 14px;
    }
    .toc-title {
      font-size: 12px;
      font-weight: 600;
      color: #999;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 12px;
    }
    .chapter {
      display: flex;
      align-items: center;
      padding: 14px;
      border-radius: 10px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s;
      background: #f8f8f8;
    }
    .chapter:hover {
      background: #f0f0f0;
      transform: translateX(4px);
    }
    .chapter-num {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      margin-right: 14px;
    }
    .chapter-title {
      flex: 1;
      font-weight: 500;
      color: #333;
    }
    .chapter-arrow {
      color: #999;
    }
  </style>
</head>
<body>
  <div class="book-card">
    <div class="book-header">
      <div class="book-cover">📚</div>
      <div class="book-info">
        <h1>The Art of Building AI Apps</h1>
        <p>by Claude & Friends</p>
      </div>
    </div>
    <div class="toc-title">Table of Contents</div>
    <div class="chapter" onclick="selectChapter(1)">
      <div class="chapter-num">1</div>
      <div class="chapter-title">Introduction to AI Applications</div>
      <div class="chapter-arrow">→</div>
    </div>
    <div class="chapter" onclick="selectChapter(2)">
      <div class="chapter-num">2</div>
      <div class="chapter-title">Understanding LLMs</div>
      <div class="chapter-arrow">→</div>
    </div>
  </div>
  <script>
    function selectChapter(num) {
      if (window.openai && window.openai.toolOutput) {
        window.openai.toolOutput({
          action: 'read_chapter',
          chapter: num
        });
      }
    }
  </script>
</body>
</html>
```

### Chapter Reader Widget

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: Georgia, serif;
      background: #fafafa;
      min-height: 100vh;
      padding: 24px;
    }
    .reader {
      max-width: 600px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      padding: 32px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    .chapter-header {
      border-bottom: 2px solid #eee;
      padding-bottom: 16px;
      margin-bottom: 24px;
    }
    .book-title {
      font-size: 12px;
      color: #999;
      margin-bottom: 8px;
    }
    .chapter-title {
      font-size: 24px;
      color: #1a1a1a;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .chapter-icon {
      font-size: 28px;
    }
    .chapter-nav {
      font-size: 12px;
      color: #666;
      margin-top: 8px;
    }
    .content {
      font-size: 17px;
      line-height: 1.8;
      color: #333;
    }
    .content p {
      margin-bottom: 16px;
    }
    .section-title {
      font-size: 18px;
      font-weight: 600;
      color: #e67e22;
      margin: 24px 0 12px;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
  </style>
</head>
<body>
  <div class="reader">
    <div class="chapter-header">
      <div class="book-title">The Art of Building AI Apps</div>
      <h1 class="chapter-title">
        <span class="chapter-icon">📖</span>
        Chapter 1: Introduction
      </h1>
      <div class="chapter-nav">1 of 5 chapters</div>
    </div>
    <div class="content">
      <p>Welcome to the world of AI application development!</p>
      <h2 class="section-title">Why AI Apps Matter</h2>
      <p>Artificial Intelligence has transformed from a research curiosity into a practical tool.</p>
    </div>
  </div>
</body>
</html>
```

---

## Testing Widgets

### Local Testing (Limited)

Create an HTML file and open in browser. Note: `window.openai` won't be available.

```javascript
// Add mock for local testing
if (!window.openai) {
  window.openai = {
    toolOutput: (data) => console.log('toolOutput:', data)
  };
}
```

### Testing in ChatGPT

1. Start your MCP server
2. Connect via ngrok
3. Register app in ChatGPT Developer Mode
4. Test in a new conversation

---

## Troubleshooting

### Widget Not Rendering

1. Check MIME type is `text/html+skybridge`
2. Verify `_meta["openai.com/widget"]` in response
3. Check server logs for errors

### Styles Not Applying

1. Use inline `<style>` tags only
2. Avoid external CSS files
3. Check for CSS syntax errors

### JavaScript Not Running

1. Check browser console for errors
2. Verify script is inside `<script>` tags
3. Test `window.openai` availability
