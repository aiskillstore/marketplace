---
name: firebase-development-project-setup
description: This skill should be used when initializing a new Firebase project with proven architecture. Triggers on "new firebase project", "initialize firebase", "firebase init", "set up firebase", "create firebase app", "start firebase project". Guides through CLI setup, architecture choices, and emulator configuration.
---

# Firebase Project Setup

## Overview

This sub-skill guides initializing a new Firebase project with proven architecture patterns. It handles Firebase CLI setup, architecture decisions, emulator configuration, and initial project structure.

**Key principles:**
- Use TypeScript for all functions
- Configure emulators from the start
- Choose architecture patterns early (hosting, auth, functions, security)
- Set up testing infrastructure immediately

## When This Sub-Skill Applies

- Starting a brand new Firebase project
- Setting up Firebase for the first time in a repository
- User says: "new firebase project", "initialize firebase", "firebase init", "set up firebase"

**Do not use for:**
- Adding features to existing projects → `firebase-development:add-feature`
- Debugging existing setup → `firebase-development:debug`

## Architecture Decisions

Use AskUserQuestion to gather these four decisions upfront:

### 1. Hosting Configuration
- **Single Site** - One hosting site, simple project
- **Multiple Sites (site:)** - Multiple independent URLs
- **Multiple with Builds (target:)** - Multiple sites with predeploy hooks

**Reference:** `docs/examples/multi-hosting-setup.md`

### 2. Authentication Approach
- **API Keys** - MCP tools, server-to-server, programmatic access
- **Firebase Auth** - User-facing app with login UI
- **Both** - Firebase Auth for web + API keys for tools

**Reference:** `docs/examples/api-key-authentication.md`

### 3. Functions Architecture
- **Express API** - Many related endpoints, need middleware, RESTful routing
- **Domain Grouped** - Feature-rich app with distinct areas (posts, admin)
- **Individual Files** - Independent functions, maximum modularity

**Reference:** `docs/examples/express-function-architecture.md`

### 4. Security Model
- **Server-Write-Only** (Preferred) - Cloud Functions handle all writes
- **Client-Write** - High-volume writes, need fastest UX, complex rules

**Reference:** `docs/examples/firestore-rules-patterns.md`

## TodoWrite Workflow

Create checklist with these 14 steps:

### Step 1: Verify Firebase CLI

```bash
firebase --version  # Install via npm install -g firebase-tools if missing
firebase login
```

### Step 2: Create Project Directory

```bash
mkdir my-firebase-project && cd my-firebase-project
git init && git branch -m main
```

Create `.gitignore` with: `node_modules/`, `.env`, `.env.local`, `.firebase/`, `lib/`, `dist/`

### Step 3: Run Firebase Init

```bash
firebase init
```

Select: Firestore, Functions, Hosting, Emulators. Choose TypeScript for functions.

### Step 4: Gather Architecture Decisions

Use AskUserQuestion for the four decisions above.

### Step 5: Configure firebase.json

Set up based on hosting decision. Critical emulator settings:
```json
{
  "emulators": {
    "singleProjectMode": true,
    "ui": { "enabled": true, "port": 4000 }
  }
}
```

**Reference:** `docs/examples/multi-hosting-setup.md`

### Step 6: Set Up Functions Structure

Based on architecture choice:

**Express:** Create `middleware/`, `tools/`, `services/`, `shared/`
**Domain-Grouped:** Create `shared/types/`, `shared/validators/`
**Individual:** Create `functions/`

Install dependencies: `express`, `cors`, `firebase-admin`, `firebase-functions`, `vitest`, `biome`

### Step 7: Create Initial Functions Code

Create `functions/src/index.ts` with ABOUTME comments. Include health check endpoint for Express pattern.

**Reference:** `docs/examples/express-function-architecture.md`

### Step 8: Configure Firestore Rules

Based on security model decision. Always include:
- Helper functions (`isAuthenticated()`, `isOwner()`)
- Default deny rule at bottom

**Reference:** `docs/examples/firestore-rules-patterns.md`

### Step 9: Set Up Testing

Create `vitest.config.ts` and `vitest.emulator.config.ts`. Set up `__tests__/` and `__tests__/emulator/` directories.

### Step 10: Configure Biome

Create `biome.json` with recommended rules. Run `npm run lint:fix`.

### Step 11: Set Up Environment Variables

Create `.env.example` template. Copy to `.env` and fill in values.

For hosting: create `hosting/.env.local` with `NEXT_PUBLIC_USE_EMULATORS=true`.

### Step 12: Initial Git Commit

```bash
git add . && git commit -m "feat: initial Firebase project setup"
```

### Step 13: Start Emulators

```bash
firebase emulators:start
open http://127.0.0.1:4000
```

Verify all services start. Test health endpoint if using Express.

### Step 14: Create Initial Tests

Create `functions/src/__tests__/setup.test.ts` with basic verification. Run `npm test`.

## Verification Checklist

Before marking complete:
- [ ] Firebase CLI installed and logged in
- [ ] TypeScript functions compile: `npm run build`
- [ ] All tests pass: `npm test`
- [ ] Linting passes: `npm run lint`
- [ ] Emulators start without errors
- [ ] Emulator UI accessible at http://127.0.0.1:4000
- [ ] Git initialized with commits
- [ ] `.env` files created and gitignored
- [ ] ABOUTME comments on all files
- [ ] Architecture decisions documented

## Project Structures

**Express API:**
```
functions/src/
├── index.ts
├── middleware/apiKeyGuard.ts
├── tools/
├── services/
└── __tests__/
```

**Domain-Grouped:**
```
functions/src/
├── index.ts
├── posts.ts
├── users.ts
├── shared/types/
└── __tests__/
```

**Individual Files:**
```
functions/
├── functions/upload.ts
├── functions/process.ts
└── index.js
```

## Next Steps

After setup complete:
1. Add first feature → `firebase-development:add-feature`
2. Review setup → `firebase-development:validate`
3. Debug issues → `firebase-development:debug`

## Pattern References

- **Hosting:** `docs/examples/multi-hosting-setup.md`
- **Auth:** `docs/examples/api-key-authentication.md`
- **Functions:** `docs/examples/express-function-architecture.md`
- **Rules:** `docs/examples/firestore-rules-patterns.md`
- **Emulators:** `docs/examples/emulator-workflow.md`
