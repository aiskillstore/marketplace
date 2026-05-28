---
name: meeting-assistant
description: Extracts key meeting information in chronological order and outputs decisions and action items; use when you need meeting minutes, action tracking, or project sync notes from transcripts or raw notes.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Meeting Assistant

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Extracts key meeting information in chronological order and outputs decisions and action items; use when you need meeting minutes, action tracking, or project sync notes from transcripts or raw notes.
- Documentation-first workflow with no packaged script requirement.
- Reference material available in `references/` for task-specific guidance.
- Reusable packaged asset(s), including `assets/meeting_minutes_template.md`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```text
Skill directory: 20260316/scientific-skills/Others/meeting-assistant
No packaged executable script was detected.
Use the documented workflow in SKILL.md together with the references/assets in this folder.
```

Example run plan:
1. Read the skill instructions and collect the required inputs.
2. Follow the documented workflow exactly.
3. Use packaged references/assets from this folder when the task needs templates or rules.
4. Return a structured result tied to the requested deliverable.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: instruction-only workflow in `SKILL.md`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Packaged assets: reusable files are available under `assets/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use
Use this skill in the following scenarios (3-5 typical cases):

1. **Meeting minutes generation** from raw notes or audio transcripts, especially when you need a clear timeline of what was discussed.
2. **Action item tracking** after recurring meetings (weekly syncs, standups, steering committees) where owners and deadlines must be captured.
3. **Project synchronization** across teams to consolidate decisions, disagreements, and follow-ups into a single structured output.
4. **Decision logging** for governance/compliance needs where decisions must be separated from items still pending confirmation.
5. **Post-meeting follow-up preparation** to produce a concise list of next steps and unresolved questions.

## 2. Key Features
- **Chronological summarization** of discussion points (timeline-first structure).
- **Decision extraction** with explicit separation of:
  - confirmed decisions
  - items pending confirmation
- **Disagreement/issue marking** to highlight unresolved conflicts or divergent viewpoints.
- **Action item extraction** including **task**, **owner**, **deadline**, and optional **status**.
- **Structured outputs** suitable for minutes, decision lists, and action tables.
- **Sensitive data masking** for common identifiers (e.g., phone numbers, emails) in the generated output.
- **No external access**: operates only on text provided in the conversation.

## 3. Dependencies
This is an instruction-based skill and requires no external packages.

| Dependency | Version | Notes |
|---|---:|---|
| None | N/A | No scripts, no network calls, no file I/O |

## 4. Example Usage
Below is a complete, runnable example (copy/paste the input; the expected output format is shown).

### Input (example transcript)
```text
Meeting: Project Progress Sync
Date: 2025-01-15
Participants: Zhang San (PM), Li Si (Finance), Wang Wu (QA)
Recorder: Li Si

[10:00] Zhang San: Q1 goals are on track. Main risk is test environment readiness.
[10:05] Wang Wu: QA environment is not stable; we need infra support by next week.
[10:10] Li Si: Budget increase request is ready, but needs approval today.
[10:15] Zhang San: Decision needed: approve budget increase and postpone non-core features.
[10:18] Wang Wu: I disagree on postponing feature X; it impacts customer demo.
[10:22] Zhang San: Noted. We'll postpone non-core features except feature X pending confirmation.
[10:25] Li Si: Action items: Zhang drafts technical solution; I submit budget report; Wang arranges test environment.
```

### Output (expected minutes)
```markdown

# Meeting Minutes

## Basic Information
- Meeting Subject: Project Progress Sync
- Time: 2025-01-15
- Participants: Zhang San, Li Si, Wang Wu
- Recorder: Li Si

## Timeline Summary (Chronological)
1. [10:00] Q1 goals reported as on track; test environment readiness identified as a key risk.
2. [10:05] QA environment instability raised; infra support requested by next week.
3. [10:10] Budget increase request prepared and requires same-day approval.
4. [10:15] Proposal raised: approve budget increase; postpone non-core features.
5. [10:18] Disagreement: postponing feature X may impact customer demo.
6. [10:22] Interim conclusion: postpone non-core features **except feature X** (feature X decision pending confirmation).
7. [10:25] Action items assigned to owners.

## Decision List (Confirmed)
1. Approved the budget increase request.

## Items Pending Confirmation
1. Whether to postpone feature X (impact on customer demo needs validation).

## Disagreements / Open Issues
- Postponing feature X: PM proposes postponement; QA objects due to demo impact.

## Action Items
| Task | Owner | Deadline | Status |
|------|------|----------|--------|
| Complete technical solution document | Zhang San | 2025-01-20 | In Progress |
| Submit budget report | Li Si | 2025-01-22 | To Start |
| Arrange test environment | Wang Wu | 2025-01-25 | To Start |
```

## 5. Implementation Details

### Processing Workflow
1. **Material normalization**
   - Prefer inputs containing **timestamps** and **speaker labels**.
   - If missing, infer ordering from paragraphs and explicit time cues.
2. **Timeline parsing**
   - Sort entries by timestamp (or inferred order).
   - Produce a concise chronological summary, preserving key context.
3. **Information extraction**
   - **Decisions**: statements indicating approval/confirmation/commitment.
   - **Pending items**: proposals, unresolved questions, or "to be confirmed" items.
   - **Disagreements**: explicit objections, conflicting viewpoints, or unresolved trade-offs.
   - **Action items**: tasks with **owner** and **deadline**; if deadline is missing, mark as `TBD`.
4. **Output structuring**
   - Generate sections: Basic Info → Timeline Summary → Decisions → Pending → Disagreements → Action Items table.

### Output Rules / Parameters
- **Chronology-first**: timeline summary must follow meeting order.
- **Separation of states**: confirmed decisions must not be mixed with pending items.
- **Action item completeness**:
  - Must include **Owner**; if unknown, use `Unassigned`.
  - Must include **Deadline**; if unknown, use `TBD`.
- **Data access constraints**
  - No local file system reads/writes.
  - No URL/API access.
  - Operates only on text provided in the conversation.
- **Sensitive information masking**
  - Mask common sensitive identifiers (e.g., emails/phone numbers) in outputs when present.

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `meeting_assistant_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: meeting_assistant_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
