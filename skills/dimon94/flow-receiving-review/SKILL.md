---
name: flow-receiving-review
description: "Handle code review feedback with technical rigor. Don't blindly agree - verify before implementing."
---

# Flow Receiving Review - 处理代码审查反馈

## The Iron Law

```
VERIFY FEEDBACK BEFORE IMPLEMENTING - DON'T BLINDLY AGREE
```

## Overview

When receiving code review feedback, maintain technical rigor. Reviewers can be wrong. Your job is to:
1. Understand the feedback
2. Verify it's correct
3. Then implement (or push back)

## The Process

### Step 1: Understand the Feedback

```yaml
For each comment:
  1. Read completely - don't skim
  2. Identify the concern:
     - Is it a bug?
     - Is it a style preference?
     - Is it a performance issue?
     - Is it a security concern?
  3. If unclear → ASK for clarification
     - "Could you elaborate on why X is problematic?"
     - "What specific scenario does this address?"
```

### Step 2: Verify the Feedback

```yaml
Before implementing ANY change:
  1. Is the feedback technically correct?
     - Does the suggested change actually fix the issue?
     - Could it introduce new problems?

  2. Does it align with project standards?
     - Check Constitution
     - Check existing patterns

  3. Is there evidence?
     - Can you reproduce the issue?
     - Does the suggested fix work?

If feedback seems wrong:
  → Don't silently disagree
  → Don't blindly implement
  → Respond with your analysis
```

### Step 3: Respond Appropriately

```yaml
If feedback is correct:
  → Acknowledge: "Good catch, fixing now"
  → Implement the fix
  → Verify the fix works

If feedback is unclear:
  → Ask: "Could you clarify what you mean by X?"
  → Don't guess the intent

If feedback seems incorrect:
  → Explain your reasoning
  → Provide evidence
  → "I considered X, but Y because Z. What do you think?"

If feedback is a preference (not a bug):
  → Discuss trade-offs
  → Defer to project standards if they exist
```

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Reviewer knows better" | Reviewers make mistakes. Verify. |
| "Just do what they say" | Blind compliance = poor code. |
| "Don't want to argue" | Technical discussion ≠ argument. |
| "It's faster to just change it" | Wrong changes waste more time. |
| "They'll reject if I push back" | Good reviewers appreciate rigor. |

## Red Flags - STOP

If you find yourself:
- Implementing changes you don't understand
- Agreeing with feedback you think is wrong
- Not asking clarifying questions
- Making changes without verifying they work

**STOP. Understand first. Verify second. Implement third.**

## Response Templates

### Agreeing with Feedback
```
Good catch! You're right that [issue]. I've updated [file] to [fix].
Verified by running [test/command].
```

### Asking for Clarification
```
I want to make sure I understand correctly. Are you suggesting [interpretation]?
If so, I'm wondering about [concern]. Could you elaborate?
```

### Respectfully Disagreeing
```
I considered [suggestion], but I went with [current approach] because:
1. [Reason 1]
2. [Reason 2]

The trade-off is [X]. What do you think about [alternative]?
```

### Requesting Evidence
```
I'm having trouble reproducing [issue]. Could you share:
- Steps to reproduce
- Expected vs actual behavior
- Environment details
```

## Integration with flow-review

This skill is used in `/flow-review` when processing reviewer feedback:

```yaml
After receiving review:
  1. Load this skill
  2. Process each comment using the 3-step process
  3. Respond appropriately
  4. Track changes in EXECUTION_LOG.md
```

## Cross-Reference

- [flow-review.md](../../commands/flow-review.md) - Two-stage review command
- [spec-reviewer.md](../../agents/spec-reviewer.md) - Spec compliance agent
- [code-quality-reviewer.md](../../agents/code-quality-reviewer.md) - Quality review agent

---

**[PROTOCOL]**: 变更时更新此头部，然后检查 CLAUDE.md
