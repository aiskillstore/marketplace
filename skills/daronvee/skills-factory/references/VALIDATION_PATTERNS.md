# Validation Patterns for Skills

## The Validation Principle

**Core concept:** Skills should include feedback loops that catch errors and guide corrections, not rely on Claude's judgment alone.

**Why validation matters:**
- Prevents propagation of errors to later steps
- Provides clear, actionable feedback
- Reduces user frustration (catch issues early)
- Enables iterative refinement
- Builds user confidence (systematic quality gates)

## Validation Pattern Types

### 1. Script-Based Validation

**When to use:** Objective, automatable checks (syntax, structure, rules)

**Pattern:**
```markdown
### Step N: Validate [Artifact]

Run validation script:
```bash
bash scripts/validate_[artifact].py [path]
```

**Expected output:** "✓ All validations passed"

**If errors found:**
- Review error messages (they include specific line/issue)
- Fix issues in [artifact]
- Re-run validation
- Repeat until all checks pass

**Do not proceed to next step until validation passes.**
```

**Example: YAML Configuration Validation**

*In SKILL.md:*
```markdown
### Step 3: Validate Configuration

Run validation:
```bash
python scripts/validate_config.py config.yaml
```

**Expected:** All checks pass

**If errors:** Fix issues and re-run
```

*In scripts/validate_config.py:*
```python
#!/usr/bin/env python3
import yaml
import sys

def validate_config(config_path):
    """Validate YAML configuration file."""
    errors = []

    # Check 1: Valid YAML syntax
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return False, f"❌ Invalid YAML syntax: {e}"

    # Check 2: Required fields present
    required_fields = ['name', 'version', 'environment']
    for field in required_fields:
        if field not in config:
            errors.append(f"❌ Missing required field: '{field}'")

    # Check 3: Valid environment value
    valid_envs = ['development', 'staging', 'production']
    if config.get('environment') not in valid_envs:
        errors.append(f"❌ Invalid environment. Must be one of: {valid_envs}")

    # Check 4: Version format (semantic versioning)
    version = config.get('version', '')
    if not version or not version.count('.') == 2:
        errors.append(f"❌ Invalid version format: '{version}'. Expected: X.Y.Z")

    # Return results
    if errors:
        return False, "\n".join(errors)
    else:
        return True, "✓ All validations passed"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python validate_config.py <config.yaml>")
        sys.exit(1)

    valid, message = validate_config(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
```

**Best Practices:**
- Return clear pass/fail status (exit code 0 = pass, 1 = fail)
- Provide actionable error messages with specific locations
- Check multiple aspects (syntax, required fields, value constraints)
- Include helpful output even on success ("✓ All checks passed")

---

### 2. Reference-Based Validation

**When to use:** Complex criteria that benefit from examples and explanations

**Pattern:**
```markdown
### Step N: Validate Against Standards

Review [artifact] against quality criteria in [references/standards.md](references/standards.md).

**Check each criterion:**
- [ ] Criterion 1 met
- [ ] Criterion 2 met
- [ ] Criterion 3 met

**If any criterion fails:**
- Review examples in standards.md
- Revise [artifact] to meet criteria
- Re-check all criteria
```

**Example: API Design Validation**

*In SKILL.md:*
```markdown
### Step 4: Validate API Design

Review API specification against [API Design Standards](references/api-standards.md).

**Quality Checklist:**
- [ ] All endpoints follow RESTful conventions (resources as nouns)
- [ ] HTTP methods used correctly (GET=read, POST=create, PUT=update, DELETE=delete)
- [ ] Error responses include standard format (status, message, details)
- [ ] Authentication/authorization documented for each endpoint
- [ ] Rate limiting strategy defined
- [ ] Versioning approach specified (URL, header, or media type)

**If any item unchecked:** Review standards.md for examples and revise design.
```

