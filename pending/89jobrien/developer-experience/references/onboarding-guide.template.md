---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: developer-experience
---

# Developer Onboarding Guide

**Project:** {{PROJECT_NAME}}
**Last Updated:** {{DATE}}
**Version:** {{VERSION}}

---

## Welcome

{{BRIEF_PROJECT_DESCRIPTION}}

### Quick Links

| Resource | Link |
|----------|------|
| Repository | {{REPO_URL}} |
| Documentation | {{DOCS_URL}} |
| Issue Tracker | {{ISSUES_URL}} |
| CI/CD | {{CI_URL}} |
| Slack/Discord | {{CHAT_URL}} |

---

## Day 1: Environment Setup

### Prerequisites

- [ ] {{PREREQUISITE_1}} (version {{VERSION}})
- [ ] {{PREREQUISITE_2}}
- [ ] Access to {{SYSTEM}}

### Clone & Install

```bash
git clone {{REPO_URL}}
cd {{PROJECT_NAME}}
{{INSTALL_COMMAND}}
```

### Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Required variables:

| Variable | Description | How to Get |
|----------|-------------|------------|
| `{{VAR_1}}` | {{DESC}} | {{INSTRUCTIONS}} |
| `{{VAR_2}}` | {{DESC}} | {{INSTRUCTIONS}} |

### Verify Setup

```bash
{{VERIFY_COMMAND}}
```

Expected output:

```
{{EXPECTED_OUTPUT}}
```

---

## Day 2: Codebase Orientation

### Project Structure

```
{{PROJECT_NAME}}/
├── {{DIR_1}}/        # {{DESCRIPTION}}
├── {{DIR_2}}/        # {{DESCRIPTION}}
├── {{DIR_3}}/        # {{DESCRIPTION}}
└── {{CONFIG_FILE}}   # {{DESCRIPTION}}
```

### Key Files

| File | Purpose |
|------|---------|
| `{{FILE_1}}` | {{PURPOSE}} |
| `{{FILE_2}}` | {{PURPOSE}} |

### Architecture Overview

{{ARCHITECTURE_DESCRIPTION}}

```
{{ARCHITECTURE_DIAGRAM}}
```

---

## Day 3: Development Workflow

### Running Locally

```bash
{{DEV_COMMAND}}
```

Access at: `http://localhost:{{PORT}}`

### Running Tests

```bash
{{TEST_COMMAND}}
```

### Code Style

We use {{LINTER/FORMATTER}}:

```bash
{{LINT_COMMAND}}
{{FORMAT_COMMAND}}
```

### Git Workflow

1. Create branch: `{{BRANCH_NAMING_CONVENTION}}`
2. Make changes
3. Run tests: `{{TEST_COMMAND}}`
4. Commit: Follow [Conventional Commits]({{COMMIT_GUIDE_URL}})
5. Push and create PR

---

## Week 1: First Tasks

### Starter Tasks

Good first issues to tackle:

1. {{STARTER_TASK_1}}
2. {{STARTER_TASK_2}}
3. {{STARTER_TASK_3}}

### Code Review Process

1. Create PR with description
2. Request review from {{REVIEWER}}
3. Address feedback
4. Merge when approved

---

## Key Concepts

### {{CONCEPT_1}}

{{EXPLANATION}}

### {{CONCEPT_2}}

{{EXPLANATION}}

### {{CONCEPT_3}}

{{EXPLANATION}}

---

## Common Tasks

### Adding a New {{COMPONENT}}

1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}

### Debugging

```bash
{{DEBUG_COMMAND}}
```

### Database Operations

```bash
{{DB_COMMAND}}
```

---

## Troubleshooting

### {{COMMON_ISSUE_1}}

**Symptom:** {{SYMPTOM}}

**Solution:**

```bash
{{SOLUTION}}
```

### {{COMMON_ISSUE_2}}

**Symptom:** {{SYMPTOM}}

**Solution:** {{SOLUTION}}

---

## Team & Communication

### Key Contacts

| Role | Name | Contact |
|------|------|---------|
| Tech Lead | {{NAME}} | {{CONTACT}} |
| Product | {{NAME}} | {{CONTACT}} |

### Meetings

| Meeting | Frequency | Time |
|---------|-----------|------|
| Standup | Daily | {{TIME}} |
| Sprint Planning | {{FREQ}} | {{TIME}} |

### Communication Norms

- {{NORM_1}}
- {{NORM_2}}

---

## Resources

### Documentation

- [{{DOC_1}}]({{URL}})
- [{{DOC_2}}]({{URL}})

### Learning Resources

- {{RESOURCE_1}}
- {{RESOURCE_2}}

---

## Checklist

### Setup Complete

- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] Environment configured
- [ ] Application runs locally
- [ ] Tests pass

### Orientation Complete

- [ ] Codebase structure understood
- [ ] Key files reviewed
- [ ] Architecture overview read
- [ ] First PR submitted

### Fully Onboarded

- [ ] Completed first task independently
- [ ] Participated in code review
- [ ] Attended team meetings
- [ ] Questions answered
