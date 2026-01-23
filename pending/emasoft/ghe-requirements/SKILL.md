---
name: ghe-requirements
description: This skill should be used when creating, updating, linking, or versioning requirements for GitHub Elements threads. Use when user mentions requirements, specs, REQ files, or when starting feature development. Provides the requirements folder structure, versioning system, and SERENA backup protocols.
---

## IRON LAW: User Specifications Are Sacred

**THIS LAW IS ABSOLUTE AND ADMITS NO EXCEPTIONS.**

1. **Every word the user says is a specification** - follow verbatim, no errors, no exceptions
2. **Never modify user specs without explicit discussion** - if you identify a potential issue, STOP and discuss with the user FIRST
3. **Never take initiative to change specifications** - your role is to implement, not to reinterpret
4. **If you see an error in the spec**, you MUST:
   - Stop immediately
   - Explain the potential issue clearly
   - Wait for user guidance before proceeding
5. **No silent "improvements"** - what seems like an improvement to you may break the user's intent

**Violation of this law invalidates all work produced.**

## Background Agent Boundaries

When running as a background agent, you may ONLY write to:
- The project directory and its subdirectories
- The parent directory (for sub-git projects)
- ~/.claude (for plugin/settings fixes)
- /tmp

Do NOT write outside these locations.

---

## GHE_REPORTS Rule (MANDATORY)

**ALL reports MUST be posted to BOTH locations:**
1. **GitHub Issue Thread** - Full report text (NOT just a link!)
2. **GHE_REPORTS/** - Same full report text (FLAT structure, no subfolders!)

**Report naming:** `<TIMESTAMP>_<title or description>_(<AGENT>).md`
**Timestamp format:** `YYYYMMDDHHMMSSTimezone`

**ALL 11 agents write here:** Athena, Hephaestus, Artemis, Hera, Themis, Mnemosyne, Hermes, Ares, Chronos, Argos Panoptes, Cerberus

**REQUIREMENTS/** is SEPARATE - permanent design documents, never deleted.

**Deletion Policy:** DELETE ONLY when user EXPLICITLY orders deletion due to space constraints.

---

# GHE Requirements Management

## Overview

Requirements in GHE are versioned markdown files stored in `REQUIREMENTS/` that serve as the source of truth for feature implementation. Every DEV thread MUST link to a requirements file before work begins.

## Folder Structure

```
REQUIREMENTS/
├── _templates/
│   └── REQ-TEMPLATE.md           # Template for new requirements
├── epic-{N}/                     # Requirements grouped by epic
│   ├── wave-{W}/                 # Further grouped by wave
│   │   ├── REQ-001-feature.md
│   │   └── REQ-002-feature.md
│   └── REQ-003-standalone.md     # Epic-level (not wave-specific)
├── standalone/                   # Requirements without epic
│   └── REQ-xxx-feature.md
└── CHANGELOG.md                  # Requirements version history
```

## Requirements File Format

Each REQ file MUST follow this structure:

```markdown
---
req_id: REQ-XXX
version: 1.0.0
status: draft|approved|implemented|deprecated
created: YYYY-MM-DD
updated: YYYY-MM-DD
epic: N (optional)
wave: W (optional)
linked_issues: [#N, #M] (filled by system)
---

# REQ-XXX: Feature Name

## 1. Overview
Brief description of the feature.

## 2. User Story
As a [user type], I want [goal] so that [benefit].

## 3. Acceptance Criteria
- [ ] AC-1: Specific, testable criterion
- [ ] AC-2: Another criterion
- [ ] AC-3: Third criterion

## 4. Technical Requirements
### 4.1 Functional
- FR-1: Functional requirement
- FR-2: Another functional requirement

### 4.2 Non-Functional
- NFR-1: Performance, security, etc.

## 5. Atomic Changes
Break down into smallest implementable units:
1. **CHANGE-1**: Description (creates: file.py, modifies: other.py)
2. **CHANGE-2**: Description (creates: test_file.py)
3. **CHANGE-3**: Description (modifies: config.yaml)

## 6. Test Requirements
For each atomic change, define tests:
- TEST-1 for CHANGE-1: What to test
- TEST-2 for CHANGE-2: What to test

## 7. Dependencies
- Requires: REQ-XXX (if any)
- Blocks: REQ-YYY (if any)

## 8. Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | YYYY-MM-DD | @user | Initial version |
```

## Creating Requirements

### Step 1: Create REQ File

```bash
# Determine next REQ number
LAST_REQ=$(find REQUIREMENTS -name "REQ-*.md" | sed 's/.*REQ-\([0-9]*\).*/\1/' | sort -n | tail -1)
NEXT_REQ=$(printf "%03d" $((LAST_REQ + 1)))

# Create from template
cp REQUIREMENTS/_templates/REQ-TEMPLATE.md "REQUIREMENTS/epic-${EPIC}/wave-${WAVE}/REQ-${NEXT_REQ}-${FEATURE_NAME}.md"
```

### Step 2: Fill Requirements
Use the orchestrator (Athena) to analyze the feature request and fill:
- User story
- Acceptance criteria
- Technical requirements
- Atomic changes breakdown
- Test requirements

### Step 3: Approve Requirements

```bash
# Change status from draft to approved
sed -i 's/status: draft/status: approved/' "$REQ_FILE"

