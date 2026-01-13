---
name: meta-cognitive-reasoning
description: Meta-cognitive reasoning specialist for evidence-based analysis, hypothesis
  testing, and cognitive failure prevention. Use when conducting reviews, making assessments,
  debugging complex issues, or any task requiring rigorous analytical reasoning. Prevents
  premature conclusions, assumption-based errors, and pattern matching without verification.
tags:
- reasoning
- analysis
- review
- debugging
- assessment
- decision-making
- cognitive failure prevention
- meta-cognitive reasoning
- evidence-based reasoning
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Meta-Cognitive Reasoning

This skill provides disciplined reasoning frameworks for avoiding cognitive failures in analysis, reviews, and decision-making. It enforces evidence-based conclusions, multiple hypothesis generation, and systematic verification.

## When to Use This Skill

- Before making claims about code, systems, or versions
- When conducting code reviews or architectural assessments
- When debugging issues with multiple possible causes
- When encountering unfamiliar patterns or versions
- When making recommendations that could have significant impact
- When pattern matching triggers immediate conclusions
- When analyzing documentation or specifications
- During any task requiring rigorous analytical reasoning

## What This Skill Does

1. **Evidence-Based Reasoning**: Enforces showing evidence before interpretation
2. **Multiple Hypothesis Generation**: Prevents premature commitment to single explanation
3. **Temporal Knowledge Verification**: Handles knowledge cutoff limitations
4. **Cognitive Failure Prevention**: Recognizes and prevents common reasoning errors
5. **Self-Correction Protocol**: Provides framework for transparent error correction
6. **Scope Discipline**: Allocates cognitive effort appropriately

## Core Principles

### 1. Evidence-Based Reasoning Protocol

**Universal Rule: Never conclude without proof**

```
MANDATORY SEQUENCE:
1. Show tool output FIRST
2. Quote specific evidence
3. THEN interpret
```

**Forbidden Phrases:**

- "I assume"
- "typically means"
- "appears to"
- "Tests pass" (without output)
- "Meets standards" (without evidence)

**Required Phrases:**

- "Command shows: 'actual output' - interpretation"
- "Line N: 'code snippet' - meaning"
- "Let me verify..." -> tool output -> interpretation

### 2. Multiple Working Hypotheses

**When identical observations can arise from different mechanisms with opposite implications - investigate before concluding.**

**Three-Layer Reasoning Model:**

```
Layer 1: OBSERVATION (What do I see?)
Layer 2: MECHANISM (How/why does this exist?)
Layer 3: ASSESSMENT (Is this good/bad/critical?)

FAILURE: Jump from Layer 1 -> Layer 3 (skip mechanism)
CORRECT: Layer 1 -> Layer 2 (investigate) -> Layer 3 (assess with context)
```

**Decision Framework:**

1. **Recognize multiple hypotheses exist**
   - What mechanisms could produce this observation?
   - Which mechanisms have opposite implications?

2. **Generate competing hypotheses explicitly**
   - Hypothesis A: [mechanism] -> [implication]
   - Hypothesis B: [different mechanism] -> [opposite implication]

3. **Identify discriminating evidence**
   - What single observation would prove/disprove each?

4. **Gather discriminating evidence**
   - Run the specific test that distinguishes hypotheses

5. **Assess with mechanism context**
   - Same observation + different mechanism = different assessment

### 3. Temporal Knowledge Currency

**Training data has a timestamp; absence of knowledge ≠ evidence of absence**

**Critical Context Check:**

```
Before making claims about what exists:
1. What is my knowledge cutoff date?
2. What is today's date?
3. How much time has elapsed?
4. Could versions/features beyond my training exist?
```

**High Risk Domains (always verify):**

- Package versions (npm, pip, maven)
- Framework versions (React, Vue, Django)
- Language versions (Python, Node, Go)
- Cloud service features (AWS, GCP, Azure)
- API versions and tool versions

**Anti-Patterns:**

- "Version X doesn't exist" (without verification)
- "Latest is Y" (based on stale training data)
- "CRITICAL/BLOCKER" without evidence

### 4. Self-Correction Protocol

**When discovering errors in previous output:**

```
STEP 1: ACKNOWLEDGE EXPLICITLY
- Lead with "CRITICAL CORRECTION"
- Make it impossible to miss

STEP 2: STATE PREVIOUS CLAIM
- Quote exact wrong statement

STEP 3: PROVIDE EVIDENCE
- Show what proves the correction

STEP 4: EXPLAIN ERROR CAUSE
- Root cause: temporal gap? assumption?

STEP 5: CLEAR ACTION
- "NO CHANGE NEEDED" or "Revert suggestion"
```

