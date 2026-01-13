---
name: action-item-organizer
description: Systematic framework for extracting actionable items from documents and
  organizing them into prioritized, trackable checklists. Use when converting reports,
  meeting notes, audits, or any document with embedded action items into structured
  TODO lists.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Action Item Organizer

This skill provides a systematic framework for extracting actionable items from unstructured documents and transforming them into well-organized, prioritized, trackable checklists in markdown format.

## When to Use This Skill

- Converting code review reports into TODO lists
- Extracting action items from meeting notes
- Organizing audit findings into remediation checklists
- Breaking down project planning documents into task lists
- Structuring issue reports into actionable work items
- Creating trackable checklists from any document containing embedded action items
- Organizing team backlogs by priority
- Creating sprint planning checklists

## Core Principles

### 1. Extraction with Context Preservation

Action items must be extracted with sufficient context so that anyone reading the checklist understands:

- **What** needs to be done
- **Why** it matters
- **Where** it applies (files, systems, components)
- **Who** is responsible
- **When** it should be completed (priority and estimates)

### 2. Priority-Based Organization

Use a clear priority framework to organize items by urgency and impact:

- **P0 / Blockers**: Critical issues that prevent progress, deployment, or merge
- **P1 / High Priority**: Significant quality, security, or correctness concerns requiring prompt attention
- **P2 / Medium Priority**: Important improvements and refactorings that enhance the system
- **P3 / Low Priority**: Future optimizations, minor suggestions, and nice-to-have enhancements

Within each priority level, group related items logically (e.g., security items together, performance items together).

### 3. Nested Structure for Complex Tasks

Break down complex action items into hierarchical checklists:

- Parent items represent the main task or goal
- Child items represent specific steps or sub-tasks
- Grandchild items represent detailed implementation steps

This creates a clear execution path and allows for granular progress tracking.

### 4. Traceability and Metadata

Maintain links between action items and their sources:

- File paths and line numbers
- Issue or tracking IDs
- Owner or responsible team
- Time estimates
- Original context from source document

This enables bidirectional traceability and informed prioritization.

## Extraction Workflow

### Step 1: Document Analysis

1. Read the complete source document
2. Identify sections containing actionable content:
   - "Action Items", "Todo List", "Recommendations"
   - "Issues", "Findings", "Follow-ups"
   - "Next Steps", "Tasks", "Requirements"
3. Understand the document structure and conventions

### Step 2: Action Item Identification

Extract items that are:

- **Actionable**: Specific tasks that can be completed
- **Testable**: Clear completion criteria
- **Assigned or assignable**: Can be owned by a person or team
- **Contextual**: Include enough detail to understand the task

Skip items that are:

- Purely informational (unless they imply action)
- Already completed
- Vague or unclear without additional context

### Step 3: Metadata Extraction

For each action item, extract:

**Required Metadata:**

- Task description
- Priority level

**Optional Metadata (extract if available):**

- File paths and line numbers
- Owner/responsible party
- Time estimate
- Issue/tracking numbers
- Category or domain (security, performance, etc.)
- Implementation steps or sub-tasks

### Step 4: Priority Classification

Assign each item to a priority level based on:

**P0 Criteria:**

- Blocks deployment or merge
- Critical security vulnerability
- Data loss or corruption risk
- System availability impact
- Compliance violation

**P1 Criteria:**

- Significant security concern
- Major performance impact
- Correctness issues affecting functionality
- Important architectural problems
- High technical debt

**P2 Criteria:**

- Code quality improvements
- Moderate refactoring needs
- Test coverage gaps
- Documentation needs
- Minor performance optimizations

**P3 Criteria:**

- Code style and consistency
- Future enhancements
- Nice-to-have features
- Minor optimizations
- Exploratory tasks

### Step 5: Hierarchical Organization

Structure items using nested checklists:

