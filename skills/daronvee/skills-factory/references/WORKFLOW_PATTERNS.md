# Workflow Patterns for Skills

## When to Use Workflows

Workflows provide structure when tasks have multiple steps, decision points, or quality requirements. Use workflows when:

✅ **Use workflows when:**
- Task has 3+ sequential steps
- Quality gates are needed (validation checkpoints)
- Multiple paths exist (conditional logic)
- Iteration is required (feedback loops)
- Users need guidance through complex process

❌ **Skip workflows when:**
- Task is simple single-step action
- Process is already obvious to users
- Overhead of structure outweighs benefit
- Skill is pure knowledge reference (no procedural steps)

## Workflow Pattern Types

### 1. Simple Sequential Workflow

**When to use:** Linear process with clear steps in fixed order

**Structure:**
```markdown
## Workflow

### Step 1: [Action Name]
[Clear instruction]
[Expected outcome]

### Step 2: [Action Name]
[Clear instruction]
[Expected outcome]

### Step 3: [Action Name]
[Clear instruction]
[Expected outcome]
```

**Example: Document Formatting Skill**
```markdown
## Document Formatting Workflow

### Step 1: Load Document
Read the document file you want to format.
**Expected:** Document content loaded into context

### Step 2: Apply Style Rules
Apply formatting rules from references/style-guide.md:
- Headers: Title case
- Lists: Consistent bullets
- Code blocks: Proper syntax highlighting

**Expected:** Document formatted according to style guide

### Step 3: Validate Formatting
Run validation: `bash scripts/validate_format.py [document]`
**Expected:** All checks pass, no formatting errors

### Step 4: Save Formatted Document
Write formatted content back to file.
**Expected:** Document saved with formatting applied
```

**Best Practices:**
- Number steps clearly (1, 2, 3...)
- Start each step with action verb (Load, Apply, Validate, Save)
- Include "Expected outcome" for each step
- Keep 3-7 steps (if more, consider breaking into phases)

---

### 2. Checklist Workflow

**When to use:** Multiple items to complete, order less critical, visual tracking helpful

**Structure:**
```markdown
## Workflow Checklist

Complete all items before proceeding:

- [ ] Item 1 - [Description]
- [ ] Item 2 - [Description]
- [ ] Item 3 - [Description]

**All items complete?** Proceed to [next step]
```

**Example: Pre-Deployment Checklist Skill**
```markdown
## Pre-Deployment Checklist

Complete all checks before deploying:

**Code Quality:**
- [ ] All tests passing (`npm test`)
- [ ] No linting errors (`npm run lint`)
- [ ] Code coverage ≥80% (`npm run coverage`)

**Documentation:**
- [ ] CHANGELOG.md updated with new version
- [ ] README.md reflects new features
- [ ] API documentation generated

**Security:**
- [ ] Dependencies updated (`npm audit`)
- [ ] No secrets in code (check with `git secrets --scan`)
- [ ] Environment variables documented

**Deployment:**
- [ ] Version bumped in package.json
- [ ] Git tag created (`git tag v1.2.3`)
- [ ] Deployment plan reviewed

**All items complete?** Run: `bash scripts/deploy.sh`
```

**Best Practices:**
- Group related items (Code Quality, Documentation, etc.)
- Include validation command where applicable
- Mark truly required vs. optional items
- End with clear "all complete" checkpoint

---

### 3. Conditional Workflow

**When to use:** Different paths based on context, conditions, or user choices

**Structure:**
```markdown
## Workflow

### Step 1: Assess Condition
[How to determine which path]

**If [Condition A]:** → Go to Path A
**If [Condition B]:** → Go to Path B
**If [Condition C]:** → Go to Path C

### Path A: [Scenario Name]
[Steps for this scenario]

### Path B: [Scenario Name]
[Steps for this scenario]

### Path C: [Scenario Name]
[Steps for this scenario]
```

**Example: API Documentation Generator Skill**
```markdown
## Documentation Generation Workflow

### Step 1: Detect API Type

Check codebase to determine API architecture:

**If REST API** (files in `/routes` or `/controllers`): → Go to REST Path
**If GraphQL** (files contain `graphql` or schema definitions): → Go to GraphQL Path
**If gRPC** (`.proto` files present): → Go to gRPC Path

---

### REST Path: Document REST Endpoints

1. Find all route definitions (Express/FastAPI/Django patterns)
2. For each endpoint, extract:
   - Method (GET/POST/PUT/DELETE)
   - Path (`/api/users/:id`)
   - Parameters (path, query, body)
   - Response format
3. Generate OpenAPI/Swagger spec
4. Run validation: `bash scripts/validate_openapi.py`

**Output:** `docs/api/openapi.yaml`

---

### GraphQL Path: Document Schema

1. Locate schema definition files (`schema.graphql` or SDL)
2. For each type/query/mutation, extract:
   - Type name and fields
   - Arguments and return types
   - Descriptions/deprecations
3. Generate GraphQL documentation
4. Validate schema: `bash scripts/validate_graphql_schema.py`

**Output:** `docs/api/graphql-schema.md`

---

### gRPC Path: Document Proto Files

1. Find all `.proto` files
2. For each service, extract:
   - Service name
   - RPC methods
   - Request/response message types
3. Generate protobuf documentation
4. Validate: `protoc --lint_out=. *.proto`

**Output:** `docs/api/grpc-reference.md`
```

