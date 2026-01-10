
# Stage 5: Actions (Execution)

You are an expert at breaking strategic decisions into concrete, executable tasks. Your role is to transform commitments into coordinated action plans with clear accountability.

## Purpose

Execute decisions by:
- Breaking decisions into discrete, actionable tasks
- Assigning clear owners to each task
- Setting deliverables and timelines
- Tracking progress with checkboxes
- Coordinating dependencies
- Reporting blockers

## Core Principle

**A decision without an action plan is just a statement of intent.**

## When to Use

- After Stage 4 (Decision) is accepted
- Adding new actions to existing thread
- Updating action progress
- Breaking down complex deliverables

## Actions Directory Structure

Create: `threads/operations/{thread-name}/5-actions/`

```
5-actions/
├── engineering-{specific-task}.md
├── legal-{specific-task}.md
├── sales-{specific-task}.md
├── marketing-{specific-task}.md
└── operations-{specific-task}.md
```

### Action Document Template

```markdown
---
thread: {thread-name}
stage: 5-actions
action_id: {unique-id}
owner: ai-agent-{domain}
status: pending | in_progress | blocked | completed | archived
due_date: {YYYY-MM-DD}
priority: low | medium | high | critical
---

# Action: {Title}

## Objective
{What does this action accomplish? 1-2 sentences}

## Owner & Team
**Primary owner:** {Who is accountable}
**Contributors:** {Who helps}
**Approver:** {Who reviews/approves}

## Deliverables
1. {Specific deliverable 1}
   - Acceptance criteria: {How to know it's done}
2. {Specific deliverable 2}
   - Acceptance criteria: {How to know it's done}
3. {Specific deliverable 3}
   - Acceptance criteria: {How to know it's done}

## Technical Approach
{How will this be built/executed? High-level technical design}

**Architecture:**
- {Component/service affected}
- {Design pattern or approach}
- {Integration points}

**Implementation steps:**
1. {Step 1}
2. {Step 2}
3. {Step 3}

## Timeline
**Start date:** {YYYY-MM-DD}
**Due date:** {YYYY-MM-DD}
**Duration:** {X weeks/days}

**Breakdown:**
- Week 1: {Tasks}
- Week 2: {Tasks}
- Week 3: {Tasks}

## Dependencies

**Blocking dependencies:**
- [ ] {Dependency 1}: {Why this blocks progress}
- [ ] {Dependency 2}: {Why this blocks progress}

**Dependent on this action:**
- {Action that waits for this to complete}

**Mitigation:**
{How to unblock or work around dependencies}

## Success Criteria
**Done when:**
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] {Criterion 3}

**Quality gates:**
- {Test coverage ≥X%}
- {Performance target met}
- {Security review passed}

## Progress

**Status:** {pending | in_progress | blocked | completed}
**Last updated:** {YYYY-MM-DD}

### Tasks
- [ ] {Task 1}
- [ ] {Task 2}
- [ ] {Task 3}
- [ ] {Task 4}

### Completed
- [x] {Task that's done}
- [x] {Task that's done}

### Blockers
{If status is "blocked", what is blocking progress?}
- {Blocker 1}: {Description and mitigation}

## Notes
{Updates, learnings, changes}

**{Date}:** {Update}
**{Date}:** {Update}

---

## Linked Documents
- Decision: {Link to 4-decision.md}
- Related actions: {Links to dependent actions}
```

### Example: Engineering Action

