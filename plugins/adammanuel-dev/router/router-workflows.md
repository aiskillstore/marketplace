---
name: router-workflows
description: Pre-defined workflow templates for common development scenarios
type: documentation
version: 1.0.0
created: 2025-11-05T10:23:50Z
lastmodified: 2025-11-05T10:23:50Z
---

# Router Workflow Templates

<context>
This document defines pre-packaged workflow templates that the router can apply to common development scenarios. Each workflow specifies the sequence of tools, execution patterns (parallel/sequential), and transition conditions.
</context>

## Standard Development Workflows

### 1. Feature Development Workflow

```yaml
name: feature_development_full
trigger_keywords: ["build feature", "create feature", "implement feature", "new feature"]
description: Complete feature development from planning to deployment

stages:
  - stage: planning
    name: "Feature Planning & Design"
    tool: /planning:feature
    type: command
    blocking: true
    duration_estimate: "5-10 minutes"
    output: "Feature specification, task breakdown, acceptance criteria"

  - stage: implementation
    name: "Parallel Implementation"
    execution: parallel
    tools:
      - name: ui-engineer
        type: agent
        condition: "if UI components needed"
        focus: "Frontend components, interactions, styling"
      - name: ts-coder
        type: agent
        condition: "if backend logic needed"
        focus: "Business logic, APIs, data handling"
    blocking: true
    duration_estimate: "20-60 minutes"
    output: "Implementation code for all components"

  - stage: quality
    name: "Quality Assurance"
    tool: /fix-all
    type: command
    execution: parallel_internal
    blocking: true
    duration_estimate: "2-5 minutes"
    output: "All type errors, test failures, lint warnings resolved"

  - stage: review
    name: "Code Review"
    tool: /review-orchestrator
    type: command
    blocking: false
    duration_estimate: "3-7 minutes"
    output: "Comprehensive review findings and recommendations"

  - stage: finalize
    name: "Commit Changes"
    tool: /git:commit
    type: command
    blocking: false
    duration_estimate: "30 seconds"
    output: "Changes committed with conventional commit message"

user_communication: |
  🔄 **Feature Development Workflow Activated**

  I'll guide you through the complete feature development process:

  1. **Planning** (/planning:feature) - Define requirements and tasks
  2. **Implementation** (parallel agents) - Build frontend + backend
  3. **Quality** (/fix-all) - Fix all issues
  4. **Review** (/review-orchestrator) - Comprehensive review
  5. **Finalize** (/git:commit) - Commit clean code

  Estimated total time: 30-80 minutes

  Starting Stage 1: Planning...
```

### 2. Bug Fix Workflow

```yaml
name: bug_fix_workflow
trigger_keywords: ["fix bug", "bug", "broken", "not working", "error"]
description: Systematic bug fixing with verification

stages:
  - stage: exploration
    name: "Understand the Bug"
    tool: Explore
    type: agent
    subagent_type: Explore
    mode: medium
    blocking: true
    duration_estimate: "2-5 minutes"
    focus: "Analyze code around bug, understand data flow, identify root cause"

  - stage: fix
    name: "Implement Fix"
    tool: ts-coder
    type: agent
    blocking: true
    duration_estimate: "5-15 minutes"
    output: "Bug fix implementation"

  - stage: verification
    name: "Verify Fix"
    execution: parallel
    tools:
      - name: /fix:types
        type: command
        purpose: "Ensure no type errors introduced"
      - name: /fix:tests
        type: command
        purpose: "Ensure all tests pass"
    blocking: true
    duration_estimate: "2-5 minutes"

  - stage: review
    name: "Review Fix"
    tool: senior-code-reviewer
    type: agent
    blocking: false
    duration_estimate: "3-5 minutes"
    focus: "Ensure fix doesn't introduce new issues"

  - stage: commit
    name: "Commit Fix"
    tool: /git:commit
    type: command
    blocking: false
    duration_estimate: "30 seconds"

user_communication: |
  🐛 **Bug Fix Workflow Activated**

  Systematic bug resolution process:

  1. **Explore** (Explore agent) - Understand root cause
  2. **Fix** (ts-coder agent) - Implement solution
  3. **Verify** (/fix:types + /fix:tests) - Ensure quality
  4. **Review** (senior-code-reviewer) - Double-check
  5. **Commit** (/git:commit) - Save the fix

  Starting investigation...
```

### 3. Code Review Workflow

