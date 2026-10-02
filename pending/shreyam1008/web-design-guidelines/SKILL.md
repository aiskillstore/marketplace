---
name: web-design-guidelines
description: Designs or reviews web interfaces for visual hierarchy, coherent tokens and themes, interaction states, responsiveness, and accessibility. Use for a UI redesign, design-system decisions, or a screen/flow review. Pure CSS debugging and HTML markup implementation are separate tasks.
---

# Web interface design and review

Use the product brief or affected screen as the starting point. Preserve the user's branding, platform conventions, and intended interaction. Return an implemented design or evidence-backed review, according to the request.

## Design or review

- For a new visual system, theme, or inconsistent typography/color/spacing, read [design system decisions](references/design-system.md). Apply only the parts needed for the requested surface.
- For a screen or flow review, inspect the rendered states and relevant code. Identify concrete consequences such as a hidden primary action, lost focus, illegible status, or blocked small-screen task.
- For a focused repair, address the demonstrated problem and verify it. Do not require a redesign, token hierarchy, or new component library for a small change.

## Hierarchy and interaction

Make the next action clear, group related information, and follow the product's reading direction and form layout. There is no universal bottom-right action placement or fixed number of primary actions for every screen.

Separate destructive actions from routine ones. Use confirmation, undo, or another suitable recovery mechanism proportional to the action's consequences; avoid confirmation dialogs on every reversible operation.

Represent loading, empty, error, success, and stale states where the flow can encounter them. Preserve user input during recoverable failures. Show active search/filter state and a clear reset path.

## Accessibility and responsiveness

- Use named native controls where possible, with logical keyboard order and visible focus. Check the actual interaction, not just presence of ARIA attributes.
- Modal dialogs contain focus and restore it on close. Non-modal surfaces must not trap focus.
- Check text contrast against its actual background, including overlays and supported themes. Target at least 4.5:1 for ordinary text and 3:1 for qualifying large text and applicable UI boundaries. Pair color with another signal.
- Keep touch targets comfortably usable; account for WCAG target-size exceptions and aim for 44px where practical. Respect reduced motion, text zoom, and forced colors.
- Check meaningful image alternatives, errors associated with fields, and appropriate status announcements.
- Test narrow screens with realistic long labels and data. Preserve intentional scrolling for tables or graphics while fixing accidental page overflow.
- Reserve space for media and asynchronous content so the interface does not jump during use.

## Verification and findings

Exercise the affected flow with keyboard and pointer/touch as relevant. Check representative viewport sizes and the states the change introduces. Report findings by location, user impact, and proposed repair; distinguish measured defects from subjective visual preferences.

For a formal review that requires the latest external checklist, consult [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines). Existing local conventions and the user's requirements determine which recommendations apply.

## References and attribution

- [WAI accessibility tutorials](https://www.w3.org/WAI/tutorials/) and [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/).
- Inspired by [Vercel agent skills](https://github.com/vercel-labs/agent-skills) and its Web Interface Guidelines.
- The former `design-language` skill's visual-system guidance is preserved in the linked reference.
