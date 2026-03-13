# BMAD Orchestrator Reference

This document provides detailed reference information for the BMAD Orchestrator skill.

## Table of Contents
- [Workflow Routing Logic](#workflow-routing-logic)
- [Project Level Guidelines](#project-level-guidelines)
- [Status File Structure](#status-file-structure)
- [Configuration Details](#configuration-details)
- [File Operations](#file-operations)
- [Variable Substitution](#variable-substitution)

## Workflow Routing Logic

### Determination Algorithm

```
Input: workflow_status array from docs/bmm-workflow-status.yaml
Output: recommended next workflow command

Step 1: Identify current phase
  - Scan workflow_status array
  - Find last completed workflow (status = file path)
  - Determine phase number of last completion

Step 2: Check for required workflows in current/next phase
  - If in Phase 1 (Analysis):
    * If no product-brief: Recommend /product-brief
    * If product-brief complete: Move to Phase 2

  - If in Phase 2 (Planning):
    * Level 0-1:
      - If no tech-spec: Recommend /tech-spec (required)
      - If PRD desired: Suggest /prd (optional)
    * Level 2+:
      - If no PRD: Recommend /prd (required)
      - If tech-spec desired: Suggest /tech-spec (optional)

  - If in Phase 3 (Solutioning):
    * Level 2+:
      - If no architecture: Recommend /architecture (required)
    * Level 0-1:
      - Skip to Phase 4

  - If in Phase 4 (Implementation):
    * If no sprint-status.yaml: Recommend /sprint-planning
    * If sprint active: Recommend /create-story
    * If stories exist: Recommend /dev-story

Step 3: Return recommendation with explanation
```

### Phase Transition Rules

**Phase 1 → Phase 2:**
- Transition when: Product brief complete OR user explicitly skips analysis
- Required before transition: None (Analysis is optional)

**Phase 2 → Phase 3:**
- Transition when: PRD or Tech Spec complete
- Required before transition:
  - Level 0-1: Tech Spec complete
  - Level 2+: PRD complete
- Gate rule: if the current phase document already has a terminal plannotator result for the same document hash, do not relaunch review until the document changes

**Phase 3 → Phase 4:**
- Transition when: Architecture complete (if required)
- Required before transition:
  - Level 0-1: None (skip Phase 3)
  - Level 2+: Architecture complete
- Gate rule: phase advancement still requires a reviewed artifact; unchanged reviewed architecture should not be re-opened

**Phase 4 completion:**
- All stories in sprint-status.yaml marked as "done"
- Final review/retrospective complete

## Project Level Guidelines

### Level 0: Single Atomic Change (1 story)

**Characteristics:**
- Bug fix
- Small configuration change
- Single file modification
- No breaking changes

**Required workflows:**
- Tech Spec (brief, 1-2 pages)
- Single story
- Direct implementation

**Skip:**
- Product brief (unless complex bug)
- PRD
- Architecture
- Sprint planning

**Typical timeline:** Hours to 1 day

### Level 1: Small Feature (1-10 stories)

**Characteristics:**
- New small feature
- Limited scope
- 1-3 files affected
- Minimal dependencies

**Required workflows:**
- Tech Spec
- Sprint planning (simple)

**Optional but recommended:**
- Product brief (if feature requires context)
- PRD (if stakeholder alignment needed)

**Skip:**
- Architecture (unless significant design needed)

**Typical timeline:** 1-5 days

### Level 2: Medium Feature Set (5-15 stories)

**Characteristics:**
- Multiple related features
- 5-20 files affected
- Some dependencies
- Database changes likely

**Required workflows:**
- PRD
- Architecture
- Sprint planning

**Optional:**
- Product brief (recommended)
- Tech spec (for complex components)

**Typical timeline:** 1-3 weeks

### Level 3: Complex Integration (12-40 stories)

**Characteristics:**
- System integration
- Multiple subsystems
- 20-50 files affected
- API contracts
- Third-party integrations

**Required workflows:**
- Product brief (strongly recommended)
- PRD (detailed)
- Architecture (comprehensive)
- Sprint planning (multiple sprints)

**Typical timeline:** 3-8 weeks

### Level 4: Enterprise Expansion (40+ stories)

**Characteristics:**
- Major system overhaul
- 50+ files affected
- Multiple teams
- Platform changes
- Infrastructure updates

**Required workflows:**
- Product brief (required)
- PRD (extensive)
- Architecture (system-wide)
- Sprint planning (multiple sprints)
- Gate checks

**Typical timeline:** 2-6 months

## Status File Structure

### Workflow Status Schema

```yaml
# docs/bmm-workflow-status.yaml

project_name: "string"
project_type: "web-app|mobile-app|api|game|library|other"
project_level: 0-4
communication_language: "string"
output_language: "string"
last_updated: "ISO-8601 timestamp"

workflow_status:
  - name: "workflow-name"
    phase: 1-4
    status: "optional|recommended|required|{file-path}|skipped"
    description: "Brief description"
    # Added by phase-gate-review.sh when plannotator approves the document:
    plannotator_review: "approved"       # set on plannotator Approve click
    reviewed_at: "ISO-8601 timestamp"   # timestamp of approval
```

### Status Values

- **"optional"** - Workflow can be skipped without impact
- **"recommended"** - Strongly suggested but not blocking
- **"required"** - Must be completed to proceed
- **"conditional"** - Required based on project level (replaced during init)
- **"{file-path}"** - Completed, shows output file location
- **"skipped"** - User explicitly chose to skip

### plannotator Review Fields

Written by `scripts/phase-gate-review.sh` when a phase document is approved via plannotator:

- **`plannotator_review`** - `"approved"` when the document passed plannotator gate review
- **`reviewed_at`** - ISO-8601 timestamp of when the review was approved

These fields are optional — they are only present on workflow entries that have been reviewed. Use them to audit which phase documents were human-reviewed before phase transition.
If you persist a document hash alongside them, the recommended policy is "same hash, same decision, no re-entry".

### Updating Status

When a workflow completes:
1. Read docs/bmm-workflow-status.yaml
2. Find workflow by name
3. Update status to file path: `"docs/prd-myapp-2025-01-11.md"`
4. Update last_updated timestamp
5. Write updated file

Example Edit operation:
```yaml
# Before
- name: prd
  phase: 2
  status: "required"
  description: "Product Requirements Document"

# After
- name: prd
  phase: 2
  status: "docs/prd-myapp-2025-01-11.md"
  description: "Product Requirements Document"
```

## Configuration Details

### Project Config (bmad/config.yaml)

Complete schema:
```yaml
# Project identification
project_name: "string"
project_type: "web-app|mobile-app|api|game|library|other"
project_level: 0-4

# Output settings
output_folder: "docs"  # relative to project root
stories_folder: "docs/stories"

# Language settings
communication_language: "English|Spanish|French|etc"
document_output_language: "English|Spanish|French|etc"

# BMAD version
bmad_version: "6.0.0"

# Optional: Custom overrides
agent_overrides_folder: "bmad/agent-overrides"
```

### Global Config (~/.claude/config/bmad/config.yaml)

```yaml
version: "6.0.0"
ide: "claude-code"

# User defaults
user_name: "string"
user_skill_level: "beginner|intermediate|expert"

# Communication defaults
communication_language: "English"
document_output_language: "English"

# Default paths
default_output_folder: "docs"

# Enabled modules
modules_enabled:
  - core
  - bmm
  # - bmb (optional)
  # - cis (optional)

# Advanced settings
auto_update_status: true
verbose_mode: false
```

### Config Priority

1. Project config (bmad/config.yaml) - highest priority
2. Global config (~/.claude/config/bmad/config.yaml) - default values
3. Built-in defaults - fallback

## File Operations

### Reading Config Files

**Load project config:**
```
Tool: Read
Path: {project-root}/bmad/config.yaml
Parse: YAML
Extract: project_name, project_type, project_level, output_folder
```

**Load global config:**
```
Tool: Read
Path: ~/.claude/config/bmad/config.yaml
Parse: YAML
Extract: user_name, communication_language, default_output_folder
```

**Merge configs:**
```
Result = Global config + Project config (project overrides global)
```

### Writing Status Files

**Create workflow status:**
```
Tool: Write
Path: {project-root}/{output_folder}/bmm-workflow-status.yaml
Content: Processed template with variables substituted
```

**Update workflow status:**
```
Tool: Edit
Path: {project-root}/{output_folder}/bmm-workflow-status.yaml
Old: status: "required"
New: status: "docs/prd-myapp-2025-01-11.md"
```

### Directory Creation

**Initialize project structure:**
```
Tool: Bash
Commands:
  mkdir -p bmad/agent-overrides
  mkdir -p docs/stories
  mkdir -p .claude/commands/bmad
```

## Variable Substitution

### Standard Variables

Used in templates during initialization:

```
{{PROJECT_NAME}}           → config: project_name
{{PROJECT_TYPE}}           → config: project_type
{{PROJECT_LEVEL}}          → config: project_level
{{USER_NAME}}              → global config: user_name
{{DATE}}                   → current date (YYYY-MM-DD)
{{TIMESTAMP}}              → current timestamp (ISO 8601)
{{OUTPUT_FOLDER}}          → config: output_folder
```

### Conditional Variables

Based on project level:

```
{{PRD_STATUS}}             → "required" if level >= 2
                           → "recommended" if level == 1
                           → "optional" if level == 0

{{TECH_SPEC_STATUS}}       → "required" if level <= 1
                           → "optional" if level >= 2

{{ARCHITECTURE_STATUS}}    → "required" if level >= 2
                           → "optional" if level <= 1
```

### Substitution Process

1. Load template file
2. Collect variable values from:
   - Project config
   - Global config
   - Current date/time
   - User input
3. Replace all {{VARIABLE}} occurrences
4. Validate no unreplaced variables remain
5. Return processed content

Example:
```yaml
# Template
project_name: "{{PROJECT_NAME}}"
project_level: {{PROJECT_LEVEL}}

# After substitution with project_name="MyApp", project_level=2
project_name: "MyApp"
project_level: 2
```

## File Path Standards

### Standard Paths

```
Project root: {project-root}/
Config: {project-root}/bmad/config.yaml
Status: {project-root}/{output_folder}/bmm-workflow-status.yaml
Sprint: {project-root}/{output_folder}/sprint-status.yaml
Stories: {project-root}/{output_folder}/stories/
Templates: {project-root}/bmad/agent-overrides/ (optional)
```

### Output File Naming

Convention: `{workflow-name}-{project-name}-{date}.md`

Examples:
```
docs/product-brief-myapp-2025-01-11.md
docs/prd-myapp-2025-01-11.md
docs/architecture-myapp-2025-01-11.md
docs/tech-spec-myapp-2025-01-11.md
```

### Story File Naming

Convention: `story-{epic-id}-{story-id}.md`

Examples:
```
docs/stories/story-E001-S001.md
docs/stories/story-E001-S002.md
docs/stories/story-E002-S001.md
```

## Error Handling Patterns

### Missing Config File

```
Error: bmad/config.yaml not found

Response:
  1. Inform user project not initialized
  2. Display: "BMAD not detected in this project."
  3. Ask: "Would you like to initialize BMAD with /workflow-init?"
  4. Do NOT proceed with operation
```

### Invalid YAML

```
Error: YAML parsing failed

Response:
  1. Show error message
  2. Display file path
  3. Show line number if available
  4. Options:
     a. "I can try to fix the YAML syntax"
     b. "You can manually edit the file"
     c. "I can reinitialize with /workflow-init (will overwrite)"
```

### Inconsistent Status

```
Error: Status file doesn't match project level

Example: Level 2 project but PRD marked as "optional"

Response:
  1. Explain inconsistency
  2. Show expected vs actual
  3. Offer: "I can regenerate the status file to match your project level"
```

### Missing Template

```
Error: Template file not found

Response:
  1. Log warning (if verbose mode)
  2. Use inline fallback template
  3. Continue operation
  4. Note: "Using default template"
```

## Display Formatting

### Status Display Format

```
Project: {project_name} ({project_type}, Level {level})

✓ Phase 1: Analysis
  ✓ product-brief (docs/product-brief-myapp-2025-01-11.md)
  - research (optional)

→ Phase 2: Planning [CURRENT]
  ⚠ prd (required - NOT STARTED)
  - tech-spec (optional)

Phase 3: Solutioning
  - architecture (required)

Phase 4: Implementation
  - sprint-planning (required)
```

### Symbols Used

- `✓` - Completed
- `⚠` - Required but not started
- `→` - Current phase indicator
- `-` - Optional or not applicable

### Color Coding (if supported)

- Green: Completed workflows
- Yellow: Required but incomplete
- Gray: Optional workflows
- Blue: Current phase

## Best Practices

### For Initialization

1. Always collect project info before creating files
2. Validate project level is 0-4
3. Create all directories before files
4. Use absolute paths for file operations
5. Confirm successful creation to user

### For Status Checks

1. Load config first to get output_folder path
2. Check if status file exists before reading
3. Parse YAML carefully with error handling
4. Display in clear, hierarchical format
5. Always provide actionable next step

### For Routing

1. Check current phase before recommending
2. Consider project level in recommendations
3. Explain why a workflow is recommended
4. Offer to execute recommended workflow
5. Allow user to choose different path

### For Updates

1. Read current file before editing
2. Update timestamp when modifying
3. Validate YAML after changes
4. Confirm update to user
5. Update related files if needed (e.g., sprint-status)
