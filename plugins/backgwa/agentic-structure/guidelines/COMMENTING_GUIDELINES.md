# Commenting Guidelines

## Purpose and Mindset
Comments should convey essential intent with the minimum necessary words. If the code is clean and self-explanatory, it should be understandable with few or no comments.

## Core Principles
- **Prefer clarity in code over comments**: Use clear naming and simple control flow to avoid needing comments.
- **Comment the "why", not the "what"**: Code already shows *what* happens; comments should explain intent, constraints, trade-offs, and impact.
- **Avoid comment noise**: Excessive comments reduce readability and make maintenance harder.
- **High-signal only**: Add comments only when passing the Comment Signal Test below.

## Application Philosophy
These guidelines are designed to be applied thoughtfully, not rigidly:

- **Strive to follow** - Aim to apply these principles consistently, but use judgment when exceptions are warranted
- **Apply incrementally** - Build good habits gradually; it's acceptable to apply these imperfectly at first and improve over time
- **Context matters** - Adapt guidelines to project size, team structure, and specific requirements
- **Progress over perfection** - Moving in the right direction is better than perfect adherence that delays delivery
- **Question and clarify** - When unsure, err on the side of asking or documenting your reasoning

### Comment Signal Test
**Strive to ensure a comment passes 2 or more of these criteria** (apply judgment, exceptions allowed for clear reasons):

#### Signal High - Prefer adding comment when these apply
- [ ] Explains non-obvious side effect (state mutation, API call, file I/O, caching, database write)
- [ ] Documents security assumption (input is trusted/untrusted, auth required, rate limited)
- [ ] Clarifies business rule from external requirement (legal, policy, API contract, client specification)
- [ ] Warns about sharp edges (performance cliff, race condition, browser incompatibility, breaking change)
- [ ] Documents intentional deviation from best practice (with reason why deviation is necessary)
- [ ] Explains non-obvious algorithm or optimization (why this specific approach was chosen)

#### Signal Low - Generally avoid unless there's a clear reason to comment
- [ ] Restates function name or variable name
- [ ] Describes what code visibly does (code already shows this)
- [ ] Adds attribution ("written by", "modified by") - use git instead
- [ ] Placeholder for future work ("TODO: add feature X") - use issue tracker instead
- [ ] Version history - use git instead
- [ ] Commented-out code - delete it, git preserves history

### Decision Protocol - Apply these thought patterns
**Before adding comment, work through these questions:**

1. **Can I make code clearer instead?**
   - Rename variables/functions to be self-explanatory?
   - Extract complex logic into named functions?
   - Simplify conditions or control flow?
2. **Is this information visible in code?**
   - Type signatures show data structure?
   - Function names show intent?
   - Variable names show purpose?
3. **Does this explain WHY (high signal) or WHAT (low signal)?**
   - WHY: Reasoning, constraints, trade-offs → Add comment
   - WHAT: Step-by-step description → Refactor code instead

**Apply judgment:**
If the answer pattern suggests the comment adds no value, prefer refactoring the code for clarity instead.

### Comment Density Indicators
Monitor comment patterns to identify potential code clarity issues:

**Warning Signals:**
- **High comment density** may indicate overly complex code
  - Consider: Does code need simplification?
  - Exceptions: Regulatory requirements, security-critical code, complex algorithms
- **Many inline comments** may suggest unclear logic
  - Consider: Could extracted functions with descriptive names replace comments?
- **Comment-heavy functions** may be doing too much
  - Consider: Does function mix multiple concerns?

**Excessive Comment Indicators** (may suggest refactoring)
- [ ] Multiple consecutive comment lines explaining code flow
- [ ] Every variable assignment has a comment
- [ ] Comment length exceeds code length in same section
- [ ] Comments have more complex vocabulary than code

**Refactoring Actions to Consider:**
When comments indicate complexity issues:
1. Extract commented blocks into named functions
2. Rename variables to eliminate need for explanation
3. Simplify logic to make flow obvious
4. Move complex explanations to documentation (not inline comments)

## When to Add Comments
Use comments when they explain something the code cannot express clearly on its own:
- Non-obvious intent or business rule (“why this behavior exists”)
- Important side effects (state mutation, IO, concurrency, caching, security implications)
- Constraints and assumptions (performance, ordering, edge cases, invariants)
- Risky areas and sharp edges (workarounds, legacy behavior, compatibility constraints)

## When Not to Add Comments
Avoid comments that restate the code or appear on every line:
- “Narration” comments that describe each step already visible in code
- Redundant comments for well-named variables/functions
- Large blocks of explanatory text that should be reflected in simpler code instead

## Preferred Locations and Style
### Function and class level
If a comment is needed, prefer placing it on the function/class rather than on individual lines. Keep it short and focused:
- What core responsibility it has
- What it affects (side effects / observable impact)
- Any key constraints or assumptions

### Inline comments (rare)
Use inline comments only for highly non-obvious logic. If you need many inline comments, refactor the code (extract functions, rename variables, simplify flow).

## Documentation Comments (JSDoc / PyDoc)
Documentation-style comments (e.g., JSDoc, PyDoc) should be written only when requested by the user.

When documentation is needed, prefer documenting only public, user-facing APIs:
- Classes/functions that are exposed to end users or external integration points
- Interfaces/contracts that others depend on

Avoid over-documentation; it can reduce readability and quickly become outdated.

## Default Strategy
Aim to not create situations that require comments:
- Keep code clean and easy to follow
- Use explicit, descriptive function and variable names
- Refactor complex logic into smaller, well-named units
