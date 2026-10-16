# Layout and accessibility

Use semantic HTML and application CSS Grid/Flexbox for page composition. Neural Card, Panel, Splitter and DashboardGrid serve specific contracts; do not invent a universal Neural layout component. Inspect their individual API references before composing them.

Use public spacing, typography, surface and border tokens from [the catalog](api/tokens.md). Prefer logical CSS properties, min-width: 0 on flexible children, and explicit local overflow on wide data regions. Test narrow viewports with real data and long labels. Avoid hiding content merely to suppress document overflow.

Use an application-wide border-box sizing baseline for elements and pseudo-elements. The integration fixture applies this reset; without it the 2.0.1 Select trigger can exceed its available width through padding and borders. This is application CSS, not a private component override.

Every form control needs a meaningful accessible name. Prefer each control's documented label input or explicit label/ID associations. Keep labels distinct from placeholders. Connect hint and error text through the supported contracts. Preserve aria-invalid and required semantics, and inspect the resulting native control, not only the Angular host.

Use native buttons and links for their corresponding actions. Neural Button is button[neu-button]; give icon-only actions an ariaLabel and use an appropriate type in forms. Keep keyboard navigation, visible focus, disabled semantics and focus order intact.

For Tabs verify tablist/tab/tabpanel names, selected state and arrow-key behavior. For tables use meaningful column headers and stable row identity. For Dialog verify its name, Escape behavior, focus containment and restoration. Accepting or rejecting a close proposal must match the product's intended behavior.

Test zoom, reduced motion, forced colors, light/dark contrast, validation announcements and screen-reader behavior where required. The bundled Chromium checks cover specific naming, keyboard and focus scenarios plus a narrow layout; they are not a WCAG conformance certificate or an assistive-technology audit.

Sources: [official accessibility guidance](https://ui.neuralui.org/v2/en/foundations/accessibility), [design tokens](https://ui.neuralui.org/v2/en/foundations/design-tokens).