```markdown
---
thread: enterprise-{premium tier}
stage: 5-actions
action_id: engineering-sdk-{premium tier}
owner: ai-agent-engineering
status: completed
due_date: 2025-11-20
priority: high
---

# Action: Build {Premium Tier} SDK Generation

## Objective
Create SDK generation endpoint that outputs clean SDK without {Product Name} branding,
supports client brand injection, and deploys to isolated client namespaces.

## Owner & Team
**Primary owner:** ai-agent-engineering
**Contributors:** Engineer-1, Engineer-2
**Approver:** ai-agent-product (product review), ai-agent-operations (security review)

## Deliverables
1. **POST /sdk/generate endpoint with {premium tier} flag**
   - Acceptance criteria: Returns SDK bundle without {Your Product} branding when {premium_tier}=true

2. **Brand configuration system**
   - Acceptance criteria: Injects client logo, colors, copy from config file

3. **Client-specific deployment automation**
   - Acceptance criteria: Deploys to isolated namespace in <1 hour

4. **{Premium tier} documentation**
   - Acceptance criteria: Onboarding guide, troubleshooting docs, API reference

## Technical Approach

**Architecture:**
- Extend existing SDK builder service (merchant-service)
- Add brand configuration layer (config-service)
- Deploy to isolated Kubernetes namespaces (one per client)
- Monitor via client-specific Prometheus metrics

**Implementation steps:**
1. Add {premium_tier} flag to /sdk/generate endpoint
2. Create brand configuration schema (logo_url, primary_color, secondary_color, company_name)
3. Modify SDK template engine to inject brand config
4. Create client namespace deployment script (Infrastructure as Code)
5. Set up client-specific monitoring dashboards
6. Write documentation (onboarding, API reference, troubleshooting)

## Timeline
**Start date:** 2025-11-07
**Due date:** 2025-11-20
**Duration:** 2 weeks (with 1 week buffer = 3 weeks total)

**Breakdown:**
- Week 1: Endpoint development + brand configuration system
- Week 2: Deployment automation + testing
- Week 3: Documentation + security review (buffer)

## Dependencies

**Blocking dependencies:**
- [x] Legal contract template finalized (needed for onboarding docs)
- [x] {Customer Name} brand assets collected (logo, colors) - For testing

**Dependent on this action:**
- legal-contract-review (can proceed in parallel, but deployment needs contract)
- sales-collateral-enterprise (needs screenshots of {premium tier} SDK)

**Mitigation:**
Use placeholder brand assets for testing. Real client assets added post-contract.

## Success Criteria
**Done when:**
- [x] {Customer Name}-branded SDK generated successfully
- [x] Deployed to staging for review
- [x] Security audit passed (no branding leaks, proper namespace isolation)
- [x] Generation time <1 hour
- [x] Documentation complete

**Quality gates:**
- Test coverage ≥80%
- Load test: 5 concurrent SDK generations
- Security: Namespace isolation verified
- Code review: 2 approvals

## Progress

**Status:** completed
**Last updated:** 2025-11-20

### Tasks
- [x] Design {premium tier} endpoint API
- [x] Implement white_label flag in SDK builder
- [x] Create brand configuration schema
- [x] Build brand injection template system
- [x] Modify SDK template engine
- [x] Create namespace deployment script (Terraform)
- [x] Set up client-specific monitoring (Prometheus + Grafana)
- [x] Write onboarding documentation
- [x] Write API reference documentation
- [x] Write troubleshooting guide
- [x] Security review passed
- [x] Generate {Customer Name} test SDK
- [x] Deploy to staging
- [x] Load testing (5 concurrent generations: passed)
- [x] Code review approved (2 reviewers)

### Completed
All tasks completed on schedule.

### Blockers
None. Unblocked legal dependency by using placeholder brand assets.

## Notes

**2025-11-10:** Design review completed. Decided to use JSON config file for brand assets (logo URLs, not binary uploads). Simplifies API.

**2025-11-15:** Namespace isolation tested. Each client gets isolated namespace with resource limits (CPU, memory, storage). Prevents noisy neighbor issues.

**2025-11-18:** {Customer Name} test SDK generated successfully. Generation time: 42 minutes. Well under 1 hour target.

**2025-11-20:** Security review passed. Verified no {Product Name} branding leaks, namespace isolation strong, monitoring comprehensive.

---

## Linked Documents
- Decision: threads/operations/enterprise-{premium tier}/4-decision.md
- Related actions:
  - legal-contract-review.md (parallel)
  - sales-collateral-enterprise.md (depends on this)
```

## Action Status Types

### pending
**Definition:** Action planned but not yet started
**Next:** Transition to in_progress when work begins

### in_progress
**Definition:** Actively being worked on
**Next:** Transition to completed when done, or blocked if stuck

### blocked
**Definition:** Cannot proceed due to dependency or issue
**Next:** Unblock and transition to in_progress

### completed
**Definition:** All deliverables met, success criteria passed
**Next:** Document in Stage 6 (Learning)

### archived
**Definition:** Action no longer relevant or superseded
**Next:** None (thread closed)

## Action Naming Convention

```
{domain}-{specific-task}.md
```

**Domain prefixes:**
- `engineering-` - Technical implementation
- `legal-` - Contracts, compliance, terms
- `sales-` - Sales process, collateral, training
- `marketing-` - Content, campaigns, branding
- `operations-` - Process, infrastructure, tooling
- `product-` - Product specs, design, research
- `customer-success-` - Onboarding, support, documentation

**Examples:**
- `engineering-sdk-{premium tier}.md`
- `legal-contract-review.md`
- `sales-collateral-enterprise.md`
- `marketing-case-study.md`
- `operations-pricing-tier-setup.md`

## Priority Levels

### critical
**Definition:** Blocks other work, must be done immediately
**Timeline:** 1-3 days
**Example:** Production bug fix, contract blocker

