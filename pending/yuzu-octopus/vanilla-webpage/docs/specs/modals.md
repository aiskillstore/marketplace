# Modals Spec

## Code

```html
<dialog id="modal">
  <form method="dialog">
    <h2>Title</h2>
    <p>Content</p>
    <button>Close</button>
  </form>
</dialog>
```

```javascript
document.getElementById('modal').showModal();
// or: dialog.close('result');
```

## Styling

```css
dialog {
  border: none;
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  max-width: 450px;
  width: 90%;

  /* Entry animation */
  opacity: 1;
  transform: scale(1);
  transition: opacity 0.3s, transform 0.3s, display 0.3s allow-discrete;

  @starting-style {
    opacity: 0;
    transform: scale(0.95);
  }
}

dialog::backdrop {
  background: rgba(0,0,0,0.5);
  opacity: 1;
  transition: opacity 0.3s, display 0.3s allow-discrete;
}
```

## Rules

- Use `<dialog>` — it handles focus trap, Escape key, and backdrop click automatically
- `method="dialog"` on the form closes the dialog on submit
- `dialog.returnValue` contains the result
- Always provide a close button
- `@starting-style` for entry animation (modern CSS)
