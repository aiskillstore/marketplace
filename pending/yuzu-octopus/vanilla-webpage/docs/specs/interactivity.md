# Interactivity Spec

## Dark Mode

```css
:root { --bg: #ffffff; --text: #1a1a1a; }
[data-theme="dark"] { --bg: #121212; --text: #e0e0e0; }
```

```javascript
// Toggle, persist, load
const setTheme = (t) => { root.setAttribute('data-theme', t); localStorage.setItem('theme', t); };
const loadTheme = () => localStorage.getItem('theme') || (matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light');
```

## Accordion

```html
<details><summary>Question</summary><p>Answer</p></details>
```

No JavaScript. Browser handles open/close, keyboard, screen readers.

## Tabs (CSS-only)

```css
.tabs input[type="radio"]:checked + label { color: var(--color-primary); }
#tab1:checked ~ .panel-1 { display: block; }
```

## Toast Notifications

```javascript
function showToast(msg) {
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}
```

## Popover API

```html
<button popovertarget="pop">Open</button>
<div popover id="pop">Content</div>
```

No JavaScript for open/close. Browser handles dismiss.

## CSS-Only Dropdown

```css
.dropdown-wrapper:hover .dropdown,
.dropdown-wrapper:focus-within .dropdown { display: block; }
```

## Rules

- Use `<dialog>` for modals (handles focus trap)
- Use `<details>` for accordions (no JS)
- Use Popover API for simple popups (no JS)
- Persist user preferences in localStorage
- Respect `prefers-color-scheme` on first visit
- Always provide keyboard access
