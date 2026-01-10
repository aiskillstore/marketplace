---
name: skill-developer
description: Claude Code 스킬, 훅, 에이전트, 명령어를 생성하고 관리하기 위한 메타 스킬. 새 스킬 생성, 스킬 트리거 설정, 훅 설정, Claude Code 인프라 관리 시 사용.
---

# Skill Developer Guide

## Purpose

Comprehensive guide for creating and managing Claude Code skills, hooks, agents, and commands. This meta-skill helps you build and configure Claude Code infrastructure components.

## When to Use This Skill

- Creating new skills
- Configuring skill triggers in skill-rules.json
- Setting up hooks
- Creating agents
- Adding slash commands
- Understanding skill activation patterns
- Customizing skill behavior

---

## Quick Start

### Creating a New Skill

1. **Create skill directory**:

   ```bash
   mkdir -p .claude/skills/{skill-name}
   ```

2. **Create SKILL.md file**:

   - Add frontmatter with `name` and `description`
   - Write comprehensive guidelines
   - Use progressive disclosure (main file + resources/)

3. **Update skill-rules.json**:
   - Add skill entry with triggers
   - Configure `fileTriggers` and `promptTriggers`
   - Set `enforcement` and `priority`

### Skill Structure

```
.claude/skills/
  {skill-name}/
    SKILL.md              # Main skill file
    resources/            # Optional: Additional resources
      pattern-1.md
      pattern-2.md
```

---

## Skill Configuration

### skill-rules.json Structure

```json
{
  "version": "1.0",
  "description": "Skill activation triggers",
  "skills": {
    "{skill-name}": {
      "type": "domain" | "guardrail",
      "enforcement": "suggest" | "block" | "warn",
      "priority": "critical" | "high" | "medium" | "low",
      "description": "Skill description",
      "promptTriggers": {
        "keywords": ["keyword1", "keyword2"],
        "intentPatterns": ["regex pattern"]
      },
      "fileTriggers": {
        "pathPatterns": ["app/**/*.tsx"],
        "pathExclusions": ["**/*.test.tsx"],
        "contentPatterns": ["import.*from.*next"]
      }
    }
  }
}
```

### Enforcement Types

- **suggest**: Skill suggestion appears but doesn't block execution
- **block**: Requires skill to be used before proceeding (guardrail)
- **warn**: Shows warning but allows proceeding

### Priority Levels

- **critical**: Highest - Always trigger when matched
- **high**: Important - Trigger for most matches
- **medium**: Moderate - Trigger for clear matches
- **low**: Optional - Trigger only for explicit matches

---

## File Triggers

### Path Patterns

Use glob patterns to match file paths:

```json
{
  "pathPatterns": [
    "app/**/*.tsx", // All .tsx files in app/
    "components/**/*.ts", // All .ts files in components/
    "**/*.tsx" // All .tsx files anywhere
  ]
}
```

### Path Exclusions

Exclude files from triggering:

```json
{
  "pathExclusions": [
    "**/*.test.tsx", // Test files
    "**/node_modules/**", // Dependencies
    "**/.next/**" // Build output
  ]
}
```

### Content Patterns

Match file content with regex:

```json
{
  "contentPatterns": [
    "from '@/components/ui/", // Shadcn imports
    "import.*from.*next", // Next.js imports
    "'use client'" // Client component directive
  ]
}
```

---

## Prompt Triggers

### Keywords

Simple keyword matching:

```json
{
  "keywords": ["component", "page", "route", "frontend"]
}
```

### Intent Patterns

Regex patterns for flexible matching:

```json
{
  "intentPatterns": [
    "(create|add|make|build).*?component", // Create component
    "(how to|best practice).*?react", // How to questions
    "app router.*?(page|route)" // App router related
  ]
}
```

---

## Skill Types

### Domain Skills

- **Purpose**: Provide guidelines for specific domains
- **Example**: frontend-dev-guidelines, backend-dev-guidelines
- **Enforcement**: Usually "suggest"

### Guardrail Skills

- **Purpose**: Enforce best practices and prevent mistakes
- **Example**: Code quality checks, security rules
- **Enforcement**: Usually "block" or "warn"

---

## Best Practices

### Skill Design

1. **Progressive Disclosure**: Main file + resources/ for detailed guides
2. **Clear Examples**: Include working code examples
3. **Quick Reference**: Add quick reference tables
4. **When to Use**: Clearly state when skill applies

### Trigger Configuration

1. **Specific Keywords**: Use domain-specific terms
2. **Flexible Patterns**: Use regex for intent matching
3. **Path Specificity**: Match actual project structure
4. **Avoid Over-triggering**: Use exclusions appropriately

### File Organization

1. **Modular Structure**: Split large skills into resources/
2. **Clear Naming**: Use descriptive skill names
3. **Documentation**: Document all configuration options

---

## Common Patterns

### Tech Stack Specific Skills

```json
{
  "frontend-dev-guidelines": {
    "fileTriggers": {
      "pathPatterns": ["app/**/*.tsx", "components/**/*.tsx"],
      "contentPatterns": ["from '@/components/ui/", "import.*from.*next"]
    },
    "promptTriggers": {
      "keywords": ["component", "shadcn", "next.js"],
      "intentPatterns": ["(create|build).*?component"]
    }
  }
}
```

### Framework Agnostic Skills

```json
{
  "error-tracking": {
    "fileTriggers": {
      "pathPatterns": ["**/*Controller.ts", "**/*Service.ts"],
      "contentPatterns": ["Sentry\\.", "captureException"]
    },
    "promptTriggers": {
      "keywords": ["error", "sentry", "exception"],
      "intentPatterns": ["(add|implement).*?error.*?handling"]
    }
  }
}
```

---

## Integration Checklist

When adding a new skill:

- [ ] Create skill directory and SKILL.md
- [ ] Write comprehensive guidelines
- [ ] Add to skill-rules.json
- [ ] Configure fileTriggers (pathPatterns, exclusions, contentPatterns)
- [ ] Configure promptTriggers (keywords, intentPatterns)
- [ ] Set appropriate enforcement and priority
- [ ] Test skill activation
- [ ] Document customization needs

---

## Troubleshooting

### Skill Not Triggering

1. Check pathPatterns match actual file paths
2. Verify keywords are spelled correctly
3. Test intentPatterns regex patterns
4. Check for pathExclusions blocking triggers

### Over-triggering

1. Add more specific pathPatterns
2. Use pathExclusions to filter out files
3. Make intentPatterns more specific
4. Lower priority level

### Skill File Not Found

1. Verify skill directory exists: `.claude/skills/{skill-name}/`
2. Check SKILL.md file exists
3. Verify skill name matches skill-rules.json entry

---

## Related Skills

- **frontend-dev-guidelines**: Frontend development patterns
- **backend-dev-guidelines**: Backend development patterns

---

**Skill Status**: Meta-skill for skill development and management
