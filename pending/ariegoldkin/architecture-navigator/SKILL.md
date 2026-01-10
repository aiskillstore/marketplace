---
name: architecture-navigator
description: Understand and navigate the DevPrep AI 7-folder architecture. Use this skill when asked about code organization, where to place new features, what modules exist, or when starting development tasks that need architecture context. Auto-triggers on keywords like "where should", "add module", "architecture", "structure", "organize", "place code", "what modules".
---

# Architecture Navigator

## Overview

Provide instant architecture intelligence for the DevPrep AI codebase. Generate architecture maps, answer placement questions ("where should X go?"), and validate code organization against the 7-folder structure. This skill eliminates the need to manually read architecture documentation at conversation start.

## Core Capabilities

### 1. Architecture Scanning

When starting a development conversation or when explicitly requested, scan the codebase to generate a real-time architecture map.

**How to scan:**

```bash
# Run the architecture scanner from project root
bash ./.claude/skills/architecture-navigator/scripts/scan_architecture.sh
```

The scanner will output:
- **7-Folder Structure**: modules/, shared/, lib/, store/, types/, styles/, app/
- **Module List**: All feature modules with file counts
- **Key Locations**: API layer, state management, UI components
- **Quick Stats**: Total files, module count, component count

**When to scan:**
- At the start of development conversations about architecture
- When asked "what modules exist?" or "what's the structure?"
- Before suggesting where new code should go
- When validating architecture compliance

**Output format:** Compact markdown summary (~50-100 lines) showing the current architecture state.

---

### 2. Interactive Placement Queries

Answer "where should X go?" questions using the 7-folder placement rules.

**Decision tree:**

1. **Is it a route/page?** → `app/` (but keep minimal, import from modules/)
2. **Is it feature-specific?** → `modules/{feature}/`
3. **Is it reusable UI/logic?** → `shared/`
4. **Is it external integration?** → `lib/`
5. **Is it global state?** → `store/`
6. **Is it a shared type?** → `types/`
7. **Is it pure styling?** → `styles/`

**Example queries and responses:**

| User Query | Response |
|------------|----------|
| "Where should social login go?" | `modules/auth/` - Feature-specific authentication logic |
| "Where should I add payment processing?" | `modules/payments/` - New feature module for payment domain logic |
| "Where do reusable buttons go?" | `shared/components/ui/Button.tsx` - Reusable UI component |
| "Where's the Claude AI integration?" | `lib/claude/` - External service integration |
| "Where should shopping cart state go?" | `store/cartStore.ts` - Global state management |
| "Where do API types go?" | `types/ai/api.ts` - Shared TypeScript definitions |

**For detailed rules**, reference `references/architecture-rules.md` which includes:
- Complete placement rules for all 7 folders
- Import direction rules (what can import what)
- Forbidden patterns (circular dependencies, wrong imports)
- Decision tree for complex placement questions
- Common examples and edge cases

---

### 3. Module Discovery

List existing modules and explain their purpose when asked.

**How to discover modules:**

```bash
# Quick module list
ls -1 frontend/src/modules/

# With file counts
find frontend/src/modules/ -mindepth 1 -maxdepth 1 -type d -exec sh -c 'echo -n "{}:" && find "{}" -name "*.ts*" | wc -l' \;
```

**Common questions:**
- "What modules exist?" → Run module discovery
- "Where does authentication live?" → Check modules/ for auth-related folders
- "What features are implemented?" → Scan modules/ directory

---

### 4. Architecture Validation

Validate that code follows the 7-folder structure rules.

**What to check:**
- ✅ Routes in `app/` are minimal (just imports)
- ✅ Business logic is in `modules/`, not `app/`
- ✅ Shared components are in `shared/`, not duplicated
- ✅ External integrations are in `lib/`
- ✅ Global state is in `store/`
- ✅ Imports follow allowed directions (see architecture-rules.md)

**Validation commands:**

```bash
# Check for business logic in app/ (should be minimal)
grep -r "useState\|useEffect\|async function" frontend/src/app/

# Check for cross-module imports (forbidden)
grep -r "from.*modules/" frontend/src/modules/

# Check for modules importing from shared (allowed)
grep -r "from.*shared/" frontend/src/modules/
```

