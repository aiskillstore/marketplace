---
name: learning-tutoring
description: Learning tutoring planning and content production skill for creating study plans, generating exercises, writing answer explanations, and providing review/adjustment guidance; triggered by requests like “study plan”, “exercise set/question bank”, “answer analysis”, “error analysis”, “exam prep plan”, or “spaced/periodic review schedule”.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Learning Tutoring Skills

## When to Use

- Use this skill when you need learning tutoring planning and content production skill for creating study plans, generating exercises, writing answer explanations, and providing review/adjustment guidance; triggered by requests like “study plan”, “exercise set/question bank”, “answer analysis”, “error analysis”, “exam prep plan”, or “spaced/periodic review schedule” in a reproducible workflow.
- Use this skill when a others task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/build_tutoring_pack.py` is the most direct path to complete the request.
- Use this skill when you need the `learning-tutoring` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Learning tutoring planning and content production skill for creating study plans, generating exercises, writing answer explanations, and providing review/adjustment guidance; triggered by requests like “study plan”, “exercise set/question bank”, “answer analysis”, “error analysis”, “exam prep plan”, or “spaced/periodic review schedule”.
- Packaged executable path(s): `scripts/build_tutoring_pack.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Others/learning-tutoring"
python -m py_compile scripts/build_tutoring_pack.py
python scripts/build_tutoring_pack.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/build_tutoring_pack.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/build_tutoring_pack.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

Use this skill when the user needs end-to-end learning support, especially in these scenarios:

1. **Study plan creation**: The user asks for a multi-week/phase plan with clear weekly tasks and milestones.
2. **Exercise/question bank generation**: The user requests practice questions by topic, difficulty, and question type.
3. **Answer explanations and solution walkthroughs**: The user wants step-by-step reasoning, not just final answers.
4. **Error analysis and remediation**: The user provides mistakes (or weak areas) and asks for diagnosis plus targeted practice.
5. **Exam preparation planning**: The user has an exam date/format and needs a structured prep + review schedule.

## 2. Key Features

- **Learner profiling**: Identify subject scope, current level, constraints (time), goals, and preferences.
- **Structured study plans**: Produce phase/week plans with explicit tasks, deliverables, and milestones.
- **Exercise generation**: Create questions across difficulty levels and key knowledge points.
- **High-quality explanations**: Provide correct logic, common pitfalls, and transfer tips (how to generalize).
- **Review and adjustment guidance**: Recommend periodic review, spaced repetition, and plan updates based on performance.
- **Batch/structured output support**: When needed, generate structured results (e.g., JSON) via scripts, then render to readable English.

## 3. Dependencies

- Python **3.10+**
- (Optional) Local script runner environment capable of executing:
  - `scripts/build_tutoring_pack.py`

## 4. Example Usage

### Example Request

> Create a 6-week study plan for high-school algebra (functions). I can study 6 hours/week. Goal: score 85+ on a school exam in 7 weeks. I prefer practice questions and concise notes.

### Example Output (Runnable Template)

#### Learner Profile
- **Subject/Scope**: High-school Algebra — Functions (domain/range, transformations, composition, inverse, graph interpretation)
- **Current Level**: Basic familiarity; inconsistent accuracy on word problems and graph questions
- **Time Budget**: 6 hours/week (4 sessions × 90 minutes)
- **Goal**: 85+ on exam in 7 weeks
- **Preferred Style**: Practice-heavy + concise notes

#### Goals
- Build reliable mastery of core function concepts and common exam patterns.
- Improve accuracy under time constraints via mixed sets and error-driven review.

#### 6-Week Plan (Weekly Focus → Tasks → Deliverables)

**Week 1 — Foundations & Graph Reading**
- Tasks:
  - Create a 1-page “Function Basics” sheet (definition, notation, domain/range).
  - Practice: evaluate functions, interpret graphs/tables.
- Deliverables:
  - 30 questions (easy→medium), error log with categories.

**Week 2 — Transformations**
- Tasks:
  - Notes: vertical/horizontal shifts, stretches/compressions, reflections.
  - Practice: match equations to graphs; graph from equation.
- Deliverables:
  - 35 questions + 5 “explain the transformation” short answers.

**Week 3 — Composition & Inverse**
- Tasks:
  - Notes: composition rules, inverse existence conditions, verifying inverses.
  - Practice: compute compositions; find inverses; domain restrictions.
- Deliverables:
  - 30 questions + 10 targeted inverse checks.

**Week 4 — Word Problems & Modeling**
- Tasks:
  - Translate contexts into functions; interpret parameters.
  - Mixed practice with graph + context.
