---
name: router-patterns
description: Pattern library for router skill with detailed routing rules and heuristics
type: documentation
version: 1.0.0
created: 2025-11-05T10:23:50Z
lastmodified: 2025-11-05T10:23:50Z
---

# Router Pattern Library

<context>
This document contains the comprehensive pattern library for the router skill, including detailed routing rules, keyword mappings, context heuristics, and edge case handling patterns.
</context>

## Pattern Matching Categories

### Action-Based Patterns

<batch>
<item n="1" action="fix">
#### Fix Patterns

**Primary Keywords**: fix, resolve, solve, repair, debug, correct, address, handle

**Routing Logic**:
```yaml
keywords:
  - "fix types" → /fix:types
  - "fix tests" → /fix:tests
  - "fix lint" → /fix:lint
  - "fix all|everything" → /fix-all
  - "fix errors" → Context check (what type of errors?)

context_checks:
  has_type_errors: → /fix:types (high confidence)
  has_test_failures: → /fix:tests (high confidence)
  has_lint_warnings: → /fix:lint (high confidence)
  has_multiple_issues: → /fix-all (high confidence)
  no_diagnostics_found: → Clarification needed (low confidence)

confidence_factors:
  + Specific error type mentioned (types, tests, lint): +0.3
  + Diagnostics confirm issue exists: +0.4
  + Clear scope (file path mentioned): +0.2
  - Generic "fix" without context: -0.3
```

**Examples**:
- "fix my typescript errors" → /fix:types (high)
- "fix failing tests in auth module" → /fix:tests (high)
- "fix everything before I commit" → /fix-all (high)
- "fix the bug" → Clarification needed (low)
</item>

<item n="2" action="review">
#### Review Patterns

**Primary Keywords**: review, audit, check, analyze, inspect, examine, look at, evaluate

**Routing Logic**:
```yaml
keywords:
  - "review code" → /review-orchestrator
  - "review security" → /reviewer:security
  - "review tests|testing" → /reviewer:testing
  - "review performance|quality" → /reviewer:quality
  - "review ui|design" → /reviewer:design
  - "review readability" → /reviewer:readability
  - "review pr|pull request" → /reviewer:ofri

context_checks:
  git_modified_files > 3: → /review-orchestrator (comprehensive review)
  security_keywords_present: → /reviewer:security
  auth_files_modified: → /reviewer:security
  ui_files_modified: → /reviewer:design
  test_files_modified: → /reviewer:testing

confidence_factors:
  + Specific review type mentioned: +0.4
  + Relevant files in context: +0.3
  + Before commit/merge keyword: +0.2
  - No modified files: -0.2
```

**Examples**:
- "review my changes before merge" → /review-orchestrator (high)
- "security audit for auth module" → /reviewer:security (high)
- "check test coverage" → /reviewer:testing (high)
- "review this" → medium confidence (use context)
</item>

<item n="3" action="document">
#### Documentation Patterns

**Primary Keywords**: document, write docs, add comments, explain, describe, jsdoc

**Routing Logic**:
```yaml
keywords:
  - "document code|api|functions" → /docs:general
  - "jsdoc" → jsdoc skill
  - "organize docs|structure documentation" → /docs:diataxis
  - "add comments" → jsdoc skill
  - "write readme" → /docs:general

context_checks:
  has_undocumented_functions: → /docs:general
  needs_jsdoc_format: → jsdoc skill
  lacks_documentation_structure: → /docs:diataxis
  specific_file_mentioned: → /docs:general {file}

confidence_factors:
  + Specific file/module mentioned: +0.3
  + Documentation type specified: +0.3
  + New code added recently: +0.2
  - Project already well-documented: -0.1
```

**Examples**:
- "document my authentication service" → /docs:general (high)
- "add jsdoc comments to utils" → jsdoc skill (high)
- "organize project documentation" → /docs:diataxis (high)
</item>

<item n="4" action="test">
#### Testing Patterns

**Primary Keywords**: test, verify, validate, check functionality, e2e, unit test

