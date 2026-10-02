---
name: html
description: "Implements semantic HTML, forms, document structure, and head metadata. Use for markup and native accessibility behavior, rather than general visual design or CSS layout."
---

# HTML

Semantic HTML is the cheapest accessibility and SEO win available — the browser gives you behavior, focus, and meaning for free when you use the right element. Reach for a `<div>` only when no semantic element fits.

## Use the right element

- Structure with landmarks: `<header>`, `<nav>`, `<main>` (one per page), `<aside>`, `<footer>`, `<section>`, `<article>`.
- Headings describe outline order — one `<h1>` per page, never skip levels for styling.
- Interactive = real elements: `<button>` for actions, `<a href>` for navigation. Never a clickable `<div>` (you lose focus, keyboard, and roles).
- Lists for collections (`<ul>`/`<ol>`/`<dl>`); `<table>` only for tabular data (with `<caption>`, `<th scope>`).
- `<figure>`/`<figcaption>`, `<time datetime>`, `<details>`/`<summary>` carry real semantics — use them.

## Forms (where most bugs live)

- Every input has a `<label for>` (or wraps the input). Placeholder is not a label.
- Use correct `type` (`email`, `tel`, `number`, `url`, `date`) and `inputmode`/`autocomplete` — better keyboards and autofill.
- Group related fields in `<fieldset>` + `<legend>` (radios, checkboxes).
- Use native validation (`required`, `pattern`, `min`/`max`) before JS; associate errors with `aria-describedby`.
- A submit control inside a `<form>` should be `<button type="submit">`.

```html
<form>
  <label for="email">Email</label>
  <input id="email" name="email" type="email" autocomplete="email" required
         aria-describedby="email-err" />
  <p id="email-err" role="alert"></p>
  <button type="submit">Subscribe</button>
</form>
```

## Accessibility

- Prefer native semantics over ARIA — "no ARIA is better than bad ARIA". Add roles/attributes only to fill genuine gaps.
- Images: meaningful `alt`; decorative images get `alt=""`.
- Keep a logical DOM/tab order; visible focus must survive your CSS.
- Use `role="status"` / `aria-live="polite"` for routine dynamic messages. Reserve `role="alert"` (assertive announcement) for urgent, time-sensitive information.

## Document head & metadata

- `<!doctype html>`, `<html lang="…">`, `<meta charset="utf-8">`, responsive `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Per-page `<title>` and `<meta name="description">`; Open Graph/Twitter tags for sharing.
- One canonical `<link rel="canonical">`; structured data (JSON-LD) where it helps search.

## Performance-aware markup

- `<img>` with explicit `width`/`height` (or `aspect-ratio`) to prevent layout shift; `loading="lazy"` for below-the-fold, and `<picture>`/`srcset` for responsive images.
- `<script defer>` (or `type="module"`, which defers by default); `async` only for independent scripts.
- Preload critical fonts/assets sparingly (`<link rel="preload">`); preconnect to required origins.

## Reference

- `GoogleChrome/modern-web-guidance-src` (HTML/forms/accessibility guides).
- MDN: HTML element reference; "HTML: A good basis for accessibility".
- WHATWG HTML Living Standard; web.dev: "Learn HTML", "Learn Forms".
- W3C WAI / ARIA Authoring Practices.