# Commit with version tag
git add "$REQ_FILE"
git commit -m "REQ-${NEXT_REQ} v1.0.0: ${FEATURE_NAME} - approved"
```

### Step 4: Link to Issue

When creating a DEV thread, the issue body MUST include:

```markdown
## Requirements
- **Primary**: [REQ-XXX](../REQUIREMENTS/path/to/REQ-XXX.md) v1.0.0
- **Related**: [REQ-YYY](../REQUIREMENTS/path/to/REQ-YYY.md) (optional)
```

## Versioning Requirements

Requirements use semantic versioning:
- **MAJOR.MINOR.PATCH**
- PATCH: Typos, clarifications (no functional change)
- MINOR: Added criteria, new atomic changes
- MAJOR: Breaking changes to acceptance criteria

### Version Update Protocol

```bash
# Read current version
CURRENT_VERSION=$(grep "^version:" "$REQ_FILE" | cut -d' ' -f2)

# Bump version (example: minor bump)
NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1"."$2+1".0"}')

# Update file
sed -i "s/version: $CURRENT_VERSION/version: $NEW_VERSION/" "$REQ_FILE"
sed -i "s/updated: .*/updated: $(date +%Y-%m-%d)/" "$REQ_FILE"

# Add to revision history (manual step)

# Commit
git add "$REQ_FILE"
git commit -m "REQ-XXX v${NEW_VERSION}: Description of changes"
```

## SERENA Backup

Requirements are automatically backed up to SERENA memory:

```bash
# Backup all requirements to SERENA
mkdir -p .serena/memories/requirements
for req in REQUIREMENTS/**/*.md; do
  if [[ "$req" != *"_templates"* && "$req" != *"CHANGELOG"* ]]; then
    cp "$req" ".serena/memories/requirements/$(basename $req)"
  fi
done
```

**When to sync**:
- After any REQ file is created or updated
- After any DEV thread is claimed
- Before any context compaction

## Linking Requirements to Issues

### At Issue Creation

```bash
gh issue create \
  --title "[${EPIC}][DEV] Feature Name" \
  --label "phase:dev,epic:${EPIC},wave:${WAVE}" \
  --body "$(cat <<EOF
## Requirements

**Primary Requirement**: [REQ-${REQ_NUM}](REQUIREMENTS/epic-${EPIC}/wave-${WAVE}/REQ-${REQ_NUM}-name.md) v${VERSION}

### Acceptance Criteria (from REQ file)
- [ ] AC-1: Criterion
- [ ] AC-2: Criterion

### Atomic Changes
1. CHANGE-1: Description
2. CHANGE-2: Description
EOF
)"
```

### Updating Linked Issues

When requirements change, update all linked issues:

```bash
# Find issues linked to a requirement
LINKED_ISSUES=$(grep -l "REQ-${REQ_NUM}" .git/*)  # Or use GitHub search

# Post update notice
for issue in $LINKED_ISSUES; do
  gh issue comment "$issue" --body "## Requirements Updated

REQ-${REQ_NUM} updated to v${NEW_VERSION}.

### Changes
${CHANGE_DESCRIPTION}

### Impact
Review your implementation against the updated acceptance criteria."
done
```

## Validation Commands

### Check Requirements Linked

```bash
# Verify issue has requirements link
ISSUE_BODY=$(gh issue view $ISSUE --json body --jq '.body')
if ! echo "$ISSUE_BODY" | grep -q "REQUIREMENTS/.*REQ-"; then
  echo "ERROR: Issue #$ISSUE has no requirements linked!"
  exit 1
fi
```

### Verify Requirements File Exists

```bash
# Extract REQ path from issue
REQ_PATH=$(echo "$ISSUE_BODY" | grep -oP 'REQUIREMENTS/[^\s\)]+\.md' | head -1)
if [ ! -f "$REQ_PATH" ]; then
  echo "ERROR: Requirements file not found: $REQ_PATH"
  exit 1
fi
```

### Check Requirements Version

```bash
# Get version from issue link
LINKED_VERSION=$(echo "$ISSUE_BODY" | grep -oP 'v[0-9]+\.[0-9]+\.[0-9]+' | head -1)

# Get current version from file
CURRENT_VERSION=$(grep "^version:" "$REQ_PATH" | cut -d' ' -f2)

if [ "$LINKED_VERSION" != "$CURRENT_VERSION" ]; then
  echo "WARNING: Issue links to v$LINKED_VERSION but current is v$CURRENT_VERSION"
fi
```

## Integration with Thread Managers

### DEV Manager (Hephaestus)
- MUST verify requirements linked before claiming
- MUST break down into atomic changes from REQ file
- MUST write tests for each atomic change BEFORE implementation

### TEST Manager (Artemis)
- MUST verify all tests from REQ file are passing
- MUST check test coverage against atomic changes

### REVIEW Manager (Hera)
- MUST verify each acceptance criterion is met
- MUST check implementation matches technical requirements
- MUST verify atomic changes are complete

## Settings Awareness

Respects `.claude/ghe.local.md`:
```yaml
requirements_folder: REQUIREMENTS  # Default folder name
require_requirements: true         # Block DEV without requirements
auto_serena_backup: true          # Auto-backup to SERENA
```