### 5. Cognitive Resource Allocation

**Parsimony Principle:**

- Choose simplest approach that satisfies requirements
- Simple verification first, complexity only when simple fails

**Scope Discipline:**

- Allocate resources to actual requirements, not hypothetical ones
- "Was this explicitly requested?"

**Information Economy:**

- Reuse established facts
- Re-verify when context changes

**Atomicity Principle:**

- Each action should have one clear purpose
- If description requires "and" between distinct purposes, split it
- Benefits: clearer failure diagnosis, easier progress tracking, better evidence attribution

### 6. Systematic Completion Discipline

**Never declare success until ALL requirements verified**

**High-Risk Scenarios for Premature Completion:**

- Multi-step tasks with many quality gates
- After successfully fixing major issues (cognitive reward triggers)
- When tools show many errors (avoidance temptation)
- Near end of session (completion pressure)

**Completion Protocol:**

1. Break requirements into explicit checkpoints
2. Complete each gate fully before proceeding
3. Show evidence at each checkpoint
4. Resist "good enough" shortcuts

**Warning Signs:**

- Thinking "good enough" instead of checking all requirements
- Applying blanket solutions without individual analysis
- Skipping systematic verification
- Declaring success while evidence shows otherwise

### 7. Individual Analysis Over Batch Processing

**Core Principle: Every item deserves individual attention**

**Apply to:**

- Error messages (read each one individually)
- Review items (analyze each line/file)
- Decisions (don't apply blanket rules)
- Suppressions (justify each one specifically)

**Anti-Patterns:**

- Bulk categorization without reading details
- Blanket solutions applied without context
- Batch processing of unique situations

### 8. Semantic vs Literal Analysis

**Look for conceptual overlap, not just text/pattern duplication**

**Key Questions:**

- What is the actual PURPOSE here?
- Does this serve a functional need or just match a pattern?
- What would be LOST if I removed/changed this?
- Is this the same CONCEPT expressed differently?

**Applications:**

- Documentation: Identify semantic duplication across hierarchy levels
- Code review: Understand intent before suggesting changes
- Optimization: Analyze actual necessity before improving

## How to Use

### Verify Before Claiming

```
Verify that package X version Y exists before recommending changes
```

```
Check if this file structure is symlinks or duplicates before recommending consolidation
```

### Generate Multiple Hypotheses

```
The tests are failing with timeout errors. What are the possible mechanisms?
```

```
These three files have identical content. What could explain this?
```

### Conduct Evidence-Based Review

```
Review this code and show evidence for every claim
```

## Reasoning Workflows

### Verification Workflow

When encountering unfamiliar versions/features:

1. **Recognize uncertainty**: "I don't recall X from training"
2. **Form hypotheses**: A) doesn't exist, B) exists but new, C) is current
3. **Verify before concluding**: Check authoritative source
4. **Show evidence, then interpret**: Command output -> conclusion

### Assessment Workflow

When analyzing code, architecture, or configurations:

1. **Observe**: What do I see?
2. **Investigate mechanism**: HOW does this exist?
3. **Then assess**: Based on mechanism, is this good/bad?

### Review Workflow

For code reviews, documentation reviews, or any analysis:

1. **Clarify scope**: Ask before assuming
2. **Show evidence for every claim**: File:line:code
3. **Generate hypotheses before concluding**
4. **Distinguish mechanism from observation**
5. **Reserve strong language for verified issues**

## Cognitive Failure Patterns

### Pattern 1: Scanning Instead of Reading

- Missing obvious issues while finding minor ones
- Prevention: Read every line/error individually

### Pattern 2: Pattern Matching Without Context

- Applying solutions without understanding problems
- Prevention: Analyze actual purpose before applying templates

### Pattern 3: Assumption-Based Conclusions

- Guessing instead of verifying
- Prevention: Evidence-based verification required

### Pattern 4: Premature Success Declaration

- "Task complete" ≠ "Requirements verified"
- Prevention: Show tool output proving completion

### Pattern 5: Temporal Knowledge Decay

- Confusing "I don't know" with "doesn't exist"
- Prevention: Verify version/feature currency

### Pattern 6: Overconfidence Cascade

