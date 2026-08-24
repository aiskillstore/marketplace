# Acquisition Policy Impact Brief specification

## Required sections

1. Executive Summary
2. Question and Scope
3. Documented Current Status
4. Source Hierarchy and Authorities
5. Change Timeline
6. Government and Industry Impacts
7. Open Issues and Comment Deadlines
8. Operational Considerations
9. Evidence Register
10. Limitations and Reserved Determinations

Use the `standard_business_brief` visual preset with a restrained memo masthead. Use US Letter portrait, one-inch margins, Calibri 11-point body text, blue heading hierarchy, quiet running header/footer, real list styles, and fixed-width tables with repeating header rows.

The title block states the agency or scope, as-of date, audience lens, and preparation status. Do not call the brief a legal opinion, authoritative policy determination, or contract-file approval.

## Evidence presentation

- Put evidence IDs beside every consequential finding and impact statement.
- Preserve canonical public hyperlinks in the evidence register.
- Keep codified text, agency deviations, model text, rulemaking, guidance, and public comments visually distinguishable.
- Use tables only for repeated comparable records such as policy layers, timelines, and the evidence register.
- Do not place internal prompts, tool names, filesystem paths, credentials, or raw private text in the document.

## Impacts

Government and industry lenses use the same evidence. They may differ only in operational framing:

- Government: acquisition planning, solicitation timing, internal policy confirmation, transition treatment, and file documentation.
- Industry: solicitation interpretation questions, proposal assumptions, compliance planning, timing, and monitoring.
- Neutral: both lenses without advocacy.

Impacts are considerations, not directives or legal conclusions.

## Validation

The builder requires `validation.findings_approved` and `validation.brief_approved` to be true. The validator checks section order, evidence-ID coverage, live hyperlinks, as-of date, decision-boundary language, fixed table geometry, repeating headers, prohibited internal content, and policy-record validity.
