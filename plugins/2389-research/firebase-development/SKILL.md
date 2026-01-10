---
name: firebase-development
description: This skill should be used when working with Firebase projects, including initializing projects, adding Cloud Functions or Firestore collections, debugging emulator issues, or reviewing Firebase code. Triggers on "firebase", "firestore", "cloud functions", "emulator", "firebase auth", "deploy to firebase", "firestore rules".
---

# Firebase Development

## Overview

This skill system guides Firebase development using proven patterns from production projects. It routes to specialized sub-skills based on detected intent.

**Sub-skills:**
- `firebase-development:project-setup` - Initialize new Firebase projects
- `firebase-development:add-feature` - Add functions/collections/endpoints
- `firebase-development:debug` - Troubleshoot emulator and runtime issues
- `firebase-development:validate` - Review Firebase code for security/patterns

## When This Skill Applies

- Starting new Firebase projects
- Adding Cloud Functions or Firestore collections
- Debugging emulator issues or rule violations
- Reviewing Firebase code for security and patterns
- Setting up multi-hosting configurations
- Implementing authentication (API keys or Firebase Auth)

## Routing Logic

### Keywords by Sub-Skill

**project-setup:**
- "new firebase project", "initialize firebase", "firebase init"
- "set up firebase", "create firebase app", "start firebase project"

**add-feature:**
- "add function", "create endpoint", "new tool", "add api"
- "new collection", "add feature", "build", "implement"

**debug:**
- "error", "not working", "debug", "emulator issue"
- "rules failing", "permission denied", "troubleshoot", "deployment failed"

**validate:**
- "review firebase", "check firebase", "validate", "audit firebase"
- "look at firebase code", "security review"

### Routing Process

1. **Analyze Request**: Check for routing keywords
2. **Match Sub-Skill**: Identify best match based on keyword density
3. **Announce**: "I'm using the firebase-development:[sub-skill] skill to [action]"
4. **Route**: Load and execute the sub-skill
5. **Fallback**: If ambiguous, use AskUserQuestion with 4 options

### Fallback Example

If intent is unclear, ask:

```
Question: "What Firebase task are you working on?"
Options:
  - "Project Setup" (Initialize new Firebase project)
  - "Add Feature" (Add functions, collections, endpoints)
  - "Debug Issue" (Troubleshoot errors or problems)
  - "Validate Code" (Review against patterns)
```

## Reference Projects

Patterns are extracted from three production Firebase projects:

| Project | Path | Key Patterns |
|---------|------|--------------|
| **oneonone** | `/Users/dylanr/work/2389/oneonone` | Express API, custom API keys, server-write-only |
| **bot-socialmedia** | `/Users/dylanr/work/2389/bot-socialmedia-server` | Domain-grouped functions, Firebase Auth + roles |
| **meme-rodeo** | `/Users/dylanr/work/2389/meme-rodeo` | Individual function files, entitlements |

## Pattern Summaries

### Multi-Hosting Setup

Three options based on needs:

| Option | When to Use | Key Feature |
|--------|-------------|-------------|
| `site:` based | Multiple independent URLs | Simple, no build coordination |
| `target:` based | Need predeploy hooks | Build scripts run automatically |
| Single + rewrites | Smaller projects | All under one domain |

**Details:** See `docs/examples/multi-hosting-setup.md`

### Authentication

| Pattern | When to Use | Example |
|---------|-------------|---------|
| Custom API keys | MCP tools, server-to-server | oneonone |
| Firebase Auth + roles | User-facing apps | bot-socialmedia |
| Hybrid | Both patterns needed | Web UI + API access |

**Details:** See `docs/examples/api-key-authentication.md`

### Cloud Functions Architecture

| Pattern | When to Use | Structure |
|---------|-------------|-----------|
| Express app | API with middleware, routing | `app.post('/mcp', handler)` |
| Domain-grouped | Feature-rich apps | `posts.ts`, `journal.ts` |
| Individual files | Maximum modularity | One function per file |

**Details:** See `docs/examples/express-function-architecture.md`

### Security Model

| Model | When to Use | Complexity |
|-------|-------------|------------|
| Server-write-only | Light-write apps, high security | Simple rules |
| Client-write + validation | High-volume writes, real-time | Complex rules |

**Strongly prefer server-write-only** for light-write applications.

**Details:** See `docs/examples/firestore-rules-patterns.md`

### Emulator-First Development

Always develop locally with emulators:

```bash
firebase emulators:start
# Access UI at http://127.0.0.1:4000
```

**Key settings in firebase.json:**
- `singleProjectMode: true` - Essential for emulators to work together
- `ui.enabled: true` - Access debug UI

**Details:** See `docs/examples/emulator-workflow.md`

## Modern Tooling Standards

All Firebase projects follow these standards:

| Tool | Purpose | Config File |
|------|---------|-------------|
| TypeScript | Type safety | `tsconfig.json` |
| vitest | Testing | `vitest.config.ts` |
| biome | Linting + formatting | `biome.json` |

### ABOUTME Comment Pattern

Every TypeScript file starts with 2-line ABOUTME comment:

```typescript
// ABOUTME: Brief description of what this file does
// ABOUTME: Second line with additional context
```

### Testing Requirements

- **Unit tests**: Test handlers/utilities in isolation
- **Integration tests**: Test with emulators running
- Both required for every feature

## Common Gotchas

| Issue | Solution |
|-------|----------|
| Emulator ports in use | `lsof -i :5001`, kill process |
| Admin SDK vs Client SDK | Admin bypasses rules, client respects rules |
| Cold start delays | First call takes 5-10s, normal |
| Data persistence | Use Ctrl+C (not kill) to export data |
| CORS in functions | `app.use(cors({ origin: true }))` |

## Summary

This orchestrator routes to specialized sub-skills:

1. Detects intent via keywords
2. Routes to appropriate sub-skill
3. Sub-skills use TodoWrite checklists
4. All reference shared patterns in `docs/examples/`

**Sub-Skills:**
- `firebase-development:project-setup` - Initialize new projects
- `firebase-development:add-feature` - Add functions/collections
- `firebase-development:debug` - Troubleshoot issues
- `firebase-development:validate` - Review code
