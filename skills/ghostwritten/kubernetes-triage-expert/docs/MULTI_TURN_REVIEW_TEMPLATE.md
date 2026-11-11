# Multi-Turn Review Template

Use this template when evaluating a multi-turn troubleshooting conversation.

It is designed for:

- model comparison
- prompt version regression
- review of realistic triage conversations

This template should be used together with:

- [EVALUATION_RUBRIC.md](./EVALUATION_RUBRIC.md)

How they work together:

- `EVALUATION_RUBRIC.md` defines what each scoring dimension means
- this template records the scores turn by turn
- reviewers should assign each field in `Turn N Review` using the rubric definitions, not ad hoc judgment

Keep the conversation ordered by turn. Do not merge user input and assistant output into a single summary block.

```md
Case
- name:
- source:
- primary scenario:
- input language:

Candidates
- candidate_a:
- candidate_b:
- candidate_c:

Turn 1
User:
...

Candidate A:
...

Candidate B:
...

Candidate C:
...

Turn 1 Review
- boundary honesty:
- evidence discipline:
- fault classification:
- hypothesis quality:
- next-check quality:
- change awareness:
- boundary handoff:
- language/structure compliance:
- hard fail:
- notes:

Turn 2
User:
...

Candidate A:
...

Candidate B:
...

Candidate C:
...

Turn 2 Review
- boundary honesty:
- evidence discipline:
- fault classification:
- hypothesis quality:
- next-check quality:
- change awareness:
- boundary handoff:
- language/structure compliance:
- hard fail:
- notes:

Turn 3
User:
...

Candidate A:
...

Candidate B:
...

Candidate C:
...

Turn 3 Review
- boundary honesty:
- evidence discipline:
- fault classification:
- hypothesis quality:
- next-check quality:
- change awareness:
- boundary handoff:
- language/structure compliance:
- hard fail:
- notes:

Overall Review
- candidate_a_total:
- candidate_b_total:
- candidate_c_total:
- strongest candidate:
- weakest candidate:
- key difference:
- production recommendation:
```

## Reviewer Guidance

- Use [EVALUATION_RUBRIC.md](./EVALUATION_RUBRIC.md) when assigning scores for each field.
- Compare candidates on the same turn, not across different turns.
- Judge each answer only against the evidence available up to that turn.
- A candidate should be penalized if it confirms a conclusion before the supporting evidence appears in the conversation.
- If a later turn contains stronger evidence, check whether the candidate updates its ranking instead of repeating earlier guesses.
- When the issue moves beyond Kubernetes triage, check whether the candidate performs a clear handoff instead of continuing Kubernetes speculation.

## How To Use This With AI

This template is intended to be filled either by a human reviewer or by an AI reviewer working from the same evaluation standard.

### What To Provide

When asking an AI system to score a conversation, provide all of the following together:

- the original user input for each turn
- the candidate response for each turn
- [EVALUATION_RUBRIC.md](./EVALUATION_RUBRIC.md)
- this template, or a request to output in this structure

Do not provide only the candidate responses. Without the original turn-by-turn user evidence, the reviewer cannot judge whether a conclusion was premature, unsupported, or appropriately updated.

### Recommended Prompt Pattern

Use a request like this:

```md
Please evaluate the following multi-turn troubleshooting conversation.

Requirements:
1. Use the scoring definitions from EVALUATION_RUBRIC.md.
2. Score each candidate turn by turn.
3. Judge each turn only against the evidence available up to that turn.
4. Mark any hard fail clearly.
5. Output the result using the Multi-Turn Review Template structure.

Scoring rubric:
<paste rubric or its relevant sections>

Conversation:
<paste the turn-by-turn conversation with Candidate A / B / C outputs>
```

### Recommended Review Flow

1. Prepare one case at a time.
2. Keep each turn ordered and explicit.
3. Ask the AI reviewer to score each candidate using the rubric.
4. Review the AI-generated scores manually, especially for:
   - boundary honesty
   - evidence discipline
   - next-check quality
   - boundary handoff

### Common Failure Mode

The most common review mistake is asking an AI reviewer to compare two answers without also showing the original user evidence. That usually produces style comparison rather than true triage-quality evaluation.
