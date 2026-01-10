# Discussion and Debate Guidelines

## Purpose and Importance
Effective communication is the cornerstone of successful collaboration. This document outlines when and how to engage in productive discussions to ensure clarity, alignment, and high-quality outcomes in our development process.

## Application Philosophy
These guidelines are designed to be applied thoughtfully, not rigidly:

- **Strive to follow** - Aim to apply these principles consistently, but use judgment when exceptions are warranted
- **Apply incrementally** - Build good habits gradually; it's acceptable to apply these imperfectly at first and improve over time
- **Context matters** - Adapt guidelines to project size, team structure, and specific requirements
- **Progress over perfection** - Moving in the right direction is better than perfect adherence that delays delivery
- **Question and clarify** - When unsure, err on the side of asking or documenting your reasoning

## When to Initiate Discussion

### Handling Ambiguous Requirements

#### Trigger Conditions (ANY = ambiguous, requires discussion)
- [ ] User request contains subjective terms without specific criteria
- [ ] Two or more implementation approaches match the description equally well
- [ ] Requirements imply technical constraints not explicitly stated
- [ ] Success criteria not defined (no clear definition of "done")
- [ ] Request references "similar to X" but X has multiple valid interpretations

#### Detecting Unmeasurable Terms
When user request contains these terms WITHOUT criteria, stop and ask for clarification:

| Ambiguous Term | Specific Question to Ask |
|----------------|--------------------------|
| "scalable" | "What scale? (number of users, requests/sec, data volume, concurrent operations)" |
| "fast" / "quick" | "What metric? (page load time, API response time, throughput, processing latency)" |
| "maintainable" | "What aspect? (testability, modularity, documentation coverage, ease of modification)" |
| "user-friendly" | "What behavior? (fewer clicks, clearer error messages, faster feedback, simpler navigation)" |
| "secure" | "What threat model? (authentication, data privacy, injection attacks, DoS prevention, secrets management)" |
| "robust" | "What failure scenarios? (network issues, invalid input, high load, service outages)" |
| "efficient" | "Optimize for what? (memory usage, CPU time, network bandwidth, database queries)" |
| "better" / "improve" | "Better than what? What specific metric should improve?" |

#### Action Protocol
When ambiguous term detected:
1. Quote the term: "You mentioned '[term]'"
2. Ask specific question from table above
3. Request measurable criteria: "To implement this correctly, I need to know: [specific question]"
4. Wait for clarification before proposing solutions

#### Multiple Interpretations Example
- Request: "Add caching to improve performance"
- Ambiguities:
  - Cache where? (Browser, CDN, application, database query results)
  - Cache what? (API responses, rendered pages, computed values, database queries)
  - What performance? (Response time, server load, database load, bandwidth)
- Action: Present 2-3 specific interpretations and ask which matches user intent

### Evaluating Implementation Options
- Technical Trade-offs: When different approaches have competing advantages
  - Performance vs. Readability
  - Development Speed vs. Long-term Maintainability
  - Custom Solution vs. Third-party Integration
- Architectural Impact: When decisions could affect system design
  - Database schema changes
  - API contracts
  - Cross-team dependencies

### Ensuring Consistency

#### Pattern Consistency Check

##### Trigger Conditions for "New Pattern" Detection
Before introducing any of the following, run this consistency check:
- [ ] A library not already in package dependencies
- [ ] An architectural pattern not found in existing code (e.g., singleton, factory, observer, repository)
- [ ] A file organization structure different from current layout
- [ ] An error handling approach not matching existing error handling
- [ ] A naming convention that differs from codebase style
- [ ] A state management approach not currently used

##### Action Protocol
1. **Search codebase** for similar implementations using Grep/Glob
2. **If pattern found in codebase:**
   - Use existing pattern for consistency
   - Example: "I found existing error handling uses custom Error classes, so I'll follow that pattern"
 3. **If pattern NOT found in codebase:**
    - **Prefer discussing with user for alignment** (unless the new pattern is clearly superior or minimal):
      - "The codebase currently uses [X pattern]"
      - "Your request would introduce [Y pattern]"
      - "Options:"
        - "A. Adapt request to use existing [X pattern]"
        - "B. Introduce new [Y pattern] (consider discussing if this affects architecture)"
    - Proceed based on user input or clear project context