```yaml
name: comprehensive_code_review
trigger_keywords: ["review my code", "code review", "review changes", "review pr"]
description: Multi-faceted code review before merge

pre_checks:
  - name: check_modified_files
    condition: "git status shows modified files"
    action: "Proceed"
    failure: "No changes to review - clean working directory"

stages:
  - stage: quality_fixes
    name: "Pre-Review Quality Fixes"
    condition: "if diagnostics show errors/warnings"
    tool: /fix-all
    type: command
    blocking: true
    duration_estimate: "2-5 minutes"
    rationale: "Reviews are more valuable on clean code"

  - stage: comprehensive_review
    name: "Orchestrated Review"
    tool: /review-orchestrator
    type: command
    blocking: true
    duration_estimate: "5-10 minutes"
    output: "Multi-reviewer analysis (quality, security, testing, readability)"

  - stage: specialized_reviews
    name: "Domain-Specific Reviews"
    execution: parallel
    condition: "based on file types and changes"
    tools:
      - name: /reviewer:security
        type: command
        condition: "if auth files or security-sensitive code modified"
      - name: /reviewer:design
        type: command
        condition: "if UI components modified"
      - name: /reviewer:testing
        type: command
        condition: "if test coverage is low or tests modified"
    blocking: false
    duration_estimate: "3-5 minutes each"

  - stage: address_findings
    name: "Address Review Findings"
    tool: user_interaction
    type: manual
    blocking: true
    guidance: "Review findings and decide: fix now, create issues, or accept"

  - stage: final_commit
    name: "Commit Review Changes"
    tool: /git:commit
    type: command
    condition: "if changes made from review feedback"
    blocking: false

user_communication: |
  🔍 **Comprehensive Code Review Workflow**

  Multi-stage review process:

  1. **Pre-Review Quality** (/fix-all) - Fix issues first
  2. **Comprehensive Review** (/review-orchestrator) - Main review
  3. **Specialized Reviews** (parallel) - Domain-specific analysis
  4. **Address Findings** (you) - Implement improvements
  5. **Final Commit** (/git:commit) - Commit improvements

  This ensures thorough review across all quality dimensions.

  Starting pre-review quality check...
```

### 4. Documentation Workflow

```yaml
name: comprehensive_documentation
trigger_keywords: ["document project", "add documentation", "write docs", "document code"]
description: Complete documentation from structure to content

stages:
  - stage: structure
    name: "Documentation Structure"
    tool: /docs:diataxis
    type: command
    blocking: true
    duration_estimate: "5-10 minutes"
    output: "Diataxis-based documentation structure (tutorials, how-tos, reference, explanation)"

  - stage: exploration
    name: "Codebase Analysis"
    tool: Explore
    type: agent
    subagent_type: Explore
    mode: thorough
    blocking: true
    duration_estimate: "5-15 minutes"
    output: "Understanding of all components, APIs, and modules"

  - stage: content_generation
    name: "Generate Documentation Content"
    execution: sequential
    tools:
      - name: /docs:general
        type: command
        target: "API reference documentation"
      - name: intelligent-documentation
        type: agent
        target: "Architectural documentation"
      - name: jsdoc
        type: skill
        target: "JSDoc comments for all public APIs"
    blocking: true
    duration_estimate: "10-30 minutes"

  - stage: review
    name: "Documentation Review"
    tool: /reviewer:readability
    type: command
    blocking: false
    duration_estimate: "3-5 minutes"
    focus: "Clarity, completeness, accuracy"

user_communication: |
  📚 **Comprehensive Documentation Workflow**

  Complete documentation process:

  1. **Structure** (/docs:diataxis) - Organize documentation framework
  2. **Explore** (Explore agent) - Understand all code components
  3. **Generate Content** (multiple tools) - Create all documentation
  4. **Review** (/reviewer:readability) - Ensure quality

  Estimated time: 25-60 minutes

  Starting with documentation structure...
```

### 5. Testing Workflow

