---
name: project-scaffolder
description: "Creates plan.md, task.md, persona.md, project-context.md, and CLAUDE.md for new self-learning resource projects. Use when: (1) /init command is invoked, (2) setting up a new tutorial/guide/documentation project, (3) structure-designer agent needs templates for learning resource structure design. Provides hierarchical Part/Chapter/Section templates with page allocation."
allowed-tools: Read, Write, Bash, Glob
---

# Project Scaffolder Skill

This skill provides templates and guidance for scaffolding new self-learning resource projects.

## Templates

The following templates are available in this skill directory:

| Template | Purpose |
|----------|---------|
| [plan-template.md](plan-template.md) | Project structure with Part/Chapter/Section hierarchy |
| [task-template.md](task-template.md) | Session-based task checklist mirroring plan.md |
| [persona-template.md](persona-template.md) | Writer/Reader persona and code policy definitions |
| [project-context-template.md](project-context-template.md) | Target environment and reference URLs |
| [claude-md-template.md](claude-md-template.md) | CLAUDE.md project instructions |

## Workflow

### 1. Information Gathering

Before scaffolding, collect the following information:

- **Topic**: Subject of the learning resource
- **Total Pages**: Estimated page count (50/100/200+)
- **Language**: Primary language (ko/en)
- **Target Audience**: Experience level (beginner/intermediate/advanced)
- **Target Environment**: OS, tools, versions

### 2. File Generation Order

1. `plan.md` - Main structure document (use plan-template.md)
2. `task.md` - Session-divided checklist (use task-template.md)
3. `persona.md` - Writer/Reader definitions (use persona-template.md)
4. `project-context.md` - Environment and references (use project-context-template.md)
5. `CLAUDE.md` - Project instructions for Claude (use claude-md-template.md)

### 3. Structure Guidelines

#### Hierarchy

- **Part**: Major theme (50-100 pages), contains 3-6 chapters
- **Chapter**: Topic group (15-30 pages), contains 3-5 sections
- **Section**: Single concept (5-12 pages)

#### Page Allocation Formula

| Content Type | Percentage |
|--------------|------------|
| Introduction/Overview | 5-8% |
| Core Content | 60-70% |
| Practice/Examples | 20-25% |
| Summary/Review | 5-8% |

### 4. Session Division Rules

When creating task.md, divide work into Claude Code sessions:

- **1 session** = 3-5 sections or 20-40 pages
- Group sections within the same Chapter/Part
- Consider dependencies (prerequisite → subsequent)
- Mark session boundaries with HTML comments:

```markdown
<!-- Session 1: Part 1 Foundations -->
- [ ] 1.1 Introduction (8p)
- [ ] 1.2 Core Concepts (7p)

<!-- Session 2: Part 1 Architecture -->
- [ ] 1.3 System Design (10p)
```

### 5. Placeholder Variables

Use `{VARIABLE_NAME}` format for all placeholders:

| Variable | Description |
|----------|-------------|
| `{PROJECT_TITLE}` | Project name |
| `{TARGET_SYSTEM}` | Target OS/environment |
| `{TARGET_AUDIENCE}` | Reader experience level |
| `{TOTAL_PAGES}` | Total estimated pages |
| `{DATE}` | Creation/update date |
| `{PART_TITLE}` | Part title |
| `{CHAPTER_TITLE}` | Chapter title |
| `{SECTION_TITLE}` | Section title |
| `{PAGES}` | Page count for section |

## Quality Checklist

Before completing scaffolding, verify:

- [ ] All placeholder variables use `{VARIABLE_NAME}` format
- [ ] plan.md has proper Part/Chapter/Section hierarchy
- [ ] task.md mirrors plan.md structure exactly
- [ ] Session boundaries are marked with HTML comments
- [ ] Page allocations sum to total target pages
- [ ] All template files are properly referenced
