# Commit Helper - Examples

This file contains real-world examples of conventional commits for the Logseq Template Graph project.

## Example 1: Adding a New Class

**Scenario:** Added Recipe class to creative-work module with cooking properties

**Git Diff:**
```diff
source/creative-work/classes.edn
+ {:user.class/Recipe-xY9zK
+  {:block/title "Recipe"
+   :build/class-properties [:user.property/recipeIngredient-aB1cD ...]
+   :build/class-parent :user.class/CreativeWork-pQ2rS
+   :build/properties {...}}}

source/creative-work/properties.edn
+ {:user.property/recipeIngredient-aB1cD {...}}
+ {:user.property/cookTime-eF3gH {...}}
+ {:user.property/recipeYield-iJ4kL {...}}
```

**Suggested Commit:**
```bash
git commit -m "$(cat <<'EOF'
feat(classes): add Recipe class to creative-work module

- Added Recipe class with cooking-specific properties
- Properties: recipeIngredient, cookTime, recipeInstructions, recipeYield, nutrition
- Parent class: CreativeWork
- Includes icon (🍳) and description

Closes #42
EOF
)"
```

**Why this works:**
- Type: `feat` (new class is a feature)
- Scope: `classes` (primary change)
- Description: Specific about what was added
- Body: Explains details and context
- Footer: References issue

---

## Example 2: Fixing a Bug

**Scenario:** Corrected spouse property cardinality from :one to :many

**Git Diff:**
```diff
source/person/properties.edn
  {:user.property/spouse-mN5oP
-  {:db/cardinality :db.cardinality/one
+  {:db/cardinality :db.cardinality/many
```

**Suggested Commit:**
```bash
git commit -m "fix(properties): correct spouse property cardinality to :many

The spouse property incorrectly used :db.cardinality/one but should
be :many to support multiple spouses (e.g., historical records,
polyamorous relationships)."
```

**Why this works:**
- Type: `fix` (correcting an error)
- Scope: `properties` (property change)
- Description: Clear about what was fixed
- Body: Explains WHY the fix was needed

---

## Example 3: Documentation Update

**Scenario:** Updated installation instructions for Windows users

**Git Diff:**
```diff
docs/user-guide/installation.md
+ ### Windows Installation
+
+ Install Babashka using Scoop:
+ ```powershell
+ scoop install babashka
+ ```
```

**Suggested Commit:**
```bash
git commit -m "docs: update installation instructions for Windows

- Added Scoop installation method for Babashka
- Clarified PowerShell script execution
- Fixed broken link to QUICK_START.md"
```

**Why this works:**
- Type: `docs` (documentation only)
- Scope: omitted (cross-cutting docs change)
- Description: Clear what was updated
- Body: Bullet points for multiple changes

---

## Example 4: Build System Change

**Scenario:** Updated GitHub Actions workflow to build all presets

**Git Diff:**
```diff
.github/workflows/release.yml
+ - name: Build all presets
+   run: |
+     npm run build:full
+     npm run build:crm
+     npm run build:research
```

**Suggested Commit:**
```bash
git commit -m "build(ci): add preset builds to release workflow

Build all template presets (full, CRM, research) during release
process to ensure they're available as release artifacts."
```

**Why this works:**
- Type: `build` (build system change)
- Scope: `ci` (CI/CD specific)
- Description: What was added
- Body: Explains the purpose

---

## Example 5: Refactoring

**Scenario:** Split misc/ module into focused modules

**Git Diff:**
```diff
source/misc/classes.edn (removed 30 classes)
source/communication/classes.edn (new file, 10 classes)
source/medical/classes.edn (new file, 12 classes)
source/financial/classes.edn (new file, 8 classes)
```

**Suggested Commit:**
```bash
git commit -m "refactor(modular): split misc module into focused domains

Reorganized 30 classes from misc/ into three focused modules:
- communication/ - EmailMessage, Message, Conversation, Comment
- medical/ - MedicalCondition, Drug, Hospital, Physician
- financial/ - Invoice, PaymentCard, BankAccount, Order

This improves module health score from 35/100 to 85/100."
```

**Why this works:**
- Type: `refactor` (code reorganization)
- Scope: `modular` (module structure)
- Description: High-level summary
- Body: Detailed breakdown of changes
- Impact: Shows the improvement

---

## Example 6: Chore (Auto-export)

**Scenario:** Automated export from Logseq

**Git Diff:**
```diff
Multiple .edn files updated with timestamps
```

**Suggested Commit:**
```bash
git commit -m "chore(templates): auto-export templates after development

Auto-generated from Logseq export on 2025-11-08"
```

**Why this works:**
- Type: `chore` (routine task)
- Scope: `templates` (template files)
- Description: What happened
- Body: Timestamp for reference

---

## Example 7: Breaking Change

**Scenario:** Removed deprecated Customer class

**Git Diff:**
```diff
source/organization/classes.edn
- {:user.class/Customer-qR6sT ...}

source/person/properties.edn
+ {:user.property/customerRole-uV7wX ...}
```

