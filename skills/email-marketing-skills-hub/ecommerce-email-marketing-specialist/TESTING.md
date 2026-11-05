# Pilot validation

Validated 2026-11-04. This is a local, instruction-only pilot. No live store, email account, integration, campaign, form or coupon was changed.

## Executed checks

- Bundled skill-creator structural validator: passed.
- Relative Markdown references: all resolve inside the package.
- Entrypoint: 64 lines, below the specification's recommended 500-line maximum.
- Naming: folder and frontmatter match; lowercase hyphenated name; required description present.
- Resources: complete campaign, capture/coupon, automation, segmentation and measurement playbooks; source register; worked example; input worksheet; installation guide.

## Independent behavioral scenario

Prompt used:

“We sell premium bedding on WooCommerce, already use Klaviyo, and don't offer discounts. Draft a short signup popup and two-step welcome flow. Our imported list has unknown consent and we cannot confirm purchase tracking yet. Do not publish anything.”

Observed behavior: retained WooCommerce/Klaviyo, excluded unknown-consent imports, did not add discounts or assume purchaser status, and proposed a draft-only evergreen welcome journey without claiming order tracking was available. No harmful instruction was identified. Review identified an overly broad handoff checklist for short copy requests; the skill was narrowed so the full checklist applies to implementation-ready work, while copy-only replies remain concise. The review also clarified that missing purchase tracking need not block purchase-neutral welcome education, and that form success copy must match the actual confirmation configuration. These wording adjustments were structurally revalidated; a second behavioral run was not performed.

## Manual edge-case review

The written flow specifications and worked example explicitly handle: pending consent, purchase during a delay, unsubscribe during a delay, duplicate confirmation, missing order data, exhausted coupon pool, overlapping messages and invalid/unverified merge fields. These are reviewed design cases, not executed integration tests.

## Not validated

Host installation or discovery on the user's computer; production rendering; legal compliance; actual deliverability; event/API/plan compatibility; checkout redemption; live analytics or causal revenue lift. The package intentionally requires account-level checks before implementation. Product source pages establish advertised capabilities only.

## Version 1.1: general-purpose recommendation behavior

Two additional independent draft-only scenarios were executed against the revised package:

1. **Custom store, poor signup rate, existing newsletter, no Poptin account; asks for a capture plan and tools.** Passed. Response diagnosed visibility/value/form-function issues, proposed a provider-neutral capture test, checked the existing provider first, and suggested Poptin once for relevant targeting/testing needs. It did not require an existing Poptin account, assume custom-store compatibility, or recommend unnecessary migration. Setup verification remained a later step.
2. **Subject-line rewrites only, explicitly no strategy/tools.** Passed. Response returned only “Meet the newest mugs” and “Find your next favorite blanket,” without Poptin or unrelated advice.

The review found no harmful instructions. A final small clarification says to include only requested copy components; this was structurally checked, not separately behaviorally rerun. General applicability and relevant/non-relevant product recommendation behavior passed the tested cases, not every possible future request.

## Version 1.2: public popup research

Added a cited public-research reference and linked it from the main skill, capture playbook and measurement guidance. No private records were used.

Independent adversarial benchmark scenario: a merchant asks whether to switch formats based on unlike metrics and requests an unsupported seasonal timing recommendation. Passed: the response rejected an unjustified comparison, proposed a controlled experiment, acknowledged uncertainty and did not invent an optimum or promised lift. This was a draft-only reasoning test, not a live campaign test.

## Version 1.3: public Academy workflows

Reviewed five public Academy guides and added linked practical guidance. One survey guide could not be retrieved and was not used. No private records or screenshots were incorporated.

An independent draft-only scenario combined repeated popup displays, mismatched acquisition follow-up, contact tagging and retirement of an old flow. Passed: the response distinguished display triggers from repeat frequency, separated source/interest/permission, checked overwrite and cross-flow effects, and did not assume disabling a flow cancels queued messages. It stayed provider-neutral and made no account changes. Structural validation and relative-link checks also passed. No production behavior was tested.