**Routing Logic**:
```yaml
keywords:
  - "test in browser|website" → playwright-skill (likely manual)
  - "write tests" → ts-coder agent or /create-tests
  - "test coverage|strategy" → /reviewer:testing
  - "e2e test" → playwright-skill or ui-engineer agent
  - "unit test" → ts-coder agent
  - "fix tests" → /fix:tests

ambiguity_resolution:
  "test X":
    - Manual testing? → playwright-skill
    - Write tests? → ts-coder agent
    - Review tests? → /reviewer:testing
    → Clarification needed

context_checks:
  has_test_failures: → /fix:tests (high)
  no_tests_exist: → ts-coder agent (write tests)
  has_tests_low_coverage: → /reviewer:testing
  browser_keywords_present: → playwright-skill

confidence_factors:
  + Clear test type (unit, e2e, manual): +0.4
  + Action clear (write vs run vs fix): +0.3
  + File path specified: +0.2
  - Ambiguous "test" only: -0.4
```

**Examples**:
- "test the login flow in browser" → playwright-skill (medium-high)
- "write unit tests for auth service" → ts-coder agent (high)
- "review test coverage" → /reviewer:testing (high)
- "test my website" → Clarification needed (low)
</item>

<item n="5" action="build">
#### Build/Create Patterns

**Primary Keywords**: build, create, implement, develop, add, write, make

**Routing Logic**:
```yaml
domain_routing:
  react|component|ui → ui-engineer agent
  typescript|function|class → ts-coder agent
  ai|ml|model → ai-engineer agent
  deployment|infrastructure → deployment-engineer agent
  test → ts-coder agent or /create-tests
  documentation → /docs:general

context_checks:
  file_type_tsx: → ui-engineer agent
  file_type_ts: → ts-coder agent
  ai_keywords_present: → ai-engineer agent
  infra_files_present: → deployment-engineer agent

confidence_factors:
  + Domain clearly specified: +0.4
  + Component/feature name given: +0.3
  + File type matches domain: +0.2
  - Generic "build" without context: -0.3
```

**Examples**:
- "build a dashboard component" → ui-engineer agent (high)
- "create authentication service" → ts-coder agent (high)
- "implement AI chat feature" → ai-engineer agent (high)
- "add a new feature" → Clarification needed (low)
</item>

<item n="6" action="explore">
#### Exploration Patterns

**Primary Keywords**: explore, understand, navigate, learn, analyze structure, what does, how does, explain codebase

**Routing Logic**:
```yaml
keywords:
  - "explore codebase|project" → Explore agent (medium)
  - "understand X" → Explore agent (quick for specific, thorough for general)
  - "how does X work" → Explore agent (medium)
  - "explain architecture" → architecture-patterns skill or Explore agent
  - "new to project" → Explore agent (thorough)

thoroughness_selection:
  specific_file_or_function: → quick
  module_or_feature: → medium
  entire_codebase: → thorough
  architecture_understanding: → thorough

confidence_factors:
  + Clear exploration target: +0.3
  + Learning/understanding keywords: +0.4
  + New contributor context: +0.2
```

**Examples**:
- "explore the authentication module" → Explore agent (medium, high)
- "I'm new to this project, help me understand it" → Explore agent (thorough, high)
- "how does the payment flow work" → Explore agent (medium, high)
</item>

<item n="7" action="plan">
#### Planning Patterns

**Primary Keywords**: plan, design, strategy, architecture, approach, brainstorm, roadmap

**Routing Logic**:
```yaml
keywords:
  - "plan feature" → /planning:feature
  - "brainstorm" → /planning:brainstorm
  - "create proposal" → /planning:proposal
  - "write prd" → /planning:prd
  - "architecture" → architecture-patterns skill or strategic-planning agent

context_checks:
  feature_keyword_present: → /planning:feature
  needs_prd: → /planning:prd
  needs_structure_guidance: → architecture-patterns skill
  complex_multi_module: → strategic-planning agent

confidence_factors:
  + Planning stage clear (brainstorm, proposal, prd): +0.4
  + Feature scope defined: +0.3
  + Architecture keywords: +0.3
```

