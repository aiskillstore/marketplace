---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: meta-cognitive-reasoning
---

# Detailed Meta-Cognitive Frameworks

This reference provides expanded decision frameworks for complex reasoning scenarios.

## Defensive Programming Skepticism

**Recognition Pattern:** Justifying code with "it's idempotent/safe/defensive" without proving the problem exists

**Decision Framework:**

```
When encountering "just in case" code:

1. What SPECIFIC problem does this solve?
   Not "might prevent X" - does X actually occur here?

2. Can that problem occur in THIS context?
   Evidence: Can I trigger the failure scenario?

3. Is defense solving real problem or imagined one?
   Real: Problem documented/observed/testable
   Imagined: "Could happen" without evidence

4. What's the cost of the defense?
   Complexity, performance, maintenance burden
```

**When Defensive Code IS Appropriate:**

- Trust boundaries (external input, API boundaries)
- Error recovery (network failures, timeouts)
- Resource availability (external dependencies)
- Race conditions (concurrent access, locking)
- Actual observed failures (documented/reproducible)

**When Defensive Code IS NOT Appropriate:**

- "Could happen" without evidence
- Patterns copied without context analysis
- Already handled by framework/tool
- Problem cannot occur given invariants

## Problem-First vs Solution-First Thinking

**Recognition Pattern:** Reaching for "better tools" instead of questioning the need

**Decision Framework:**

1. **Question First**: Why does this problem exist?
2. **Consider Prevention**: Can we avoid creating the problem?
3. **Benchmark Elimination**: Is prevention faster than optimization?
4. **Resist Pattern Matching**: Does this case really need the standard solution?

**Thinking Pattern:**

```
WRONG: "How do I make X faster?"
RIGHT: "Why do I need X at all?"

WRONG: "Better post-processing tools"
RIGHT: "Smarter construction to avoid post-processing"
```

## Structured Roadmap for Complex Multi-Issue Tasks

**When to Use:** Analysis identifies 10+ issues across different severity levels

**Roadmap Structure:**

```markdown
## Critical Issues (Blockers)
[Issues that prevent merge/deployment/completion]
- Explicit: will cause failure if not fixed
- Evidence-based: shown with file:line:evidence

## High-Priority Issues
[Significant quality/security/correctness concerns]
- Important but not blocking
- Should address before considering done

## Medium Priority
[Improvements that enhance quality]
- Nice-to-have refactorings
- Documentation gaps

## Low Priority / Future
[Future optimizations, minor suggestions]
- Can be deferred
- Track but don't block on

## Summary & Recommendations
**Blockers for completion:** [Explicit checklist]
**Suggested next steps:** [Clear action items]
```

## Reader vs Writer Optimization

**Recognition Pattern:** Proposing changes that make writing easier at expense of reading

**Decision Framework:**

```
1. IDENTIFY the activities
   - Reading/using the artifact
   - Writing/updating the artifact

2. MEASURE frequency
   - How often is this read/used?
   - How often is this written/updated?

3. CALCULATE costs
   - Cost per read (context switching, searching)
   - Cost per write (updating multiple places)

4. COMPUTE total cost over time
   - Total read cost: Read_cost x Read_frequency
   - Total write cost: Write_cost x Write_frequency

5. OPTIMIZE for higher total cost
   - If Total_read >> Total_write -> Optimize for reader
   - If Total_write >> Total_read -> Optimize for writer
```

**When Writer Optimization IS Appropriate:**

- Content changes frequently (volatile)
- Many writers, few readers
- Consistency is critical
- Write cost is very high

**When Reader Optimization IS Appropriate:**

- Content is stable (rare updates)
- Many readers, few writers
- Cognitive flow matters
- Read cost compounds over time

## Organizational Structure Debates

**Recognition Pattern:** Multiple valid proposals, no convergence, debate feels unresolvable

**Core Insight:** Structure debates are rarely about structure - they're about unstated architectural philosophy differences

**Decision Framework:**

```
STEP 1: RECOGNIZE DEEPER QUESTIONS
Not "Where should files go?"
But: "What assumptions drive each proposal?"

STEP 2: SURFACE UNSTATED ASSUMPTIONS
Option A assumes: Polyglot future
Option B assumes: Current scope
Option C assumes: Application boundaries

STEP 3: FACILITATE ALIGNMENT ON PHILOSOPHY
Ask clarifying questions:
- "Is this a monorepo or single-project?"
- "Will we add other languages?"
- "What's the 6-12 month growth plan?"

STEP 4: STRUCTURE FOLLOWS PHILOSOPHY
Once philosophy aligned, structure becomes obvious

STEP 5: DOCUMENT DECISION AND RATIONALE
"We chose X because [philosophy]"
```

## Mid-Task Feedback Integration

**When user provides mid-task feedback:**

1. **Pause and reassess** - Don't compartmentalize feedback
2. **Extract underlying principle** - What broader lesson applies?
3. **Apply throughout task** - Not just to immediate item
4. **Show integration** - Demonstrate corrected understanding

## Documentation Quality Detection

**Core Principle:** Documentation should justify existence by adding non-obvious information