```
False premise: "X doesn't exist" (unverified)
    ↓
Amplified: "This is CRITICAL/BLOCKER"
    ↓
Harmful: "Change X to older version Y"
    ↓
Impact: Downgrade from newer to older

BREAK THE CASCADE: Verify the premise first
```

## Examples

### Example 1: Version Verification

**Situation**: Reviewing code that uses `certifi==2025.10.5`

**Wrong Approach:**

```markdown
CRITICAL: Version 2025.10.5 doesn't exist!
Action: Change to 2024.x.x
```

**Correct Approach:**

```markdown
Let me verify this version exists...

$ grep -A 3 'name = "certifi"' uv.lock
name = "certifi"
version = "2025.10.5"
source = { registry = "https://pypi.org/simple" }

Evidence shows version EXISTS on PyPI.
Action: NO CHANGE NEEDED - version is valid.
```

### Example 2: File Structure Analysis

**Observation**: Three files with identical 1494-line content

- specs/AGENTS.md
- specs/CLAUDE.md
- specs/GEMINI.md

**Wrong Approach:**

```markdown
CRITICAL: File duplication - consolidate to single file
```

**Correct Approach:**

```markdown
Competing hypotheses:
A: Duplicated copies -> CRITICAL: Consolidate
B: Symlinks to single source -> EXCELLENT: Keep

Gathering discriminating evidence:
$ ls -la specs/
lrwxrwxrwx CLAUDE.md -> AGENTS.md
lrwxrwxrwx GEMINI.md -> AGENTS.md

Mechanism: Symlinks (Hypothesis B confirmed)
Assessment: EXCELLENT architecture - agent-specific entry points with single source of truth
Action: Keep as-is
```

### Example 3: Test Failure Analysis

**Observation**: 5 tests failing with "connection timeout"

**Hypotheses:**

- A: Single dependency down (fix one thing)
- B: Multiple independent timeouts (fix five things)
- C: Test infrastructure issue (fix setup)
- D: Environment config missing (fix config)

**Investigation:**

- Check test dependencies
- Check error timestamps (simultaneous vs sequential)
- Run tests in isolation

**Then conclude based on evidence.**

## Anti-Patterns

```
DO NOT:
- "File X doesn't exist" without: ls X
- "Function not used" without: grep -r "function_name"
- "Version invalid" without: checking registry/lockfile
- "Tests fail" without: running tests
- "CRITICAL/BLOCKER" without verification
- Use strong language without evidence
- Skip mechanism investigation
- Pattern match to first familiar case

DO:
- Show grep/ls/find output BEFORE claiming
- Quote actual lines: "file.py:123: 'code here' - issue"
- Check lockfiles for resolved versions
- Run available tools and show output
- Reserve strong language for evidence-proven issues
- "Let me verify..." -> tool output -> interpretation
- Generate multiple hypotheses before gathering evidence
- Distinguish observation from mechanism
```

## Clarifying Questions

**Before proceeding with complex tasks, ask:**

1. What is the primary goal/context?
2. What scope is expected (simple fix vs comprehensive)?
3. What are the success criteria?
4. What constraints exist?

**For reviews specifically:**

- Scope: All changed files or specific ones?
- Depth: Quick feedback or comprehensive analysis?
- Focus: Implementation quality, standards, or both?
- Output: List of issues or prioritized roadmap?

## Task Management Patterns

### Review Request Interpretation

**Universal Rule: ALL reviews are comprehensive unless explicitly scoped**

**Never assume limited scope based on:**

- Recent conversation topics
- Previously completed partial work
- Specific words that seem to narrow scope
- Apparent simplicity of request

**Always include:**

- All applicable quality gates
- Evidence for every claim
- Complete verification of requirements
- Systematic coverage (not spot-checking)

### Context Analysis Decision Framework

**Universal Process:**

1. **Analyze actual purpose** (don't assume from patterns)
2. **Check consistency** with actual usage
3. **Verify with evidence** (read/test to confirm)
4. **Ask before acting** when uncertain

**Recognition Pattern:**

```
WRONG: "Other components do X, so this needs X"
RIGHT: "Let me analyze if this component actually needs X for its purpose"
```

## Related Use Cases

- Code reviews requiring evidence-based claims
- Version verification before recommendations
- Architectural assessments
- Debugging with multiple possible causes
- Documentation analysis
- Security audits
- Performance investigations
- Any analysis requiring rigorous reasoning
