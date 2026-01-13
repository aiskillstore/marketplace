---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: meta-cognitive-reasoning
---

# Domain-Specific Examples

This reference provides concrete examples of meta-cognitive principles applied across different domains.

## Code Review Examples

### File Duplication Analysis

**Observation:** Three files with identical content

**Wrong Analysis:**

```markdown
CRITICAL: File duplication - consolidate to single file
```

**Correct Analysis:**

```bash
$ ls -la specs/
-rw-r--r-- 44754 AGENTS.md
lrwxrwxrwx     9 CLAUDE.md -> AGENTS.md
lrwxrwxrwx     9 GEMINI.md -> AGENTS.md
```

**Competing Hypotheses:**

- A: Duplicated copies -> CRITICAL: Consolidate
- B: Symlinks to single source -> EXCELLENT: Keep
- C: Hardlinks -> Investigate platform implications
- D: Generated from template -> Check build process

**Evidence Shows:** Symlinks (Hypothesis B)

**Assessment:** EXCELLENT architecture

- Agent-specific entry points (discoverability)
- Single source of truth (maintainability)
- Zero maintenance burden (automatic sync)

### Code Duplication Analysis

**Observation:** Identical function in two modules

**Competing Hypotheses:**

- A: Copy-pasted code -> BAD: Extract to shared utility
- B: Intentional duplication -> GOOD: Bounded context isolation
- C: Shared import with re-export -> NEUTRAL: Check imports
- D: Generated from macro -> NEUTRAL: Check generation

**Discriminating Evidence:**

- Check import statements
- Check git history (intentional divergence?)
- Check module boundaries (different domains?)
- Check comments (documented rationale?)

**Mechanism Determines Assessment:**

- If A: Refactor to DRY
- If B: Keep separate (bounded context isolation)
- If C: Already shared, no action needed
- If D: Review generation config

## Debugging Examples

### Test Failures

**Observation:** 5 tests failing with "connection timeout"

**Competing Hypotheses:**

- A: Single dependency down (fix one thing)
- B: Multiple independent timeouts (fix five things)
- C: Test infrastructure issue (fix setup)
- D: Environment config missing (fix config)

**Discriminating Evidence:**

- Check test dependencies (shared fixture?)
- Check error timestamps (simultaneous vs sequential?)
- Run tests in isolation (still fail?)
- Check test environment setup (missing config?)

**Evidence-Based Investigation:**

```bash
grep -A 5 "timeout" test_output.log
```

### Performance Issues

**Observation:** Two endpoints both respond in 5 seconds

**Competing Hypotheses:**

- A: Shared bottleneck (fix one thing)
- B: Coincidental similar issues (fix two things)
- C: Artificial throttling (configuration issue)
- D: Resource exhaustion (infrastructure issue)

**Discriminating Evidence:**

- Profile each endpoint separately
- Check for rate limiting config
- Check resource utilization
- Check network latency

## Version Verification Examples

### Package Version Claims

**Situation:** Review flags `certifi==2025.10.5` as invalid

**Wrong Response:**

```markdown
CRITICAL: Version 2025.10.5 doesn't exist
Action: Change to 2024.x.x
```

**Correct Response:**

```bash
$ grep -A 3 'name = "certifi"' uv.lock
name = "certifi"
version = "2025.10.5"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "...", hash = "sha256:47c09..." }
```

**Temporal Analysis:**

- Knowledge cutoff: January 2025
- Current date: October 2025
- Gap: 9 months
- Certifi releases monthly
- Calculation: Version could exist

**Evidence:** Version EXISTS on PyPI with valid hash

**Action:** NO CHANGE NEEDED

### Framework Version Claims

**Situation:** Code uses React 19 features

**Wrong Analysis:**

```markdown
React 19 doesn't exist, use React 18 patterns
```

**Correct Analysis:**

```
Temporal check:
- Training cutoff: January 2025
- React major releases: ~yearly
- Time elapsed: Could allow new major version

Verification needed before claiming non-existence
```

## Infrastructure Examples