**Examples**:
- "plan a new authentication feature" → /planning:feature (high)
- "brainstorm dashboard improvements" → /planning:brainstorm (high)
- "how should I structure my domain models" → architecture-patterns skill (high)
</item>

<item n="8" action="commit">
#### Git Commit Patterns

**Primary Keywords**: commit, save changes, git commit, commit message

**Routing Logic**:
```yaml
keywords:
  - "commit" → /git:commit
  - "save changes" → /git:commit
  - "stash" → /git:stash

pre_checks:
  has_type_errors: → Suggest /fix:types first (warning)
  has_test_failures: → Suggest /fix:tests first (warning)
  has_lint_warnings: → Suggest /fix:lint first (warning)
  all_clean: → /git:commit (high confidence)

confidence_factors:
  + Clean diagnostics: +0.4
  + Modified files present: +0.3
  + Explicit commit intent: +0.3
  - Blocking issues exist: -0.3
```

**Examples**:
- "commit my changes" → /git:commit (high if clean, medium if issues)
- "save my work with a good message" → /git:commit (high)
- "commit before I switch branches" → Check for issues, then /git:commit
</item>

<item n="9" action="deploy">
#### Deployment Patterns

**Primary Keywords**: deploy, ship, release, ci/cd, docker, kubernetes, infrastructure, pipeline

**Routing Logic**:
```yaml
keywords:
  - "deploy" → deployment-engineer agent
  - "setup ci/cd" → deployment-engineer agent
  - "docker|kubernetes" → deployment-engineer agent
  - "infrastructure" → deployment-engineer agent

confidence_factors:
  + Deployment keywords clear: +0.5
  + Infrastructure files present: +0.3
  + Deploy intent explicit: +0.2
```

**Examples**:
- "deploy my app to production" → deployment-engineer agent (high)
- "setup ci/cd pipeline" → deployment-engineer agent (high)
- "configure docker container" → deployment-engineer agent (high)
</item>

<item n="10" action="optimize">
#### Optimization Patterns

**Primary Keywords**: optimize, improve, performance, faster, efficient, refactor, slow

**Routing Logic**:
```yaml
keywords:
  - "optimize performance|speed" → /reviewer:quality
  - "improve code quality" → senior-code-reviewer agent
  - "refactor" → senior-code-reviewer agent or ts-coder agent
  - "make faster" → /reviewer:quality

domain_specific:
  react_performance: → ui-engineer agent
  general_performance: → /reviewer:quality
  code_quality: → senior-code-reviewer agent

confidence_factors:
  + Specific optimization type: +0.3
  + Performance metrics mentioned: +0.3
  + Domain specified: +0.2
  - Generic "make better": -0.3
```

**Examples**:
- "optimize my React component performance" → ui-engineer agent (medium-high)
- "app is slow, make it faster" → /reviewer:quality (medium)
- "refactor authentication logic" → senior-code-reviewer agent (high)
</item>
</batch>

## Domain-Based Patterns

### Technology Domain Routing

<batch>
<item n="1" domain="typescript">
**Keywords**: typescript, types, ts, type error, interface, generic, type definition

**Routing**:
- Error fixing: /fix:types
- Code writing: ts-coder agent
- Architecture: architecture-patterns skill
- Review: senior-code-reviewer agent

**Confidence Boosters**:
- Type error count visible: +0.4
- Specific type issue mentioned: +0.3
- File path with .ts extension: +0.2
</item>

<item n="2" domain="react">
**Keywords**: react, component, jsx, tsx, hook, state, props, useState, useEffect

**Routing**:
- Component creation: ui-engineer agent
- Performance: ui-engineer agent
- Testing: playwright-skill or /reviewer:e2e
- Review: /reviewer:design

**Confidence Boosters**:
- Component name mentioned: +0.3
- UI behavior described: +0.3
- File path with .tsx extension: +0.3
</item>

<item n="3" domain="security">
**Keywords**: security, auth, authentication, authorization, vulnerability, xss, sql injection, cors, jwt

**Routing**:
- Review/audit: /reviewer:security
- Implementation: ts-coder agent (with security focus)
- Compliance: legal-compliance-checker agent

