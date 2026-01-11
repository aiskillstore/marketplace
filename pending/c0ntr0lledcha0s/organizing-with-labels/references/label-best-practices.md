# Label Best Practices

## Naming Conventions

### Use Lowercase with Hyphens
```
✅ Good: bug, feature-request, priority:high
❌ Bad: Bug, Feature_Request, PRIORITY_HIGH
```

### Use Prefixes for Categories
```
Type:       bug, feature, enhancement (no prefix)
Priority:   priority:critical, priority:high, priority:medium, priority:low
Scope:      scope:frontend, scope:backend, scope:database
Status:     status:needs-triage, status:blocked, status:in-progress
Size:       size:xs, size:s, size:m, size:l, size:xl
```

### Keep Names Short and Clear
```
✅ Good: priority:high, scope:backend
❌ Bad: this-is-a-high-priority-item, backend-related-changes
```

## Color Coding

### Standard Color Palette

**Red (#d73a4a, #b60205)** - Urgent, critical, bugs
- bug
- priority:critical
- security
- breaking-change
- status:blocked

**Orange (#d93f0b)** - Important, high priority
- priority:high

**Yellow (#fbca04, #fef2c0)** - Caution, medium priority
- priority:medium
- refactor
- chore
- status:needs-review

**Green (#0e8a16)** - Good, approved, completed
- status:in-progress
- status:ready-to-merge

**Blue (#0075ca, #1d76db, #5319e7)** - Informational
- feature
- documentation
- scope:frontend
- scope:backend

**Purple (#d4c5f9)** - Testing, triage
- test
- status:needs-triage

**Light Blue (#c5def5, #bfdadc)** - Low priority, minor
- priority:low
- scope:docs
- size:xs

## Taxonomy Design

### Core Hierarchy

1. **Type** (What is it?) - Required
   - bug, feature, enhancement, documentation, refactor, test, chore

2. **Priority** (How urgent?) - Recommended for open issues
   - priority:critical, priority:high, priority:medium, priority:low

3. **Scope** (Where does it affect?) - Useful for larger projects
   - scope:frontend, scope:backend, scope:database, scope:infrastructure

4. **Status** (What state?) - Optional, use for workflow tracking
   - status:needs-triage, status:blocked, status:in-progress, status:needs-review

5. **Size** (How big?) - Optional, useful for estimation
   - size:xs, size:s, size:m, size:l, size:xl

### Label Combinations

**Every issue should have**:
- At least one type label (bug, feature, etc.)

**Open issues should have**:
- Type + Priority

**Active issues should have**:
- Type + Priority + Scope (if applicable)

**Examples**:
```
Issue #42: "Login button not working"
Labels: bug, priority:high, scope:frontend

Issue #43: "Add dark mode"
Labels: feature, priority:medium, scope:frontend

Issue #44: "Optimize database queries"
Labels: enhancement, priority:low, scope:backend, scope:database
```

## Label Limits

### Recommended Limits

**Minimal setup**: 6-10 labels
- Essential types and priorities only
- Good for small projects or starting out

**Standard setup**: 10-15 labels
- Types, priorities, basic scopes
- Recommended for most projects

**Comprehensive setup**: 20-30 labels
- Full taxonomy with statuses and sizes
- Good for larger projects with multiple contributors

**Too many**: 50+ labels
- Hard to maintain consistency
- Decision paralysis when labeling
- Consider label groups or custom fields instead

### Anti-Patterns

❌ **Too many type labels**: bug, bug-frontend, bug-backend, bug-critical
- Use: bug + scope:frontend + priority:critical

❌ **Redundant labels**: high-priority, important, urgent
- Use: priority:high only

❌ **Person-specific labels**: alice, bob, carol
- Use: assignees instead

❌ **Date-based labels**: sprint-1, sprint-2, sprint-3
- Use: milestones instead

## Automation

### Auto-Label from File Paths

Use GitHub Actions to auto-apply scope labels:

```yaml
# .github/workflows/auto-label.yml
on: [pull_request]
jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@v4
        with:
          configuration-path: .github/labeler.yml
```

```yaml
# .github/labeler.yml
scope:frontend:
  - 'frontend/**'
  - 'ui/**'
  - 'src/components/**'

scope:backend:
  - 'backend/**'
  - 'api/**'
  - 'src/server/**'

documentation:
  - '**/*.md'
  - 'docs/**'
```

### Auto-Label from Issue Templates

Include labels in issue templates:

```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug Report
labels: ['bug', 'needs-triage']
```

### Auto-Label from Content

Use label inference script:
```bash
python scripts/label-operations.py infer-labels --issue 42
```

## Maintenance

### Regular Review

**Monthly**:
- Check for unused labels (0 issues)
- Identify inconsistent naming
- Look for duplicate meanings

**Quarterly**:
- Review label effectiveness
- Audit coverage (% of issues labeled)
- Update descriptions

### Cleanup Process

1. **Export current labels**:
   ```bash
   gh label list --json name,description,color --limit 1000 > labels-backup.json
   ```

2. **Fix consistency**:
   ```bash
   python scripts/label-operations.py fix-consistency
   ```

3. **Remove unused**:
   ```bash
   python scripts/label-operations.py report
   # Review unused labels
   gh label delete "unused-label" --yes
   ```

4. **Update documentation**:
   - Update README with current taxonomy
   - Add label guide to CONTRIBUTING.md

## Integration with Project Boards

### Map Labels to Fields

Automatically set project fields based on labels:

**Priority field**:
- priority:critical → Priority: Critical
- priority:high → Priority: High
- priority:medium → Priority: Medium
- priority:low → Priority: Low

**Scope field**:
- scope:frontend → Scope: Frontend
- scope:backend → Scope: Backend

**Size field**:
- size:xs → Size: XS
- size:s → Size: S
- size:m → Size: M
- size:l → Size: L
- size:xl → Size: XL

### Automation Rules

**Auto-add to board**:
- Issues with `priority:high` → Add to "Sprint Planning" board
- Issues with `bug` → Add to "Bug Triage" board

**Auto-move columns**:
- Add `status:in-progress` → Move to "In Progress" column
- Add `status:needs-review` → Move to "Review" column

## Documentation

### Label Guide in README

Include a label guide in your README.md:

````markdown
## Labels

We use labels to categorize and prioritize issues:

### Types
- `bug` - Something isn't working
- `feature` - New feature request
- `documentation` - Documentation improvements

### Priority
- `priority:high` - Address soon
- `priority:medium` - Normal priority
- `priority:low` - Nice to have

### Scope
- `scope:frontend` - UI/UX changes
- `scope:backend` - Server/API changes

For a complete guide, see [LABELS.md](docs/LABELS.md)
````

### CONTRIBUTING.md Section

Add labeling guidelines to CONTRIBUTING.md:

````markdown
## Labeling Issues

When creating an issue:
1. Add a type label (bug, feature, etc.)
2. Add a priority label if urgent
3. Add scope labels if you know what area is affected

When triaging issues:
1. Verify type label is appropriate
2. Assign priority based on impact and urgency
3. Add scope labels after investigation
4. Add to relevant project boards
````

## Migration Guide

### From Old Labels to New Taxonomy

**Step 1**: Export current labels
```bash
gh label list --json name,description,color > old-labels.json
```

**Step 2**: Create migration mapping
```json
{
  "Bug": "bug",
  "High Priority": "priority:high",
  "Front End": "scope:frontend",
  "Backend": "scope:backend"
}
```

**Step 3**: Apply new taxonomy
```bash
python scripts/label-operations.py apply-preset --name comprehensive --force
```

**Step 4**: Migrate issues
```bash
# For each old → new mapping
gh issue list --label "High Priority" --json number | \
  jq -r '.[].number' | \
  xargs -I {} gh issue edit {} --add-label "priority:high" --remove-label "High Priority"
```

**Step 5**: Clean up old labels
```bash
gh label delete "High Priority" --yes
```

## Common Questions

### When should I use priority:critical vs priority:high?

**priority:critical**:
- System is down or unusable
- Security vulnerability
- Data loss risk
- Blocks multiple people

**priority:high**:
- Important feature broken
- Affects many users
- Should fix this sprint
- Blocks some work

### Should every issue have a scope label?

No, scope labels are optional and most useful for:
- Larger codebases with distinct areas
- Teams with specialized roles
- Routing issues to right people

Skip scope labels for:
- Small projects
- Documentation-only repos
- Issues that span multiple scopes

### How many labels is too many for one issue?

**Good**: 2-4 labels
- Type + Priority + Scope
- Example: bug, priority:high, scope:backend

**Acceptable**: 5-6 labels
- Add status or size if needed
- Example: feature, priority:medium, scope:frontend, size:l, status:in-progress

**Too many**: 7+ labels
- Probably over-categorizing
- Consider if all labels add value

### Should I use labels or milestones for versions?

**Use milestones for**:
- Version numbers (v1.0, v2.0)
- Sprint numbers (Sprint 5, Sprint 6)
- Time-based releases (Q1 2024, Q2 2024)

**Use labels for**:
- Categories (bug, feature)
- Priorities (priority:high)
- Scopes (scope:backend)
- Statuses (status:blocked)

Milestones group issues by delivery date, labels categorize by type/priority.
