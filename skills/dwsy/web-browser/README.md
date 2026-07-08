# Web Browser Skill

Full-featured browser automation with Chrome DevTools Protocol (CDP).

## Overview

This skill provides comprehensive browser automation capabilities through a collection of Node.js scripts. It uses Puppeteer to control a standalone Chrome instance, allowing you to navigate pages, interact with forms, extract data, monitor network requests, and perform advanced browser operations.

## Features

### 🎯 Core Features
- ✅ **36 powerful scripts** covering all browser automation needs
- ✅ **Independent browser instance** - doesn't affect your main Chrome
- ✅ **Random port management** - avoids conflicts automatically
- ✅ **Persistent sessions** - cookies and localStorage persist across restarts

### 📦 Functionality Modules

#### Browser Management
- Start/stop browser with random ports
- Port persistence and management
- Profile management (fresh or copied)

#### Navigation
- Navigate to URLs
- Page reload with cache control
- Tab management (list, open, switch, close)

#### Form Interaction
- Click elements
- Type text (with clear option)
- Select dropdown options
- Check/uncheck/toggle checkboxes
- Submit forms

#### Waiting & Detection
- Wait for elements, visibility, text, URL
- Check element visibility
- Get detailed element information

#### Storage & Cookies
- Cookie management (CRUD operations)
- localStorage/sessionStorage management
- Clear browser data

#### Network & Performance
- Monitor network requests
- Capture and export requests
- Get performance metrics
- Request interception (block, mock, log)

#### Advanced Features
- Page scrolling
- Mouse hover
- File upload
- File download management
- PDF export
- Tab management

#### Debugging & Tools
- Debug information
- Element inspection
- Text search
- Page metadata extraction

## Quick Start

### 1. Start the Browser

\`\`\`bash
cd ~/.pi/agent/skills/web-browser

# Start Chromium with persistent storage (default)
node scripts/start.js

# Use Google Chrome instead of Chromium
node scripts/start.js --chrome
\`\`\`

### 2. Navigate to a Page

\`\`\`bash
# Navigate current tab
node scripts/nav.js https://example.com

# Open in new tab
node scripts/nav.js https://example.com --new
\`\`\`

### 3. Interact with the Page

\`\`\`bash
# Type into input
node scripts/type.js "#username" "john@example.com"

# Click button
node scripts/click.js "#submit-button"

# Take screenshot
node scripts/screenshot.js
\`\`\`

### 4. Stop the Browser

\`\`\`bash
node scripts/stop.js
\`\`\`

## Complete Script Reference

### Browser Management

| Script | Description | Example |
|--------|-------------|---------|
| `start.js` | Start Chromium with random port | `node scripts/start.js` |
| `stop.js` | Stop Chromium | `node scripts/stop.js` |
| `get-port.js` | Get current port | `node scripts/get-port.js` |

### Navigation

| Script | Description | Example |
|--------|-------------|---------|
| `nav.js` | Navigate to URL | `node scripts/nav.js https://example.com --new` |
| `reload.js` | Reload page | `node scripts/reload.js --force-no-cache` |
| `tabs.js` | Manage tabs | `node scripts/tabs.js list` |

### Form Interaction

| Script | Description | Example |
|--------|-------------|---------|
| `click.js` | Click element | `node scripts/click.js "#submit-button"` |
| `type.js` | Type text | `node scripts/type.js "#username" "john@example.com" --clear` |
| `select.js` | Select option | `node scripts/select.js "#country" "United States"` |
| `checkbox.js` | Check/uncheck/toggle | `node scripts/checkbox.js "#terms" check` |
| `submit.js` | Submit form | `node scripts/submit.js "#login-form"` |

### Waiting & Detection

| Script | Description | Example |
|--------|-------------|---------|
| `wait-for.js` | Wait for element/visible/hidden/text/url | `node scripts/wait-for.js visible ".loading"` |
| `wait-for-url.js` | Wait for URL change | `node scripts/wait-for-url.js "/success"` |
| `check-visible.js` | Check visibility | `node scripts/check-visible.js "#button"` |
| `get-element.js` | Get element info | `node scripts/get-element.js "#button"` |

### Storage & Cookies

| Script | Description | Example |
|--------|-------------|---------|
| `cookies.js` | Cookie management | `node scripts/cookies.js list` |
| `storage.js` | Storage management | `node scripts/storage.js get local "token"` |
| `clear-data.js` | Clear data | `node scripts/clear-data.js all` |

### Network & Performance

| Script | Description | Example |
|--------|-------------|---------|
| `network.js` | Network monitoring | `node scripts/network.js capture "https://example.com"` |
| `performance.js` | Performance metrics | `node scripts/performance.js` |
| `intercept.js` | Request interception | `node scripts/intercept.js block "*.png"` |

### Advanced Features

| Script | Description | Example |
|--------|-------------|---------|
| `scroll.js` | Page scrolling | `node scripts/scroll.js down 500` |
| `hover.js` | Mouse hover | `node scripts/hover.js "#menu"` |
| `upload.js` | File upload | `node scripts/upload.js "#file-input" "/path/to/file.txt"` |
| `download.js` | File download | `node scripts/download.js click "#download-btn"` |
| `pdf.js` | PDF export | `node scripts/pdf.js ./page.pdf` |
| `tabs.js` | Tab management | `node scripts/tabs.js switch 1` |

### Debugging & Tools

