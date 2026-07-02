# File Structure Guide

## Simple Page (single file)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page</title>
  <style>/* All CSS here */</style>
</head>
<body>
  <!-- All HTML here -->
  <script>/* All JS here */</script>
</body>
</html>
```

**When:** Landing pages, prototypes, single-component pages. Keep until the file exceeds ~400 lines.

## Multi-file (split at root)

```
index.html
style.css
script.js
```

**When:** Multiple sections, reusable CSS, or when the HTML exceeds 400 lines.

## With tokens

```
index.html
style.css
script.js
tokens/
  base.css
  semantic.css
  components.css
  typography.css
  index.css
```

**When:** Building a design system or multiple pages sharing the same tokens.

## Naming conventions

- **HTML:** `index.html` for main pages, `about.html`, `contact.html` for others
- **CSS:** `style.css` for main styles, `tokens/*.css` for design tokens
- **JS:** `app.js` for main logic, `storage.js` for localStorage helpers
- **Directories:** lowercase, hyphen-separated (`hero-section/`, not `heroSection/`)

## What NOT to create

- No `src/` directory (no build step)
- No `dist/` directory (no compilation)
- No `node_modules/` (no npm)
- No `package.json` (no dependencies)
- No `.babelrc`, `vite.config.js`, `webpack.config.js`