```yaml
name: comprehensive_testing
trigger_keywords: ["add tests", "write tests", "test coverage", "improve testing"]
description: Complete testing from strategy to implementation

stages:
  - stage: strategy
    name: "Test Strategy Review"
    tool: /reviewer:testing
    type: command
    blocking: true
    duration_estimate: "3-5 minutes"
    output: "Current coverage analysis, strategy recommendations"

  - stage: unit_tests
    name: "Write Unit Tests"
    tool: ts-coder
    type: agent
    blocking: true
    duration_estimate: "15-45 minutes"
    focus: "Unit tests for business logic, utilities, services"

  - stage: integration_tests
    name: "Write Integration Tests"
    tool: ts-coder
    type: agent
    blocking: true
    duration_estimate: "10-30 minutes"
    focus: "API endpoints, database operations, external integrations"

  - stage: e2e_tests
    name: "Write E2E Tests"
    execution: sequential
    tools:
      - name: playwright-skill
        type: skill
        purpose: "Manual E2E test exploration and scripting"
      - name: ui-engineer
        type: agent
        purpose: "Automated E2E test infrastructure"
    condition: "if UI components exist"
    blocking: true
    duration_estimate: "15-45 minutes"

  - stage: verification
    name: "Run All Tests"
    tool: /fix:tests
    type: command
    blocking: true
    duration_estimate: "2-5 minutes"
    output: "All tests passing"

  - stage: coverage_review
    name: "Final Coverage Check"
    tool: /reviewer:testing
    type: command
    blocking: false
    duration_estimate: "2-3 minutes"
    output: "Coverage report and recommendations"

user_communication: |
  🧪 **Comprehensive Testing Workflow**

  Complete test implementation:

  1. **Strategy** (/reviewer:testing) - Analyze current state
  2. **Unit Tests** (ts-coder) - Test business logic
  3. **Integration Tests** (ts-coder) - Test boundaries
  4. **E2E Tests** (playwright + ui-engineer) - Test user flows
  5. **Verification** (/fix:tests) - Ensure all pass
  6. **Coverage Review** (/reviewer:testing) - Final check

  Estimated time: 45-120 minutes

  Starting with test strategy analysis...
```

## Emergency Workflows

### 6. Production Emergency Workflow

```yaml
name: production_emergency
trigger_keywords: ["URGENT", "CRITICAL", "PRODUCTION DOWN", "BROKEN", "EMERGENCY"]
description: Fast-path resolution for critical production issues

urgency: critical
skip_confirmations: true

stages:
  - stage: rapid_diagnostics
    name: "Identify Issues"
    execution: parallel
    tools:
      - name: /fix:types
        type: command
        purpose: "Check for type errors"
      - name: /fix:tests
        type: command
        purpose: "Check for test failures"
    blocking: true
    duration_estimate: "1-2 minutes"

  - stage: parallel_fixes
    name: "Emergency Fixes"
    execution: parallel
    tools:
      - name: /fix:types
        type: command
        condition: "if type errors found"
      - name: /fix:tests
        type: command
        condition: "if tests failing"
      - name: /fix:lint
        type: command
        condition: "if lint errors critical"
    blocking: true
    duration_estimate: "2-5 minutes"

  - stage: quick_review
    name: "Rapid Security Check"
    tool: /reviewer:security
    type: command
    condition: "if auth or security-related files modified"
    blocking: true
    duration_estimate: "2-3 minutes"

  - stage: immediate_commit
    name: "Emergency Commit"
    tool: /git:commit
    type: command
    blocking: true
    duration_estimate: "30 seconds"
    message_prefix: "fix(critical):"

  - stage: deployment_ready
    name: "Ready for Deploy"
    output: "All checks passed - ready for immediate deployment"
    next_steps:
      - "Verify in staging if available"
      - "Deploy to production"
      - "Monitor error rates"

user_communication: |
  🚨 **EMERGENCY WORKFLOW ACTIVATED**

  Critical issue detected - executing fast-path resolution:

  1. **Diagnostics** (parallel) - Identify all issues (1-2min)
  2. **Fixes** (parallel) - Fix all critical issues (2-5min)
  3. **Security Check** (/reviewer:security) - Rapid audit (2-3min)
  4. **Commit** (/git:commit) - Emergency commit (30s)
  5. **Ready** - Prepared for immediate deployment

  EXECUTING NOW - No confirmations required
```

### 7. Hotfix Workflow

