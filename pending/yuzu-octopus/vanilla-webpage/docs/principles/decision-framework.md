# Decision Framework

Use this flowchart before starting any webpage project:

```
Start
  │
  ▼
Can semantic HTML do it?
  │
  ├─ Yes → Done. Use <dialog>, <details>, <nav>, <form>, etc.
  │
  └─ No
      │
      ▼
  Can 20 lines of vanilla CSS do it?
      │
      ├─ Yes → Write the CSS. Check cookbook/ for patterns.
      │
      └─ No
          │
          ▼
      Does a classless CSS framework solve it in one <link>?
      │
      ├─ Yes → Use Pico, EdibleCSS, Acorn, or similar.
      │         Check SKILL.md §7 for the full allowlist.
      │
      └─ No
          │
          ▼
      Is the problem interactivity?
      │
      ├─ Yes → Use vanilla JS (querySelector + addEventListener)
      │         For complex cases: HTMX from CDN
      │
      └─ No
          │
          ▼
      Consider a lightweight component approach.
      Check SKILL.md §7 Category B/C for options.
```

## Quick Reference

| Need | Solution |
|------|----------|
| Modal | `<dialog>` element |
| Accordion | `<details>/<summary>` |
| Dropdown | CSS `:focus-within` or Popover API |
| Carousel | `scroll-snap` + `::scroll-button` |
| Dark mode | CSS custom properties + `data-theme` attribute |
| Responsive grid | `repeat(auto-fit, minmax())` |
| Fluid typography | `clamp()` |
| Theme switching | `light-dark()` or `[data-theme]` |