| Script | Description | Example |
|--------|-------------|---------|
| `debug.js` | Debug information | `node scripts/debug.js` |
| `inspect.js` | Element inspection | `node scripts/inspect.js "#button"` |
| `find-text.js` | Text search | `node scripts/find-text.js "Hello World"` |
| `get-meta.js` | Page metadata | `node scripts/get-meta.js` |

### Core

| Script | Description | Example |
|--------|-------------|---------|
| `eval.js` | JavaScript evaluation | `node scripts/eval.js 'document.title'` |
| `screenshot.js` | Screenshot | `node scripts/screenshot.js` |
| `pick.js` | Element picker | `node scripts/pick.js "Click the submit button"` |
| `check-console.js` | Console check | `node scripts/check-console.js` |

## Usage Examples

### Example 1: Login Flow

\`\`\`bash
# Start browser
node scripts/start.js

# Navigate to login page
node scripts/nav.js https://example.com/login

# Type credentials
node scripts/type.js "#username" "john@example.com"
node scripts/type.js "#password" "secret123"

# Submit form
node scripts/click.js "#login-button"

# Wait for success
node scripts/wait-for.js text "Welcome"

# Take screenshot
node scripts/screenshot.js

# Stop browser
node scripts/stop.js
\`\`\`

### Example 2: Data Scraping

\`\`\`bash
# Start browser
node scripts/start.js

# Navigate to page
node scripts/nav.js https://example.com/products

# Wait for content to load
node scripts/wait-for.js visible ".product-card"

# Extract data
node scripts/eval.js 'Array.from(document.querySelectorAll(".product-card")).map(p => ({ name: p.querySelector(".name").textContent, price: p.querySelector(".price").textContent }))'

# Stop browser
node scripts/stop.js
\`\`\`

### Example 3: Network Monitoring

\`\`\`bash
# Start browser
node scripts/start.js

# Start network monitoring
node scripts/network.js start

# Navigate to page
node scripts/nav.js https://example.com

# Stop monitoring and view results
node scripts/network.js stop

# Export requests
node scripts/network.js export requests.json

# Stop browser
node scripts/stop.js
\`\`\`

### Example 4: Form Testing

\`\`\`bash
# Start browser
node scripts/start.js

# Navigate to form
node scripts/nav.js https://example.com/contact

# Fill form
node scripts/type.js "#name" "John Doe"
node scripts/type.js "#email" "john@example.com"
node scripts/type.js "#message" "Hello"

# Select dropdown
node scripts/select.js "#topic" "Support"

# Checkbox
node scripts/checkbox.js "#subscribe" check

# Submit
node scripts/click.js "#submit"

# Wait for confirmation
node scripts/wait-for.js visible ".success-message"

# Stop browser
node scripts/stop.js
\`\`\`

### Example 5: PDF Export

\`\`\`bash
# Start browser
node scripts/start.js

# Navigate to page
node scripts/nav.js https://example.com/report

# Wait for content
node scripts/wait-for.js visible ".report-content"

# Export as PDF
node scripts/pdf.js ~/Downloads/report.pdf

# Stop browser
node scripts/stop.js
\`\`\`

## Configuration

### Port Management

The browser automatically uses a random port between 9222-9999:

\`\`\`bash
# View current port
node scripts/get-port.js

# Reset port (get new random port)
rm ~/.cache/scraping-web-browser/port.txt
node scripts/start.js
\`\`\`

### Profile Management

\`\`\`bash
# Start Chromium with persistent storage
node scripts/start.js

# Use Google Chrome instead of Chromium
node scripts/start.js --chrome
\`\`\`

### Data Persistence

Browser data is stored in \`~/.cache/scraping-web-browser/\`:

- **Port**: \`port.txt\`
- **Cookies**: \`Default/Cookies\`
- **LocalStorage**: \`Default/Local Storage/\`
- **Session**: \`Default/Session Storage/\`

## Best Practices

1. **Always stop the browser** when done to release resources
2. **Use wait-for.js** for dynamic content instead of fixed delays
3. **Check element visibility** before interacting
4. **Use network monitoring** to debug API calls
5. **Export cookies** for session reuse
6. **Use inspect.js** to understand page structure
7. **Clear data** between tests for isolation

## Troubleshooting

### Browser won't start

\`\`\`bash
# Check if port is in use
lsof -i :$(cat ~/.cache/scraping-web-browser/port.txt)

# Kill existing process
node scripts/stop.js

# Reset port
rm ~/.cache/scraping-web-browser/port.txt
node scripts/start.js
\`\`\`

### Element not found

\`\`\`bash
# Wait for element
node scripts/wait-for.js visible "#button"

# Inspect page to find correct selector
node scripts/inspect.js "button"

# Find text to locate element
node scripts/find-text.js "Submit"
\`\`\`

### Timeout errors

\`\`\`bash
# Increase timeout in wait-for.js
node scripts/wait-for.js visible "#loading" 60000

# Check network requests
node scripts/network.js start
node scripts/nav.js https://example.com
node scripts/network.js stop
\`\`\`

## Testing

\`\`\`bash
# Test all scripts
node test-all-scripts.js

# Run integration tests
node test-integration.js

# Run demo
node demo.js
\`\`\`

## License

Stolen from Mario

## Related Documentation

- [SKILL.md](./SKILL.md) - Skill documentation
- [FIX_NOTE.md](./FIX_NOTE.md) - Fix notes
- [COMPLETE_GUIDE.md](./COMPLETE_GUIDE.md) - Complete usage guide