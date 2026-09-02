# Template builder wireflows

## New draft

`intent → multiChannel body → variables → overrides → optional components → previews → validation → draft save`

- The internal draft may have a product label, but serialization drops it because create does not accept top-level `name`.
- Variable insertion writes the placeholder and entity together.
- Switching a channel override off preserves it locally until the user confirms deletion.

## Validate

`serialize → local linter → fix field errors → sandbox request → reconcile server response`

- Mark Meta `components[]` imports as unconverted and block Sent submission.
- Preserve the last valid server response separately from the working draft.
- Server normalization should appear as a reviewable diff.

## Submit for review

`draft → final preview → confirmation → submit_for_review=true → PENDING or returned state`

Do not autosubmit. The confirmation displays category, language, samples, buttons, overrides, and warnings.

## Status changes

`DRAFT → PENDING → APPROVED | REJECTED | PAUSED | unknown`

This is a UI model, not a promise of an exhaustive provider state machine. Template webhooks can forward `CATEGORY_UPDATED`, `DISABLED`, or future values. Render unknown states and keep raw values.

## Rejection recovery

`webhook/poll → retrieve current resource → show reason → fork editable revision → lint → sandbox → confirm resubmission`

Avoid destructive in-place edits when content is locked. Keep the submitted version and revision history visible.

## RCS preview

`text → zero-to-four suggestion chips → device preview`

Do not add rich-card, carousel, or attachment branches to current Sent workflows. If a mockup illustrates future capability, label it roadmap-only and exclude it from serialized requests.

## Routing simulator

If the product includes a send simulator, keep routing semantics explicit:

- no `channel` / `["sent"]`: automatic routing and fallback;
- one explicit channel: pinned;
- two or more explicit channels: broadcast with one message per recipient/channel pair.
