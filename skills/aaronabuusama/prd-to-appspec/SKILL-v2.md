---
name: prd-to-appspec
description: Transform PRDs (Product Requirements Documents) into structured XML app specifications optimized for AI coding agents. Converts developer-focused docs with code examples into declarative agent-consumable format. USE WHEN user says "convert PRD", "generate app spec", "transform PRD", "create specification from requirements", or wants to prepare a PRD for agent consumption.
---

# PRD to App Spec Converter

Transform Product Requirements Documents into structured XML application specifications optimized for AI coding agents.

## When to Activate This Skill

- Convert PRD to app spec format
- Generate XML specification from requirements
- Transform technical PRD for agent consumption
- Prepare documentation for autonomous coding agent
- Create app_spec.txt from existing PRD

## What Is a PRD? (Input Format)

A **Product Requirements Document** is a developer-focused specification containing:

**Required Sections**:
- Project name/title
- Technology stack (languages, frameworks, dependencies)
- Feature descriptions or user stories
- Data models (classes, schemas, types)

**Common Sections**:
- Implementation details (code snippets, algorithms)
- Directory structure
- Test plans or assertions
- CLI/API interface definitions
- Architecture decisions
- Epic/milestone breakdown

**PRD Style**: Technical, implementation-focused, shows **HOW** to build

**Examples**:
- Pydantic models with validators
- Function implementations with error handling
- TDD test cases with assertions
- CLI command definitions with typer decorators
- Database migrations or ORM schemas

See `references/prd-examples.md` for annotated examples.

## What Is an App Spec? (Output Format)

A **Project Specification** is an agent-consumable requirements document:

**Format**: XML with semantic sections
**Style**: Declarative, constraint-focused, describes **WHAT** to build

**Core Philosophy**:
1. **No code snippets** - Convert to descriptions
2. **Keep constraints** - "positive values", "required field", "max 100 chars"
3. **Remove implementation** - No "use try/except" or "call func()"
4. **Preserve intent** - Why this feature exists, what problem it solves

**Two Appspec Archetypes**:
- **Product-focused** (UI/UX heavy): User flows, design systems, interactions
  - Example: [Claude.ai clone](../../docs/og_appspec.txt)
- **System-focused** (Algorithm heavy): State machines, edge cases, data flows
  - Example: [Alpha Arena](../../docs/app_spec.txt)

See `references/appspec-styles.md` for detailed comparison.

## Core Transformation Principles

| # | Principle | Example |
|---|-----------|---------|
| 1 | Code → Descriptions | `def validate(x): assert x > 0` → "Must be positive value" |
| 2 | Models → Schema | `class User(BaseModel):` → `<users>` table with fields |
| 3 | Tests → Criteria | `assert len(df) == 50` → "Returns exactly 50 records" |
| 4 | Functions → Features | `async def fetch()` → "Fetch data with retry logic" |
| 5 | Epics → Steps | Task list → `<implementation_steps>` with milestones |
| 6 | Comments → Constraints | `# Must be UTC` → "All timestamps in UTC format" |
| 7 | Imports → Tech Stack | `from fastapi import` → `<framework>FastAPI</framework>` |

## How to Execute

**Run the multi-agent workflow**: `workflows/convert-prd.md`

### Workflow Overview (5 Phases)

```
1. SCAN (Haiku agent)
   └─ Classify project type, identify PRD sections

2. TRANSFORM (3-5 parallel Sonnet agents)
   ├─ Agent A: Extract metadata + tech stack
   ├─ Agent B: Transform data models → schema
   ├─ Agent C: Extract features + API surface
   ├─ Agent D: Convert implementation plan → steps
   └─ Agent E: Derive success criteria from tests

3. VALIDATE (Parallel Haiku agents)
   └─ Score each section 0-100 for quality/completeness

4. REFINE (Sonnet agent)
   └─ Synthesize sections, ensure coherence, fix gaps

5. OUTPUT
   └─ Write app_spec.txt with validation report
```

### Quality Scoring (Used in Phase 3)

Each section scored 0-100:
- **0-25**: Incomplete, missing critical info, has code snippets
- **26-50**: Partial, lacks constraints or context
- **51-75**: Good, mostly declarative, minor gaps
- **76-100**: Excellent, complete, clear, agent-ready

