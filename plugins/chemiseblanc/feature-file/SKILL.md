---
name: feature-file
description: Manage features.yml for tracking requirements and progress; use proactively ONLY when features.yml already exists, or invoke manually to create one; complements TodoWrite for persistent project state.
---

# Feature File Management

Manage `features.yml` - a waterfall-style planning document combining structured requirements tracking with incremental development.

## Quick Reference

```yaml
feature: "Feature Name"
phase: Requirements | Design | Implementation | Testing | Complete
version: 1
changelog: |
  ## [1]
  ### Added
  - Initial feature
decisions:
  - Decision rationale
known-issues:
  - Known bug or limitation
requirements:
  req-id:
    description: "When X, the system SHALL Y"
    status: Not-Started | In-Progress | Needs-Work | Complete
    tested-by: [test-id]
test-cases:
  test-id:
    name: "test_function_name"
    file: "tests/test_file.py"
    description: "Given X, when Y, then Z"
    passing: true | false
    type: unit | [integration, rainy-day]  # optional, string or list
---
# Next feature...
```

See `references/schema.md` for complete field documentation.

## Proactive Usage

This skill should be used automatically when features.yml exists.

### Before Starting Implementation

1. Check if `features.yml` exists in project root
2. If missing: do not use this skill proactively (stop here)
3. **Plan the work in features.yml before writing code:**
   - Add/update the feature with all requirements extracted from the user's request
   - Add anticipated test cases to `test-cases` (with `passing: false`)
   - Document design decisions in `decisions` if non-trivial choices are involved
4. Set the first requirement to `status: In-Progress`

### During Implementation

- Update `status` to `Complete` as requirements are finished
- Add test cases to `test-cases` when writing tests
- Update `passing` field after running tests
- Add discovered issues to `known-issues`

### After Completing Work

- Verify all implemented requirements are marked `Complete`
- Run `./scripts/feature-status.py --validate` to check consistency
- Commit features.yml changes with the implementation

### Relationship with TodoWrite

| Tool | Purpose | Persistence |
|------|---------|-------------|
| TodoWrite | Immediate session actions | Ephemeral |
| features.yml | Requirements and progress | Persistent (in repo) |

Use both: TodoWrite for what to do now, features.yml for durable project state.

## Phase Transitions

| From | To | Conditions |
|------|----|------------|
| Requirements | Design | All requirements have descriptions |
| Design | Implementation | `decisions` field exists (use `[]` if none needed) |
| Implementation | Testing | All requirements `In-Progress` or `Complete` |
| Testing | Complete | All requirements `Complete` AND all tests `passing: true` |

Scripts validate these rules and report errors.

## Workflows

### Agent Workflow (Condensed)

1. `ls features.yml` → exists? Read it : Create it
2. **Plan first**: Add feature, requirements, test-cases, decisions
3. Set first requirement `status: In-Progress`
4. Implement, then set `status: Complete`
5. Run tests, update `passing` status
6. `./scripts/feature-status.py --validate`
7. Commit with implementation changes

### Creating a New Feature File

1. Create `features.yml` with first feature:
   ```yaml
   feature: "Feature Name"
   phase: Requirements
   version: 1
   changelog: |
     ## [1]
     ### Added
     - Initial planning
   requirements:
     req-1:
       description: "Requirement description using EARS syntax"
       status: Not-Started
   ```
2. Run `./scripts/feature-status.py` to validate structure

**Minimal start** (for quick bootstrapping during implementation):

```yaml
feature: "Feature Name"
phase: Implementation
version: 1
changelog: |
  ## [1]
  ### Added
  - Initial implementation
requirements:
  req-1:
    description: "Requirement from user request"
    status: In-Progress
```

### Building from Existing Codebase

1. Identify logical feature boundaries in the code
2. For each feature:
   - Create feature document, set `phase` based on current maturity
   - Extract requirements from code behavior, comments, documentation
   - Discover existing tests and add to `test-cases`
   - Link tests to requirements via `tested-by`
   - Set `status` based on implementation state and test coverage
3. Run `./scripts/feature-status.py --validate` to check consistency
4. Run `./scripts/extract-work.py` to see gaps

### Development Workflow (Incremental Progress)

Work on ONE requirement at a time:

1. Run `./scripts/extract-work.py` to see incomplete requirements
2. Pick highest priority requirement, update `status: In-Progress`
3. Implement the requirement
4. Write/update tests, add to `test-cases` with `passing: false`
5. Run tests, update `passing: true` when passing
6. Update requirement `status: Complete`
7. Run `./scripts/feature-status.py` to check phase advancement eligibility
8. Repeat

### Version Management

1. Run `./scripts/check-version.py` to check for needed bumps
2. If bump recommended:
   - Increment `version` field
   - Add new changelog section:
     ```yaml
     changelog: |
       ## [2]
       ### Added
       - New capability
       
       ## [1]
       ...
     ```
   - Commit the update

## Scripts

All scripts read from `features.yml` in current directory. Scripts are executable and use inline dependencies via `uv run --script`.

### feature-status.py

Overview of all features with progress and test status (with breakdown by type if defined).

```bash
./scripts/feature-status.py                    # Plain text output
./scripts/feature-status.py --format markdown  # Markdown table
./scripts/feature-status.py --validate         # Exit 1 if validation errors
```

### extract-work.py

List requirements needing work (status != Complete).

```bash
./scripts/extract-work.py                      # All incomplete
./scripts/extract-work.py --phase Implementation
./scripts/extract-work.py --status In-Progress
./scripts/extract-work.py --format markdown
```

### extract-issues.py

List known issues across all features.

```bash
./scripts/extract-issues.py
./scripts/extract-issues.py --format json
```

### check-version.py

Check git history to see if versions need bumping.

```bash
./scripts/check-version.py
```

Compares when feature sections were last modified vs when `version` was last set.

## Best Practices

- **One requirement at a time**: Complete and verify before starting next
- **Update status immediately**: Keep file in sync with actual state
- **Document decisions**: Capture rationale in `decisions` before implementation
- **Track known issues**: Document bugs and limitations in `known-issues`
- **Bump version on requirement changes**: Any add, modify, or remove
- **Use EARS syntax** for requirements: "When X, the system SHALL Y"
- **Use Given/When/Then** for test descriptions

## Change Management

All requirement changes require a version bump. This ensures traceability and clear history.

### Adding Requirements to Existing Feature

1. Add requirement with `status: Not-Started`
2. Increment `version` field
3. Add changelog entry under `### Added`
4. If feature is past Design phase, consider whether new requirement needs design review

### Modifying Existing Requirements

1. Document rationale for the change
2. Update requirement `description`
3. Update `status`:
   - If was `Complete`: set to `Needs-Work`
   - Otherwise: keep current status
4. Review affected test cases in `tested-by` - update or mark as needing revision
5. Increment `version` field
6. Add changelog entry under `### Changed`

### Deprecating/Removing Requirements

1. Document rationale
2. Either:
   - Remove requirement entirely, OR
   - Move to `known-issues` as historical note (e.g., "req-x removed: no longer needed")
3. Remove or update associated test cases
4. Increment `version` field
5. Add changelog entry under `### Removed`

### Version Bump Triggers

Always bump version when:
- Adding, modifying, or removing requirements
- Shipping a milestone
- Significant scope changes
- Phase transitions to `Complete`
