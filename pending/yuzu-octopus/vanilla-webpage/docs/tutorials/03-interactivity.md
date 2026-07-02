# Tutorial 3: Interactivity

Add dark mode, accordion, and modal to your page with vanilla JavaScript.

## Dark Mode

### HTML

```html
<button id="dark-toggle">🌙</button>
```

### CSS

```css
:root { --bg: #ffffff; --text: #1a1a1a; }
[data-theme="dark"] { --bg: #121212; --text: #e0e0e0; }
body { background: var(--bg); color: var(--text); transition: background 0.3s, color 0.3s; }
```

### JavaScript

```javascript
const toggle = document.getElementById('dark-toggle');
const root = document.documentElement;

function setTheme(theme) {
  root.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// Load saved or system preference
const saved = localStorage.getItem('theme');
const preferred = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
setTheme(saved || preferred);

toggle.addEventListener('click', () => {
  setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
});
```

## Accordion (no JavaScript)

```html
<details>
  <summary>Question 1</summary>
  <p>Answer 1</p>
</details>
<details>
  <summary>Question 2</summary>
  <p>Answer 2</p>
</details>
```

The browser handles open/close, keyboard support, and screen readers.

## Modal Dialog

### HTML

```html
<button id="open-modal">Open</button>
<dialog id="modal">
  <h2>Confirm</h2>
  <p>Are you sure?</p>
  <button onclick="this.closest('dialog').close()">Close</button>
</dialog>
```

### JavaScript

```javascript
document.getElementById('open-modal').addEventListener('click', () => {
  document.getElementById('modal').showModal();
});
```

`<dialog>` handles focus trap, Escape key, and backdrop click automatically.

## Toast Notifications

```javascript
function showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}
```

```css
.toast {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  background: #16a34a;
  color: white;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  animation: slide-in 0.3s ease;
}
```
