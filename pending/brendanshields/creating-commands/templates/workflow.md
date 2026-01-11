# Workflow Command Template

Use for commands that integrate with skills or agents.

## With Skills

```markdown
---
description: "{Brief description}"
allowed-tools:
  - Skill({skill-name})
---

# {Command Name}

Use the {skill-name} skill to {purpose}.

Context: $ARGUMENTS

Follow the skill's workflow to complete this task.
```

## With Agents

```markdown
---
description: "{Brief description}"
allowed-tools:
  - Task
---

# {Command Name}

Launch the {agent-name} agent to {purpose}.

Focus on: $ARGUMENTS

Report findings when complete.
```

## Example: Start Feature

```markdown
---
description: "Start a new feature using orbit workflow"
allowed-tools:
  - Skill(orbit-workflow)
argument-hint: "feature_name"
---

# Start Feature

Use the orbit-workflow skill to initialize a new feature.

Feature: $ARGUMENTS

1. Create feature directory in .spec/features/
2. Generate spec.md with user stories
3. Set status to specification
4. Report feature ID when complete
```

## Example: Code Review

```markdown
---
description: "Deep code review using analysis agent"
allowed-tools:
  - Task
argument-hint: "file_or_directory"
---

# Review Code

Launch the analyzing-codebase agent to review:

Target: $ARGUMENTS

Focus areas:
- Security vulnerabilities
- Performance issues
- Code quality
- Test coverage

Provide actionable recommendations.
```

## Example: Multi-Step Deploy

```markdown
---
description: "Full deployment pipeline"
allowed-tools:
  - Bash(npm:*)
  - Bash(git:*)
  - Task
argument-hint: "environment"
---

# Deploy

Deploy to $1:

1. Run tests
   - Execute `npm test`
   - Fail if tests don't pass

2. Build
   - Execute `npm run build`
   - Verify output in dist/

3. Pre-deploy checks
   - Launch validating-artifacts agent
   - Ensure no breaking changes

4. Deploy
   - Push to $1 environment
   - Wait for health check

5. Verify
   - Report deployment status
   - Show access URL
```

## Usage

Save as `.claude/commands/{command-name}.md`

Run: `/{command-name} args`