```yaml
name: hotfix_workflow
trigger_keywords: ["hotfix", "urgent fix", "quick fix", "patch"]
description: Fast hotfix with minimal process

stages:
  - stage: create_hotfix_branch
    name: "Create Hotfix Branch"
    action: suggest
    command: "git checkout -b hotfix/<description>"
    blocking: true

  - stage: implement_fix
    name: "Implement Hotfix"
    tool: ts-coder
    type: agent
    blocking: true
    duration_estimate: "5-15 minutes"
    focus: "Minimal, targeted fix only"

  - stage: verify
    name: "Quick Verification"
    tool: /fix-all
    type: command
    blocking: true
    duration_estimate: "1-3 minutes"

  - stage: commit
    name: "Commit Hotfix"
    tool: /git:commit
    type: command
    blocking: true
    message_prefix: "fix(hotfix):"

  - stage: pr
    name: "Create Hotfix PR"
    action: suggest
    command: "gh pr create --label hotfix"

user_communication: |
  ⚡ **Hotfix Workflow**

  Fast-path hotfix process:

  1. **Branch** (suggested) - Create hotfix branch
  2. **Implement** (ts-coder) - Minimal targeted fix
  3. **Verify** (/fix-all) - Quick quality check
  4. **Commit** (/git:commit) - Commit hotfix
  5. **PR** (suggested) - Create PR for review

  Focus: Speed + Minimal Changes
```

## Specialized Workflows

### 8. Refactoring Workflow

```yaml
name: safe_refactoring
trigger_keywords: ["refactor", "restructure", "improve code structure"]
description: Safe refactoring with comprehensive checks

stages:
  - stage: analysis
    name: "Analyze Current State"
    execution: parallel
    tools:
      - name: Explore
        type: agent
        subagent_type: Explore
        mode: thorough
        focus: "Understand current architecture and dependencies"
      - name: /reviewer:quality
        type: command
        focus: "Identify code smells and improvement opportunities"
    blocking: true
    duration_estimate: "5-10 minutes"

  - stage: strategy
    name: "Refactoring Strategy"
    tool: architecture-patterns
    type: skill
    blocking: true
    duration_estimate: "5-10 minutes"
    output: "Recommended patterns and approach"

  - stage: test_baseline
    name: "Establish Test Baseline"
    tool: /fix:tests
    type: command
    blocking: true
    duration_estimate: "2-5 minutes"
    rationale: "Ensure all tests pass before refactoring"

  - stage: refactor
    name: "Implement Refactoring"
    tool: senior-code-reviewer
    type: agent
    blocking: true
    duration_estimate: "20-60 minutes"
    approach: "Incremental, safe transformations"

  - stage: verify
    name: "Verify No Breakage"
    execution: parallel
    tools:
      - name: /fix:types
        type: command
      - name: /fix:tests
        type: command
    blocking: true
    duration_estimate: "2-5 minutes"

  - stage: review
    name: "Review Improvements"
    tool: /reviewer:quality
    type: command
    blocking: false
    duration_estimate: "3-5 minutes"
    output: "Confirm improvements achieved"

user_communication: |
  ♻️ **Safe Refactoring Workflow**

  Systematic refactoring process:

  1. **Analyze** (Explore + /reviewer:quality) - Understand current state
  2. **Strategy** (architecture-patterns) - Plan approach
  3. **Test Baseline** (/fix:tests) - Ensure tests pass
  4. **Refactor** (senior-code-reviewer) - Implement changes
  5. **Verify** (/fix:types + /fix:tests) - Ensure no breakage
  6. **Review** (/reviewer:quality) - Confirm improvements

  Safety-first approach with comprehensive verification.
```

### 9. Security Audit Workflow

```yaml
name: security_audit
trigger_keywords: ["security audit", "security review", "vulnerability check", "security scan"]
description: Comprehensive security analysis

stages:
  - stage: automated_scan
    name: "Automated Security Scan"
    tool: /reviewer:security
    type: command
    blocking: true
    duration_estimate: "5-10 minutes"
    output: "Vulnerability findings, security issues"

  - stage: auth_review
    name: "Authentication & Authorization Review"
    tool: /reviewer:security
    type: command
    focus: "auth*,jwt*,session*,permission*"
    blocking: true
    duration_estimate: "5-10 minutes"

  - stage: input_validation
    name: "Input Validation Check"
    tool: /reviewer:security
    type: command
    focus: "SQL injection, XSS, command injection"
    blocking: true
    duration_estimate: "3-5 minutes"

  - stage: dependency_audit
    name: "Dependency Vulnerability Scan"
    action: suggest
    command: "npm audit"
    blocking: false

  - stage: compliance_check
    name: "Compliance Review"
    tool: legal-compliance-checker
    type: agent
    condition: "if applicable"
    blocking: false
    duration_estimate: "10-20 minutes"

  - stage: report
    name: "Security Report"
    output: "Comprehensive security findings and recommendations"

user_communication: |
  🔐 **Security Audit Workflow**

  Comprehensive security analysis:

  1. **Automated Scan** (/reviewer:security) - Find vulnerabilities
  2. **Auth Review** (/reviewer:security) - Authentication/authorization
  3. **Input Validation** (/reviewer:security) - Injection attacks
  4. **Dependency Audit** (npm audit) - Third-party vulnerabilities
  5. **Compliance** (legal-compliance-checker) - Regulatory requirements
  6. **Report** - Comprehensive findings

  Estimated time: 25-50 minutes
```