- Deliverables:
  - 25 application problems + written explanations for 5.

**Week 5 — Mixed Sets + Timed Practice**
- Tasks:
  - 2 timed sets (exam-like), then deep review.
  - Build a “Top 10 Mistakes” list from the error log.
- Deliverables:
  - 2 timed sets + corrected solutions + mistake list.

**Week 6 — Final Consolidation & Spaced Review**
- Tasks:
  - Spaced review sessions: revisit weakest 3 topics.
  - 1 full mock + targeted drills.
- Deliverables:
  - Mock exam report (score, weak points, next actions).

#### Milestones
- End of Week 2: ≥80% accuracy on transformation questions.
- End of Week 4: Can solve modeling problems with a consistent setup method.
- End of Week 6: Mock exam score ≥85 with stable timing.

#### Exercises (Sample Set with Required Fields)

1) **Type**: choice  
   **Stem**: If \( f(x)=2x-3 \), what is \( f(5) \)?  
   **Answer**: 7  
   **Explanation**: Substitute \(x=5\): \(2(5)-3=10-3=7\).  
   **Difficulty**: easy  
   **Tags**: [evaluation, function-notation]

2) **Type**: short_answer  
   **Stem**: Describe the transformation from \( y=x^2 \) to \( y=(x-2)^2+3 \).  
   **Answer**: Shift right 2, up 3  
   **Explanation**: \(x-2\) shifts right; \(+3\) shifts up.  
   **Common Pitfall**: Confusing \(x-2\) with left shift.  
   **Transfer Tip**: For \(y=f(x-h)+k\), shift right by \(h\), up by \(k\).  
   **Difficulty**: medium  
   **Tags**: [transformations, quadratics]

3) **Type**: application  
   **Stem**: A taxi charges a base fee of \$4 plus \$1.5 per mile. Write a function for cost \(C(m)\) and find \(C(10)\).  
   **Answer**: \(C(m)=4+1.5m\), \(C(10)=19\)  
   **Explanation**: Base fee is the intercept; per-mile rate is the slope. \(4+1.5(10)=19\).  
   **Common Pitfall**: Swapping base fee and rate.  
   **Transfer Tip**: Linear models often follow “fixed + variable × quantity”.  
   **Difficulty**: medium  
   **Tags**: [modeling, linear-functions]

#### Review & Adjustment Suggestions
- Maintain an **error log** with categories (concept, algebra slip, misread graph, time pressure).
- Use **spaced review**: revisit weak topics after 1 day, 3 days, 7 days.
- If Week 3 accuracy on inverses <70%, reduce new content in Week 4 and add 2 extra inverse drill sessions.

## 5. Implementation Details

### Core Workflow (Execute as Needed)
1. **Clarify goals and learner profile**
2. **Produce a phased/weekly study plan**
3. **Generate exercises** aligned to weekly focus, key points, and difficulty distribution
4. **Write answer explanations** including:
   - Correct logic (step-by-step where needed)
   - Common pitfalls (typical mistakes)
   - Transfer tips (generalization patterns)
5. **Provide review and adjustment guidance** based on milestones and observed errors

### Required Clarifying Questions (Ask if Missing)
- **Subject and topic scope** (required)
- **Current level/foundation** (required)
- **Learning cycle and weekly time budget** (required)
- **Goal and exam format/date** (if applicable)
- **Preferred learning style** (notes, projects, practice-heavy, etc.)

### Output Specifications

**Study Plan Format**
- Use a clear hierarchy:
  - Learner Profile → Goals → Weekly/Phase Plan → Milestones → Review Suggestions
- Weekly tasks must be **specific and measurable** (avoid vague wording like “study more”).
- Write in **English**; keep technical terms in their original form when appropriate.

**Exercises & Explanations Format**
- Supported question types: `choice` / `short_answer` / `application`
- Each question includes:
  - stem, answer, explanation, difficulty, knowledge point tags
- Explanations should include:
  - correct logic, common pitfalls, transfer tips
- Quantity and difficulty should be adjusted to the plan, time budget, and goal.

### Structured Batch Generation (Preferred for Stable Output)
If consistent batch output is required, generate structured data first (e.g., JSON), then render to readable English:

1. Open and fill in `CONFIG` in `scripts/build_tutoring_pack.py`
2. Run:
   ```bash
   python scripts/build_tutoring_pack.py
   ```
3. Read `outputs/tutoring_pack.json` and convert it into a readable English deliverable.

### Reference Templates
For consistent layout and quality standards, see: `references/tutoring_templates.md`.
