# Model-Native Optimization Notes (Gemini tuned)

These patterns were tuned on Gemini models. They generalize to other
instruction-following coding models, but re-validate on each model you run:
prompt-structure preferences and context-window behavior differ across
model families.

---

## 1. Adaptive Reasoning

Match reasoning depth to expected error cost and uncertainty. Do not set fixed
token floors or prompt for narrated chain-of-thought.

| Signal | Response |
|---|---|
| Low risk, clear, reversible | Brief reasoning and targeted checks |
| Multiple dependencies or ambiguity | Compare failure modes before editing |
| Security, migration, or destructive action | Deep review and explicit checkpoint |
| Prior failed approach | Diagnose before choosing a different strategy |

See `../references/reasoning.md` for the adaptive formula.

---

## 2. Outcome-First Prompting

Gemini rewards direct instructions. Lead with the goal, not the persona.

```
BAD:  "You are an expert TypeScript engineer with 15 years of experience.
       Please carefully review the following code for potential issues..."

GOOD: "Review this TypeScript file for bugs and security issues.
       Return: list of issues with file:line, severity (HIGH/MED/LOW), and fix."
```

**Pattern:** Goal → constraints → output format. Skip the setup.

---

## 3. Few-Shot Examples — Gemini's Strongest Lever

When defining output format, show one concrete example. Gemini calibrates to
examples far more reliably than abstract descriptions.

```markdown
Review the code below. Output format:

## Issues Found

| File | Line | Severity | Issue | Fix |
|------|------|----------|-------|-----|
| src/auth.ts | 42 | HIGH | SQL injection | Use parameterized query |
| src/utils.ts | 17 | LOW | Unused import | Remove import |

[your code here]
```

**Rule:** One example beats 10 paragraphs of description.

---

## 4. Markdown Structure Over XML

Gemini responds better to Markdown headings than XML tags in prompts.

```markdown
## Goal
Review for security vulnerabilities

## Context
Express.js API, TypeScript, connects to PostgreSQL

## Constraints
- Don't suggest framework changes
- Focus on injection and auth issues only

## Output Format
[example as above]
```

**Note:** GRAVITAS uses markdown-first structure throughout. XML-style prompts
are less effective on Gemini than markdown headings.

---

## 5. Context Window — Large, But Use Wisely

Current Pro-class models offer very large context windows (order of 1M
tokens; verify the exact limit for the model revision you run). Key
principles:

**Use large context for:**
- Full codebase review
- Multi-file refactoring with full context
- Long document analysis
- Cross-file dependency tracing

**Don't use large context for:**
- Single-function fixes (waste of tokens)
- Tasks where progressive disclosure is better
- Cases where you should summarize, not dump

**Attention degradation:** Quality degrades in the middle of very long contexts.
Structure important content at the start and end, not buried in the middle.

```
[Task description] ← HIGH ATTENTION
[Important constraints] ← HIGH ATTENTION
[Large code dumps] ← MEDIUM ATTENTION (middle)
[Output format + examples] ← HIGH ATTENTION (end)
```

---

## 6. Grounding with Google Search

When Gemini has search access, use it for:
- API documentation (current versions, not training data)
- Dependency compatibility (actual current versions)
- Security vulnerability databases
- Anything where recency matters

**Don't use search for:**
- Things in the codebase (use file tools)
- Things you can read from config files
- General programming patterns (training data is sufficient)

---

## 7. Parallel Tool Calls

Gemini can execute independent tool calls in parallel in one response.
This is the single biggest performance multiplier in GRAVITAS.

```python
# GOOD — parallel, one response
[read auth.ts] + [read auth.test.ts] + [grep SESSION_TIMEOUT src/]

# BAD — sequential, three round-trips
[read auth.ts]
→ wait →
[read auth.test.ts]  
→ wait →
[grep SESSION_TIMEOUT src/]
```

**Rule:** Any tool calls that don't depend on each other's output → batch them.

---

## 8. Temperature Settings

| Task | Temperature | Notes |
|------|------------|-------|
| Code generation | 0.0–0.2 | Deterministic, no creativity |
| Bug analysis | 0.2–0.3 | Slight variation helps find alternatives |
| Code review | 0.3–0.5 | Some creativity in finding issues |
| Architecture | 0.5–0.7 | Exploration of options |
| Documentation | 0.3–0.5 | Readable but accurate |

---

## 9. Gemini-Specific Prompt Patterns

### The GRAVITAS Invocation Pattern

When starting a complex task:

```
[task in one sentence]

Context:
- Language: TypeScript (strict)
- Test runner: Vitest
- Relevant files: [list]

Constraints:
- Read before writing
- Verify with actual test output
- Stay within scope: [what's in scope]

Output:
## What Changed
## Evidence (verbatim command output)
## Why
VERDICT: PASS/FAIL
```

### The Recon Pattern

```
Map this codebase section:
- Entry point: [file]
- Find all files that [X]
- Return: dependency graph, key line numbers, risks

Don't edit anything.
```

### The Adversarial Review Pattern

```
Review this implementation plan. Find every way it could fail.

Plan: [plan]

Output:
- Failure modes with probability (HIGH/MED/LOW)
- Missing edge cases
- Downstream risks
- Alternative approaches I should consider

Don't be nice. Find real problems.
```

---

## 10. Integration with GRAVITAS Tiers

| Tier | Reasoning | Tools |
|------|-----------|-------|
| 0 | Brief | Direct action |
| 1 | Proportional to uncertainty | Recon + implement + targeted verify |
| 2 | Deep | Critique + checkpoint + full verify |

---

## 11. Portability Notes (tuned on Gemini, re-validate elsewhere)

| Behavior | Tuned observation (Gemini) | When porting |
|---------|---------------------------|--------------|
| Prompt structure | Markdown headings preferred | Re-test on the target model |
| Few-shot power | Very high | Very high on most models |
| Context use | Large window, mid-degradation | Measure for the target model |
| Tool parallelism | Native, fast | Depends on host support |
| Reasoning | Thinking budget via API | Map to target API's effort control |
| Output verbosity | Needs constraints to be brief | Re-tune brevity constraints |

**Implication:** When porting these patterns to another model, re-validate
prompt structure and output-length constraints first; they vary the most.

---

## 12. Anti-patterns for Gemini

**Don't:**
- Use XML tags as primary structure (works but suboptimal)
- Ask for "step-by-step" reasoning (it reasons internally — just give space)
- Dump the whole codebase then ask a simple question (mid-context degradation)
- Use very high temperature for code (hallucination risk)
- Pad prompts with persona setup ("You are an expert...")

**Do:**
- Structure with Markdown
- Show one example of desired output format
- Put the task first, context second
- Batch parallel tool calls
- Use thinking budget for complex tasks