**Confidence Boosters**:
- Security concern explicit: +0.5
- Auth files involved: +0.3
- Vulnerability keywords: +0.4
</item>

<item n="4" domain="testing">
**Keywords**: test, spec, e2e, integration, unit test, jest, vitest, playwright, coverage

**Routing**:
- Fix tests: /fix:tests
- Write tests: ts-coder agent or /create-tests
- E2E browser: playwright-skill
- Review strategy: /reviewer:testing

**Confidence Boosters**:
- Test type specified: +0.4
- Test file path mentioned: +0.3
- Coverage percentage mentioned: +0.2
</item>

<item n="5" domain="documentation">
**Keywords**: docs, documentation, readme, jsdoc, comments, guide, tutorial, api docs

**Routing**:
- General docs: /docs:general
- Structure: /docs:diataxis
- JSDoc: jsdoc skill
- Advanced: intelligent-documentation agent

**Confidence Boosters**:
- Documentation type clear: +0.3
- Target files specified: +0.3
- Format mentioned (JSDoc, markdown): +0.2
</item>

<item n="6" domain="architecture">
**Keywords**: architecture, design pattern, structure, ddd, clean architecture, hexagonal, solid, separation of concerns

**Routing**:
- Guidance: architecture-patterns skill
- Planning: strategic-planning agent
- Review: senior-code-reviewer agent

**Confidence Boosters**:
- Pattern name mentioned: +0.4
- Architecture question explicit: +0.4
- Design problem described: +0.3
</item>

<item n="7" domain="browser">
**Keywords**: browser, playwright, e2e, screenshot, automation, click, form, navigate, selenium

**Routing**:
- Manual testing: playwright-skill
- Test infrastructure: ui-engineer agent
- Test review: /reviewer:e2e

**Confidence Boosters**:
- Browser action mentioned: +0.4
- Screenshot requested: +0.5
- Playwright mentioned: +0.5
</item>

<item n="8" domain="ai">
**Keywords**: ai, ml, machine learning, model, llm, openai, anthropic, gpt, embeddings, rag

**Routing**:
- Implementation: ai-engineer agent
- General tasks: general-purpose agent

**Confidence Boosters**:
- AI feature clearly described: +0.5
- Model type mentioned: +0.3
- AI service mentioned: +0.3
</item>
</batch>

## Context-Aware Routing Patterns

### Git Status Patterns

```yaml
clean_working_directory:
  status: "nothing to commit, working tree clean"
  enables:
    - /git:commit (no warnings)
    - branch operations (safe)
    - deployment operations (safe)

modified_files_present:
  status: "Changes not staged for commit"
  actions:
    - Increase commit suggestion priority
    - Check for diagnostics before commit
    - Consider stash for branch switch

uncommitted_changes:
  status: "Changes to be committed"
  actions:
    - Enable /git:commit immediately
    - High confidence for commit operations
    - Warning for destructive operations

ahead_of_remote:
  status: "Your branch is ahead of origin"
  suggestions:
    - After commit: suggest push
    - Before major operations: warn about unpushed changes

merge_conflicts:
  status: "both modified"
  actions:
    - Route to Explore agent for conflict analysis
    - Suggest conflict resolution tools
    - Block automated commits
```

### Diagnostic Patterns

```yaml
type_errors_present:
  count: "> 0"
  actions:
    - Route "fix" to /fix:types
    - Warn before commit operations
    - Block "review" until fixed (suggest fixing first)
    - Priority: High (blocking)

test_failures_present:
  count: "> 0"
  actions:
    - Route "fix" to /fix:tests
    - Warn before commit/deploy
    - Block deployment operations
    - Priority: High (blocking)

lint_warnings_present:
  count: "> 0"
  actions:
    - Route "fix" to /fix:lint
    - Allow commit but suggest fixing
    - Priority: Medium (non-blocking)

all_diagnostics_clean:
  type_errors: 0
  test_failures: 0
  lint_warnings: 0
  actions:
    - Enable all operations without warnings
    - High confidence for commits
    - Green light for deployment
    - Suggest review as next step
```

### File Type Patterns