*In references/api-standards.md:*
```markdown
# API Design Standards

## 1. RESTful Conventions

**Resources as nouns (not verbs):**

✅ GOOD:
- GET /api/users
- POST /api/users
- GET /api/users/123

❌ BAD:
- GET /api/getUsers
- POST /api/createUser
- GET /api/user/get/123

**Collection vs. resource:**
- Collections: plural nouns (`/users`, `/orders`)
- Individual resources: plural + ID (`/users/123`, `/orders/456`)

## 2. HTTP Methods

| Method | Purpose | Request Body | Response |
|--------|---------|--------------|----------|
| GET | Retrieve resource(s) | None | Resource(s) |
| POST | Create new resource | New resource data | Created resource + Location header |
| PUT | Update entire resource | Full resource data | Updated resource |
| PATCH | Partial update | Changed fields only | Updated resource |
| DELETE | Remove resource | None | 204 No Content |

## 3. Error Response Format

**Standard structure:**
```json
{
  "status": 400,
  "error": "Bad Request",
  "message": "Validation failed",
  "details": [
    {"field": "email", "issue": "Invalid email format"},
    {"field": "age", "issue": "Must be 18 or older"}
  ]
}
```

... [more standards with examples]
```

**Best Practices:**
- Include both good and bad examples in reference
- Make criteria checkable (yes/no questions)
- Provide rationale for standards (why this matters)
- Link to external resources (RFCs, industry standards) where applicable

---

### 3. Plan-Validate-Execute Pattern

**When to use:** Complex tasks where planning ahead prevents costly errors

**Pattern:**
```markdown
### Step 1: Plan Approach
[Analyze situation and create plan]

### Step 2: Validate Plan
**Review plan for:**
- Completeness (all requirements addressed?)
- Feasibility (can this actually work?)
- Risk mitigation (what could go wrong?)

**If plan has issues:** Revise plan, re-validate

### Step 3: Execute Plan
[Only after plan validation passes]

### Step 4: Validate Execution
[Check that execution matched plan and meets requirements]
```

**Example: Database Migration Skill**

```markdown
## Database Migration Workflow

### Step 1: Analyze Required Changes

Review code changes to identify database schema modifications needed:
- New tables/columns
- Modified columns (type, constraints)
- Dropped tables/columns
- Index additions/removals

**Output:** List of schema changes required

---

### Step 2: Design Migration Plan

For each change, specify:
- **UP migration:** SQL to apply change
- **DOWN migration:** SQL to rollback change
- **Data migration:** Any data transformations needed
- **Risks:** What could fail? (foreign keys, not-null constraints, etc.)

**Example Plan:**
```sql
-- UP: Add email_verified column
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;

-- DOWN: Remove email_verified column
ALTER TABLE users DROP COLUMN email_verified;

-- Data migration: Mark existing users as verified
UPDATE users SET email_verified = TRUE WHERE created_at < '2024-01-01';

-- Risk: Large table, UPDATE may lock table for extended time
-- Mitigation: Run during low-traffic window, batch updates
```

---

### Step 3: Validate Migration Plan

**Safety Checklist:**
- [ ] DOWN migration fully reverses UP migration
- [ ] Data migrations preserve existing data
- [ ] Foreign key constraints won't break
- [ ] NOT NULL constraints satisfied (defaults or backfill)
- [ ] Performance impact considered (large table updates batched)
- [ ] Rollback plan tested on copy of production DB

**If any item fails:** Revise migration plan, re-validate

**Do not proceed until all safety checks pass.**

---

### Step 4: Execute Migration (Staging First)

1. Apply migration to staging environment
2. Run application tests against staging DB
3. Verify data integrity
4. Test rollback (apply DOWN migration, verify restoration)

**If staging fails:** Fix issues, return to Step 2 (revise plan)

**If staging succeeds:** Proceed to production

---

### Step 5: Execute Migration (Production)

1. Backup production database
2. Apply migration during low-traffic window
3. Monitor for errors
4. Run smoke tests
5. Monitor application metrics

**If errors occur:** Execute rollback (DOWN migration)

---

### Step 6: Validate Production Execution

**Post-Migration Checks:**
- [ ] All expected schema changes applied (verify with `DESCRIBE table`)
- [ ] Data migrations completed successfully
- [ ] Application functioning correctly
- [ ] No unexpected errors in logs
- [ ] Performance within acceptable range

**If validation fails:** Investigate and fix or rollback
```

