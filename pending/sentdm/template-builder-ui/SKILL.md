---
name: template-builder-ui
description: Designs and audits tenant-facing Sent template builders, previews, validation, lifecycle UX, and API payload mapping. Use for template editor forms, variables, channel overrides, WhatsApp review, RCS suggestion chips, authentication templates, and safe submission flows.
---

# Sent Template Builder UI

Design the interface around Sent's v3 `definition` contract. The UI may import Meta material, but its canonical saved and submitted model must never be Meta's `components[]` payload.

## Product model

Use one draft object with:

- optional `category` and `language`;
- required `definition.body.multiChannel`;
- optional complete body overrides for `sms`, `whatsapp`, and `rcs`;
- optional `definition.header`, `footer`, `buttons`, `definitionVersion`, and `authenticationConfig`;
- submission controls for `creation_source`, `submit_for_review`, and `sandbox`.

Do not expose top-level create fields named `name`, `channels`, `body`, `header`, or `buttons`. If the product needs an internal display label, keep it outside the Sent create payload.

## Recommended editor sequence

1. Capture intent and category.
2. Write the `multiChannel` body.
3. Insert variables as structured entities.
4. Add optional per-channel overrides.
5. Add header, footer, and buttons where supported.
6. Review live previews and accessibility.
7. Validate locally and with `sandbox: true`.
8. Save a draft, then explicitly submit for provider review.

Category should not block the first keystroke, but it must be visible before submission because it affects authentication rules and WhatsApp policy review.

## Variable UX

Inserting a variable creates both:

- a placeholder such as `{{0:variable}}`; and
- a matching entity with `id`, `name`, `type`, and `props.sample`.

Renumber atomically when variables move. Never let users edit placeholder syntax independently of the entity table. Show a clear error for naked `{{1}}` or IDs without definitions.

## Validation matrix

Apply the exact rules in [references/template-validation-matrix.md](references/template-validation-matrix.md), including:

- a 1,024-character maximum for every body;
- 60 characters for header and footer;
- no footer variables;
- 10 buttons total;
- button types `QUICK_REPLY`, `URL`, `VOICE_CALL`, `PHONE_NUMBER`, and `COPY_CODE` with their per-type limits;
- no invented quick-reply-versus-CTA exclusivity;
- `authenticationConfig` and authentication restrictions;
- complete, independently valid channel overrides.

Run the bundled `waba-template-author` linter against serialized JSON. Server validation remains authoritative.

## Channel previews

### SMS

Preview plain text and estimated GSM/UCS-2 segments. Make clear that segment estimates affect billing and are not template body limits.

### WhatsApp

Preview header, body, footer, and buttons. Show sample values, category, language, and provider-review impact.

### RCS

Current Sent RCS guidance supports text plus up to four suggestion chips. Rich cards, carousels, and media attachments are roadmap capabilities, not current Sent builder controls. Do not generate capability declarations for unavailable features.

Channel routing belongs to the send flow, not the template editor. If routing is shown in a simulator:

- omitted `channel` or `["sent"]` means automatic routing and fallback;
- `["rcs"]` pins RCS with no cross-channel fallback;
- multiple explicit values mean broadcast and separate billable messages.

Never describe an explicit RCS-plus-SMS array as ordered fallback.

## Save and review behavior

Use `sandbox: true` for validation. Save with `submit_for_review: false`. Before switching it to `true`, show:

- category and language;
- rendered previews with sample values;
- channel overrides;
- button actions;
- any warnings;
- the fact that provider review is an external state change.

Do not autosubmit on save.

## Lifecycle UX

Resource status values currently include `DRAFT`, `PENDING`, `APPROVED`, `REJECTED`, and `PAUSED`. Keep an unknown-state renderer.

WhatsApp template webhook events use `field: "templates"`, no `sub_type`, and no `event`; the status is `payload.status`. Provider values can include `CATEGORY_UPDATED`, `DISABLED`, and other future strings. See [references/template-status-handling.md](references/template-status-handling.md).

## Accessibility and failure recovery

- Associate every error with a field and a summary.
- Do not rely on preview color alone.
- Preserve user edits after validation failures.
- Keep raw JSON inspection available for advanced users.
- Label imported Meta JSON as “Meta Cloud API source” until converted.
- Provide a diff for server normalization and provider-driven category/status changes.

Use [references/template-ui-wireflows.md](references/template-ui-wireflows.md) for state transitions. Use `waba-template-author` for copy and policy judgment, `sent-templates` for existing-resource operations, and `rcs-agent-onboarding` for RCS launch readiness.