```yaml
tsx_files_dominant:
  pattern: "*.tsx"
  percentage: "> 50%"
  default_routing:
    - build/create → ui-engineer agent
    - review → /reviewer:design
    - test → playwright-skill

ts_files_dominant:
  pattern: "*.ts"
  percentage: "> 50%"
  default_routing:
    - build/create → ts-coder agent
    - fix → /fix:types
    - review → senior-code-reviewer agent

test_files_present:
  pattern: "*.test.ts, *.spec.ts"
  default_routing:
    - fix → /fix:tests
    - review → /reviewer:testing
    - improve → /reviewer:testing

config_files_modified:
  pattern: "*.config.js, package.json, tsconfig.json"
  actions:
    - Careful review suggested
    - Deployment considerations
    - Build verification needed
```

## Multi-Step Orchestration Patterns

### Sequential Patterns

```yaml
fix_then_commit:
  pattern: "fix ... (and|then) commit"
  execution:
    - step1: /fix-all (blocking)
    - step2: /git:commit (after step1)
  reasoning: "Fixes must complete before commit"

plan_then_implement:
  pattern: "plan ... (and|then) (build|implement|create)"
  execution:
    - step1: /planning:feature (blocking)
    - step2: Domain-specific agent (ui-engineer, ts-coder)
  reasoning: "Planning informs implementation"

implement_then_test:
  pattern: "(build|create) ... (and|then) test"
  execution:
    - step1: Domain-specific agent (blocking)
    - step2: ts-coder agent or playwright-skill
  reasoning: "Implementation must exist before testing"

test_then_deploy:
  pattern: "test ... (and|then) deploy"
  execution:
    - step1: /fix:tests (blocking)
    - step2: deployment-engineer agent (after tests pass)
  reasoning: "Tests must pass before deployment"

review_then_commit:
  pattern: "review ... (and|then) commit"
  execution:
    - step1: /review-orchestrator (blocking)
    - step2: Address findings (if any)
    - step3: /git:commit
  reasoning: "Review findings should be addressed"
```

### Parallel Patterns

```yaml
fix_all_quality:
  pattern: "fix (everything|all)"
  execution:
    parallel: ["/fix:types", "/fix:tests", "/fix:lint"]
  reasoning: "Independent quality checks can run concurrently"

multiple_reviews:
  pattern: "review security and performance"
  execution:
    parallel: ["/reviewer:security", "/reviewer:quality"]
  reasoning: "Different review aspects are independent"

implement_multiple_components:
  pattern: "build X and Y"
  execution:
    parallel: ["ui-engineer agent for X", "ui-engineer agent for Y"]
  reasoning: "Independent components can be built concurrently"
```

### Hybrid Patterns (Sequential + Parallel)

```yaml
comprehensive_quality_workflow:
  pattern: "fix, review, and commit"
  execution:
    - stage1_parallel: ["/fix:types", "/fix:tests", "/fix:lint"]
    - stage2_sequential: "/review-orchestrator"
    - stage3_sequential: "/git:commit"
  reasoning: "Fixes run in parallel, then review clean code, then commit"

feature_development_workflow:
  pattern: "plan, build, test, and deploy feature"
  execution:
    - stage1: "/planning:feature"
    - stage2_parallel: ["ui-engineer agent", "ts-coder agent"]
    - stage3: "/fix-all"
    - stage4: "/review-orchestrator"
    - stage5: "deployment-engineer agent"
  reasoning: "Plan first, implement in parallel, then quality/review, then deploy"
```

## Urgency-Based Routing Patterns

