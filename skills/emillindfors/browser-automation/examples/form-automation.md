# Form Automation Examples

Common patterns for automating web forms using the browser automation skill.

## Basic Form Filling

```
Task: Fill out a simple contact form

Steps:
1. Navigate to form page
2. Fill each field
3. Submit the form
4. Verify submission
```

### Example Workflow

```json
// Navigate to form
{"tool": "navigate", "args": {"url": "https://example.com/contact"}}

// Wait for form to load
{"tool": "wait_for_element", "args": {"selector": "form#contact", "timeout_ms": 5000}}

// Fill name field
{"tool": "send_keys", "args": {"selector": "#name", "text": "John Doe"}}

// Fill email field
{"tool": "send_keys", "args": {"selector": "#email", "text": "john@example.com"}}

// Fill message
{"tool": "send_keys", "args": {"selector": "#message", "text": "Hello, this is my message."}}

// Submit
{"tool": "click", "args": {"selector": "button[type='submit']"}}

// Verify success
{"tool": "wait_for_element", "args": {"selector": ".success-message", "timeout_ms": 5000}}
```

## Using fill_and_submit_form

For simpler cases, use the convenience tool:

```json
{
  "tool": "fill_and_submit_form",
  "args": {
    "form_selector": "form#registration",
    "fields": {
      "#first_name": "John",
      "#last_name": "Doe",
      "#email": "john@example.com",
      "#phone": "555-1234",
      "#company": "Acme Inc"
    },
    "submit_selector": "button.submit-btn"
  }
}
```

## Handling Select Dropdowns

```json
// Using execute_script to select option
{
  "tool": "execute_script",
  "args": {
    "script": "document.querySelector('#country').value = 'US'; document.querySelector('#country').dispatchEvent(new Event('change', { bubbles: true }));"
  }
}
```

## Handling Checkboxes and Radio Buttons

```json
// Click checkbox if not already checked
{
  "tool": "execute_script",
  "args": {
    "script": "const cb = document.querySelector('#agree-terms'); if (!cb.checked) cb.click();"
  }
}

// Select a radio button
{
  "tool": "click",
  "args": {"selector": "input[name='plan'][value='premium']"}
}
```

## File Upload Fields

```json
// Set file input value via JavaScript
{
  "tool": "execute_script",
  "args": {
    "script": "// Note: Due to security restrictions, actual file uploads need special handling"
  }
}
```

## Multi-Step Forms (Wizards)

```
Task: Complete a multi-step registration wizard

Pattern:
1. Fill step 1, click next
2. Wait for step 2, fill fields, click next
3. Continue until completion
```

### Example Workflow

```json
// Step 1: Personal Information
{"tool": "send_keys", "args": {"selector": "#first_name", "text": "John"}}
{"tool": "send_keys", "args": {"selector": "#last_name", "text": "Doe"}}
{"tool": "click", "args": {"selector": "button.next-step"}}

// Wait for step 2
{"tool": "wait_for_element", "args": {"selector": ".step-2.active", "timeout_ms": 3000}}

// Step 2: Contact Information
{"tool": "send_keys", "args": {"selector": "#email", "text": "john@example.com"}}
{"tool": "send_keys", "args": {"selector": "#phone", "text": "555-1234"}}
{"tool": "click", "args": {"selector": "button.next-step"}}

// Wait for step 3
{"tool": "wait_for_element", "args": {"selector": ".step-3.active", "timeout_ms": 3000}}

// Step 3: Review and Submit
{"tool": "click", "args": {"selector": "#agree-terms"}}
{"tool": "click", "args": {"selector": "button.submit-registration"}}

// Verify completion
{"tool": "wait_for_element", "args": {"selector": ".registration-complete", "timeout_ms": 10000}}
```

## Dynamic Forms with AJAX

```
Task: Handle forms that load options dynamically

Pattern:
1. Select a value that triggers AJAX
2. Wait for dependent fields to populate
3. Continue filling
```

### Example

```json
// Select country (triggers state dropdown to populate)
{
  "tool": "execute_script",
  "args": {
    "script": "document.querySelector('#country').value = 'US'; document.querySelector('#country').dispatchEvent(new Event('change', { bubbles: true }));"
  }
}

// Wait for state dropdown to populate
{
  "tool": "execute_script",
  "args": {
    "script": "return new Promise(resolve => { const check = setInterval(() => { if (document.querySelectorAll('#state option').length > 1) { clearInterval(check); resolve(true); }}, 100); setTimeout(() => { clearInterval(check); resolve(false); }, 5000); });"
  }
}

// Now select state
{
  "tool": "execute_script",
  "args": {
    "script": "document.querySelector('#state').value = 'CA'; document.querySelector('#state').dispatchEvent(new Event('change', { bubbles: true }));"
  }
}
```

## Form Validation Handling

```
Task: Handle and verify form validation

Pattern:
1. Submit form with invalid data
2. Capture validation errors
3. Fix errors and resubmit
```

### Example

```json
// Submit form (will fail validation)
{"tool": "click", "args": {"selector": "button[type='submit']"}}

// Check for validation errors
{
  "tool": "execute_script",
  "args": {
    "script": "return Array.from(document.querySelectorAll('.error-message')).map(el => el.textContent)"
  }
}

// Screenshot the error state
{"tool": "screenshot", "args": {"path": "/tmp/validation-errors.png"}}
```

## Handling CAPTCHAs

```
Note: CAPTCHAs are designed to prevent automation. For legitimate testing:
1. Use test environments with CAPTCHAs disabled
2. Use reCAPTCHA test keys in development
3. Consider using CAPTCHA solving services for authorized testing

This skill cannot bypass CAPTCHAs as that would be against their purpose.
```

## Recipe for Reusable Form

```json
{
  "name": "contact-form-submission",
  "description": "Submit a contact form",
  "version": "1.0.0",
  "parameters": {
    "url": {"type": "string", "required": true},
    "name": {"type": "string", "required": true},
    "email": {"type": "string", "required": true},
    "message": {"type": "string", "required": true}
  },
  "browsers": ["auto"],
  "steps": [
    {"action": "navigate", "arguments": {"url": "${url}"}},
    {"action": "wait_for_element", "arguments": {"selector": "form", "timeout_ms": 5000}},
    {"action": "send_keys", "arguments": {"selector": "[name='name'], #name", "text": "${name}"}},
    {"action": "send_keys", "arguments": {"selector": "[name='email'], #email", "text": "${email}"}},
    {"action": "send_keys", "arguments": {"selector": "[name='message'], #message, textarea", "text": "${message}"}},
    {"action": "click", "arguments": {"selector": "button[type='submit'], input[type='submit']"}},
    {"action": "wait_for_element", "arguments": {"selector": ".success, .thank-you, .confirmation", "timeout_ms": 10000}, "continue_on_error": true}
  ]
}
```
