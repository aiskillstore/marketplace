# Workflow Patterns for Skills

Source: https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf

## Choosing: Problem-first vs. Tool-first

- **Problem-first:** User describes an outcome → skill orchestrates the right MCP calls in sequence
- **Tool-first:** User has MCP access → skill teaches optimal workflows and best practices

## Pattern 1: Sequential Workflow Orchestration

Use when: Users need multi-step processes in a specific order.

```
## Workflow: Onboard New Customer

### Step 1: Create Account
Call MCP tool: `create_customer`
Parameters: name, email, company

### Step 2: Setup Payment
Call MCP tool: `setup_payment_method`
Wait for: payment method verification

### Step 3: Create Subscription
Call MCP tool: `create_subscription`
Parameters: plan_id, customer_id (from Step 1)
```

Key techniques:

- Explicit step ordering with numbered steps
- Document dependencies between steps
- Validation gate at each stage
- Rollback instructions for failures

## Pattern 2: Multi-MCP Coordination

Use when: Workflows span multiple services.

```
### Phase 1: Design Export (Figma MCP)
1. Export design assets
2. Generate design specifications

### Phase 2: Asset Storage (Drive MCP)
1. Create project folder
2. Upload all assets

### Phase 3: Task Creation (Linear MCP)
1. Create development tasks
2. Attach asset links
```

Key techniques:

- Clear phase separation per service
- Explicit data passing between MCPs
- Validation before moving to next phase
- Centralized error handling section

## Pattern 3: Iterative Refinement

Use when: Output quality improves with iteration.

```
### Initial Draft
1. Fetch data via MCP
2. Generate first draft

### Quality Check
1. Run validation: `scripts/check_report.py`
2. Identify issues: missing sections, formatting errors

### Refinement Loop
1. Fix each issue
2. Re-validate
3. Repeat until quality threshold met
```

Key techniques:

- Explicit quality criteria (not "good enough")
- Validation scripts for deterministic checks
- Define the stop condition clearly

## Pattern 4: Context-Aware Tool Selection

Use when: Same outcome, different tools depending on context.

```
### Decision Tree
1. Check file type and size
2. Determine storage:
   - Large files (>10MB): cloud storage MCP
   - Collaborative docs: Notion/Docs MCP
   - Code files: GitHub MCP

### Execute
- Call appropriate MCP tool
- Explain choice to user
```

Key techniques:

- Explicit decision criteria
- Fallback options for each branch
- Transparency about which tool was chosen and why

## Pattern 5: Domain-Specific Intelligence

Use when: Skill adds specialized knowledge beyond tool access.

```
### Before Processing (Compliance Check)
1. Fetch transaction details via MCP
2. Apply compliance rules:
   - Check sanctions lists
   - Verify jurisdiction allowances
3. Document compliance decision

### Processing
IF compliance passed → call payment MCP tool
ELSE → flag for review, create compliance case

### Audit Trail
- Log all checks
- Record decisions
- Generate audit report
```

Key techniques:

- Embed domain rules in explicit logic (IF/ELSE, not vague language)
- Compliance/validation before action
- Comprehensive audit documentation
- Clear governance (who reviews flagged cases)