```yaml
critical_urgency:
  keywords: ["URGENT", "CRITICAL", "BROKEN", "PRODUCTION", "DOWN", "NOW", "ASAP"]
  actions:
    - Skip normal confidence checks
    - Route to fastest parallel fix: ["/fix:types", "/fix:tests"]
    - Prioritize fixes over reviews
    - Enable fast-path commit after fixes
    - Suggest immediate deployment if applicable
  communication: "🚨 Emergency routing activated"

high_urgency:
  keywords: ["blocking", "blocker", "urgent", "immediate", "priority"]
  actions:
    - Reduce clarification threshold (proceed with medium confidence)
    - Prefer commands over agents (faster execution)
    - Parallel execution preferred
    - Skip learning tips (focus on execution)
  communication: "⚡ Priority routing"

normal_urgency:
  default: true
  actions:
    - Standard confidence thresholds
    - Include learning tips
    - Suggest alternatives
    - Educational communication

low_urgency:
  keywords: ["when you can", "eventually", "nice to have", "explore", "learn"]
  actions:
    - Can ask more clarifying questions
    - Suggest comprehensive approaches
    - Offer educational alternatives
    - Include detailed explanations
  communication: "💡 Thoughtful routing"
```

## Confidence Adjustment Patterns

### Confidence Boosters

```yaml
explicit_tool_mention:
  pattern: User mentions specific tool/command name
  adjustment: +0.5
  example: "use the playwright skill to test" → playwright-skill (high)

exact_keyword_match:
  pattern: Request keywords exactly match routing pattern
  adjustment: +0.4
  example: "fix typescript errors" → /fix:types (high)

context_confirms_intent:
  pattern: Project context aligns with intent
  adjustment: +0.3
  example: "fix types" + 5 type errors found → /fix:types (very high)

file_path_specified:
  pattern: User provides specific file path
  adjustment: +0.2
  example: "document src/auth.ts" → /docs:general (medium-high)

domain_clear:
  pattern: Domain keywords strongly present
  adjustment: +0.3
  example: "build react component with hooks" → ui-engineer (high)
```

### Confidence Reducers

```yaml
generic_request:
  pattern: "fix", "help", "do this", "make better"
  adjustment: -0.3
  action: Gather context or ask clarification

ambiguous_action:
  pattern: Multiple interpretations possible
  adjustment: -0.4
  example: "test my website" (manual? write tests? review?)
  action: Ask clarifying question

conflicting_signals:
  pattern: Request has contradictory elements
  adjustment: -0.3
  example: "quickly do a thorough review"
  action: Prioritize based on context

no_context_available:
  pattern: Cannot gather git/diagnostic context
  adjustment: -0.2
  action: Proceed with lower confidence, explain assumptions

unknown_domain:
  pattern: Request outside known domains
  adjustment: -0.5
  action: Route to general-purpose agent with warning
```

## Error Recovery Patterns

```yaml
tool_not_found:
  error: "Requested tool/command does not exist"
  actions:
    - Fuzzy match: Check Levenshtein distance < 3
    - Suggest correction: "Did you mean X?"
    - Offer alternatives: "Similar tools available: ..."
    - Provide help: "Available tools in this category: ..."

execution_failed:
  error: "Tool execution returned error"
  actions:
    - Analyze error message
    - Suggest alternative approach
    - Offer to try fallback tool
    - Provide debugging guidance

timeout:
  error: "Tool execution exceeded time limit"
  actions:
    - Check if partial results available
    - Suggest scoping down
    - Offer to retry with smaller scope
    - Switch to alternative tool

permission_denied:
  error: "Insufficient permissions for operation"
  actions:
    - Explain permission requirement
    - Suggest permission grant steps
    - Offer alternative approach without permissions
    - Document for user resolution
```

## Learning Patterns

```yaml
successful_routing:
  signal: User proceeds without correction
  actions:
    - Increment pattern success count
    - Strengthen keyword associations
    - Cache context + intent + route for future

user_correction:
  signal: User manually corrects routing decision
  actions:
    - Log: intent + context + wrong_route + correct_route
    - Analyze: Why was routing incorrect?
    - Adjust: Confidence thresholds for similar patterns
    - Document: Add to confused scenarios list

repeated_clarification:
  signal: Same request type requires clarification multiple times
  actions:
    - Review pattern matching rules
    - Add disambiguation rules
    - Improve context gathering
    - Update keyword mappings

high_override_rate:
  signal: >20% of routing decisions corrected by user
  actions:
    - Full pattern review needed
    - Confidence calibration adjustment
    - User preference learning
    - Documentation improvement
```

---

**Version**: 1.0.0
**Last Modified**: 2025-11-05T10:23:50Z