**Suggested Commit:**
```bash
git commit -m "$(cat <<'EOF'
feat(classes)!: remove deprecated Customer class

BREAKING CHANGE: Customer class removed from template.

Use Person class with customerRole property instead.

Migration steps for existing graphs:
1. Export all pages using Customer class
2. Re-import as Person pages
3. Add customerRole property to indicate customer status

Closes #78
EOF
)"
```

**Why this works:**
- Type: `feat!` (breaking change indicator)
- Scope: `classes`
- Description: What changed
- Footer: BREAKING CHANGE with migration guide
- Issue: References related issue

---

## Example 8: Performance Improvement

**Scenario:** Optimized build script to skip unchanged modules

**Git Diff:**
```diff
scripts/build.clj
+ (defn module-changed? [module]
+   (let [last-modified (get-last-modified module)
+         last-build (get-last-build module)]
+     (> last-modified last-build)))
```

**Suggested Commit:**
```bash
git commit -m "perf(scripts): skip unchanged modules during build

Build script now checks modification times and only rebuilds
modules that have changed since last build. This reduces full
build time from ~30s to ~5s for incremental changes."
```

**Why this works:**
- Type: `perf` (performance improvement)
- Scope: `scripts`
- Description: What was optimized
- Body: Explains the improvement with metrics

---

## Example 9: Multiple Related Changes

**Scenario:** Added Event class with multiple properties and updated docs

**Git Diff:**
```diff
source/event/classes.edn (new Event class)
source/event/properties.edn (5 new properties)
source/event/README.md (documentation)
docs/user-guide/using-events.md (new guide)
```

**Suggested Commit:**
```bash
git commit -m "$(cat <<'EOF'
feat(classes): add Event class with comprehensive properties

- Added Event class to event module
- Properties: eventStatus, attendee, organizer, startDate, endDate
- Parent class: Thing
- Created module README with usage examples
- Added user guide for event management workflows

This enables users to track meetings, conferences, and other
scheduled events with full Schema.org compatibility.

Closes #23
Refs #45
EOF
)"
```

**Why this works:**
- Type: `feat` (new feature)
- Scope: `classes` (main change)
- Body: Comprehensive list of changes
- Context: Explains the user benefit
- References: Multiple issue links

---

## Common Patterns

### Simple Addition
```bash
feat(classes): add Book class
```

### Simple Fix
```bash
fix(properties): correct cardinality for author property
```

### Documentation
```bash
docs: update README with installation steps
```

### Automated Export
```bash
chore(templates): auto-export templates
```

### Multiple Files, Single Purpose
```bash
feat(properties): add social media properties to Person class
```

### Cross-Module Change
```bash
refactor: standardize icon format across all modules
```

---

## Anti-Patterns (What NOT to Do)

### ❌ Bad: Vague Description
```bash
git commit -m "update files"
```

### ✅ Good: Specific Description
```bash
git commit -m "feat(classes): add Recipe class to creative-work module"
```

---

### ❌ Bad: Past Tense
```bash
git commit -m "Added Recipe class"
```

### ✅ Good: Imperative Mood
```bash
git commit -m "feat(classes): add Recipe class"
```

---

### ❌ Bad: No Type/Scope
```bash
git commit -m "recipe class with properties"
```

### ✅ Good: Proper Format
```bash
git commit -m "feat(classes): add Recipe class with cooking properties"
```

---

### ❌ Bad: Period at End
```bash
git commit -m "feat(classes): add Recipe class."
```

### ✅ Good: No Period
```bash
git commit -m "feat(classes): add Recipe class"
```

---

### ❌ Bad: Too Generic
```bash
git commit -m "fix: bug"
```

### ✅ Good: Specific Issue
```bash
git commit -m "fix(properties): correct spouse cardinality to :many"
```

---

## Quick Reference

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | New feature/class/property | `feat(classes): add Recipe class` |
| `fix` | Bug fix | `fix(properties): correct spouse cardinality` |
| `docs` | Documentation only | `docs: update installation guide` |
| `style` | Formatting (no logic change) | `style: format EDN files` |
| `refactor` | Code restructure | `refactor(modular): split misc module` |
| `perf` | Performance improvement | `perf(scripts): optimize build time` |
| `test` | Add/update tests | `test: add validation for EDN format` |
| `build` | Build system/deps/CI | `build(ci): add preset builds` |
| `ops` | Infrastructure/deployment | `ops: update GitHub Actions runner` |
| `chore` | Miscellaneous | `chore(templates): auto-export` |

## Scope Reference

| Scope | When to Use | Example |
|-------|-------------|---------|
| `classes` | Class changes | `feat(classes): add Recipe` |
| `properties` | Property changes | `fix(properties): correct cardinality` |
| `templates` | Template file changes | `chore(templates): auto-export` |
| `ci` | CI/CD changes | `build(ci): add workflow` |
| `scripts` | Script changes | `perf(scripts): optimize build` |
| `docs` | Documentation | `docs: update README` |
| `modular` | Module structure | `refactor(modular): split misc` |
| `workflow` | Dev workflow | `build(workflow): add git hooks` |
| `release` | Release-related | `chore(release): bump version` |