##### Example
Request: "Add Redux for state management"
Current codebase: Uses React Context API
Action:
1. Search reveals Context API in 5 components
2. Present: "Codebase uses Context API. Options: (A) Use Context API for this feature, (B) Introduce Redux (affects architecture)"
3. Wait for user choice

#### Style Guide Adherence
When existing code style might be affected:
- Exception handling approaches
- Naming conventions (camelCase vs snake_case, etc.)
- Code organization (feature-based vs layer-based)
- Comment style and density

Before deviating from observed patterns, discuss with user.

### Scope Definition
- Feature Boundaries: When requirements lack clear parameters
  - Define MVP vs. Future Enhancements
  - Identify must-have vs. nice-to-have features
  - Set clear acceptance criteria

## Effective Communication Strategies

### Structured Decision Making

#### When to Present Options
- [ ] Multiple valid implementation approaches exist with different trade-offs
- [ ] Choosing one approach excludes benefits of others
- [ ] Trade-off impacts core requirements (performance, maintainability, security)
- [ ] Architectural decision affects multiple parts of system

#### Option Presentation Protocol
1. **Aim to present 2-3 viable approaches** (more options rarely improves decision quality)
2. **Use structured comparison table when it clarifies trade-offs** (don't force it for simple decisions)
3. **Include complexity assessment when scope is unclear** (not needed for trivial changes)
4. **Always state your recommendation** with reasoning based on project context

#### Complexity Assessment Criteria
Replace "effort estimates" with these concrete measures:

| Assessment Dimension | Small | Medium | Large |
|---------------------|-------|--------|-------|
| Implementation Scope | Single file/function | Multiple related files (2-5) | Architectural change (6+ files) |
| Risk Level | Well-established pattern | New pattern to codebase | Novel approach, unproven |
| Dependency Count | 0-1 files modified | 2-5 files modified | 6+ files or new external dependency |
| Testing Impact | Existing tests sufficient | Need new test cases | Need test infrastructure changes |
| Reversibility | Easy to undo | Moderate refactoring to undo | Difficult/impossible to reverse |

#### Structured Comparison Table Template
Present options using this format:

| Criterion | Option A: [Name] | Option B: [Name] | Option C: [Name] |
|-----------|------------------|------------------|------------------|
| Implementation Scope | [Small/Medium/Large] | [Small/Medium/Large] | [Small/Medium/Large] |
| Risk Level | [Low/Medium/High] | [Low/Medium/High] | [Low/Medium/High] |
| Dependency Count | [#] files affected | [#] files affected | [#] files affected |
| Maintainability Impact | [Improves/Neutral/Degrades] | [Improves/Neutral/Degrades] | [Improves/Neutral/Degrades] |
| Performance Impact | [Improves/Neutral/Degrades] | [Improves/Neutral/Degrades] | [Improves/Neutral/Degrades] |
| Compatibility Impact | [None/Minor/Breaking] | [None/Minor/Breaking] | [None/Minor/Breaking] |
| Alignment with Codebase | [Consistent/New pattern/Deviation] | [Consistent/New pattern/Deviation] | [Consistent/New pattern/Deviation] |

**Recommendation:** [State which option and why, based on above comparison]

#### Impact Assessment
After presenting comparison table, address these dimensions:
- **Technical debt implications**: Will this create future maintenance burden?
- **Performance considerations**: What are the runtime/memory/network impacts?
- **Maintenance requirements**: How easy is it to modify, debug, or extend?
- **Team familiarity**: Does team have experience with this approach?

### Context Provision
- Situation Analysis
  - Current system state
  - Relevant constraints (time, resources, technical)
  - Previous decisions that might impact current choices

- Stakeholder Impact
  - How will this affect different teams?
  - What are the user experience implications?
  - Are there business priorities to consider?

### Recommendation Framework
1. Best Practices
   - Industry standards
   - Framework-specific conventions
   - Team agreements

2. Decision Documentation
   - Record the chosen approach
   - Note rejected alternatives and why
   - Document any assumptions made