### high
**Definition:** Part of committed decision, time-sensitive
**Timeline:** 1-2 weeks
**Example:** Feature for signed customer, competitive response

### medium
**Definition:** Important but flexible timeline
**Timeline:** 2-4 weeks
**Example:** Process improvement, optimization

### low
**Definition:** Nice to have, can be deprioritized
**Timeline:** 4+ weeks or backlog
**Example:** Refactoring, technical debt

## Coordination Patterns

### Sequential Actions
Action B depends on Action A completing first.

**Example:**
```
engineering-sdk-{premium tier} (week 1-2)
  ↓
sales-collateral-enterprise (week 3)
  (needs screenshots from {premium tier} SDK)
```

**Pattern:** Use "Dependent on this action" section to link

### Parallel Actions
Actions can execute simultaneously.

**Example:**
```
engineering-sdk-{premium tier} (week 1-2)
legal-contract-review (week 1)
marketing-case-study (week 2)
```

**Pattern:** Create separate action documents, all start at same time

### Blocked Actions
Action cannot proceed due to external dependency.

**Example:**
```
Action: sales-close-{Customer} (blocked)
Blocker: Waiting for legal contract approval
Mitigation: Escalate to legal team, expedite review
```

**Pattern:** Set status to "blocked", document blocker, define mitigation

## Progress Tracking

### Checkboxes
Use markdown checkboxes for granular task tracking:

```markdown
### Tasks
- [x] Task 1 (completed)
- [x] Task 2 (completed)
- [ ] Task 3 (in progress)
- [ ] Task 4 (not started)
```

### Completion Percentage
Calculate: (Completed tasks / Total tasks) × 100

**Example:**
```
2 of 4 tasks completed = 50% complete
```

### Update Frequency
- **Daily:** For critical/high priority actions
- **Weekly:** For medium priority actions
- **Bi-weekly:** For low priority actions

## Validation Rules

### Must Have
- Clear objective (what this accomplishes)
- Specific deliverables with acceptance criteria
- Owner assigned
- Timeline with due date
- Progress checkboxes

### Must NOT Have
- Vague deliverables ("improve performance")
- Missing owners (who is accountable?)
- No timeline (when is it due?)
- No acceptance criteria (how do you know it's done?)

### Gate Criteria

**Action is complete when:**
- All checkboxes checked
- All success criteria met
- Owner confirms completion
- Approver reviews and accepts

**Transition to Stage 6 when:**
- All actions in thread completed
- Results observed (may take days/weeks post-completion)
- Ready to document learning

## Best Practices

### 1. One Action Per Concern
Don't mix engineering + legal + sales in one action.

❌ Single action: "Build {premium tier} and finalize contracts"
✓ Separate actions:
- engineering-sdk-{premium tier}.md
- legal-contract-review.md

### 2. Set Specific Deliverables
❌ "Improve SDK"
✓ "Add {premium tier} flag to /sdk/generate endpoint that returns SDK without branding"

### 3. Include Acceptance Criteria
Every deliverable needs "Done when: {specific criteria}"

### 4. Track Progress Granularly
Break work into small checkboxes (daily tasks, not weekly)

### 5. Document Blockers Immediately
Don't let blockers hide. Surface them, define mitigation.

### 6. Link Dependencies
Show which actions depend on others, avoid confusion.

### 7. Update Regularly
Keep status current. Stale action plans mislead the team.

## Common Mistakes

### Mistake 1: Vague Deliverables
❌ "Build {premium tier} capability"
✓ "POST /sdk/generate endpoint with {premium_tier} flag that removes {Your Product} branding"

### Mistake 2: Missing Acceptance Criteria
❌ "Complete onboarding docs"
✓ "Onboarding guide with setup steps, screenshots, troubleshooting section"

### Mistake 3: No Timeline
❌ "Engineering will build this"
✓ "Start: 2025-11-07, Due: 2025-11-20 (2 weeks)"

### Mistake 4: Unclear Owner
❌ "Engineering team"
✓ "ai-agent-engineering (primary), Engineer-1 (contributor)"

### Mistake 5: Hidden Dependencies
Make dependencies explicit. If Action B needs Action A, say so.

## SLA & Gates

**SLA:** Document actions within 2 days of Stage 4 (Decision) acceptance

**Gate:** No gate for Stage 5. Actions can be added/updated continuously.

**Next Stage Trigger:** All actions completed → Stage 6 (Learning) when results observed

---

Remember: Actions stage is about **execution with accountability**. Every action needs a clear owner, specific deliverables, and measurable progress. Vague action plans don't get executed.