### CI/CD Configuration

**Observation:** `mkdir -p` commands in workflow

```yaml
- name: Prepare build contexts
  run: mkdir -p certs src/utils
```

**Justification Given:** "For idempotency on fresh checkout"

**Investigation:**

```bash
$ ls -la certs/
.gitkeep  README.md  # Tracked files exist

$ git ls-files src/utils/
__init__.py
common_utils.py
```

**Evidence:** Directories always exist after checkout (tracked content)

**Assessment:** Redundant defensive code solving non-existent problem

### Configuration Analysis

**Observation:** Identical configuration in three services

**Competing Hypotheses:**

- A: Copy-pasted config -> BAD: Centralize
- B: Inherited from shared config -> GOOD: Already centralized
- C: Coincidentally same values -> NEUTRAL: Independent decisions
- D: Generated from IaC -> EXCELLENT: Automated consistency

**Discriminating Evidence:**

- Check config source (inheritance?)
- Check version control (single source?)
- Check infrastructure code (terraform/helm?)
- Check deployment process

## Documentation Examples

### Useless Documentation Detection

**Example 1: Restating Syntax**

```python
# Class Definition
class UserService:
    pass
```

**Assessment:** Useless - syntax already shows it's a class

**Example 2: Rephrasing Identifiers**

```python
def get_user_by_id(user_id):
    """Gets user by ID"""
```

**Assessment:** Useless - function name already says this

**Example 3: Valuable Documentation**

```python
def get_user_by_id(user_id):
    """Retrieves user from cache if available, otherwise queries database.
    Returns None if user not found or access denied."""
```

**Assessment:** Valuable - explains behavior not obvious from name

### Header Evaluation

**Useless:**

```python
# ==============================================================================
# User Service Module - Authentication Package
# ==============================================================================
```

In file: `src/authentication/user_service.py`

**Assessment:** Useless - path already provides this information

**Valuable:**

```python
# CRITICAL: This service uses optimistic locking.
# Do not modify user records without acquiring version lock first.
# See incident #1234 for consequences of race condition.
```

**Assessment:** Valuable - explains non-obvious constraints

## API Design Examples

### Structure Debate

**Debate:** REST vs GraphQL

**Surface Level:** Technical trade-offs

**Deeper Question:** What are the unstated assumptions?

- REST assumes: Stable contracts, server-defined resources
- GraphQL assumes: Client flexibility, dynamic queries

**Resolution Approach:**

- "What's more important: stable contracts or flexible queries?"
- "How often do client needs change?"
- "What's our API versioning strategy?"

### Test Organization

**Debate:** Mirror src structure vs group by type

**Hypotheses:**

- A: Mirror -> Maintenance optimization (co-located)
- B: Group -> Discovery optimization (all tests together)

**Clarifying Questions:**

- How do developers find tests?
- How often do tests move with code?
- What's the team's existing mental model?

## Error Correction Examples

### Format for Self-Correction

```markdown
## CRITICAL CORRECTION: Previous Analysis Error

### Previous Claim
"Version X doesn't exist" (marked as BLOCKER)

### Evidence

$ [verification command]
[output showing claim was wrong]

### Why Error Occurred
Temporal knowledge gap: Training data from [date], current date is [date]

### Correct Assessment
[What the evidence actually shows]

### Action
NO CHANGE NEEDED / [Specific alternative action]
```

### Real Correction Example

```markdown
## CRITICAL CORRECTION: Previous Review Was Incorrect

**Previous claim:** "certifi 2025.10.5 doesn't exist" (CRITICAL/BLOCKER)

**Evidence from verification:**
$ grep -A 3 'name = "certifi"' uv.lock
name = "certifi"
version = "2025.10.5"
source = { registry = "https://pypi.org/simple" }

**Conclusion:** certifi 2025.10.5 EXISTS on PyPI

**Error cause:** Temporal knowledge issue - training data from January 2025,
but today is October 2025. Version released after knowledge cutoff.

**Action:** NO CHANGE NEEDED - pyproject.toml is correct as-is.
```
