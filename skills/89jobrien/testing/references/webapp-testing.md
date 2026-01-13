---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: testing
---

# Web Application Testing

Comprehensive guide for testing web applications using Playwright and browser automation.

## Playwright Basics

### Installation

```bash
pip install playwright
playwright install chromium
```

### Basic Script Structure

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')  # CRITICAL: Wait for JS
    # ... your test logic
    browser.close()
```

## Server Management

### Using with_server.py Helper

The `scripts/with_server.py` helper manages server lifecycle automatically:

**Single server:**

```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_test.py
```

**Multiple servers:**

```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_test.py
```

**Always run with `--help` first** to see current usage:

```bash
python scripts/with_server.py --help
```

## Decision Tree

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Reconnaissance-Then-Action Pattern

### Step 1: Inspect Rendered DOM

```python
# Navigate and wait for full load
page.goto('http://localhost:5173')
page.wait_for_load_state('networkidle')

# Take screenshot for visual reference
page.screenshot(path='/tmp/inspect.png', full_page=True)

# Get page content
content = page.content()

# Discover elements
buttons = page.locator('button').all()
links = page.locator('a[href]').all()
inputs = page.locator('input, textarea, select').all()
```

### Step 2: Identify Selectors

Use multiple selector strategies:

- `text=` - Match by visible text
- `role=` - Match by ARIA role
- CSS selectors - Standard CSS selectors
- IDs - Element IDs

**Best Practice:** Prefer `text=` and `role=` over CSS selectors for better maintainability.

### Step 3: Execute Actions

```python
# Click button by text
page.click('text=Submit')

# Fill form field
page.fill('#email', 'test@example.com')

# Select dropdown
page.select_option('#country', 'US')

# Wait for element
page.wait_for_selector('.success-message')
```

## Common Patterns

### Element Discovery

```python
# Discover all buttons
buttons = page.locator('button').all()
for i, button in enumerate(buttons):
    text = button.inner_text() if button.is_visible() else "[hidden]"
    print(f"  [{i}] {text}")

# Discover links
links = page.locator('a[href]').all()
for link in links:
    text = link.inner_text().strip()
    href = link.get_attribute('href')
    print(f"  - {text} -> {href}")

# Discover input fields
inputs = page.locator('input, textarea, select').all()
for input_elem in inputs:
    name = input_elem.get_attribute('name') or input_elem.get_attribute('id')
    input_type = input_elem.get_attribute('type') or 'text'
    print(f"  - {name} ({input_type})")
```

### Static HTML Testing

```python
import os

html_file_path = os.path.abspath('path/to/your/file.html')
file_url = f'file://{html_file_path}'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Navigate to local HTML file
    page.goto(file_url)

    # Interact with elements
    page.click('text=Click Me')
    page.fill('#name', 'John Doe')

    browser.close()
```

### Console Log Capture

```python
console_logs = []

def handle_console_message(msg):
    console_logs.append(f"[{msg.type}] {msg.text}")
    print(f"Console: [{msg.type}] {msg.text}")

page.on("console", handle_console_message)

# Navigate and interact
page.goto(url)
page.wait_for_load_state('networkidle')
page.click('text=Dashboard')

# Save logs
with open('console.log', 'w') as f:
    f.write('\n'.join(console_logs))
```

## Best Practices

### Waiting Strategies

**Always wait for networkidle on dynamic apps:**

```python
page.goto(url)
page.wait_for_load_state('networkidle')  # CRITICAL
```

**Wait for specific elements:**

```python
page.wait_for_selector('.loading-spinner', state='hidden')
page.wait_for_selector('.success-message', state='visible')
```

**Wait for navigation:**

```python
with page.expect_navigation():
    page.click('text=Submit')
```

### Selector Best Practices

**Prefer semantic selectors:**

```python
# Good: Text-based selector
page.click('text=Submit Form')

# Good: Role-based selector
page.click('role=button[name="Submit"]')

# Acceptable: CSS selector
page.click('#submit-button')

# Avoid: Fragile CSS selectors
page.click('div.container > div.row > div.col > button.btn-primary')
```

### Error Handling

```python
try:
    page.goto(url)
    page.wait_for_load_state('networkidle', timeout=10000)
except Exception as e:
    print(f"Error loading page: {e}")
    page.screenshot(path='error.png')
    raise
```

### Screenshots

```python
# Full page screenshot
page.screenshot(path='full_page.png', full_page=True)

# Element screenshot
element = page.locator('.widget')
element.screenshot(path='widget.png')

# Screenshot on failure
try:
    page.click('text=Submit')
except Exception:
    page.screenshot(path='failure.png')
    raise
```

## Common Pitfalls

### ❌ Don't Inspect Before networkidle

**Bad:**

```python
page.goto(url)
content = page.content()  # Too early! JS hasn't executed
```

**Good:**

```python
page.goto(url)
page.wait_for_load_state('networkidle')  # Wait first
content = page.content()  # Now safe
```

### ❌ Don't Use Hardcoded Timeouts

**Bad:**

```python
page.click('text=Submit')
time.sleep(5)  # Arbitrary wait
```

**Good:**

```python
page.click('text=Submit')
page.wait_for_selector('.success-message')  # Wait for actual condition
```

### ❌ Don't Forget to Close Browser

**Bad:**

```python
browser = p.chromium.launch()
page = browser.new_page()
# ... test code
# Browser never closed!
```

**Good:**

```python
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    # ... test code
    browser.close()  # Automatically closed by context manager
```

## Examples

See `examples/` directory for complete examples:

- `element_discovery.py` - Discovering buttons, links, and inputs
- `static_html_automation.py` - Testing static HTML files
- `console_logging.py` - Capturing console logs during automation

## Integration with Test Frameworks

### With pytest

```python
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

def test_login(browser):
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')
    page.fill('#email', 'test@example.com')
    page.fill('#password', 'password')
    page.click('text=Login')
    page.wait_for_selector('.dashboard')
    assert page.locator('.dashboard').is_visible()
    page.close()
```

### With unittest

```python
import unittest
from playwright.sync_api import sync_playwright

class WebAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page()

    def tearDown(self):
        self.page.close()

    def test_homepage_loads(self):
        self.page.goto('http://localhost:5173')
        self.page.wait_for_load_state('networkidle')
        self.assertIn('Welcome', self.page.content())
```