**Universal Decision Framework:**

```
For each piece of documentation, ask in order:

1. Does it explain WHY, not WHAT?
   KEEP: "Single-threaded to avoid race conditions"
   DELETE: "Single-threaded implementation"

2. Does it provide non-obvious context?
   KEEP: "Must be called before initialize() due to DI order"
   DELETE: "Configuration class" when class is named Config

3. Does it explain business rules, constraints, or edge cases?
   KEEP: "Returns null for suspended users per GDPR requirements"
   DELETE: "Returns user or null"

4. Does it explain technical mechanisms or gotchas?
   KEEP: "Uses weak references to prevent memory leaks"
   DELETE: "Uses weak references"

5. Would a new team member lose important information?
   KEEP: "CRITICAL: Must acquire lock before modifying"
   DELETE: "Acquires lock" (obvious from code)

If all answers are NO -> Documentation is useless
```

## Multi-Level Documentation Structure

**Recognition Pattern:** Reviewing parent-child documentation hierarchy

**Usage-First Decision Framework:**

```
1. WHO is the actual user?
   - AI agent loading specific context
   - Human reader navigating hierarchy

2. WHAT is the usage pattern?
   - Top-down: Read root -> specialize
   - Current-and-up: Load specific -> reference general
   - Reference: Search/jump to specific concept

3. WHAT is being "duplicated"?
   - Literal repetition (consolidate)
   - Contextual adaptation (keep separated)

4. WHAT is the cost tradeoff?
   - Context switching cost (every use)
   - Maintenance burden (rare updates)

5. WHAT is the document TYPE?
   - Code: optimize for DRY
   - Cognitive framework: optimize for flow
   - API reference: optimize for lookup
```

**Critical Distinction:**

```
DUPLICATION (consolidate):
Same principle, same examples, same commands
Different location only

CONTEXTUAL ADAPTATION (keep separate):
Same principle core concept
Different domain-specific recognition patterns
Different decision frameworks
Different verification commands
```

## Session Artifact Detection

**Recognition Pattern:** References to specific PRs, issues, incidents in universal documentation

**Decision Framework:**

```
1. EVALUATE function
   - Does the example work without the reference?
   - Is the reference needed for verification?

2. ASSESS accessibility
   - Can future readers access the artifact?
   - Or is it just a reference number?

3. DETERMINE priority
   - Does removing it significantly improve universality?
   - Or is the example already clear?

4. CALIBRATE effort vs impact
   - How much work to refactor?
   - How much clarity gained?
```

**Priority Calibration:**

```
HIGH priority to remove:
- Reference required for example to make sense
- Blocks understanding without external artifact

LOW priority (optional polish):
- Example is self-contained and clear
- Reference adds traceability but not needed for comprehension
```

## Real-Time Assumption Correction

**Recognition:** When user feedback challenges your approach

**Correct Response Protocol:**

1. **PAUSE immediately** - Stop current approach, don't just acknowledge
2. **Extract the principle** - What assumption was incorrect?
3. **Apply consistently** - Update ALL similar decisions in current task
4. **Demonstrate integration** - Show you've corrected the understanding

**Anti-Pattern:**

```
WRONG: Continue with original plan while acknowledging feedback
RIGHT: Revert approach based on corrected understanding
```

**Key Insight:** User feedback often reveals fundamental approach errors affecting entire task, not just minor adjustments

## Systematic Completion Discipline (Extended)

**Structured Roadmap for Complex Multi-Issue Tasks:**

When analysis identifies 10+ issues across different severity levels, use this structure:

```markdown
## Critical Issues (Blockers)
[Issues that prevent merge/deployment/completion]
- Explicit: will cause failure if not fixed
- Evidence-based: shown with file:line:evidence

## High-Priority Issues
[Significant quality/security/correctness concerns]
- Important but not blocking
- Should address before considering done

## Medium Priority
[Improvements that enhance quality]
- Nice-to-have refactorings
- Documentation gaps

## Low Priority / Future
[Future optimizations, minor suggestions]
- Can be deferred
- Track but don't block on

## Summary & Recommendations
**Blockers for completion:** [Explicit checklist]
**Suggested next steps:** [Clear action items]
```

**Benefits:**

- Prevents overwhelm (clear priorities vs undifferentiated list)
- Enables parallel work (different people tackle different priorities)
- Clear completion criteria (what MUST be done vs nice-to-have)
- Progress tracking (check off completed items)

## Context Analysis Decision Framework

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

**Application Examples:**

- Before adding error handling: Does this error path actually occur?
- Before adding validation: Is input already validated upstream?
- Before refactoring: Does this pattern serve a purpose I'm missing?

## Meta-Pattern Documentation

**When capturing learnings:**

**Focus on:**

- Recognition patterns that apply across contexts
- Decision frameworks that prevent common failures
- Universal cognitive principles
- Anti-patterns and how to avoid them

**Avoid:**

- Session-specific implementation details
- Framework-specific solutions without broader applicability
- File paths, line numbers, exact error messages from specific sessions

**Test:** "Would this apply to completely different domain/project?"