**Best Practices:**
- Separate planning from execution (catch errors early)
- Make validation criteria explicit and checkable
- Require validation to pass before proceeding
- Include rollback plans (validate those too)
- Test in safe environment before production

---

### 4. Multi-Stage Validation Pattern

**When to use:** Long workflows benefit from validation at multiple checkpoints

**Pattern:**
```markdown
### Stage 1: [Phase Name]
[Work steps]

**Checkpoint 1: Validate Stage 1**
[Specific checks for this stage]
**Must pass before Stage 2**

---

### Stage 2: [Phase Name]
[Work steps]

**Checkpoint 2: Validate Stage 2**
[Specific checks for this stage]
**Must pass before Stage 3**

---

### Final Validation: Complete System
[Comprehensive end-to-end checks]
```

**Example: Full-Stack Feature Development Skill**

```markdown
## Feature Development Workflow

### Stage 1: Backend API

Implement API endpoints for new feature.

**Checkpoint 1: Backend Validation**
```bash
# Unit tests pass
npm run test:backend

# API contract matches spec
npm run validate:api-spec

# No security vulnerabilities
npm audit
```

**All checks must pass before proceeding to Stage 2.**

---

### Stage 2: Frontend UI

Implement UI components for new feature.

**Checkpoint 2: Frontend Validation**
```bash
# Component tests pass
npm run test:frontend

# TypeScript type checking clean
npm run type-check

# No accessibility violations
npm run test:a11y
```

**All checks must pass before proceeding to Stage 3.**

---

### Stage 3: Integration

Connect frontend to backend API.

**Checkpoint 3: Integration Validation**
```bash
# Integration tests pass
npm run test:integration

# E2E tests pass
npm run test:e2e

# Performance benchmarks met
npm run test:perf
```

**All checks must pass before proceeding to Final Validation.**

---

### Final Validation: Complete Feature

**End-to-End Checklist:**
- [ ] All unit tests passing (backend + frontend)
- [ ] All integration tests passing
- [ ] E2E tests covering happy path + edge cases
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Feature flag configured
- [ ] Deployment plan reviewed

**Only deploy when all final validation items complete.**
```

**Best Practices:**
- Validate at logical breakpoints (not after every single step)
- Make checkpoint criteria specific and automatable
- Prevent proceeding past failed checkpoint ("must pass before...")
- Final validation should be comprehensive (catches anything missed earlier)

---

## Validation Anti-Patterns

### ❌ Anti-Pattern 1: Validation by Claude Judgment Only

**Problem:** "Claude, does this look good?"

**Why it fails:**
- Subjective, inconsistent
- Claude may miss issues
- No systematic checking
- Hard to reproduce

**Fix:** Use script-based validation for objective criteria
```markdown
❌ BAD:
"Review the code and make sure it looks correct"

✅ GOOD:
"Run: `npm run lint && npm test`
 All checks must pass."
```

---

### ❌ Anti-Pattern 2: Vague Error Messages

**Problem:** "Validation failed" (no details)

**Why it fails:**
- User doesn't know what to fix
- Trial-and-error debugging
- Frustration and time waste

**Fix:** Provide specific, actionable errors
```python
❌ BAD:
print("Validation failed")

✅ GOOD:
print("❌ Line 23: Missing required field 'email'")
print("❌ Line 45: Invalid date format. Expected: YYYY-MM-DD, got: 12/25/2024")
print("Fix these issues and re-run validation.")
```

---

### ❌ Anti-Pattern 3: Validation Without Correction Loop

**Problem:** Check fails, but workflow continues anyway

**Why it fails:**
- Errors propagate to later steps
- Wastes time on doomed path
- Poor user experience

**Fix:** Require validation to pass before proceeding
```markdown
❌ BAD:
Step 1: Generate code
Step 2: Validate code (but continue even if fails)
Step 3: Deploy code (deploys broken code!)

✅ GOOD:
Step 1: Generate code
Step 2: Validate code
  **If validation fails:**
  - Review errors
  - Fix code
  - Re-run validation
  **Do not proceed to Step 3 until validation passes**
Step 3: Deploy code
```