### 10. Performance Optimization Workflow

```yaml
name: performance_optimization
trigger_keywords: ["optimize performance", "make faster", "improve speed", "performance issues"]
description: Systematic performance improvement

stages:
  - stage: baseline
    name: "Establish Performance Baseline"
    action: suggest
    commands:
      - "npm run build -- --analyze"
      - "Lighthouse audit"
    blocking: true
    output: "Current performance metrics"

  - stage: analysis
    name: "Performance Analysis"
    tool: /reviewer:quality
    type: command
    blocking: true
    duration_estimate: "5-10 minutes"
    focus: "Identify performance bottlenecks"

  - stage: optimization
    name: "Implement Optimizations"
    tool: ui-engineer
    type: agent
    condition: "if frontend performance"
    blocking: true
    duration_estimate: "20-60 minutes"
    techniques:
      - "React.memo, useMemo, useCallback"
      - "Code splitting, lazy loading"
      - "Bundle size reduction"
      - "Image optimization"

  - stage: verification
    name: "Verify Improvements"
    action: suggest
    commands:
      - "npm run build -- --analyze"
      - "Lighthouse audit"
    blocking: true
    output: "Compare metrics with baseline"

  - stage: review
    name: "Final Performance Review"
    tool: /reviewer:quality
    type: command
    blocking: false
    duration_estimate: "3-5 minutes"

user_communication: |
  ⚡ **Performance Optimization Workflow**

  Systematic performance improvement:

  1. **Baseline** (build analysis) - Current performance metrics
  2. **Analysis** (/reviewer:quality) - Identify bottlenecks
  3. **Optimization** (ui-engineer) - Implement improvements
  4. **Verification** (build analysis) - Measure improvements
  5. **Review** (/reviewer:quality) - Final assessment

  Data-driven approach with before/after metrics.
```

## Workflow Selection Logic

```yaml
workflow_selection_rules:
  - trigger: "URGENT|CRITICAL|PRODUCTION|EMERGENCY"
    workflow: production_emergency
    confidence: high
    skip_confirmation: true

  - trigger: "plan.*feature|create.*feature|build.*feature"
    workflow: feature_development_full
    confidence: high

  - trigger: "fix.*bug|bug|broken"
    workflow: bug_fix_workflow
    confidence: medium
    context_check: "verify it's a bug, not a feature request"

  - trigger: "review.*code|code.*review"
    workflow: comprehensive_code_review
    confidence: high

  - trigger: "document|docs|documentation"
    workflow: comprehensive_documentation
    confidence: high

  - trigger: "test|tests|testing|coverage"
    workflow: comprehensive_testing
    confidence: medium
    context_check: "distinguish from 'fix tests'"

  - trigger: "hotfix|urgent.*fix"
    workflow: hotfix_workflow
    confidence: high

  - trigger: "refactor|restructure"
    workflow: safe_refactoring
    confidence: high

  - trigger: "security.*audit|security.*review"
    workflow: security_audit
    confidence: high

  - trigger: "optimize.*performance|performance|slow|faster"
    workflow: performance_optimization
    confidence: medium
    context_check: "verify performance is the issue"
```

## Workflow Customization

Users can customize workflows by:

1. **Skipping Stages**: Request to skip non-blocking stages
2. **Adjusting Scope**: Limit to specific files or modules
3. **Changing Sequence**: Reorder non-dependent stages
4. **Parallel Override**: Force sequential or parallel execution
5. **Tool Substitution**: Use alternative tools for stages

**Example Customization**:
```
User: "Run feature development workflow but skip the planning stage"
Router: Acknowledged - Starting at Stage 2: Implementation
```

---

**Version**: 1.0.0
**Last Modified**: 2025-11-05T10:23:50Z
