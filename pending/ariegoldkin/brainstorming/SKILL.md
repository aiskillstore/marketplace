---
name: brainstorming
description: Use when creating or developing anything, before writing code or implementation plans - refines rough ideas into fully-formed designs through structured Socratic questioning, alternative exploration, and incremental validation
---

# Brainstorming Ideas Into Designs

## Overview

Transform rough ideas into fully-formed designs through structured questioning and alternative exploration.

**Core principle:** Ask questions to understand, explore alternatives, present design incrementally for validation.

**Announce skill usage at start of session.**

## When to Use This Skill

Activate this skill when:
- Request contains "I have an idea for..." or "I want to build..."
- User asks "help me design..." or "what's the best approach for..."
- Requirements are vague or high-level
- Multiple approaches might work
- Before writing any code or implementation plans

## The Three-Phase Process

| Phase | Key Activities | Tool Usage | Output |
|-------|----------------|------------|--------|
| **1. Understanding** | Ask questions (one at a time) | AskUserQuestion for choices | Purpose, constraints, criteria |
| **2. Exploration** | Propose 2-3 approaches | AskUserQuestion for approach selection | Architecture options with trade-offs |
| **3. Design Presentation** | Present in 200-300 word sections | Open-ended questions | Complete design with validation |

### Phase 1: Understanding

**Goal:** Gather purpose, constraints, and success criteria.

**Process:**
- Check current project state in working directory
- Ask ONE question at a time to refine the idea
- Use AskUserQuestion tool when presenting multiple choice options
- Gather: Purpose, constraints, success criteria

**Tool Usage:**
Use AskUserQuestion for clarifying questions with 2-4 clear options.

Example: "Where should the authentication data be stored?" with options for Session storage, Local storage, Cookies, each with trade-off descriptions.

See `references/example-session-auth.md` for complete Phase 1 example.

### Phase 2: Exploration

**Goal:** Propose 2-3 different architectural approaches with explicit trade-offs.

**Process:**
- Propose 2-3 different approaches
- For each: Core architecture, trade-offs, complexity assessment
- Use AskUserQuestion tool to present approaches as structured choices
- Include trade-off comparison table when helpful

**Trade-off Format:**

| Approach | Pros | Cons | Complexity |
|----------|------|------|------------|
| Option 1 | Benefits | Drawbacks | Low/Med/High |
| Option 2 | Benefits | Drawbacks | Low/Med/High |
| Option 3 | Benefits | Drawbacks | Low/Med/High |

See `references/example-session-dashboard.md` for complete Phase 2 example with SSE vs WebSockets vs Polling comparison.

### Phase 3: Design Presentation

**Goal:** Present complete design incrementally, validating each section.

**Process:**
- Present in 200-300 word sections
- Cover: Architecture, components, data flow, error handling, testing
- Ask after each section: "Does this look right so far?"
- Use open-ended questions to allow freeform feedback

**Typical Sections:**
1. Architecture overview
2. Component details
3. Data flow
4. Error handling
5. Security considerations
6. Implementation priorities

**Validation Pattern:**
After each section, pause for feedback before proceeding to next section.

## Tool Usage Guidelines

### Use AskUserQuestion Tool For:
- Phase 1: Clarifying questions with 2-4 clear options
- Phase 2: Architectural approach selection (2-3 alternatives)
- Any decision with distinct, mutually exclusive choices
- When options have clear trade-offs to explain

**Benefits:**
- Structured presentation of options with descriptions
- Clear trade-off visibility
- Forces explicit choice (prevents vague "maybe both" responses)

### Use Open-Ended Questions For:
- Phase 3: Design validation
- When detailed feedback or explanation is needed
- When the user should describe their own requirements
- When structured options would limit creative input

## Non-Linear Progression

**Flexibility is key.** Go backward when needed - don't force linear progression.

**Return to Phase 1 when:**
- User reveals new constraint during Phase 2 or 3
- Validation shows fundamental gap in requirements
- Something doesn't make sense

**Return to Phase 2 when:**
- User questions the chosen approach during Phase 3
- New information suggests a different approach would be better

**Continue forward when:**
- All requirements are clear
- Chosen approach is validated
- No new constraints emerge

## Key Principles

| Principle | Application |
|-----------|-------------|
| **One question at a time** | Phase 1: Single question per message, use AskUserQuestion for choices |
| **Structured choices** | Use AskUserQuestion tool for 2-4 options with trade-offs |
| **YAGNI ruthlessly** | Remove unnecessary features from all designs |
| **Explore alternatives** | Always propose 2-3 approaches before settling |
| **Incremental validation** | Present design in sections, validate each |
| **Flexible progression** | Go backward when needed - flexibility > rigidity |

## After Brainstorming Completes

Consider these optional next steps:
- Document the design in project's design documentation
- Break down the design into actionable implementation tasks
- Create a git branch or workspace for isolated development

Use templates in `assets/design-doc-template.md` and `assets/decision-matrix-template.md` for structured documentation.

## Examples

**Complete brainstorming sessions:**
- `references/example-session-auth.md` - Authentication storage design (JWT vs Session vs Cookies)
- `references/example-session-dashboard.md` - Real-time dashboard design (SSE vs WebSockets vs Polling)

**Output templates:**
- `assets/design-doc-template.md` - Structured design document format
- `assets/decision-matrix-template.md` - Weighted decision comparison format
