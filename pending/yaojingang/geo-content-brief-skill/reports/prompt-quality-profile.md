# Prompt Quality Profile

Skill: `geo-content-brief-skill`
Relevance: `prompt-heavy`
Overall quality score: `85.0/100`

## Primary Task Family

**Creative generation**
- Matched keywords: copy, content, 内容

## Complexity

- Band: `complex`
- Score: `6`
- Reason: multiple inputs, constraints, or task families require tradeoff handling

## Need Model

- Explicit Need: 将 GEO 内容访谈、关键词笔记和渠道约束整理成可执行的中文内容简报 Skill，适用于团队复用、触发边界审查和后续质量评估。
- Implicit Need: The reusable skill needs a stable role, task, and output contract rather than a one-off prompt.
- Scenario: not yet explicit
- User Level: infer from examples and standards; ask only if it changes output depth
- Success Standard: usable output with clear validation cues

## RTF To Skill Mapping

- Role: Use a taste-aware creator role with clear audience, tone, and originality boundaries.
- Task: Generate variants, explain selection logic, and preserve the user's distinctive constraints.
- Format: Return options with rationale, selection criteria, and refinement paths.

## Quality Matrix

### Completeness — 80/100
- Matched signals: input, output, constraint, example, 约束
- Repair: Name missing inputs, outputs, constraints, or success standards before deepening the package.

### Clarity — 90/100
- Matched signals: clear, specific
- Repair: Replace broad verbs with observable actions and define what done means.

### Consistency — 90/100
- Matched signals: boundary, 边界
- Repair: Check that role, task, format, exclusions, and examples do not contradict each other.

### Practicality — 95/100
- Matched signals: execute, use, workflow, 执行
- Repair: Add runnable steps, examples, or verification cues instead of abstract advice.

### Specificity — 70/100
- Matched signals: none
- Repair: Anchor wording in the user's audience, domain nouns, and target outcome.

## Matched Task Families

### Creative generation
- Score: `3`
- Keywords: copy, content, 内容
- Role: Use a taste-aware creator role with clear audience, tone, and originality boundaries.
- Task: Generate variants, explain selection logic, and preserve the user's distinctive constraints.
- Format: Return options with rationale, selection criteria, and refinement paths.

### Execution operation
- Score: `3`
- Keywords: workflow, execute, 执行
- Role: Use an operator role with explicit boundaries, inputs, outputs, and failure handling.
- Task: Convert the job into ordered steps with validation checks and stop conditions.
- Format: Return a runbook-like handoff with commands, checks, owners, and next actions when relevant.

### Prompt engineering
- Score: `3`
- Keywords: prompt, role, format
- Role: Use a prompt engineer role only when role design materially improves execution.
- Task: Map Role, Task, and Format into skill behavior rather than copying a large prompt template.
- Format: Return a compact prompt contract plus tests, quality matrix, and usage notes.

### Dialogue interaction
- Score: `2`
- Keywords: dialogue, 访谈
- Role: Use a conversational role that asks only high-leverage questions and remembers the user's goal.
- Task: Clarify intent, resolve uncertainty, and converge toward a recommendation instead of a long option list.
- Format: Return concise prompts, decision points, and reviewer-visible assumptions.

## Self-Repair Checks

- Check explicit need, implicit need, scenario, user level, and success standard before deepening.
- Map Role, Task, and Format into skill behavior, not decorative prompt labels.
- Ask one focused clarification only when missing information changes the package boundary.
- Add tests or examples for prompt-heavy behavior before treating it as reusable.
- Keep prompt methodology in references and reports instead of bloating SKILL.md.

## Reviewer Note

Use this profile when the package depends on prompt behavior, role design, output contracts, or conversation quality.
