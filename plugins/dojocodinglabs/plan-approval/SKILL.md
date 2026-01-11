---
name: plan-approval
description: Plan-approval workflow patterns for user control over AI actions in Claude Code Waypoint Plugin. Use when planning complex changes, need user approval before execution, want to prevent mistakes, or need to document proposed changes. Covers plan creation, approval checkpoints, plan deviation tracking, revision management, and learning from approved/rejected plans.
---

# Plan-Approval Skill

## Purpose

Enable user control over AI actions by requiring explicit approval for complex or risky changes, preventing mistakes and ensuring alignment with user intent.

## When to Use This Skill

Automatically activates when you mention:
- Creating or reviewing plans
- Approval or confirmation needed
- Proposed changes or approach
- Want to see plan before execution
- Complex or risky operations
- Need user sign-off

## The Problem: No User Control

**Without plan approval**:
- ❌ AI jumps straight to implementation
- ❌ No chance to review approach
- ❌ Mistakes expensive to undo
- ❌ User left out of decision process
- ❌ No learning from rejections

**With plan approval**:
- ✅ User reviews before execution
- ✅ Can modify or reject approach
- ✅ Prevents costly mistakes
- ✅ User maintains control
- ✅ AI learns from feedback

---

## Core Principles

### 1. User is Always in Control

**Never execute without approval for**:
- Database schema changes
- Breaking API changes
- Dependency updates
- Architecture refactors
- File deletions
- Deployment actions

### 2. Plans are Detailed

**Good plans include**:
- What will be done (specific files/changes)
- Why this approach (rationale)
- What alternatives were considered
- What risks exist
- What the impact is
- How long it will take

### 3. Approval is Explicit

**Require clear user response**:
- ✅ "approve", "yes", "proceed", "looks good"
- ❌ Silence, vague response, "maybe"
- ⚠️ "modify: [changes]" triggers plan revision

### 4. Learning from Feedback

**Track approved/rejected plans**:
- Store approved approaches (do more like this)
- Store rejected approaches (avoid in future)
- Learn user preferences over time

---

## When to Require Approval

### Always Require Approval

✅ **Database changes**:
- Schema migrations
- RLS policy changes
- Data migrations
- Index additions

✅ **Breaking changes**:
- API signature changes
- Function signature changes
- Component prop changes

✅ **Architecture changes**:
- New dependencies
- Framework changes
- State management approach
- Routing structure

✅ **Risky operations**:
- File deletions
- Bulk updates
- Production deployments

### Optional Approval

⚠️ **Complex features** (> 5 files affected)
⚠️ **Refactoring** (multiple components)
⚠️ **Performance optimization** (cache strategies)

### No Approval Needed

❌ **Simple changes**:
- Bug fixes (< 10 lines)
- Documentation updates
- Code formatting
- Minor UI tweaks

**Rule of Thumb**: If user might say "wait, not like that!", require approval.

---

## Plan Structure

### Minimal Plan Template

```markdown
# [Feature/Change Name]

## Summary
[1-2 sentence overview]

## What Will Change
- File 1: [what changes]
- File 2: [what changes]
- Database: [migrations if any]
- Dependencies: [new packages if any]

## Why This Approach
[Rationale for chosen approach]

## Risks
- Risk 1: [description + mitigation]
- Risk 2: [description + mitigation]

## Estimated Time
[How long to implement]

---
**Approve to proceed**, or reply with modifications
```

### Comprehensive Plan Template