```markdown
- [ ] **Category: Main task description** (#tracking-id)
  - [ ] Sub-task 1
  - [ ] Sub-task 2
    - [ ] Detailed implementation step
  - **File**: `path/to/file.ext:lines`
  - **Owner**: Team/Person
  - **Estimate**: Time estimate
  - **Context**: Why this matters and what it achieves
```

### Step 6: Summary Generation

For each priority section, calculate:

- Total number of items
- Total estimated hours (if available)
- Completion percentage (if tracking existing checklist)

### Step 7: Output Formatting

Create a structured markdown document with:

1. **Header**: Title, generation metadata, source reference
2. **Overview**: Total items and time across all priorities
3. **Priority Sections**: P0, P1, P2, P3 with summaries
4. **Completion Tracking**: Progress metrics at the bottom

## Checklist Format Standards

### Basic Checkbox Item

```markdown
- [ ] Task description
```

### Item with Metadata

```markdown
- [ ] **Category: Task description** (#123)
  - **File**: `src/file.js:45-67`
  - **Owner**: Backend Team
  - **Estimate**: 3 hours
  - **Context**: Explanation of why this matters
```

### Nested Sub-tasks

```markdown
- [ ] **Security: Implement authentication** (#456)
  - [ ] Add session validation
  - [ ] Implement rate limiting
  - [ ] Add authorization checks
  - **File**: `api/auth.ts`
  - **Owner**: Security Team
  - **Estimate**: 8 hours
```

### Section Summary

```markdown
## P0 - Blockers (Must Fix Before Merge)

**Summary**: 5 items | 12 hours estimated

- [ ] Item 1...
- [ ] Item 2...
```

## Complete Output Template

```markdown
# TODO List

> Generated from: [source-document.md]
> Date: YYYY-MM-DD HH:MM:SS
> Total Items: X | Total Estimated Hours: Y

## P0 - Blockers (Must Fix Before Merge)

**Summary**: N items | M hours estimated

- [ ] **Category: Task description** (#id)
  - [ ] Sub-task
  - **File**: `path/file.ext:lines`
  - **Owner**: Team
  - **Estimate**: X hours
  - **Context**: Why this matters

## P1 - High Priority

**Summary**: N items | M hours estimated

[items...]

## P2 - Medium Priority

**Summary**: N items | M hours estimated

[items...]

## P3 - Low Priority / Future

**Summary**: N items | M hours estimated

[items...]

---

## Completion Tracking

- P0 Blockers: 0/N completed (0%)
- P1 High Priority: 0/M completed (0%)
- P2 Medium Priority: 0/K completed (0%)
- P3 Low Priority: 0/J completed (0%)

**Overall Progress**: 0/X tasks completed (0%)
```

## Best Practices

### Context Preservation

- Include enough detail that readers understand WHY each task matters
- Preserve the original rationale and justification
- Link to related issues or documentation
- Capture the impact of not completing the task

### Logical Grouping

- Group related items within priority levels
- Use category prefixes (Security, Performance, Testing, etc.)
- Keep dependent tasks near each other
- Consider execution order in grouping

### Actionability

- Each checkbox should be a clear, completable action
- Avoid vague tasks like "improve performance"
- Use specific verbs: implement, add, remove, refactor, fix
- Include success criteria when helpful

### Traceability

- Always link back to source files and line numbers
- Include issue or tracking IDs
- Reference original documentation
- Enable bidirectional navigation

### Completeness

- Verify all action items from source are included
- Preserve nested relationships
- Don't lose metadata in extraction
- Handle edge cases explicitly

## Handling Edge Cases

### Missing Priority

- Place in "Uncategorized" section at bottom
- Flag for review and prioritization
- Use context clues to infer if possible

### Missing Metadata

- Use "TBD" markers for missing estimates
- Note "File: TBD" to prompt investigation
- Flag items with insufficient context

### Conflicting Priorities

- Defer to explicit priority markers in source
- Consider impact and urgency
- Document rationale for priority assignment

