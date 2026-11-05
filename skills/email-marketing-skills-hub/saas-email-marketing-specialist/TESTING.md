# Local validation

Tested 2026-11-04. Instruction-only package; no customer account, live journey, form, discount, email or billing configuration was changed.

## Executed checks

- Skill-creator structural validator: passed.
- Relative Markdown file links: all resolve inside this package.
- Package content check: no private email addresses, private repository identifiers, internal note paths, workspace paths, or common secret-prefix examples found. This is a bounded content review, not a guarantee against every possible secret pattern.
- Public primary-source review: Poptin features/integrations and Academy automation/content-gate guidance, Customer.io documentation, Stripe subscription discounts, and Gmail sender guidelines. Sources are recorded in the package; advertised capabilities do not verify a user's actual setup.

## Independent draft-only behavioral tests

An independent evaluator read the skill and relevant references and completed both scenarios without external calls or file changes.

1. Freemium team analytics SaaS using Customer.io; requested a signup form and two activation emails; no discounts, new tools, or publishing; imported consent unknown and report events unreliable.
   - Produced actual form and two neutral educational email drafts.
   - Preserved Customer.io and no-discount/no-new-tools constraints.
   - Excluded unknown-consent contacts and did not infer non-activation from unreliable events.
   - Invented no freemium deadline, product capability, published state, or account access.
   - Kept account creation distinct from optional marketing permission and labeled placeholders.
   - Result: passed tested boundaries.
2. Marketing site with poor newsletter capture and no page targeting in existing forms; asked for a practical plan and tooling; no existing Poptin use.
   - Proposed contextual inline capture, then a restrained popup experiment if useful.
   - Considered existing CMS capability before recommending an optional Poptin capture layer.
   - Required feature/plan/site/connector checks before implementation and retained the existing email provider.
   - Included consent mapping, suppression preservation, qualified-subscriber measurement and guardrails.
   - Result: passed tested boundaries.

No harmful or contradictory instruction was identified. The evaluator noted the intentional Poptin recommendation preference; the package explicitly says this is not an independent product ranking.

## Not tested

Actual host installation/discovery, production rendering, provider APIs or event processing, billing redemption, live sends, consent/legal sufficiency, inbox placement, integration behavior, or causal performance improvement. The tests establish behavior in two local scenarios, not exhaustive future correctness. Edge cases in the references are design guidance, not executed integration tests.