```markdown
# [Feature/Change Name]

## Summary
[2-3 sentence overview of the change and its purpose]

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Proposed Approach

### Architecture
[High-level architecture description]

### Implementation Steps
1. **Step 1**: [Description]
   - Files: [list]
   - Changes: [brief description]
   - Risk: [if any]

2. **Step 2**: [Description]
   - Files: [list]
   - Changes: [brief description]
   - Risk: [if any]

[Continue for all steps...]

### Files to Create (3)
1. `path/to/file1.ts` - [Purpose]
2. `path/to/file2.ts` - [Purpose]
3. `path/to/file3.ts` - [Purpose]

### Files to Modify (2)
1. `path/to/existing1.ts` - [What will change]
2. `path/to/existing2.ts` - [What will change]

### Database Changes
**Migration**: `supabase/migrations/xxx_add_feature.sql`
- Add table: `feature_table`
- Add column: `users.feature_flag`
- Add RLS policy: `feature_access_policy`

### Dependencies
**New**:
- package-name@^1.0.0 (Purpose: [why])

**Updates**:
- existing-package: 1.0.0 → 2.0.0 (Reason: [why])

## Alternatives Considered

### Alternative 1: [Name]
**Approach**: [Description]
**Pros**: [Benefits]
**Cons**: [Drawbacks]
**Why not chosen**: [Reason]

### Alternative 2: [Name]
**Approach**: [Description]
**Pros**: [Benefits]
**Cons**: [Drawbacks]
**Why not chosen**: [Reason]

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk 1] | Medium | High | [How to prevent/handle] |
| [Risk 2] | Low | Medium | [How to prevent/handle] |

## Breaking Changes

⚠️ **API Changes**:
- `oldFunction()` → `newFunction()` signature changed
- Migration path: [How to update]

⚠️ **Database Changes**:
- Table `old_name` renamed to `new_name`
- Migration script: [Path]

## Testing Strategy
- [ ] Unit tests for [components]
- [ ] Integration tests for [flows]
- [ ] Manual testing: [scenarios]

## Rollback Plan
If this fails:
1. [Step to revert]
2. [Step to restore]
3. [Data recovery if needed]

## Estimated Time
- Implementation: [X hours]
- Testing: [Y hours]
- **Total**: [Z hours]

---

## Approval

**Reply with**:
- `approve` - Proceed with this plan
- `reject` - Cancel, don't proceed
- `modify: [your changes]` - Adjust plan first

```

---

## Approval Workflow

### Step 1: Generate Plan

```markdown
User: "Add Stripe payment integration"

Claude:
"I'll create a plan for Stripe integration first.

[Generates detailed plan using template]

Review the plan above. Reply:
- 'approve' to proceed
- 'reject' to cancel
- 'modify: [changes]' to adjust
"
```

### Step 2: Wait for Explicit Approval

**Valid approvals**:
- "approve"
- "yes, proceed"
- "looks good"
- "go ahead"
- "lgtm" (looks good to me)

**Modifications**:
- "modify: use Stripe Checkout instead of Elements"
- "change: store payment methods in Supabase"
- "add: webhook handling"

**Rejections**:
- "reject"
- "no"
- "cancel"
- "let's do something different"

### Step 3: Execute or Revise

**If approved**:
1. Save plan to `.claude/memory/plans/approved/`
2. Execute implementation
3. Track progress in dev docs
4. Mark complete when done

**If modified**:
1. Update plan with user's changes
2. Re-present revised plan
3. Wait for approval again

**If rejected**:
1. Save to `.claude/memory/plans/rejected/` with reason
2. Learn from rejection
3. Don't proceed

### Step 4: Track Execution

```markdown
## Plan Execution Status

**Plan ID**: stripe-integration-2025-01-15
**Status**: In Progress
**Approved**: 2025-01-15 10:00
**Started**: 2025-01-15 10:05

**Progress**:
- [x] Step 1: Install Stripe SDK
- [x] Step 2: Create Stripe client
- [ ] Step 3: Implement checkout flow (IN PROGRESS)
- [ ] Step 4: Add webhook handler
- [ ] Step 5: Test payment flow

**Current**: Implementing checkout flow in app/api/checkout/route.ts
**Next**: Add webhook handler for payment events
```

---

## Plan Storage

### Directory Structure

```
.claude/memory/plans/
├── proposed/                    # Plans awaiting approval
│   └── stripe-integration-2025-01-15.json
├── approved/                   # Approved plans
│   └── stripe-integration-2025-01-15.json
├── rejected/                   # Rejected plans (learn from these)
│   └── alternative-approach-2025-01-14.json
└── completed/                  # Completed implementations
    └── stripe-integration-2025-01-15.json
```