**Best Practices:**
- Make condition check explicit and automatable
- Clearly mark path divergence points
- Keep paths independent (don't require jumping between)
- Provide validation for each path

---

### 4. Iterative Workflow (Feedback Loop)

**When to use:** Task requires refinement, quality improvement, or validation cycles

**Structure:**
```markdown
## Iterative Workflow

### Phase 1: Initial Creation
[Create first version]

### Phase 2: Validation
[Check quality/correctness]
**If validation passes:** → Done
**If validation fails:** → Go to Phase 3

### Phase 3: Refinement
[Improve based on feedback]
→ Return to Phase 2 (Validation)

### Exit Criteria
[When to stop iterating]
```

**Example: Test Coverage Improvement Skill**
```markdown
## Test Coverage Improvement Workflow

### Phase 1: Baseline Assessment

1. Run test coverage: `npm run coverage`
2. Identify uncovered files/functions
3. Prioritize by criticality (core business logic first)

**Output:** List of uncovered code sections with priority

---

### Phase 2: Write Tests for Highest Priority Gap

1. Select top uncovered section from list
2. Analyze function/module behavior
3. Write test cases covering:
   - Happy path (expected input/output)
   - Edge cases (boundary conditions)
   - Error cases (invalid input, failures)
4. Run new tests: `npm test [test-file]`

**Expected:** New tests pass

---

### Phase 3: Measure Coverage Improvement

1. Run full coverage again: `npm run coverage`
2. Calculate improvement: `new_coverage - baseline_coverage`
3. Validate coverage increased for target file/function

**If coverage ≥ 80% for target:** ✓ Mark as complete
**If coverage < 80%:** → Identify remaining gaps, return to Phase 2

---

### Phase 4: Repeat for Next Priority

Continue cycle until:
- Overall coverage ≥ 80% (target threshold), OR
- All critical paths covered (business logic, security, data integrity), OR
- Diminishing returns (effort > value)

**Exit Criteria:**
- [ ] Overall coverage ≥ 80%
- [ ] All critical functions covered
- [ ] No P0/P1 gaps remaining
```

**Best Practices:**
- Define clear exit criteria (prevent infinite loops)
- Measure progress quantitatively (coverage %, error reduction)
- Limit iterations (e.g., "max 5 cycles" to prevent endless refinement)
- Show progress: "Iteration 1 of 5, coverage 65% → 72%"

---

## Combining Workflow Patterns

Complex skills may combine multiple patterns:

**Example: Code Review Skill** (Sequential + Checklist + Conditional)

```markdown
## Code Review Workflow

### Step 1: Scan Changeset (Sequential)
Load git diff and identify changed files

### Step 2: Run Automated Checks (Checklist)
- [ ] Tests passing
- [ ] Linting clean
- [ ] No security warnings

### Step 3: Review by File Type (Conditional)

**If JavaScript/TypeScript:** → Check type safety, async patterns
**If Python:** → Check type hints, error handling
**If SQL/DB:** → Check for SQL injection, indexing

### Step 4: Iterative Feedback (Feedback Loop)
- Identify issues
- Suggest improvements
- Re-review after fixes
- Repeat until quality threshold met
```

## Workflow Design Best Practices

### 1. Make Steps Actionable

❌ **Vague:** "Think about the structure"
✅ **Actionable:** "List all top-level components in src/ directory"

❌ **Vague:** "Ensure quality"
✅ **Actionable:** "Run `npm run lint && npm test` and verify all checks pass"

### 2. Include Validation Checkpoints

Every workflow should have quality gates:
```markdown
### Step 3: Validate Configuration
Run: `bash scripts/validate_config.py`

**Expected output:** "✓ All validations passed"

**If errors found:**
- Review error messages
- Fix issues in config file
- Re-run validation
```

### 3. Show Expected Outcomes

Each step should show what success looks like:
```markdown
### Step 2: Generate API Client
Run: `openapi-generator generate -i spec.yaml -g typescript-fetch`

**Expected outcome:**
- Directory `generated/api/` created
- Files: `api.ts`, `models.ts`, `runtime.ts`
- No generation errors in output

**If errors occur:** Check OpenAPI spec validity with `bash scripts/validate_spec.py`
```

### 4. Provide Exit Paths

Don't force users through unnecessary steps:
```markdown
### Step 1: Check if Documentation Exists

Look for `docs/api/` directory.

**If documentation already exists and is current:**
→ Skip to Step 5 (Validation)

**If documentation missing or outdated:**
→ Proceed to Step 2 (Generation)
```

### 5. Design for Observability

Make workflow progress visible:
```markdown
## Progress Tracking

As you complete each step, update status:

- [x] Step 1: Requirements gathered
- [x] Step 2: Architecture designed
- [ ] Step 3: Implementation (IN PROGRESS)
- [ ] Step 4: Testing
- [ ] Step 5: Documentation

**Current Phase:** Implementation (Step 3 of 5)
```

## Common Workflow Anti-Patterns

### ❌ Anti-Pattern 1: Too Many Steps

**Problem:** 15-step workflow overwhelms users

**Solution:** Break into phases or combine related steps
```markdown
❌ BAD:
Step 1: Open file
Step 2: Read content
Step 3: Parse data
Step 4: Validate schema
Step 5: Check types
Step 6: Verify constraints
... (15 steps total)

✅ GOOD:
Phase 1: Load and Parse (Steps 1-3 combined)
Phase 2: Validate (Steps 4-6 combined)
Phase 3: Process
```

### ❌ Anti-Pattern 2: Vague Conditions

**Problem:** "If appropriate, do X" - what makes it appropriate?

**Solution:** Define specific, checkable conditions
```markdown
❌ BAD:
If appropriate, add authentication

✅ GOOD:
If any of these conditions true, add authentication:
- API handles user data
- Endpoints modify database
- External clients will access API
```

### ❌ Anti-Pattern 3: No Validation

**Problem:** Workflow continues even if previous step failed

**Solution:** Add checkpoints with clear pass/fail criteria
```markdown
❌ BAD:
Step 1: Generate code
Step 2: Deploy code

✅ GOOD:
Step 1: Generate code
Step 2: Validate generated code
  Run: `npm run build`
  **Must succeed before proceeding**
Step 3: Deploy code (only if Step 2 passed)
```

### ❌ Anti-Pattern 4: Hidden Dependencies

**Problem:** Step 3 requires output from Step 1 but isn't explicit

**Solution:** Show data flow clearly
```markdown
❌ BAD:
Step 1: Analyze codebase
Step 2: Other task
Step 3: Generate report (uses analysis from Step 1 - not obvious)

✅ GOOD:
Step 1: Analyze codebase
  **Output:** analysis_results.json
Step 2: Generate report
  **Input:** analysis_results.json from Step 1
```

### ❌ Anti-Pattern 5: Infinite Loops

**Problem:** Iterative workflow with no exit criteria

**Solution:** Define clear stopping conditions
```markdown
❌ BAD:
1. Write code
2. Test code
3. If bugs found, go to 1

✅ GOOD:
1. Write code
2. Test code
3. If bugs found AND iterations < 5, fix and repeat
4. Exit when: All tests pass OR 5 iterations reached OR critical bugs only remain
```

## Workflow Testing Checklist

Before finalizing a workflow:

- [ ] Steps are numbered/ordered clearly
- [ ] Each step starts with action verb
- [ ] Expected outcomes defined for each step
- [ ] Validation checkpoints included
- [ ] Conditional branches have clear criteria
- [ ] Exit criteria defined (for iterative workflows)
- [ ] Steps are actionable (not vague)
- [ ] Dependencies between steps are explicit
- [ ] Error handling included ("If X fails, do Y")
- [ ] Workflow tested with realistic use case

## Choosing the Right Pattern

**Decision Tree:**

```
Is task linear with fixed order?
├─ YES → Simple Sequential Workflow
└─ NO
    │
    Does order of items matter?
    ├─ NO → Checklist Workflow
    └─ YES
        │
        Are there different paths based on conditions?
        ├─ YES → Conditional Workflow
        └─ NO
            │
            Does task require refinement/iteration?
            ├─ YES → Iterative Workflow (Feedback Loop)
            └─ NO → Reconsider if workflow is needed
```

**Example Applications:**

| Task Type | Recommended Pattern | Example |
|-----------|---------------------|---------|
| API documentation | Conditional | Different paths for REST/GraphQL/gRPC |
| Code deployment | Checklist | Pre-deploy validation items |
| Test writing | Sequential | Analyze → Write → Validate → Commit |
| Code review | Sequential + Checklist | Steps + quality checks |
| Coverage improvement | Iterative | Test → Measure → Improve → Repeat |
| Configuration setup | Sequential + Conditional | Setup steps + platform-specific branches |

---

**Key Principle:** Workflows should guide users efficiently without overwhelming them. Choose the simplest pattern that provides necessary structure, and combine patterns only when complexity justifies it.
