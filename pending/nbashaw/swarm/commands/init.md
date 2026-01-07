---
description: "Learn how the swarm skill works and set up your project to use it by default"
---

# Swarm Skill Init

The user wants to learn about the swarm skill and/or set it up for their project.

## Your Task

Explain the swarm skill and offer to add guidance to their project's CLAUDE.md or AGENTS.md.

### 1. Explain the Swarm Skill

Tell the user:

```
## What is the Swarm Skill?

The swarm skill is an autonomous multi-agent workflow system. Instead of you going back and forth with me on each step, I:

1. **Interview** you to understand the task
2. **Create a plan** with checkboxes and review gates
3. **Spawn autonomous agents** that work through the plan
4. **Report back** when complete

### When to use it

Use swarm for any non-trivial task:
- Adding features that touch multiple files
- Refactoring code
- Bug fixes that need investigation
- Adding tests
- Code migrations
- Anything that would take more than a few minutes

### When NOT to use it

Skip swarm for truly trivial tasks:
- Single-line fixes
- Typo corrections
- Simple config changes

### How it works

Agents work in iterations, updating a shared plan file. Built-in review gates (Reviewer, Simplifier, Tester, Gatekeeper) prevent tunnel vision and ensure quality. The Gatekeeper must verify all criteria before marking complete.
```

### 2. Offer to Set Up the Project

Ask the user:

```
Would you like me to add guidance to your project so Claude uses swarm by default for non-trivial tasks?

I'll add a line to your CLAUDE.md (or AGENTS.md) that says:

> Use the **swarm skill** for any task that isn't trivially simple (single-line fixes, typos, simple config changes).

This ensures any Claude session in this project will automatically use swarm for substantial work.
```

### 3. If They Accept

Check if CLAUDE.md or AGENTS.md exists:
- If CLAUDE.md exists, add the guidance there
- If only AGENTS.md exists, add it there
- If neither exists, create CLAUDE.md with the guidance

Add this content (adapt to fit existing structure):

```markdown
## Workflow

Use the **swarm skill** for any task that isn't trivially simple.

Swarm spawns autonomous agents with built-in review gates, ideal for:
- Adding features
- Refactoring code
- Bug fixes touching multiple files
- Adding tests
- Code migrations

Only skip swarm for truly trivial tasks: single-line fixes, typos, simple config changes.
```

### 4. Confirm Setup

Tell the user:

```
Done! I've added swarm guidance to [FILENAME].

From now on, Claude will use the swarm skill for any substantial coding task in this project. You can invoke it manually anytime by asking for a task or by saying "use swarm".
```