### Plan File Schema

```json
{
  "plan_id": "stripe-integration-2025-01-15",
  "created": "2025-01-15T10:00:00Z",
  "status": "approved" | "proposed" | "rejected" | "in_progress" | "completed",
  "summary": "Add Stripe payment integration for subscriptions",
  "approved_at": "2025-01-15T10:05:00Z",
  "started_at": "2025-01-15T10:10:00Z",
  "completed_at": null,
  "user_modifications": [
    "Use Stripe Checkout instead of Elements",
    "Store payment methods in Supabase"
  ],
  "files_to_create": [
    "lib/stripe/client.ts",
    "app/api/checkout/route.ts"
  ],
  "files_to_modify": [
    "package.json",
    "lib/supabase/schema.sql"
  ],
  "risks": [
    "Webhook reliability",
    "Payment state synchronization"
  ],
  "estimated_hours": 4,
  "actual_hours": null,
  "outcome": null,
  "lessons_learned": []
}
```

---

## Learning from Plans

### Track Approval Patterns

```json
{
  "approval_patterns": {
    "stripe_payments": {
      "preferred_approach": "Stripe Checkout (not Elements)",
      "storage": "Supabase tables",
      "reason": "User approved this twice, rejected Elements once",
      "confidence": "high"
    },
    "database_changes": {
      "requires_approval": true,
      "wants_rollback_plan": true,
      "prefers_separate_migration_file": true,
      "confidence": "high"
    }
  }
}
```

### Apply Learnings

**Future similar requests**:
```markdown
User: "Add subscription billing"

Claude:
"Based on previous approvals, I'll plan to use:
- Stripe Checkout (you preferred this over Elements)
- Supabase tables for subscription state
- Separate webhook handler

[Presents plan following learned preferences]
```

### Track Rejections

```json
{
  "rejections": [
    {
      "plan_id": "complex-state-management-2025-01-10",
      "reason": "Too complex, prefer simpler approach",
      "rejected_approach": "Redux Toolkit",
      "preferred_instead": "React Context",
      "lesson": "User prefers simpler solutions when possible"
    }
  ]
}
```

---

## Plan Deviations

### When Implementation Differs from Plan

**Acceptable deviations**:
- Minor implementation details
- Better solution discovered
- Library API changed

**Require new approval**:
- Different architecture approach
- More files affected than planned
- Additional dependencies
- Higher risk than estimated

### Handling Deviations

```markdown
User: "Continue with Stripe integration"

Claude:
"⚠️ PLAN DEVIATION DETECTED

**Original plan**: Use Stripe Elements
**Current need**: Stripe Checkout is better for our use case

**Reason**: Elements requires more frontend work, Checkout is simpler

**Impact**:
- Different files affected
- Simpler implementation
- Less custom UI needed

**Do you approve this deviation?**
- 'yes' - Proceed with Checkout
- 'no' - Stick to original plan
- 'revise' - Create new plan
"
```

---

## Commands

Provide these commands:

```bash
# Create plan
/create-plan [feature-name]       # Generate plan for approval

# Review plans
/show-plans                       # Show all plans
/show-plan [plan-id]              # Show specific plan

# Approve/reject
/approve [plan-id]                # Approve a plan
/reject [plan-id]                 # Reject a plan

# Track progress
/plan-status [plan-id]            # Show execution progress

# History
/approved-plans                   # Show approved plans
/rejected-plans                   # Show rejected (learn from these)
```

---

## Integration with Other Skills

### With memory-management

**memory-management** stores long-term preferences.
**plan-approval** handles one-time decisions.

**Example**:
- Memory: "User always prefers TypeScript" (permanent)
- Plan: "Use Stripe Checkout for payments" (this feature)

### With context-persistence

**context-persistence** tracks implementation progress.
**plan-approval** handles pre-implementation planning.

**Workflow**:
1. Plan approval: Generate and approve plan
2. Context persistence: Track implementation in dev docs
3. Memory: Store outcome and learnings

