<!-- Copyright 2026 artinnok. SPDX-License-Identifier: Apache-2.0 -->

# Audience rules

The user may select customers, internal developers, or both. Apply one audience
to each output: `knowledge/customer/` and `knowledge/internal/`. Both outputs may
share an investigation, but each needs its own writing, validation, and baseline.
The detailed process map and provenance remain private working material.

## Customer-facing knowledge

Write for customers using the product or seeking L1 support. Explain what they
can do, what they need, what happens next, and how to resolve a problem. Use
customer-visible terminology and safe, fictional examples.

Include supported information about:

- Features, user journeys, permissions, and documented customer configuration.
- Customer-relevant validation, supported formats, limits, and error recovery.
- Subscription behavior and public plan terms when supported by suitable
  public-facing evidence. Treat code-only prices or entitlements as unverified
  customer terms, not a current commercial offer.
- Known product limitations and the practical effect on the customer.

Exclude:

- Internal revenue, profit, margins, costs, forecasts, transaction aggregates,
  customer lists, headcount, and nonpublic organizational information.
- Actual personal data, customer conversations, account records, logs, or dumps
  identifying people or organizations. Use synthetic examples instead.
- Credentials, tokens, private keys, connection strings, internal endpoints,
  private repository links, infrastructure topology, and security bypass details.
- Nonpublic contracts, negotiations, incident narratives, roadmaps, staff
  commentary, or other confidential business information.
- Private source paths, internal process-map links, and sensitive facts concealed
  in comments, filenames, citations, screenshots, or metadata.

Public API paths and intended customer configuration are appropriate when they
are part of the supported customer interface. Do not confuse them with private
administrative interfaces or infrastructure addresses.

Base inclusion on evidence that information belongs in the customer interface,
public documentation, or an explicitly approved public scope. Its presence in a
repository does not establish that it is suitable for publication. If disclosure
status is unclear, omit the sensitive detail, keep the customer explanation
useful, and record the unresolved issue privately. Do not block unrelated safe
articles while resolving it.

Protecting reputation means protecting confidential information, not hiding
truthful limitations or making unsupported promises. Describe a known limitation
and supported workaround plainly without exposing its confidential internal
cause. Do not invent an escalation channel, guarantee, policy, or workaround.

Review the entire customer output, not just article bodies. Keep it separate
from internal documents and never link customer articles to the internal base or
private working material. The public Reposaur attribution link is permitted;
it must not contain local paths, repository identifiers, or other private data.
If the agent cannot establish the customer output's disclosure safety, report
it as a draft requiring review rather than declaring it ready for distribution.

## Internal developer knowledge

Write for developers who need to understand, maintain, debug, and extend the
product. Include the full relevant business mechanics and implementation detail:

- Actors, permissions, invariants, state transitions, and boundary conditions.
- Business calculations, charging rules, accounting flows, and internal limits.
- Entry points, models, services, scheduled jobs, APIs, and integrations.
- Configuration names, defaults, feature flags, and environment dependencies.
- Failure handling, recovery, operational procedures, and relevant tests.
- Source references, implementation gaps, technical constraints, and conflicts
  between current behavior and documented plans.

Explain business meaning as well as implementation. Do not reproduce source code
or every symbol merely to make a document more detailed. Separate historical
design proposals from implemented behavior.

Internal scope permits relevant business rules; it does not justify copying
production data, unrelated financial or personnel reports, or personal records.
Document a calculation or data schema using fictional values. Refer to secrets
by their configuration names and purpose, never by their actual values. Avoid
reading secret stores, `.env` files, private keys, or data dumps; use code,
sanitized examples, and schema definitions instead.

## Working material and distribution boundary

Keep the external working directory private. It may reveal source locations and
business mechanics even without secret values. Do not automatically publish,
upload, or commit it. Customer exports contain only `knowledge/customer/`;
sharing the whole knowledge root would include any internal output too.

Use private evidence to support public claims without reproducing private
evidence in the customer output. Store only the information necessary for
coverage, traceability, and updates. Do not copy sensitive values into the map,
inventory, state, article drafts, or the final chat response.
