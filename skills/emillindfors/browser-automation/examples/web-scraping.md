# Web Scraping Examples

Common patterns for web scraping using the browser automation skill.

## Scraping a Product List

```
Task: Extract all products from an e-commerce page

Steps:
1. Navigate to product listing page
2. Wait for products to load
3. Find all product cards
4. Extract data from each product

Tools used:
- navigate: Load the page
- wait_for_element: Ensure products are loaded
- find_elements: Get all product cards
- execute_script: Extract structured data
```

### Example Workflow

```json
// Step 1: Navigate
{"tool": "navigate", "args": {"url": "https://shop.example.com/products"}}

// Step 2: Wait for content
{"tool": "wait_for_element", "args": {"selector": ".product-card", "timeout_ms": 10000}}

// Step 3: Extract all product data
{
  "tool": "execute_script",
  "args": {
    "script": "return Array.from(document.querySelectorAll('.product-card')).map(card => ({name: card.querySelector('.title').textContent, price: card.querySelector('.price').textContent, link: card.querySelector('a').href}))"
  }
}
```

## Paginated Content

```
Task: Scrape content across multiple pages

Pattern:
1. Extract data from current page
2. Check for "next" button
3. Click next and repeat
4. Stop when no more pages

Key considerations:
- Use wait_for_element after each navigation
- Track page numbers to avoid infinite loops
- Handle varying page load times
```

### Example Workflow

```json
// Step 1: Extract current page data
{"tool": "execute_script", "args": {"script": "return Array.from(document.querySelectorAll('.item')).map(el => el.textContent)"}}

// Step 2: Check and click next
{
  "tool": "execute_script",
  "args": {
    "script": "const next = document.querySelector('.pagination .next:not(.disabled)'); if (next) { next.click(); return true; } return false;"
  }
}

// Step 3: Wait for new content
{"tool": "wait_for_element", "args": {"selector": ".item", "timeout_ms": 5000}}
```

## Handling Infinite Scroll

```
Task: Scrape content that loads on scroll

Pattern:
1. Scroll to bottom
2. Wait for new content
3. Check if more content loaded
4. Repeat until no new content
```

### Example Script

```javascript
// execute_script to handle infinite scroll
async function scrollAndCollect() {
  const results = [];
  let previousHeight = 0;

  while (true) {
    // Collect current items
    document.querySelectorAll('.item').forEach(el => {
      const text = el.textContent;
      if (!results.includes(text)) results.push(text);
    });

    // Scroll to bottom
    window.scrollTo(0, document.body.scrollHeight);

    // Wait for content
    await new Promise(r => setTimeout(r, 2000));

    // Check if we've reached the end
    if (document.body.scrollHeight === previousHeight) break;
    previousHeight = document.body.scrollHeight;
  }

  return results;
}
return scrollAndCollect();
```

## Extracting Tables

```
Task: Extract data from HTML tables

Pattern:
1. Find the table element
2. Extract headers
3. Extract row data
4. Return structured object
```

### Example Script

```javascript
// execute_script to extract table data
const table = document.querySelector('table');
const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => {
  const cells = Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim());
  return headers.reduce((obj, header, i) => {
    obj[header] = cells[i];
    return obj;
  }, {});
});
return { headers, rows };
```

## Handling Authentication

```
Task: Scrape content behind login

Pattern:
1. Navigate to login page
2. Fill credentials
3. Submit form
4. Wait for redirect
5. Navigate to protected content
6. Scrape data
```

### Example Workflow

```json
// Step 1: Login
{"tool": "login_form", "args": {
  "username_selector": "#email",
  "password_selector": "#password",
  "username": "${username}",
  "password": "${password}",
  "submit_selector": "button[type='submit']"
}}

// Step 2: Wait for authentication
{"tool": "wait_for_element", "args": {"selector": ".dashboard", "timeout_ms": 10000}}

// Step 3: Navigate to protected content
{"tool": "navigate", "args": {"url": "https://example.com/protected/data"}}

// Step 4: Extract data
{"tool": "execute_script", "args": {"script": "return document.querySelector('.data-container').innerHTML"}}
```

## Error Handling Patterns

### Retry on Failure

```json
{
  "tool": "find_element",
  "args": {"selector": ".dynamic-content"},
  "retry_count": 3,
  "retry_delay_ms": 2000
}
```

### Check Before Action

```json
// Check if element exists before clicking
{
  "tool": "execute_script",
  "args": {
    "script": "const el = document.querySelector('.optional-button'); if (el) { el.click(); return true; } return false;"
  }
}
```

### Screenshot on Error

```json
// In recipe, add continue_on_error and capture screenshot
{
  "name": "capture-state-on-error",
  "action": "screenshot",
  "arguments": {"path": "/tmp/error-state.png"},
  "continue_on_error": true
}
```
