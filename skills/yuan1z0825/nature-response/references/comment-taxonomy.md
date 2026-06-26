# Comment taxonomy

Use this file to classify reviewer comments before drafting responses.

## Severity

| Severity | Meaning | Default handling |
|---|---|---|
| `minor` | Presentation, clarity, formatting, citation, or small method-detail issue that does not alter the main evidence chain | Usually draftable with text change or citation placeholder |
| `major` | Evidence, validation, method, statistics, interpretation, or scope issue that may affect claims or editorial confidence | Requires explicit action, evidence, or author input |
| `blocking` | Ethics, compliance, data integrity, missing required approval, unsupported central claim, or unresolved fatal methodological issue | Do not draft a confident response without author action |
| `unclear` | Insufficient information to judge severity | Flag for author confirmation |

## Categories

### Editorial / presentation

Includes unclear writing, structure problems, missing definitions, figure readability, title/abstract mismatch, or confusing terminology.

Default strategy:

- Usually `ACCEPT_TEXT` or `ACCEPT_FIGURE`.
- Revise wording, structure, legend, definition, or abstract-title alignment.
- Give section, page, line, figure, or placeholder.

### Evidence / interpretation

Includes unsupported claims, overinterpretation, missing control, causal claim not justified, clinical relevance not shown, or alternative explanation.

Default strategy:

- Use `ACCEPT_EXPERIMENT`, `ACCEPT_ANALYSIS`, `SOFTEN_CLAIM`, `CLARIFY_EXISTING`, `PARTIAL`, or `DISAGREE`.
- Do not invent results.
- If evidence is absent, soften the claim and add a limitation.

### Methodological

Includes missing method detail, reproducibility issue, missing baseline, missing validation, unclear sample size, software/model/version not stated.

Default strategy:

- Use `ACCEPT_TEXT`, `ACCEPT_ANALYSIS`, or `AUTHOR_INPUT_NEEDED`.
- Request exact method details when author notes are vague.
- Map to Methods, Supplementary Methods, protocol, code, or figure/table.

### Statistical

Includes inappropriate test, missing effect size, multiple testing issue, insufficient power, missing confidence interval, unclear replicate definition.

Default strategy:

- Treat major statistical critiques as high risk until details are supplied.
- Ask for test name, replicate unit, sample size, correction method, effect size, confidence interval, and exact results where relevant.
- Do not invent p-values, confidence intervals, sample sizes, or effect sizes.

### Data / code / materials

Includes missing accession number, source data unavailable, code not provided, restricted data not justified, FAIR metadata incomplete, materials availability.

Default strategy:

- Use `ACCEPT_TEXT`, `CLARIFY_EXISTING`, `AUTHOR_INPUT_NEEDED`, or `BLOCKING`.
- Request repository, accession, DOI, license, access route, or restriction reason.
- Coordinate with `nature-data` if the user asks for full data-availability wording.

### Citation / positioning

Includes missing prior work, inaccurate novelty claim, wrong comparison, field context incomplete, reviewer-requested citation.

Default strategy:

- Use `ADD_CITATION`, `SOFTEN_CLAIM`, `CLARIFY_EXISTING`, or `DISAGREE`.
- Add citations only when genuinely relevant and verified.
- Do not fabricate DOI, publication year, title, journal, or authors.

### Scope / feasibility

Includes requested experiments beyond scope, future-work suggestions, journal-fit concerns, transfer-related concerns.

Default strategy:

- Use `PARTIAL`, `OUT_OF_SCOPE`, `SOFTEN_CLAIM`, or `DISAGREE`.
- Acknowledge scientific value.
- Give a study-design or scope reason, offer alternative evidence, and add a limitation.
- Avoid time, funding, or convenience as the primary reason.

### Ethics / compliance

Includes ethics approval missing, consent missing, animal/human-subject reporting, competing interests, image/data integrity, or permissions.

Default strategy:

- Usually `BLOCKING` or `AUTHOR_INPUT_NEEDED`.
- Request exact approval number, institution, consent statement, reporting checklist, image-processing details, or data-integrity explanation.
- Do not draft around missing required compliance.
