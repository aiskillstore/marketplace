# Human Reception Rubric

## Purpose

Estimate likely reading friction without claiming measured audience behavior. Keep this assessment blind to detector output and origin verdicts.

## Reader stances

Create exactly three views:

- `supporter`: broadly agrees with the author, brand, or central claim and tolerates some promotion or emotion.
- `neutral`: has no prior commitment and asks whether the post is clear, specific, relevant, and worth the time.
- `skeptic`: scrutinizes motive, evidence, authority, persuasion, commercial intent, and disclosure.

These are attitudes, not demographic profiles. Do not infer age, gender, race, nationality, health, politics, or other protected traits.

## Diagnostic dimensions

Use only dimensions supported by a quoted excerpt or explicit page signal:

- `specificity`: concrete events, examples, limits, or verifiable details versus interchangeable claims.
- `genericness`: template-like openings, empty summaries, repetitive parallel structure, or low information gain.
- `emotional_fit`: tone appropriate to the topic and the people affected.
- `reader_agency`: respect for disagreement versus lecturing, moral pressure, false urgency, or forced calls to action.
- `credibility_friction`: unsupported certainty, vague authority, missing sources, or implied experience without detail.
- `platform_fit`: tone and structure aligned with the visible platform and discussion context.
- `commercial_pressure`: hidden promotion, manufactured intimacy, scarcity, fear, or disguised lead generation.
- `disclosure_expectation`: whether AI assistance matters in this context and whether disclosure is visible.
- `media_text_fit`: consistency between images, captions, claims, and emotional tone.
- `empathy`: recognition of affected people instead of opportunistic brand positioning.

Do not use “looks AI,” “has no soul,” or similar labels as analysis.

## Required output

For each stance provide:

- A short `likely_reaction`.
- `aversion_risk` as `low`, `medium`, `high`, or `unknown`.
- Zero or more `friction_points`.
- Zero or more grounded `positive_signals`.
- A specific `uncertainty` statement.

Each friction point requires:

- `dimension`
- `excerpt` copied from the case text, alt text, image ID, or observation
- `reason` explaining why that stance may experience friction

Keep excerpts short. Do not reproduce a full post.

Each positive signal and cross-reader pattern must be an object with `statement`, an explanatory `reason`, and either a short case-grounded `excerpt` or structured `evidence` locator. Cross-reader patterns also name two or three unique `personas`; this prevents a one-stance observation from being labeled consensus. Bare strings and unknown fields are rejected. The validator checks traceability, not semantic truth: the blind reviewer must still verify that the reason genuinely follows from the cited material. It records `validation_profile: grounded_reception_v1` and an evidence index in the normalized report.

## Blind procedure

1. Read the case content and public context.
2. Record audience and platform assumptions.
3. Produce the three stance views.
4. Identify patterns shared by two or more stances.
5. Record interpretation uncertainty.
6. Save `reception.json`.
7. Only then run origin detectors.

## Prohibitions

Do not:

- Diagnose the author’s personality, morality, effort, or mental state.
- Treat irritation as AI evidence.
- Produce numeric human-likeness or aversion probabilities.
- Generate a complete replacement post.
- Recommend edits, additions, deletions, tone changes, or conversion tactics; describe the observed friction instead.
- Provide detector-evasion or “make it pass as human” instructions.
- Claim that an inferred reaction was observed in real users.

## Interpreting risk

- Low: few supported friction points and clear positive signals.
- Medium: one meaningful friction point or material stance disagreement.
- High: several supported friction points likely to undermine trust or respect for that stance.
- Unknown: missing context, irony, dialect, cultural references, inaccessible media, or unclear intent.

Use real reader testing for consequential publishing decisions.