---

## Workflow: Using This Skill

### Scenario 1: Conversation Start

When a development conversation begins, proactively scan the architecture:

1. Run `scripts/scan_architecture.sh` to generate current architecture map
2. Present the map concisely (don't overwhelm with details)
3. Use this context for subsequent placement questions

### Scenario 2: Placement Questions

When asked "where should X go?":

1. Identify the nature of the code (feature, reusable, integration, etc.)
2. Apply the decision tree from `references/architecture-rules.md`
3. Provide specific path recommendation
4. Explain WHY (which rule applies)

**Example:**

```
User: "Where should I add OAuth authentication?"

Response:
OAuth authentication should go in `modules/auth/oauth/`:
- It's feature-specific (authentication domain)
- It belongs in modules/ (not reusable across other features)
- Structure: modules/auth/oauth/GoogleAuth.tsx, OAuthProvider.tsx, etc.

The OAuth client setup (SDK wrapper) should go in `lib/oauth/client.ts` (external integration).
```

### Scenario 3: New Feature Module

When creating a new feature module:

1. Confirm it's truly a feature (domain-specific, not cross-cutting)
2. Create structure: `modules/{feature-name}/`
3. Recommend typical structure:
   ```
   modules/{feature}/
   ├── components/     - Feature-specific UI
   ├── hooks/          - Feature-specific hooks
   ├── utils/          - Feature-specific utilities
   └── types.ts        - Feature-specific types (if not shared)
   ```
4. Remind about import rules (can import from shared/, lib/, store/, types/)

---

## Auto-Trigger Keywords

This skill automatically activates when these phrases are detected:

- "where should"
- "add module"
- "architecture"
- "structure"
- "organize"
- "place code"
- "what modules"
- "where does [X] live"
- "where's the API"
- "folder structure"

**Manual invocation:** Use `/architecture` or explicitly request "scan the architecture".

---

## Resources

### scripts/scan_architecture.sh

Fast bash script that scans the 7-folder structure and generates a markdown architecture map. Outputs module list, key locations, and quick stats.

**Usage:**
```bash
bash scripts/scan_architecture.sh [project-root]
```

**Output:** Compact markdown summary (~50-100 lines) suitable for loading into context.

### references/architecture-rules.md

Comprehensive placement rules for the 7-folder architecture. Reference this document when:
- Answering complex placement questions
- Validating architecture compliance
- Explaining import direction rules
- Handling edge cases or ambiguous scenarios

**Key sections:**
- 7-Folder structure overview
- Detailed placement rules for each folder
- Import direction rules (what can import what)
- Forbidden patterns
- Decision tree for placement
- Common examples table

---

## Best Practices

1. **Start with scanning**: Generate architecture map at conversation start for context
2. **Be specific**: Always provide exact paths, not just folder names
3. **Explain reasoning**: Don't just say "put it in modules/", explain WHY
4. **Reference rules**: Point to `architecture-rules.md` for detailed justification
5. **Validate imports**: Check that suggested placements respect import direction rules
6. **Detect drift**: Flag when actual code structure deviates from documented architecture
7. **Keep it concise**: Architecture maps should be scannable (~50-100 lines)

---

## Example Usage

**User**: "I want to add a notification system that shows toast messages across the app."

**Response**:

Let me scan the current architecture first:

```bash
bash ./.claude/skills/architecture-navigator/scripts/scan_architecture.sh
```

[Architecture map output]

For a global notification system with toast messages:

1. **Toast UI Component** → `shared/components/Toast.tsx` (reusable UI)
2. **Notification State** → `store/uiStore.ts` (global state for managing active toasts)
3. **Toast Hook** → `shared/hooks/useToast.ts` (convenient API: `useToast().show()`)

**Reasoning:**
- Toast component is reusable across all features → shared/
- Notification state is global (not feature-specific) → store/
- Hook provides ergonomic API and is reusable → shared/

**Import flow:**
- Features call `useToast()` from `shared/hooks/`
- Hook accesses `store/uiStore.ts`
- Hook renders `shared/components/Toast.tsx`

This follows the architecture rules: modules/ → shared/ → store/ (allowed import direction).
