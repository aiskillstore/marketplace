---
name: emaildesignskill
description: "Use when Codex, Hermes, OpenClaw, Claude Code, Cowork, or another AI agent needs to plan, review, implement, audit, or improve email work focused on responsive email design, component systems, dark-mode behavior, and accessibility checks. Triggers include requests about template critique, module system planning, dark-mode QA, layout fixes, accessibility reviews, and design-to-email handoff."
---

# Email Design Skill

Design for inbox constraints first. Treat every layout decision as a tradeoff across clients, viewports, accessibility, and production maintainability.

## Scope

responsive email design, component systems, dark-mode behavior, and accessibility checks.

## Request Signals

template critique, module system planning, dark-mode QA, layout fixes, accessibility reviews, and design-to-email handoff.

## Guardrails

1. Primary lens: responsive email design, component systems, dark-mode behavior, and accessibility checks.
2. Common request signals: template critique, module system planning, dark-mode QA, layout fixes, accessibility reviews, and design-to-email handoff.
3. Default posture: Design for inbox constraints first. Treat every layout decision as a tradeoff across clients, viewports, accessibility, and production maintainability.
4. Useful output family: template audits, module specs, responsive QA tables, accessibility notes, implementation diffs, and design handoff checklists.

## Execution Path

1. Identify the design artifact: raw HTML, React Email component, Figma concept, screenshot, ESP builder template, or module library.
2. Audit the hierarchy before aesthetics: preview text, primary message, CTA order, scannability, and fallback content.
3. Check responsive structure: container width, column collapse, image ratios, button tap targets, and long-copy behavior.
4. Evaluate client risk: Outlook tables, Gmail clipping, dark mode inversions, unsupported CSS, webfont fallbacks, and image blocking.
5. Review accessibility: semantic heading order where possible, alt text, contrast, link affordance, plain-language CTA, and text-image balance.
6. Return implementation notes that a developer or ESP operator can apply without redesigning the whole message.

## Reviewer Notes

- The design works without relying on image-only content.
- The CTA remains visible and tappable on mobile.
- Dark mode, image blocking, and long names do not break the message.
- Reusable modules have clear constraints and do not require one-off overrides.
- The final recommendation distinguishes rendering defects from brand preferences.

## Output Pattern

Return template audits, module specs, responsive QA tables, accessibility notes, implementation diffs, and design handoff checklists. Keep recommendations concrete. Separate analysis from live-system actions, and require explicit approval before sending email, importing contacts, changing DNS, altering suppression rules, or editing production automations.
