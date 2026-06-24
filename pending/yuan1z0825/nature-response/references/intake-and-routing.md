# Intake and routing

Use this file before splitting comments or drafting prose. Its job is to decide what task the
user is asking for, whether the supplied information is enough, and what output state is honest.

## Task modes

| Mode | Use when | Minimum useful input | Default output |
|---|---|---|---|
| `draft` | User wants a new point-by-point response package | Reviewer comments plus any author actions or manuscript-change notes | Full response package with placeholders where needed |
| `audit` | User provides an existing response draft and asks whether it is good enough | Response draft; reviewer comments when available | Findings first, then revised or annotated response sections |
| `revise` | User wants a draft rewritten for tone, traceability, or Nature-style response | Existing draft plus target change request | Revised response text plus changed-risk notes |
| `triage-only` | User wants strategy, action list, or missing inputs before writing prose | Reviewer comments or editor letter | Tracker, action map, missing-input list, no final letter |
| `appeal-like` | User wants to challenge rejection or process rather than revise | Decision letter and disputed points | Route out of default workflow and explain separate appeal handling |

If the mode is unclear, infer the safest useful mode. Prefer `triage-only` when drafting would
require many unsupported facts.

## Readiness states

Use one readiness state for each comment and one package-level state:

| State | Meaning | Allowed output |
|---|---|---|
| `ready_to_submit` | Direct answer, supplied action, and traceable manuscript location are all present | Final response wording without unresolved placeholders |
| `draft_with_placeholders` | A useful draft can be written, but visible placeholders remain | Draft wording with bracketed placeholders and risk flags |
| `needs_author_input` | Final text would require facts the user has not supplied | Tracker, questions, partial draft only if placeholders are explicit |
| `blocked` | Ethics, compliance, data integrity, missing central evidence, or appeal-like routing prevents credible revision response | Blocking issue first; do not produce confident final wording |

Do not call a package `ready_to_submit` if any comment remains `draft_with_placeholders`,
`needs_author_input`, or `blocked`.

## Editor instruction handling

When editor instructions are supplied:

- Assign editor-level IDs before reviewer IDs: `E.1`, `E.2`, `E.3`.
- Address editor instructions before Reviewer 1, Reviewer 2, etc.
- If editor instructions conflict with reviewer suggestions, surface the conflict in the strategy summary.
- Treat explicit editor constraints as higher priority than reviewer-level preference.

Example:

```text
E.1: Focus on clarifying the central claim without substantial manuscript expansion.
R1.1: Make the causal claim stronger.
R2.1: Soften unsupported causal language.
```

The response strategy should explain that the editor's constraint and the observational design
support claim softening rather than stronger causal language.

## Minimum information by output type

### Full draft response

Requires:

- reviewer comments or editor comments;
- enough author notes to know which actions were taken;
- manuscript locations or placeholders for claimed changes.

If locations are missing, use section names or bracketed placeholders. Do not invent line numbers.

### Final submission-ready response

Requires:

- all reviewer and editor comments identified;
- all claimed actions supplied by the author;
- traceable locations for every manuscript change;
- real details for experiments, analyses, statistics, citations, figures, tables, supplements, ethics, and data availability.

If any required fact is missing, the output is not `ready_to_submit`.

### Audit

Requires:

- user draft;
- reviewer comments when available.

If reviewer comments are absent, audit only the visible draft and flag that completeness cannot be verified.

## Clarifying question rules

Usually proceed with placeholders and risk flags. Ask concise questions only when:

- the user explicitly asks for final submission-ready text and required facts are missing;
- the draft would otherwise fabricate data, locations, approvals, statistics, citations, or figure panels;
- reviewer boundaries are too ambiguous to assign stable IDs;
- the case appears appeal-like or outside normal revision response.

When asking, keep questions specific:

```text
I need three facts before final wording: the validation result summary, the Methods/Results location,
and whether Fig. 5 is a main or supplementary figure.
```

## Routing shortcuts

- Vague author note such as "we fixed it" -> `needs_author_input`.
- Existing response with hostile language -> `audit` or `revise`.
- Reviewer asks for impossible new work -> normal revision mode with `PARTIAL` or `OUT_OF_SCOPE`, not appeal.
- Rejection challenge -> `appeal-like`.
- User asks only "what should we do?" -> `triage-only`.