---

### ❌ Anti-Pattern 4: Validation Too Late

**Problem:** Only validate at the very end (after all work done)

**Why it fails:**
- Errors detected late require extensive rework
- Demotivating to redo large amounts of work
- Inefficient use of time

**Fix:** Validate early and often (multi-stage checkpoints)
```markdown
❌ BAD:
1. Design architecture (1 hour)
2. Implement backend (3 hours)
3. Implement frontend (3 hours)
4. Validate entire system (find architecture flaw - redo everything!)

✅ GOOD:
1. Design architecture
2. **Validate architecture** (catch flaws early)
3. Implement backend
4. **Validate backend** (API contract, tests)
5. Implement frontend
6. **Validate frontend** (components, accessibility)
7. **Final validation** (integration, E2E)
```

---

### ❌ Anti-Pattern 5: No Exit Criteria

**Problem:** "Keep improving until perfect" (never done)

**Why it fails:**
- Infinite refinement
- Diminishing returns
- Never ship

**Fix:** Define "good enough" criteria upfront
```markdown
❌ BAD:
Iterate until code is perfect

✅ GOOD:
Iterate until:
- All tests pass (100% required)
- Code coverage ≥ 80% (sufficient)
- No P0/P1 issues (critical bugs fixed)
- Performance within SLA (fast enough)

**Exit when all criteria met** (don't over-optimize)
```

---

## Designing Effective Validation Scripts

### Structure Template

```python
#!/usr/bin/env python3
"""
Validation script for [artifact name].

Checks:
1. [Check 1 description]
2. [Check 2 description]
3. [Check 3 description]

Usage: python validate_[artifact].py <path>
Exit codes: 0 = all checks passed, 1 = validation failed
"""

import sys

def validate_[aspect_1](data):
    """Check [aspect 1]."""
    errors = []
    # Perform checks
    # Append specific errors with line numbers
    return errors

def validate_[aspect_2](data):
    """Check [aspect 2]."""
    errors = []
    # Perform checks
    return errors

def validate_all(file_path):
    """Run all validation checks."""
    all_errors = []

    # Load data
    try:
        with open(file_path) as f:
            data = f.read()
    except FileNotFoundError:
        return False, f"❌ File not found: {file_path}"

    # Run all checks
    all_errors.extend(validate_aspect_1(data))
    all_errors.extend(validate_aspect_2(data))

    # Return results
    if all_errors:
        error_msg = "\n".join(all_errors)
        return False, f"Validation failed:\n{error_msg}\n\nFix these issues and re-run validation."
    else:
        return True, "✓ All validations passed"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <file_path>")
        sys.exit(1)

    valid, message = validate_all(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
```

### Error Message Guidelines

**Good error messages include:**
1. **Location:** Line number, field name, file path
2. **Issue:** What's wrong (specific)
3. **Expected:** What it should be
4. **Actual:** What was found (if helpful)

**Examples:**

✅ **Good:**
```
❌ Line 23: Missing required field 'email'
❌ Line 45: Invalid date format. Expected: YYYY-MM-DD, got: 12/25/2024
❌ config.yaml: 'environment' must be one of: [development, staging, production], got: dev
```

❌ **Bad:**
```
Error in configuration
Invalid format
Missing field
```

---

## Validation Checklist

Before finalizing a skill with validation:

- [ ] Validation checkpoints at logical stages (not too early, not too late)
- [ ] Scripts provide specific, actionable error messages
- [ ] Exit codes used correctly (0 = pass, 1 = fail)
- [ ] Correction loop included ("fix and re-run")
- [ ] Validation required before proceeding to next stage
- [ ] Reference docs include good/bad examples
- [ ] Exit criteria defined (prevent infinite refinement)
- [ ] Scripts tested with both valid and invalid inputs
- [ ] Error messages include line numbers/locations where applicable
- [ ] Success messages clear and confirmatory

---

**Key Principle:** Validation is not bureaucracy—it's how skills provide systematic quality assurance. Scripts catch objective errors, references guide subjective decisions, and feedback loops enable iterative improvement. Always include validation; never rely on Claude's judgment alone.
