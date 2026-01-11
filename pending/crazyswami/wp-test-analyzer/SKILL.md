# WordPress Test Analyzer Skill

Analyze WordPress theme PHP files to extract testable elements for E2E test generation.

## Usage

Invoke this skill when you need to analyze a WordPress theme for E2E testing:
- "Analyze the theme at /path/to/theme for testable elements"
- "Generate test cases for this WordPress theme"
- "What should I test in this WordPress site?"

## Arguments

- `theme_path` (required): Path to the WordPress theme directory

## Workflow

1. Run the analyzer script on the theme directory
2. Review the JSON output of testable elements
3. Use the output to generate Playwright test files

## Testable Elements Extracted

### Forms
- Form action URLs and methods
- Input fields (name, type, required)
- Submit buttons
- Nonce fields (WordPress security)
- Success/error message patterns

### Navigation
- Menu structures
- Internal links
- External links
- Anchor links

### Dynamic Content
- WP_Query loops
- Conditional displays (if/else)
- Post meta fields
- Custom post types

### JavaScript Interactions
- onclick handlers
- Class toggles
- Data attributes
- Event listeners mentioned in PHP

### WordPress-Specific
- Custom post types
- Meta boxes
- Theme options
- AJAX hooks

## Example Output

```json
{
  "forms": [
    {
      "file": "page-contact.php",
      "action": "POST to self",
      "fields": [
        {"name": "first_name", "type": "text", "required": true},
        {"name": "email", "type": "email", "required": true},
        {"name": "message", "type": "textarea", "required": true}
      ],
      "nonce": "csr_contact_nonce",
      "success_param": "?contact=success",
      "error_param": "?contact=error"
    }
  ],
  "pages": [
    {
      "file": "index.php",
      "template": "Home",
      "sections": ["hero", "philosophy", "featured_works"],
      "animations": ["initHomePage"]
    }
  ],
  "custom_post_types": ["property"],
  "navigation": {
    "primary": ["Home", "About", "Portfolio", "Contact"],
    "footer": ["Privacy Policy", "Terms of Service"]
  }
}
```

## Running the Analyzer

```bash
python3 /root/.claude/skills/wp-test-analyzer/analyze.py /path/to/theme
```
