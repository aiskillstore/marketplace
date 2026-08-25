# Status model and decision boundaries

## Approved policy statuses

- `codified_current`: text currently reflected in eCFR as of its latest available date.
- `model_deviation`: FAR Council model text published for possible agency adoption; never mark operative for an agency by itself.
- `agency_class_deviation`: an agency-issued deviation whose document supplies scope and effective terms.
- `proposed_rule`: published proposal or supplemental proposal; not current policy.
- `final_rule_pending_effective`: final rule published with a future effective date.
- `final_rule_effective`: final rule effective as of the analysis date.
- `withdrawn`: proposal, rule, notice, or initiative explicitly withdrawn.
- `superseded`: text or deviation replaced, rescinded, expired, or otherwise displaced by cited evidence.
- `nonregulatory_guidance`: FAQ, companion, practitioner album, memorandum, buying guide, or other guidance that is not codified regulation.

Do not compress these statuses into a single undifferentiated answer.

## Documented-status finding

A documented-status finding may say what the cited sources indicate for a named agency and date. It must:

1. Identify the codified baseline.
2. Identify any posted agency deviation and quote or pinpoint its scope and timing.
3. Identify related model text, final rule, proposed rule, or guidance without treating it as the same authority layer.
4. State conflicts, missing internal policy, and source limitations.
5. End with the procurement-specific determination boundary.

Every documented-status finding records `status_resolution` as `documented_clear`, `documented_conflict`, or `authorized_resolution`, plus the IDs of any material conflicts. If a cited conflict is unresolved, the finding must use `documented_conflict`; it may describe both source positions but may not decide which value controls, governs, applies, or is the operative threshold.

Only an authorized official's explicit resolution may change a conflict to `resolved_by_authorized_official`. Model inference, source hierarchy, incorporation language, drafting context, repetition count, or the fact that one document is newer does not resolve the conflict. Preserve the official's role, resolution, and timestamp in the record.

Permitted example: `The cited agency class deviation states that covered procurements use the incorporated RFO Part 10 text effective July 8, 2025; eCFR remains the codified baseline. Confirm transaction-specific treatment with the agency policy office.`

Prohibited example: `RFO Part 10 legally governs this procurement.`

## Timing rules

- Compare every effective, expiration, rescission, transition, solicitation, award, modification, and option date that the source makes material.
- A Federal Register publication date is not automatically its effective date.
- A posted update date is not automatically an effective date.
- Do not infer dates from filenames.
- When a final rule is effective but eCFR has not caught up, describe the published final rule and the eCFR lag separately.

## Public comments

Comments do not establish the governing rule. Present themes as `observed in the reviewed sample`, name the sampling method, and report contrary positions. Do not label a view majority, consensus, industry position, or government position without a defined denominator and supporting evidence.

## Supplied policy documents

Record title, issuer, date, version, status, controlling sections/pages, and whether the user represents it as approved. A later draft does not supersede an earlier approved document merely because it is newer. Ask the user to resolve material precedence conflicts.

## Reserved matters

The workflow does not:

- Provide legal advice.
- Decide procurement-specific applicability.
- Approve a deviation or policy.
- Select clauses or certify solicitation compliance.
- Determine protest risk, allowability, responsibility, or price reasonableness.
- Submit comments or communicate with an agency.