### Existing TODO Files

- Confirm before overwriting
- Consider timestamped filenames
- Merge with existing if appropriate

### Multiple Sources

- Process each independently
- Or consolidate into single list with source markers
- Deduplicate when appropriate

## Anti-Patterns to Avoid

### Losing Context

Bad: `- [ ] Fix bug`
Good: `- [ ] **Bug Fix: Handle null response in user fetch** (#789)`

### Flat Structure

Bad: Ten separate items for one complex task
Good: One parent with nested sub-tasks

### Missing Traceability

Bad: No file paths or line numbers
Good: Always include location metadata

### Vague Tasks

Bad: `- [ ] Improve performance`
Good: `- [ ] **Performance: Add caching to user query** - reduces DB calls from 100/req to 1/req`

### Priority Inflation

Bad: Everything is P0
Good: Reserve P0 for true blockers

## Examples

### Example 1: Code Review Report to TODO

**Input**: Code review report with security findings

**Output**:

```markdown
# TODO List

> Generated from: CODE_REVIEW_REPORT.md
> Date: 2025-12-09 10:30:00
> Total Items: 8 | Total Estimated Hours: 23

## P0 - Blockers (Must Fix Before Merge)

**Summary**: 2 items | 5 hours estimated

- [ ] **Security: Add authentication to token endpoint** (#1)
  - [ ] Implement getServerSession check
  - [ ] Add authorization verification
  - [ ] Add rate limiting (10 req/min per IP)
  - **File**: `app/api/livekit/token/route.ts:15-30`
  - **Owner**: Backend Team
  - **Estimate**: 4 hours
  - **Context**: Public endpoint exposed without auth allows unauthorized access

- [ ] **Security: Remove hardcoded credentials** (#2)
  - [ ] Remove fallback values from environment reads
  - [ ] Add explicit validation for required credentials
  - [ ] Fail fast if credentials missing at startup
  - **File**: `experiments/livekit/src/index.ts:182-183`
  - **Owner**: Backend Team
  - **Estimate**: 1 hour
  - **Context**: Hardcoded fallbacks create security risk in production
```

### Example 2: Meeting Notes to Action Items

**Input**: Team meeting notes with scattered action items

**Output**:

```markdown
# Action Items - Q4 Planning Meeting

> Generated from: team-meeting-2025-12-09.md
> Date: 2025-12-09 14:00:00
> Total Items: 12 | Total Estimated Hours: 45

## P1 - High Priority

**Summary**: 5 items | 20 hours estimated

- [ ] **Architecture: Design new API gateway** (#45)
  - [ ] Research existing solutions (Kong, Tyk, AWS API Gateway)
  - [ ] Document requirements and constraints
  - [ ] Create comparison matrix
  - [ ] Present findings to team
  - **Owner**: Sarah
  - **Estimate**: 8 hours
  - **Context**: Current gateway hitting scale limits at 1000 req/s

- [ ] **Documentation: Update onboarding guide** (#46)
  - [ ] Add sections on local development setup
  - [ ] Document deployment process
  - [ ] Add troubleshooting guide
  - **Owner**: Mike
  - **Estimate**: 4 hours
  - **Context**: New engineers spending 2 days on setup
```

## Reference Files

For detailed guidance on specific aspects of action item organization:

- **`references/priority-framework.md`**: Comprehensive priority classification criteria with domain-specific examples
- **`references/metadata-extraction-patterns.md`**: Detailed patterns for extracting different types of metadata from various document formats
- **`references/TODO_LIST.template.md`**: TODO list template with priority-based organization (P0-P3), blocked tasks, and completion tracking

Load these references when you need deeper guidance on priority decisions or metadata extraction strategies.

## Related Workflows

- Code review processes
- Sprint planning
- Issue triage
- Project management
- Audit remediation
- Meeting facilitation
- Documentation review
