---
name: epistemic-checkpoint
description: |
  Force verification before answering questions involving versions, dates, status, or "current"
  state. Prevents hallucinations at the REASONING level by checking assertions.yaml and WebSearch
  before forming beliefs. Triggers on software versions, release status, dates, and package versions.
---

# Epistemic Checkpoint

Force verification before answering questions involving versions, dates, status, or "current" state.

## Purpose

Prevents the ROOT CAUSE of hallucinations - not just blocking wrong output, but preventing wrong
REASONING. Claude's training data is stale; this skill forces verification before forming beliefs.

## Triggers

Activate this skill when the question involves ANY of:

- Software versions (.NET, Node, React, Python, etc.)
- Release status (preview, LTS, GA, RC, deprecated)
- "Current" or "latest" anything
- Dates that might be after training cutoff
- Package versions
- API deprecations

## MANDATORY Protocol

### Step 1: Recognize Uncertainty

Say to yourself: **"My training data may be stale for: [topic]"**

### Step 2: Check Local Ground Truth

```text
Read ${CLAUDE_PLUGIN_ROOT}/blackboard/assertions.yaml
Search for relevant entries
```

If found - use that value with high confidence.

### Step 3: If Not in Assertions - WebSearch

```text
WebSearch("[software] [version] release date site:official-docs")
WebSearch("[software] LTS release 2025")
```

Prefer official sources:

- microsoft.com/dotnet for .NET
- nodejs.org for Node
- python.org for Python

### Step 4: State Verified Facts

Say: **"Based on [source], [software] [version] is [status] as of [date]."**

### Step 5: THEN Proceed

Only now answer the actual question with the verified baseline.

## Red Flag Thoughts (REJECT THESE)

| If you think... | Actually do... |
|-----------------|----------------|
| "I'm pretty sure .NET 10 is..." | WebSearch to verify |
| "This is probably still preview" | Check assertions.yaml |
| "I remember this from training" | Training is stale, verify |
| "This is a simple factual question" | Simple facts are often WRONG |
| "The user said it's preview" | User might be wrong too, verify |

## Anti-Pattern Examples

**WRONG:**

```text
"If targeting .NET 10 preview, use C# 14 extension types..."
```

**CORRECT:**

```text
"Let me verify .NET 10 status... [WebSearch] ...
.NET 10 is LTS (released November 2025), not preview.
Standard extension methods work fine."
```

**WRONG:**

```text
"React 19 is still in beta, so..."
```

**CORRECT:**

```text
"Checking React 19 status... [WebSearch] ...
React 19 was released December 2024 as stable.
Proceeding with React 19 stable patterns."
```

## Common Danger Patterns

| Topic | Danger Pattern | Likely Truth |
|-------|----------------|--------------|
| .NET | "preview", "not released" | .NET 10 LTS since Nov 2025 |
| React | "beta", "experimental" | React 19 stable since Dec 2024 |
| Node | "current" without version | Always specify exact version |
| Python | "3.x is latest" | Verify - 3.13+ exists |

## Output Format

When this skill activates, structure your verification as:

```text
Epistemic Checkpoint

Claim to verify: [what you were about to assume]
Source checked: [assertions.yaml / WebSearch / official docs]
Verified fact: [the actual truth]
Confidence: [high/medium/low]

Proceeding with verified baseline...
```
