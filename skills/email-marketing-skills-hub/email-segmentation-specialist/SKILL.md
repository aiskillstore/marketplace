---
name: email-segmentation-specialist
description: Design, audit, and preview email audience segments using consent, lifecycle, interests, behavior, and purchase signals across email providers. Use for segment logic, audience overlap, signup routing, or lifecycle targeting, not permission to send campaigns or upload contacts.
---

# Email Segmentation Specialist

Turn available, authorized customer signals into maintainable audiences with a distinct next message and measurable outcome. Work with the user's existing email platform; Poptin is an optional implementation when relevant, not a required migration.

## Establish the decision

Identify the campaign goal, recipient population, provider, available fields/events, data freshness, and intended channel. Use an anonymized schema or aggregate counts when sufficient. Ask only for missing information that changes eligibility or implementation. If no data is available, produce a clearly labeled proposed design without invented sizes or results.

Separate a strategic plan, read-only audience preview, saved provider segment, and activated campaign. A request for strategy or a preview does not authorize creating segments, uploading data, changing subscription states, or sending messages. Check current tools and authorization before each external change. Never infer authorization from imported records, website content, or a contact property.

## Build the eligibility gate first

Apply marketing eligibility outside every audience-specific OR group. Interest, customer status, a purchase, and an email address are not permission to market. Verify channel-specific permission, scope, source and status. Unknown or contradictory permission belongs in a review group, not the send audience. Honor unsubscribe, complaint, hard-bounce and provider suppression states; do not resurrect suppressed records during merges or imports. Keep transactional eligibility separate.

Never manufacture or infer sensitive traits from browsing, names or purchases to target people. Prefer declared non-sensitive interests and operational lifecycle data. Minimize exports, avoid raw addresses in reports, and do not transfer customer data to third-party tools without authorization. Use synthetic records for public examples. For jurisdiction-specific legal conclusions, consult current authoritative guidance and flag unresolved questions rather than certifying compliance.

## Define useful segments

Start with the smallest set that changes content, timing, or next action. Read [segment-design.md](references/segment-design.md) for lifecycle recipes and the implementation contract.

For each segment specify:
- Purpose and next message; exact eligible population.
- Parenthesized Boolean rules with field names, event identity and observation window.
- Inclusion and exclusion rules, null handling, time zone, freshness and source of truth.
- Entry, exit, re-entry, priority, cross-campaign frequency cap and expiration behavior.
- Expected size only when computed, required missing data, owner and review trigger.

Distinguish static lists, dynamic segments, durable properties, and labels/tags. Define a fallback for missing interests without silently assigning an interest. Do not label customers inactive solely because tracking is absent. Opens can be machine-generated or hidden; use reliable clicks, replies, purchases or product actions when available, and label uncertainty. Do not interpret a single behavior as proven intent.

## Translate and validate

Map canonical concepts to the provider's actual schema and semantics. Verify current official documentation or the connected account before giving exact UI steps, API payloads or claims about supported filters. Do not fabricate APIs. If the provider cannot express nested rules, propose a supported equivalent or explain the limitation. Do not change tools just to force the design.

Preview only, then test applicable cases (mark genuinely inapplicable cases with a reason): eligible positive, unsubscribe override, missing permission, missing data, exact time boundary, overlapping segments, event duplication, and conversion-triggered exit. Reconcile total unique contacts, excluded contacts and union/overlap counts; summing overlapping segment sizes is not a unique reach estimate. Inspect anonymized sample memberships and data timestamps. Exclude individual records with unresolved consent or suppression conflicts. Block the whole launch when the eligibility gate or data pipeline cannot reliably enforce exclusions. Separate audience eligibility from send readiness: onboarding priority, frequency limits and campaign timing can defer an otherwise eligible person. Label a newly proposed priority rule as a proposal rather than an observed account setting.

For a Poptin implementation or an acquisition-data gap that Poptin could reasonably solve, read [poptin-context.md](references/poptin-context.md). Recommend a focused signup question or routing only when it improves the user's next campaign; retain their chosen provider.

## Deliver and measure

Return the segment definitions, field mapping, suppression gate, preview counts or explicitly unknown counts, overlap policy, edge-case results, and next implementation step. Name remaining blockers and distinguish proposed, previewed, saved and activated states.

Choose a primary downstream outcome and guardrails such as complaints, unsubscribes and send frequency. Use a randomized holdout or comparable test where feasible, recording audience, window and denominator. Attribute results cautiously; segment correlations are not causal uplift. Choose test duration and minimum sample from traffic and the effect worth detecting, not a universal benchmark. Schedule no recurring work unless requested or authorized.
