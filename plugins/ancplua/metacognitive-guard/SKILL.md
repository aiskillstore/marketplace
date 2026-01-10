---
name: Metacognitive Guard
description: >-
    Monitors Claude's responses for struggle signals and suggests escalation
    to deep-thinking agents when complexity exceeds comfortable reasoning capacity.
---

# Metacognitive Guard Skill

This skill provides awareness of the struggle detection system and guidance on when to proactively engage deep-thinking resources.

## When to Self-Escalate

Even before the struggle detector triggers, consider spawning `deep-think-partner` when:

### High-Complexity Indicators

1. **Architectural decisions** with competing constraints
    - Multiple valid approaches exist
    - Trade-offs span different dimensions (performance, maintainability, cost)
    - Decision affects multiple system components

2. **Ambiguous requirements** requiring interpretation
    - User hasn't specified implementation details
    - Multiple reasonable interpretations exist
    - Wrong choice has significant rework cost

3. **Multi-domain synthesis** required
    - Problem spans multiple technology areas
    - Integration patterns aren't obvious
    - Prior art doesn't directly apply

4. **Edge case analysis** needed
    - Happy path is clear but edge cases aren't
    - Failure modes need systematic exploration
    - Concurrency or timing issues involved

### Self-Assessment Checklist

Before responding to complex questions, ask yourself:

- [ ] Can I give a concrete recommendation (not "it depends")?
- [ ] Do I have high confidence in my answer?
- [ ] Is this answerable without multiple follow-up exchanges?
- [ ] Would a structured analysis add significant value?

If you answer "no" to any of these, consider proactive escalation.

## How to Escalate

Use the Task tool with the deep-think-partner agent:

```yaml
Task tool:
    subagent_type: deep-think-partner
    prompt: [Detailed problem statement with all constraints]
    description: [3-5 word summary]
```

### Good Prompts for Deep-Think Partner

Include:

- **Context**: What system/codebase is this for?
- **Constraints**: What limits the solution space?
- **Success criteria**: How do we know we got it right?
- **Specific question**: What decision needs to be made?

### Example Escalation

**User asks:** "Should we use Redis or PostgreSQL for session storage?"

**Self-assessment:** Multiple valid approaches, depends on constraints not yet explored, "it depends" isn't helpful.

**Escalation:**

```yaml
Task tool:
    subagent_type: deep-think-partner
    prompt: |
        Context: Web application with 10k concurrent users, existing PostgreSQL database.
        Question: Redis vs PostgreSQL for session storage.
        Constraints: Team has PostgreSQL expertise, no Redis experience.
        Must handle session expiry. Cost-sensitive.
        Success: Clear recommendation with migration path.
    description: Analyze session storage options
```

## Understanding Struggle Signals

The automatic detector looks for these patterns in your responses:

| Signal        | What It Means                      | Better Approach                             |
| ------------- | ---------------------------------- | ------------------------------------------- |
| Hedging       | Uncertainty about recommendation   | Escalate for deeper analysis                |
| Deflecting    | Avoiding commitment with questions | Answer then ask clarifying questions        |
| Verbose       | Rambling without concrete output   | Structure response, include code/tables     |
| Contradiction | Changed position mid-response      | Stop, think, give one coherent answer       |
| Apologetic    | Previous response was wrong        | Acknowledge, correct, move forward          |
| Weaseling     | Non-committal to avoid being wrong | Make a recommendation with confidence level |

## Integration with Deep-Think Partner

When deep-think-partner returns its analysis:

1. **Don't just paste it** - synthesize for the user
2. **Highlight the key insight** - what's the non-obvious finding?
3. **Present the recommendation clearly** - don't bury it
4. **Offer the implementation plan** - if user wants to proceed

## Metrics

Track your struggle detection rate to improve:

- How often does the detector trigger?
- Are triggers false positives or genuine struggles?
- Does escalation produce better outcomes?

Self-awareness of your own patterns helps calibrate both the detector and your escalation instincts.
