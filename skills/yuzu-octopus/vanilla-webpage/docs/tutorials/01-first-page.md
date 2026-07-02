# Tutorial 1: Your First Page

Build a personal website with HTML and CSS — no setup, no frameworks.

## Step 1: Create the HTML

Create `index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Website</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; color: #1a1a1a; line-height: 1.6; }
  </style>
</head>
<body>
  <header>
    <nav>
      <span>Brand</span>
      <ul>
        <li><a href="#about">About</a></li>
        <li><a href="#work">Work</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main>
    <section class="hero">
      <h1>Hi, I'm Alex</h1>
      <p>I build things for the web.</p>
    </section>

    <section id="work">
      <h2>My Work</h2>
      <div class="grid">
        <article><h3>Project 1</h3><p>A web app built with vanilla JS.</p></article>
        <article><h3>Project 2</h3><p>A responsive landing page.</p></article>
        <article><h3>Project 3</h3><p>A CSS animation experiment.</p></article>
      </div>
    </section>
  </main>

  <footer>
    <p>Built with vanilla HTML & CSS.</p>
  </footer>
</body>
</html>
```

## Step 2: Add styles

Add to the `<style>` block:

```css
nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: #1a1a2e;
  color: white;
}

nav ul { display: flex; gap: 1rem; list-style: none; }
nav a { color: #ccc; text-decoration: none; }
nav a:hover { color: white; }

.hero {
  min-height: 60vh;
  display: grid;
  place-items: center;
  text-align: center;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.hero h1 { font-size: clamp(2rem, 5vw, 3.5rem); }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

article {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 1.5rem;
}

footer {
  text-align: center;
  padding: 2rem;
  color: #999;
}
```

## Step 3: Serve it

```bash
python3 -m http.server 8000
# Open http://localhost:8000
```

## What you learned

- Semantic HTML (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`)
- Flexbox for navigation
- CSS Grid for the card layout
- `clamp()` for responsive typography
- Gradient backgrounds
