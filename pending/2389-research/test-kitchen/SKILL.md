---
name: test-kitchen
description: This skill should be used when implementing features with parallel exploration or competition. Triggers on "build", "create", "implement", "try both approaches", "compare implementations". Routes to omakase-off (entry gate for design exploration) or cookoff (exit gate for parallel implementation).
---

# Test Kitchen

Parallel implementation framework with two gate skills:

| Skill | Gate | Trigger |
|-------|------|---------|
| `test-kitchen:omakase-off` | **Entry** | FIRST on any build/create/implement request |
| `test-kitchen:cookoff` | **Exit** | At design→implementation transition |

## Flow

```
"Build X" / "Create Y" / "Implement Z"
    ↓
┌─────────────────────────────────────┐
│  OMAKASE-OFF (entry gate)           │
│  Wraps brainstorming                │
│                                     │
│  Choice:                            │
│  1. Brainstorm together             │
│  2. Omakase (3-5 parallel designs)  │
└─────────────────────────────────────┘
    ↓
[Brainstorming / Design phase]
    ↓
Design complete, "let's implement"
    ↓
┌─────────────────────────────────────┐
│  COOKOFF (exit gate)                │
│  Wraps implementation               │
│                                     │
│  Choice:                            │
│  1. Cookoff (2-5 parallel agents)   │
│  2. Single subagent                 │
│  3. Local implementation            │
└─────────────────────────────────────┘
    ↓
[Implementation]
```

## Key Insight

**Skills need aggressive triggers to work.** They can't passively detect "uncertainty" or "readiness" - they must claim specific moments in the conversation flow.

- **Omakase-off**: Claims the BUILD/CREATE moment (before brainstorming)
- **Cookoff**: Claims the IMPLEMENT moment (after design)

## When Each Triggers

### Omakase-off (Three Triggers)

**Trigger 1: BEFORE brainstorming**
- "I want to build...", "Create a...", "Implement...", "Add a feature..."
- ANY signal to start building something
- Offers choice: Brainstorm together OR Omakase (parallel designs)

**Trigger 2: DURING brainstorming (slot detection)**
- 2+ uncertain responses on architectural decisions
- "not sure", "don't know", "either works", "you pick", "no preference"
- Offers to explore detected slots in parallel

**Trigger 3: Explicitly requested**
- "try both approaches", "explore both", "omakase"
- "implement both variants", "let's see which is better"

### Cookoff
- "Let's implement"
- "Looks good, let's build"
- "Ready to code"
- Design doc just committed
- ANY signal to move from design to code

## Omakase Mode (Skip Brainstorming)

If user picks "Omakase" at the entry gate:
1. Quick context gathering (1-2 questions)
2. Generate 3-5 best architectural approaches
3. Implement ALL in parallel
4. Tests pick the winner
5. Skip detailed brainstorming entirely

Best for: "I'm flexible, show me options in working code"

## Cookoff Mode (Parallel Implementation)

If user picks "Cookoff" at the exit gate:
1. Each agent reads the same design doc
2. Each agent creates their OWN implementation plan
3. All implement in parallel
4. Compare results, pick winner

Best for: "I want to see different implementation approaches"

## Key Distinction

| | Omakase-off | Cookoff |
|-|-------------|---------|
| **Gate** | Entry (before/during brainstorming) | Exit (after design) |
| **Question** | HOW to explore? | HOW to implement? |
| **Parallel on** | Different DESIGNS | Same design, different PLANS |
| **Triggers** | Build request, indecision detection, explicit | "let's implement" signal |
| **Skips** | Brainstorming (optional via short-circuit) | Nothing - always after design |

## Slot Detection (During Brainstorming)

When omakase-off delegates to brainstorming, it passively tracks architectural decisions where user shows uncertainty:

**Detection signals:**
- "not sure", "don't know", "either works", "both sound good"
- "you pick", "whatever you think", "no preference"
- User defers 2+ decisions in a row

**Slot classification:**
| Type | Examples | Worth exploring? |
|------|----------|------------------|
| **Architectural** | Storage engine, framework, auth method | Yes - different code paths |
| **Trivial** | File location, naming, config format | No - easy to change |

**At end of brainstorming:**
- If architectural slots exist → offer parallel exploration
- If no slots → hand off to cookoff for implementation
