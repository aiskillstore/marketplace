# Accessibility Checklist

Designs rarely document accessibility. Treat this checklist as mandatory when translating any design into code.

## Semantic HTML

- Use native `<button>` for actions, `<a>` for navigation. Never attach `onClick` to a `<div>` or `<span>` for primary interaction.
- Use native form controls (`<input>`, `<select>`, `<textarea>`) inside a `<form>` with proper labels.
- Use `<nav>`, `<main>`, `<header>`, `<footer>`, `<aside>` for landmarks. Exactly one `<main>` per page.
- Headings form a single hierarchical outline. One `<h1>` per page; do not skip levels for visual sizing.

## Interactive elements

- Every interactive element is reachable by Tab in a logical order.
- Visible focus state on every interactive element. Use a token-backed ring (`focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2`), not `outline: none`.
- Hover-only affordances must have a non-hover equivalent (focus, persistent state on touch).
- Disabled state communicates via `disabled` attribute on form controls or `aria-disabled` on buttons that intentionally remain focusable.

## Labels and names

- Icon-only buttons must have `aria-label` or visually hidden text.
- Form fields have an associated `<label>` (via `htmlFor`/`id` or wrapping). Placeholder text is not a label.
- Images use `alt`. Decorative images use `alt=""`. Never omit the attribute.

## ARIA

- Use ARIA only when semantic HTML is insufficient. Native first.
- For composite widgets (combobox, tabs, dialog, menu), prefer a tested primitive library (Radix, shadcn/ui, Headless UI) over hand-rolled ARIA.
- Live regions (`aria-live="polite"`) for async feedback (toasts, validation, status updates).

## Color and contrast

- Body text contrast at minimum 4.5:1 against its background. Large text minimum 3:1.
- Do not rely on color alone to communicate state. Pair color with icon, text, or shape.
- Verify contrast for both light and dark themes.

## Keyboard

- Modals trap focus while open and restore focus on close.
- Escape closes dialogs, popovers, command menus.
- Arrow-key navigation inside composite widgets (tabs, menus, radio groups, listboxes).

## Motion

- Honor `prefers-reduced-motion`. Disable non-essential animation when the user has requested reduced motion.
- Auto-playing media has a pause control.

## States to implement for every interactive component

- default
- hover
- focus-visible
- active / pressed
- disabled
- loading (if the component triggers async work)
- error (if the component can produce one)

## Quick failures to look for

- `<div onClick={...}>` instead of `<button>`.
- `outline: none` without a replacement focus ring.
- Icon-only buttons without `aria-label`.
- Images without `alt`.
- Modals that do not trap focus or do not close on Escape.
- Color-only error indication (red text without an icon or message).
- Skipped heading levels for visual weight.
