# Difficult cases

Use this file when comments cannot be handled with straightforward acceptance and revision.

## Impossible or out-of-scope experiment

Use when the requested work requires a new cohort, long follow-up, new animal model, new clinical
trial, new platform, or different study design.

Strategy:

1. Acknowledge scientific value.
2. Explain the study-design or scope boundary.
3. Offer alternative evidence if supplied.
4. Soften the claim or add a limitation.
5. Avoid time, budget, convenience, or ability excuses.

Template:

```text
We agree that [experiment] would provide an additional test of [claim]. However, the central
conclusion of the present study is based on [existing evidence], and the requested experiment
would require [new system/cohort/longitudinal design] beyond the scope of this revision.
To avoid overstatement, we have revised [location] to acknowledge this limitation and now state
that [revised text or placeholder].
```

## Reviewer factual error

Use when the reviewer appears to have missed existing data or made a factually incorrect statement.

Strategy:

1. Do not accuse the reviewer.
2. Cite the existing manuscript location or supplied evidence.
3. Clarify wording if the manuscript invited confusion.
4. Consider a small revision even when the reviewer is wrong.

Template:

```text
We appreciate the reviewer raising this point. The relevant data are provided in [location],
where we show [supplied evidence]. We have revised [location] to make this clearer.
```

## Conflicting reviewer requests

Use when two reviewers ask for incompatible changes.

Strategy:

1. Surface the conflict internally in the strategy summary.
2. Prioritize explicit editor instructions if supplied.
3. Find the minimal revision that satisfies both concerns.
4. Avoid making incompatible promises.
5. If necessary, explain the balancing choice in the relevant responses.

## Reviewer-requested citation

Use when a reviewer asks for a specific citation or broader literature coverage.

Strategy:

1. Evaluate relevance.
2. Add only genuinely relevant and verified citations.
3. Do not imply coercion or reviewer self-citation.
4. Use neutral positioning language.
5. If citation metadata is missing, use `AUTHOR_INPUT_NEEDED`.

## Major statistical critique

Treat as high risk or blocking until details are supplied.

Request:

- statistical test name
- replicate unit
- sample size or replicate count
- effect size or estimate when relevant
- confidence interval when relevant
- p-value only when supplied and appropriate
- multiple-testing correction
- software and version if relevant
- Methods and Results locations

Do not invent statistical output.

## Ethics, compliance, or data-integrity critique

Usually `BLOCKING` until author provides exact facts.

Request:

- ethics approval body and approval number
- consent statement
- animal or human-subject reporting details
- competing-interest correction
- image-processing or data-integrity explanation
- data, code, materials, or accession information

Do not write around missing required compliance.

## Transfer after review

Use when a manuscript is transferred with reviewer reports.

Strategy:

1. Identify whether the receiving journal expects a response to transferred reports.
2. Preserve reviewer IDs from the transferred review package when possible.
3. Address comments as normal revision concerns unless the new editor gives different instructions.
4. Flag journal-specific formatting or scope differences.

## Appeal-like case

Appeals are not ordinary revision responses.

Route separately when:

- the user wants to challenge rejection rather than revise;
- the decision letter invites an appeal path;
- the author alleges major factual error, bias, or process failure;
- no revised manuscript is being prepared.

Default action:

```text
This appears to be an appeal-like case rather than a revision response. `nature-response`
can identify the disputed points, but a full appeal letter should be handled as a separate task
with journal-specific appeal rules.
```
