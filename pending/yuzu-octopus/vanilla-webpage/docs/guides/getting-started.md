# Getting Started

## 0 to Running in 2 Minutes

### Option 1: Single HTML file

Create `index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Page</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; line-height: 1.5; padding: 2rem; }
    h1 { font-size: clamp(1.5rem, 4vw + 1rem, 3rem); text-wrap: balance; }
  </style>
</head>
<body>
  <h1>Hello World</h1>
  <p>Start building here.</p>
</body>
</html>
```

### Option 2: With design tokens

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Page</title>
  <link rel="stylesheet" href="tokens/index.css">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font-body);
      color: var(--color-text);
      background: var(--color-bg);
      line-height: var(--leading-normal);
      padding: var(--space-4);
    }
    h1 { font-size: var(--text-h1); text-wrap: balance; }
  </style>
</head>
<body>
  <h1>Hello World</h1>
  <p>Using design tokens from tokens/.</p>
</body>
</html>
```

### Option 3: With a classless framework

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Page</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.classless.min.css">
</head>
<body>
  <main class="container">
    <h1>Hello World</h1>
    <p>Pico styles semantic HTML automatically.</p>
  </main>
</body>
</html>
```

## Serve Locally

```bash
python3 -m http.server 8000
# Open http://localhost:8000
```

## Next Steps

1. Browse `cookbook/` for patterns
2. Read `docs/guides/modern-css.md` for the latest CSS features
3. Check `SKILL.md` for the full reference
