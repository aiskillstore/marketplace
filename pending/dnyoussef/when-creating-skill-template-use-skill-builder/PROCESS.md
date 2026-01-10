# Skill Builder - Detailed Workflow

## Process Overview

Generate complete Claude Code Skills with proper structure, YAML frontmatter, documentation, and validation.

## Phase Breakdown

### Phase 1: Design Structure (5 min)

**Objective**: Define skill components and metadata

**Agent**: Base-Template-Generator

**Steps**:
1. Gather skill requirements (name, category, agents, phases)
2. Define YAML frontmatter structure
3. Plan phase architecture
4. Identify triggers and outputs

**Outputs**: `requirements.json`, `phase-structure.json`

---

### Phase 2: Generate Template (5 min)

**Objective**: Create 4 core skill files

**Agent**: Base-Template-Generator

**Steps**:
1. Generate SKILL.md with YAML and phase structure
2. Create README.md quick start guide
3. Build PROCESS.md detailed workflow
4. Generate process-diagram.gv GraphViz visualization

**Outputs**: `SKILL.md`, `README.md`, `PROCESS.md`, `process-diagram.gv`

---

### Phase 3: Implement Functionality (8 min)

**Objective**: Add implementation details

**Agent**: Coder

**Steps**:
1. Add code examples for each phase
2. Define memory patterns
3. Integrate hooks (pre-task, post-task)
4. Create script templates

**Outputs**: Enhanced files with implementation

---

### Phase 4: Test Skill (5 min)

**Objective**: Validate skill correctness

**Agent**: Coder

**Steps**:
1. Validate YAML syntax
2. Validate GraphViz syntax
3. Run skill dry-run test
4. Check documentation completeness

**Outputs**: `validation-report.json`

---

### Phase 5: Document Usage (2 min)

**Objective**: Add usage guide and examples

**Agent**: Base-Template-Generator

**Steps**:
1. Add usage examples (CLI, programmatic)
2. Create troubleshooting guide
3. Generate completion report

**Outputs**: Updated documentation, `completion-report.json`

---

## Workflow Diagram

```
Requirements
    ↓
[Design Structure]
    ↓
Phase Plan
    ↓
[Generate Template]
    ↓
4 Core Files
    ↓
[Implement]
    ↓
Enhanced Files
    ↓
[Test]
    ↓
Validation Results
    ↓
[Document]
    ↓
Complete Skill
```

## YAML Frontmatter Structure

```yaml
name: when-[trigger]-use-[skill-name]
version: 1.0.0
description: Purpose
category: utilities|development|testing|machine-learning
tags: [tag1, tag2]
agents: [agent1, agent2]
difficulty: beginner|intermediate|advanced
estimated_duration: 15-30min
success_criteria: [criterion1, criterion2]
validation_method: test_type
dependencies: [claude-flow@alpha]
prerequisites: [requirement1]
outputs: [output1, output2]
triggers: [trigger1, trigger2]
```

## File Structure

```
skill-name/
├── SKILL.md          # Main specification (YAML + phases)
├── README.md         # Quick start guide
├── PROCESS.md        # Detailed workflow
└── process-diagram.gv # Visual diagram
```

## Best Practices

1. **Naming Convention**: `when-[condition]-use-[skill-name]`
2. **Phase Count**: 3-5 phases optimal
3. **Duration**: Keep phases 2-10 minutes each
4. **Validation**: Always include validation criteria
5. **Examples**: Provide concrete code examples

For implementation details, see SKILL.md