**Threshold**: Sections scoring <60 trigger refinement loop.

## Expected Output Structure

```xml
<project_specification>
  <project_name>Name (no version)</project_name>
  <version>X.Y.Z</version>
  <overview>3-5 sentence summary</overview>

  <technology_stack>
    <language>Primary language</language>
    <core_dependencies>
      <dependency name="lib">Purpose</dependency>
    </core_dependencies>
  </technology_stack>

  <prerequisites>
    <existing_assets>What already exists</existing_assets>
    <constraints>Limitations and rules</constraints>
  </prerequisites>

  <core_features>
    <feature_group>
      - Declarative feature descriptions
      - With constraints and requirements
    </feature_group>
  </core_features>

  <database_schema>
    <table_name>
      - field: type (constraint)
      - related_id: foreign key (references table)
    </table_name>
  </database_schema>

  <api_endpoints_summary>
    <group>
      - VERB /path/to/endpoint
        Description of what it does
    </group>
  </api_endpoints_summary>

  <implementation_steps>
    <step number="1">
      <title>Milestone name</title>
      <deliverable>What is done</deliverable>
      <tasks>
        - Concrete actionable tasks
      </tasks>
    </step>
  </implementation_steps>

  <success_criteria>
    <functionality>
      - Measurable outcomes
    </functionality>
    <technical_quality>
      - Code quality metrics
    </technical_quality>
  </success_criteria>

  <directory_structure>
    Annotated tree showing where code lives
  </directory_structure>
</project_specification>
```

## Common Transformation Patterns

### Pydantic → Schema

**PRD**:
```python
class Order(BaseModel):
    id: str = Field(default_factory=uuid4)
    amount: float = Field(gt=0)
    status: Literal["pending", "filled", "cancelled"]
```

**Appspec**:
```xml
<order>
  - id: string (UUID, auto-generated)
  - amount: float (positive)
  - status: enum ["pending", "filled", "cancelled"]
</order>
```

### Try/Except → Error Handling

**PRD**:
```python
try:
    result = api.fetch()
except NetworkError:
    retry_with_backoff()
```

**Appspec**:
```xml
<error_handling>
  - Network errors: Retry with exponential backoff
  - API errors: Log and return descriptive message
</error_handling>
```

### Test → Criteria

**PRD**:
```python
def test_fills_on_touch():
    order = place_order(entry=100)
    candle = Candle(low=99, high=101)
    assert order.status == "filled"
```

**Appspec**:
```xml
<success_criteria>
  <functionality>
    - Order fills when candle touches entry price
    - Fill simulation accurate for limit orders
  </functionality>
</success_criteria>
```

## Validation Checklist

Before finalizing app_spec.txt:

- [ ] No code snippets remain (all converted to descriptions)
- [ ] All constraints preserved ("positive", "required", "max N")
- [ ] Clear project archetype (product vs system vs library)
- [ ] Sections match archetype (UI flows for product, edge cases for system)
- [ ] Implementation steps are actionable (not just "write tests")
- [ ] Success criteria are measurable (not vague "good UX")
- [ ] XML is well-formed (matching tags, valid structure)
- [ ] Tech stack includes all major dependencies
- [ ] Database schema shows relationships (foreign keys)

## Key Anti-Patterns to Avoid

❌ **Including code snippets**
```xml
<bad>
  Use this function:
  ```python
  def foo(): ...
  ```
</bad>
```

✅ **Describe behavior**
```xml
<good>
  - Function validates input before processing
  - Returns error for invalid format
</good>
```

❌ **Prescribing implementation**
```xml
<bad>
  Use FastAPI decorators with async/await pattern
</bad>
```

✅ **State requirements**
```xml
<good>
  - REST API with async request handling
  - Support concurrent requests efficiently
</good>
```

❌ **Vague success criteria**
```xml
<bad>
  - Application works well
  - Good user experience
</bad>
```

✅ **Measurable outcomes**
```xml
<good>
  - All API endpoints return within 200ms
  - Form validation provides instant feedback
</good>
```

## Full Workflow

For complete agent-centric workflow with parallel agents and validation:
→ `workflows/convert-prd.md`

For appspec style examples and when to use each:
→ `references/appspec-styles.md`

For annotated PRD examples showing good vs. problematic structure:
→ `references/prd-examples.md`
