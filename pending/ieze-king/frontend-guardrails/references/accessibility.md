# Accessibility / a11y (detail)

Read this when building any interactive UI, form, or content layout. Accessibility widens your audience and is often a legal requirement — and accessible markup is usually cleaner markup.

## Semantic HTML first
Use the right element for the job: `<button>` for actions, `<a>` for navigation, `<nav>`, `<main>`, `<header>`, `<footer>`, and headings (`<h1>`–`<h6>`) in logical order. Semantic elements give correct behavior, focus handling, and screen-reader support for free. Reach for ARIA only to fill genuine gaps a semantic element can't cover — misused ARIA is worse than none.

## Keyboard operability
Everything operable by mouse must be operable by keyboard:
- Logical tab order that follows the visual flow.
- Visible focus indicators on every interactive element (never remove focus outlines without replacing them).
- No keyboard traps — users must be able to tab out of any widget.
- Custom interactive elements need appropriate `role`, `tabindex`, and key handlers (Enter/Space/Escape/arrows as relevant).

## Color and contrast
- Maintain sufficient contrast between text and background (WCAG AA: 4.5:1 for normal text, 3:1 for large text).
- Never convey meaning by color alone — pair it with text, an icon, or a pattern, so color-blind and low-vision users get the same information.

## Forms
- Every input has an associated `<label>` (not just a placeholder).
- Errors are associated with their field (e.g. `aria-describedby`) and announced, not only shown visually.
- Group related controls (`fieldset`/`legend`) where appropriate.

## Images and media
- Meaningful images get descriptive `alt` text; purely decorative images get empty `alt=""` so screen readers skip them.
- Provide captions/transcripts for video and audio where relevant.

## Dynamic updates
- Announce important dynamic changes (notifications, live results, loading completion) with `aria-live` regions so screen-reader users are aware of them.

## Quick checklist
- [ ] Correct semantic elements used; ARIA only where needed and correct.
- [ ] Fully keyboard-operable with visible focus; no traps.
- [ ] Contrast meets AA; meaning never by color alone.
- [ ] All inputs labelled; errors associated and announced.
- [ ] Images have appropriate alt (descriptive or empty); media captioned.
- [ ] Important dynamic updates announced via aria-live.