---

## Best Practices

### DO ✅

1. **Present clear, detailed plans**
2. **Wait for explicit approval**
3. **Track plan execution progress**
4. **Learn from approvals and rejections**
5. **Notify user of deviations**
6. **Store plans for future reference**
7. **Include rollback strategy for risky changes**

### DON'T ❌

1. **Don't skip approval for complex changes**
2. **Don't assume silence means approval**
3. **Don't deviate significantly without asking**
4. **Don't forget to track approved plans**
5. **Don't make plans too vague**
6. **Don't proceed if user is uncertain**

---

## Example: Complete Plan-Approval Flow

### User Request

```
User: "Add Stripe subscription billing to the app"
```

### Plan Generation

```markdown
Claude: "I'll create a detailed plan for Stripe subscriptions.

# Stripe Subscription Billing Plan

## Summary
Add Stripe subscription billing with monthly/yearly plans, customer portal, and webhook handling.

## What Will Change

### Files to Create (5)
1. `lib/stripe/client.ts` - Stripe client initialization
2. `lib/stripe/subscriptions.ts` - Subscription management
3. `app/api/stripe/webhook/route.ts` - Webhook handler
4. `app/api/checkout/route.ts` - Checkout session creation
5. `app/pricing/page.tsx` - Pricing page

### Files to Modify (3)
1. `package.json` - Add stripe package
2. `.env.example` - Add Stripe keys
3. `lib/supabase/schema.sql` - Add subscriptions table

### Database Changes
**Migration**: `supabase/migrations/20250115_subscriptions.sql`
- Table: `subscriptions` (user_id, stripe_subscription_id, status, plan_id)
- Table: `subscription_plans` (name, price, interval)
- RLS policies for subscription access

## Why This Approach
- Stripe Checkout: Hosted, PCI-compliant, less frontend work
- Webhooks: Reliable payment event handling
- Supabase storage: Sync subscription state with user data

## Alternatives Considered
- **Stripe Elements**: More control but more work. Rejected: Overkill for MVP
- **Manual billing**: Can't scale. Rejected: Need automation

## Risks
- ⚠️ Webhook reliability: Mitigate with retry logic + monitoring
- ⚠️ State sync: Mitigate with idempotent webhook handlers

## Estimated Time
- Implementation: 3 hours
- Testing: 1 hour
- **Total**: 4 hours

---

**Do you approve this plan?**
Reply: 'approve', 'modify: [changes]', or 'reject'
```

### User Approval

```
User: "approve"
```

### Execution

```markdown
Claude: "✅ Plan approved. Starting implementation.

Saving plan to: .claude/memory/plans/approved/stripe-subscriptions-2025-01-15.json

Creating dev docs: /create-plan stripe-subscriptions

Starting with Step 1: Install Stripe SDK..."

[Proceeds with implementation while tracking progress]
```

### Completion

```markdown
Claude: "✅ Stripe subscription billing complete!

**Completed**:
- ✅ All 5 files created
- ✅ Database migration applied
- ✅ Webhooks tested with Stripe CLI
- ✅ Checkout flow working

**Time**: 3.5 hours (30 min under estimate)

Marking plan as completed.
Storing lessons learned:
- Stripe Checkout works well for subscriptions
- Webhook testing critical (caught 2 bugs)
```

---

## Summary

**Plan-approval workflow enables**:
1. ✅ User control over AI actions
2. ✅ Prevention of costly mistakes
3. �� Clear communication of approach
4. ✅ Learning from user feedback
5. ✅ Transparent decision making

**Key steps**:
1. Generate detailed plan
2. Wait for explicit approval
3. Execute or revise based on feedback
4. Track progress
5. Learn from outcome

**Storage**: `.claude/memory/plans/` with status tracking

**Commands**: `/create-plan`, `/approve`, `/reject`, `/show-plans`

**Rule**: Always require approval for complex, risky, or breaking changes!

Use this skill to ensure Claude Code never acts without your explicit permission for important changes.
