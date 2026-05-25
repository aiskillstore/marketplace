# Browser Audit Criteria

Use this reference after opening `browser-audit` when you need a detailed checklist or a rubric for manual checks.

Sources to consult when precision matters:

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- WAI-ARIA overview and APG entry point: https://www.w3.org/WAI/standards-guidelines/aria/
- Lighthouse docs: https://developer.chrome.com/docs/lighthouse
- Context7 Lighthouse docs: `/googlechrome/lighthouse`

## Automated Checks

Run or approximate these checks in the rendered page:

- Lighthouse scores and failing audits for accessibility, SEO, best practices, and performance.
- Console errors, unhandled promise rejections, hydration/runtime errors, failed network requests, mixed content, and blocked assets.
- Head metadata: unique `<title>`, useful meta description, canonical URL, robots/indexability, viewport, `html[lang]`, Open Graph/Twitter basics when social previews matter.
- SEO renderability: meaningful content is present in rendered DOM, links use crawlable `href`, important pages are not hidden behind client-only interactions, structured data is valid when present.
- Headings: exactly one page-level `h1` unless a deliberate document outline justifies more; headings describe topics and do not skip structure in confusing ways.
- Images: informative images have meaningful `alt`; decorative images use empty `alt` or are ignored by assistive tech; linked image purpose is exposed.
- Controls: buttons/links/inputs have accessible names; links have discernible destinations/purpose; disabled states are programmatically and visually clear.
- Forms: labels are programmatically associated; required fields and errors are announced; inputs use appropriate type and autocomplete; error summary links to fields for larger forms.
- ARIA: roles are valid; required ARIA attributes are present; `aria-*` IDREFs point to existing IDs; no focusable element is inside `aria-hidden="true"`; native HTML is preferred over unnecessary ARIA.
- Landmarks: header/nav/main/footer/search/complementary are present and not excessive; repeated navigation is distinguishable.
- Contrast: check text contrast, non-text contrast for meaningful icons/borders/focus indicators, and state contrast for hover/focus/error/disabled.
- Responsive: no horizontal scroll at mobile widths, text stays readable, targets are at least 24 by 24 CSS pixels or satisfy WCAG 2.5.8 exceptions.

## Manual Browser Checks

These checks are not reliably proven by automation and must be marked manual or partial:

- Keyboard order matches visual/logical order.
- Every interactive element is reachable and operable by keyboard.
- Focus indicator is visible, not hidden behind sticky headers/footers, and not removed by CSS.
- Escape closes dismissible overlays; focus returns to the triggering control.
- Modal dialogs trap focus while open and expose name, role, and state.
- Menus, tabs, accordions, comboboxes, sliders, and other composite widgets follow expected ARIA/APG keyboard behavior.
- Hover-only content is also available by focus/touch.
- Form validation is understandable after failed submit and does not erase user input.
- 200% zoom and mobile layouts preserve content and controls without overlap.
- Motion, autoplay, carousels, videos, and animated content provide pause/stop/reduce-motion behavior when relevant.
- The primary user journey can be completed without mouse input.

When manual checks are skipped because of auth, tool limits, time, or unavailable user flows, include a `Residual Risk` item.

## WCAG 2.2 AA Focus Areas

Prioritize these for pre-deploy review:

- 1.1.1 Non-text Content: alternatives for images and icon-only controls.
- 1.3.1 Info and Relationships: semantic structure, labels, tables, lists, landmarks.
- 1.4.3 Contrast Minimum: normal text 4.5:1, large text 3:1.
- 1.4.10 Reflow: content works at narrow widths without two-dimensional scrolling except where essential.
- 1.4.11 Non-text Contrast: meaningful UI components and graphical objects have 3:1 contrast.
- 2.1.1 Keyboard and 2.1.2 No Keyboard Trap: all functionality works by keyboard.
- 2.4.3 Focus Order, 2.4.7 Focus Visible, 2.4.11 Focus Not Obscured Minimum.
- 2.4.4 Link Purpose and 2.4.6 Headings and Labels.
- 2.5.7 Dragging Movements: provide non-drag alternatives unless dragging is essential.
- 2.5.8 Target Size Minimum: target is at least 24 by 24 CSS pixels or has sufficient spacing/equivalent control.
- 3.1.1 Language of Page and 3.2.x predictable navigation/behavior.
- 3.3.x labels, instructions, error identification, suggestions, redundant entry, and accessible authentication.
- 4.1.2 Name, Role, Value: custom controls expose accessible name, role, value, and state.

## Lighthouse Interpretation

Use Lighthouse failures as evidence, but inspect the page before assigning severity:

- Accessibility score below 100 usually needs itemized findings, not a generic "low score" issue.
- SEO failures involving `robots`, canonical, title, description, crawlable links, HTTP status, or mobile viewport are often P1 before deploy.
- Best-practices failures involving HTTPS, mixed content, vulnerable libraries, console errors, unsafe links, or permission prompts can be P0/P1 depending on user impact.
- Performance failures are P1 when they break user journeys or Core Web Vitals targets; otherwise P2 unless the user requested strict performance gating.

## Finding Quality Bar

A useful finding includes:

- The exact user impact.
- The affected element/page/state.
- Reproduction steps when manual.
- The standard or tool signal involved.
- A concrete fix that fits the existing implementation.

Avoid vague findings such as "improve accessibility" or "SEO is bad". Split separate root causes into separate findings.
