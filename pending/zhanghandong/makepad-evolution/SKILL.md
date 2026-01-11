---
name: makepad-evolution
description: Self-improving skill system for Makepad development. Features self-evolution (accumulate knowledge), self-correction (fix errors automatically), self-validation (verify accuracy), usage feedback (track pattern health), version adaptation (multi-branch support), and personalization (adapt to project style). Use to continuously improve makepad-skills during development.
---

# Makepad Skills Evolution

This skill enables makepad-skills to self-improve continuously during development.

---

## Automatic vs Manual Triggers

**IMPORTANT FOR CLAUDE**: Some mechanisms should trigger automatically without user request.

### Automatic (Claude should do proactively)

| Mechanism | When to Auto-Trigger |
|-----------|---------------------|
| **Version Adaptation** | At session start, read Cargo.toml and detect Makepad branch |
| **Personalization** | On first code generation, scan 2-3 existing widgets for style |
| **Self-Correction** | Immediately when skill-suggested code fails |
| **Usage Feedback** | After each pattern usage (success or failure) |

### Semi-Automatic (Claude proposes, user confirms)

| Mechanism | When to Propose |
|-----------|-----------------|
| **Self-Evolution** | After solving a non-trivial problem worth documenting |

### Manual (User must request)

| Mechanism | Trigger Phrase |
|-----------|---------------|
| **Self-Validation** | "validate makepad-skills" |
| **Health Report** | "show pattern health report" |

---

## Session Start Checklist (Auto-Execute)

When starting a Makepad development session, Claude should automatically:

```
1. [ ] Detect Makepad version from Cargo.toml
       → Set internal context: "Using Makepad {branch}"

2. [ ] Scan project style (if not done before)
       → Note naming conventions, module structure

3. [ ] Apply version-specific and personalized suggestions
       → All subsequent advice adapted automatically
```

**Claude: Do these silently. Don't announce unless relevant to user's question.**

---

## When to Evolve

Trigger skill evolution when any of these occur during development:

| Trigger | Target Skill | Priority |
|---------|--------------|----------|
| New widget pattern discovered | makepad-patterns | High |
| Shader technique learned | makepad-shaders | High |
| Compilation error solved | makepad-troubleshooting | High |
| Layout solution found | makepad-adaptive-layout | Medium |
| Build/packaging issue resolved | makepad-packaging | Medium |
| New project structure insight | makepad-init | Low |
| Core concept clarified | makepad-fundamentals | Low |

## Evolution Process

### Step 1: Identify Knowledge Worth Capturing

Ask yourself:
- Is this a reusable pattern? (not project-specific)
- Did it take significant effort to figure out?
- Would it help other Makepad developers?
- Is it not already documented in makepad-skills?

### Step 2: Classify the Knowledge

```
Widget/Component Pattern     → makepad-patterns/SKILL.md
Shader/Visual Effect         → makepad-shaders/SKILL.md
Error/Debug Solution         → makepad-troubleshooting/SKILL.md
Layout/Responsive Design     → makepad-adaptive-layout/SKILL.md
Build/Deploy Issue           → makepad-packaging/SKILL.md
Project Structure            → makepad-init/SKILL.md
Core Concept/API             → makepad-fundamentals/SKILL.md
```

### Step 3: Format the Contribution

**For Patterns (makepad-patterns)**:
```markdown
## Pattern N: [Pattern Name]

Brief description of what this pattern solves.

### live_design!
\```rust
live_design! {
    // DSL code
}
\```

### Rust Implementation
\```rust
// Rust code
\```

### Usage
\```rust
// How to use
\```
```

**For Troubleshooting (makepad-troubleshooting)**:
```markdown
### [Error Type/Message]

**Symptom**: What the developer sees

**Cause**: Why this happens

**Solution**:
\```rust
// Fixed code
\```
```

**For Shaders (makepad-shaders)**:
```markdown
### [Effect Name]

\```rust
draw_bg: {
    // shader code with comments
    fn pixel(self) -> vec4 {
        // implementation
    }
}
\```
```

### Step 4: Update the Skill File

1. Read the target SKILL.md file
2. Find the appropriate section
3. Add new content following existing format
4. Ensure no duplicate content

### Step 5: Mark Evolution (NOT Version)

**Important**: Do NOT update version number locally. Add an evolution marker instead:

```markdown
<!-- Evolution: 2024-01-15 | source: my-app | author: @zhangsan -->
```

Place this comment above the new content you added.

### Step 6: Submit via Git

```bash
# Create branch for your contribution
git checkout -b evolution/add-loading-pattern

# Commit your changes
git add makepad-patterns/SKILL.md
git commit -m "evolution: add loading state pattern from my-app"

# Push and create PR
git push origin evolution/add-loading-pattern
```

---

## Multi-Developer Collaboration

### The Problem

```
Developer A: evolves locally → version 1.4.1
Developer B: evolves locally → version 1.4.1  ← Conflict!
```

### The Solution: Content-First Model

```
┌─────────────────────────────────────────────────────────┐
│  Local Development (Each Developer)                     │
│  - Add content only                                     │
│  - Add evolution markers (date, source, author)         │
│  - Do NOT change version number                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Git PR / Merge                                         │
│  - Content reviewed and merged                          │
│  - Conflicts resolved at content level                  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Release (Maintainer / CI)                              │
│  - Bump version based on accumulated changes            │
│  - Tag release                                          │
│  - Publish                                              │
└─────────────────────────────────────────────────────────┘
```

### Evolution Marker Format

Each contribution should include a marker:

```markdown
<!-- Evolution: YYYY-MM-DD | source: project-name | author: @github-handle -->
```

Example in makepad-patterns/SKILL.md:

```markdown
## Pattern 15: Loading State Button

<!-- Evolution: 2024-01-15 | source: moly | author: @zhangsan -->

A button that shows loading spinner when processing...
```

### Git Workflow

```bash
# 1. Sync with upstream before evolving
git fetch upstream
git rebase upstream/main

# 2. Create evolution branch
git checkout -b evolution/descriptive-name

# 3. Make your changes (content only, no version bump)
# ... edit SKILL.md files ...

# 4. Commit with conventional prefix
git commit -m "evolution(patterns): add loading state button"
git commit -m "evolution(troubleshooting): fix for timer not firing"
git commit -m "evolution(shaders): add glassmorphism effect"

# 5. Push and create PR
git push origin evolution/descriptive-name
gh pr create --title "evolution: add loading patterns from moly"
```

### Handling Content Conflicts

When multiple developers add to the same section:

```markdown
<<<<<<< HEAD
## Pattern 15: Loading Button
<!-- Evolution: 2024-01-15 | source: moly | author: @zhangsan -->
=======
## Pattern 15: Expandable Card
<!-- Evolution: 2024-01-15 | source: robrix | author: @lisi -->
>>>>>>> evolution/add-card-pattern
```

Resolution: **Renumber and keep both**

```markdown
## Pattern 15: Loading Button
<!-- Evolution: 2024-01-15 | source: moly | author: @zhangsan -->
...

## Pattern 16: Expandable Card
<!-- Evolution: 2024-01-15 | source: robrix | author: @lisi -->
...
```

### Version Bumping (Maintainer Only)

At release time, maintainer reviews accumulated changes:

```bash
# Check what's new since last release
git log v1.4.0..HEAD --oneline

# Determine version bump
# - Only troubleshooting fixes → patch (1.4.1)
# - New patterns/shaders → minor (1.5.0)
# - New skill files → major (2.0.0)

# Update version in plugin.json
# Tag and release
git tag v1.5.0
git push --tags
```

### CI Automation (Optional)

`.github/workflows/version.yml`:

```yaml
name: Auto Version on Release
on:
  push:
    branches: [main]
    paths:
      - '*/SKILL.md'

jobs:
  version:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Bump version
        run: |
          # Count evolution markers since last tag
          # Auto-bump patch version
          # Update plugin.json
```

## Evolution Templates

### Quick Pattern Addition

```
I discovered a useful pattern during development:
[Describe the pattern]

Let me add it to makepad-skills:
1. Read makepad-patterns/SKILL.md
2. Add Pattern N: [Name] following existing format
3. Bump patch version
```

### Quick Troubleshooting Addition

```
I solved an error that others might encounter:
[Describe the error and solution]

Let me add it to makepad-skills:
1. Read makepad-troubleshooting/SKILL.md
2. Add under appropriate section
3. Bump patch version
```

### Quick Shader Addition

```
I created a useful shader effect:
[Describe the effect]

Let me add it to makepad-skills:
1. Read makepad-shaders/SKILL.md
2. Add under "Advanced Effects" or appropriate section
3. Bump patch version
```

## Skill File Locations

### Locating the Skills Directory (IMPORTANT)

**Claude: When this skill is loaded, you know the path of THIS file. Use it to locate other skills.**

```
THIS_SKILL_PATH = path of this SKILL.md file you just read
SKILLS_ROOT = dirname(dirname(THIS_SKILL_PATH))

Example:
  THIS_SKILL_PATH = /home/user/project/.claude/skills/makepad-skills/makepad-evolution/SKILL.md
  SKILLS_ROOT     = /home/user/project/.claude/skills/makepad-skills/
```

### Auto-Detection Instructions for Claude

When evolving skills, Claude MUST:

1. **Remember the path of this skill file** (you just read it, you know where it is)

2. **Calculate the skills root**:
   - This file is at: `<skills-root>/makepad-evolution/SKILL.md`
   - So `<skills-root>` = go up two directory levels from this file

3. **Construct target paths relatively**:
   ```
   To edit makepad-patterns:
     <skills-root>/makepad-patterns/SKILL.md

   To edit makepad-troubleshooting:
     <skills-root>/makepad-troubleshooting/SKILL.md

   To edit makepad-shaders:
     <skills-root>/makepad-shaders/SKILL.md
   ```

4. **Use the Read tool with the constructed absolute path**

5. **Use the Edit tool to update the file**

### Example Evolution Flow

```
1. Claude reads this skill from:
   /Users/someone/myapp/.claude/skills/makepad-skills/makepad-evolution/SKILL.md

2. Claude calculates skills root:
   /Users/someone/myapp/.claude/skills/makepad-skills/

3. Claude wants to add a pattern, constructs path:
   /Users/someone/myapp/.claude/skills/makepad-skills/makepad-patterns/SKILL.md

4. Claude uses Read tool to read that file

5. Claude uses Edit tool to add the new pattern

6. File is automatically saved ✓
```

**No hardcoded paths. Always derive from THIS file's location.**

### Relative Structure (from skills root)

```
<makepad-skills-root>/
├── .claude-plugin/
│   └── plugin.json           ← Version (maintainer only)
├── makepad-init/
│   └── SKILL.md              ← Project templates
├── makepad-fundamentals/
│   └── SKILL.md              ← Core concepts, widgets, events
├── makepad-shaders/
│   └── SKILL.md              ← SDF, effects, animations
├── makepad-patterns/
│   └── SKILL.md              ← Production patterns
├── makepad-adaptive-layout/
│   └── SKILL.md              ← Responsive layouts
├── makepad-packaging/
│   └── SKILL.md              ← Build & deployment
├── makepad-troubleshooting/
│   └── SKILL.md              ← Errors & debugging
└── makepad-evolution/
    └── SKILL.md              ← This file
```

### Where Updates Are Saved

| Scenario | Save Location | Sync Method |
|----------|---------------|-------------|
| Working in makepad-skills repo | Source directory | Direct |
| Using skills in project (copy) | Project's .claude/skills/ | Manual PR to upstream |
| Using skills in project (symlink) | Source directory | Direct |

**Recommended Setup**: Symlink to source for active contributors

```bash
# In your project
ln -s /path/to/makepad-skills .claude/skills/makepad-skills

# Now evolutions save directly to source
```

## Auto-Evolution Prompts

Use these prompts to trigger self-evolution:

### After Solving a Problem
> "This solution should be added to makepad-skills for future reference."

### After Creating a Widget
> "This widget pattern is reusable. Let me add it to makepad-patterns."

### After Debugging
> "This error and its fix should be documented in makepad-troubleshooting."

### After Completing a Feature
> "Review what I learned and update makepad-skills if applicable."

## Quality Guidelines

### DO Add
- Generic, reusable patterns
- Common errors with clear solutions
- Well-tested shader effects
- Platform-specific gotchas
- Performance optimizations

### DON'T Add
- Project-specific code
- Unverified solutions
- Duplicate content
- Incomplete examples
- Personal preferences without rationale

## Evolution Log

When evolving skills, optionally log the change:

```markdown
<!-- Evolution: YYYY-MM-DD -->
<!-- Source: [project name or context] -->
<!-- Added: [brief description] -->
```

## Continuous Improvement Checklist

After each Makepad development session, consider:

- [ ] Did I discover a new widget composition pattern?
- [ ] Did I solve a tricky shader problem?
- [ ] Did I encounter and fix a confusing error?
- [ ] Did I find a better way to structure layouts?
- [ ] Did I learn something about packaging/deployment?
- [ ] Would any of this help other Makepad developers?

If yes to any, evolve the appropriate skill!

---

## Self-Correction (自我修正)

When skill content causes errors, automatically correct it.

**AUTO-TRIGGER: Yes** - Claude should automatically correct skills when errors occur.

### Trigger Conditions

```
User follows skill advice → Code fails to compile/run → Claude identifies skill was wrong
                                                      ↓
                                         AUTO: Correct skill immediately
```

### Claude Auto-Behavior

When Claude detects that code from a skill caused an error:

1. **Recognize** - "This error is because the skill advice was wrong"
2. **Fix user's code** - Provide correct solution
3. **Update skill** - Automatically edit the skill file (no need to ask)
4. **Inform user** - "I've also updated makepad-skills to prevent this error for others"

### Self-Correction Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. DETECT: Skill advice led to an error                │
│     - Compilation error from suggested code             │
│     - Runtime error from recommended pattern            │
│     - API mismatch (method doesn't exist)               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  2. VERIFY: Confirm the skill content is wrong          │
│     - Check Makepad source code                         │
│     - Test the correct approach                         │
│     - Ensure fix works                                  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  3. CORRECT: Update the skill file                      │
│     - Fix the incorrect code/advice                     │
│     - Add correction marker                             │
│     - Optionally add to troubleshooting                 │
└─────────────────────────────────────────────────────────┘
```

### Correction Marker Format

```markdown
<!-- Correction: YYYY-MM-DD | was: [old advice] | reason: [why it was wrong] -->
```

### Example Self-Correction

**Scenario**: Skill said `timer.start(cx, 0.1)` but it fails

```
1. Claude detects: "method `start` not found on Timer"

2. Claude investigates Makepad source, finds correct API:
   timer = cx.start_interval(0.1)

3. Claude updates makepad-fundamentals/SKILL.md:
```

```markdown
### Timer Setup

<!-- Correction: 2024-01-20 | was: timer.start(cx, 0.1) | reason: API changed in dev branch -->

```rust
// Correct way to start a timer
fn setup_timer(&mut self, cx: &mut Cx) {
    self.timer = cx.start_interval(0.1);  // Returns Timer directly
}
```

4. Claude also adds to makepad-troubleshooting:

```markdown
### "method `start` not found on Timer"

**Symptom**: `timer.start(cx, duration)` doesn't compile

**Cause**: Timer API changed. Timer is now returned from Cx methods.

**Solution**:
```rust
// Old (wrong)
self.timer.start(cx, 0.1);

// New (correct)
self.timer = cx.start_interval(0.1);
```
```

### Auto-Correction Prompt

When Claude detects skill-caused errors:

> "The skill advice I followed caused an error. Let me correct the skill and document this fix."

---

## Self-Validation (自我验证)

Periodically verify skill content is still accurate.

### Validation Triggers

| Trigger | Action |
|---------|--------|
| User asks "validate skills" | Full validation |
| Compilation fails with skill code | Targeted validation |
| New Makepad version detected | API validation |
| Skill hasn't been validated in 30 days | Scheduled validation |

### Validation Checklist

```markdown
## Validation Report

### Code Examples
- [ ] All `live_design!` examples parse correctly
- [ ] All Rust code compiles
- [ ] All patterns work as documented

### API Accuracy
- [ ] Widget names exist in makepad-widgets
- [ ] Method signatures are correct
- [ ] Event types are accurate

### External Links
- [ ] GitHub links resolve
- [ ] Documentation links work
- [ ] Example project links valid

### Completeness
- [ ] No deprecated patterns without warnings
- [ ] No missing common use cases
- [ ] Error messages match current Makepad
```

### Validation Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. READ: Load all SKILL.md files                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  2. EXTRACT: Find all code blocks                       │
│     - live_design! blocks                               │
│     - Rust implementation blocks                        │
│     - Cargo.toml snippets                               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  3. VERIFY: Check against current Makepad               │
│     - Parse DSL syntax                                  │
│     - Check widget/method existence                     │
│     - Verify API signatures                             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  4. REPORT: List issues found                           │
│     - Outdated code                                     │
│     - Broken examples                                   │
│     - Missing updates                                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  5. FIX: Correct issues (with user approval)            │
└─────────────────────────────────────────────────────────┘
```

### Validation Marker

After validation, add to skill file:

```markdown
<!-- Validated: YYYY-MM-DD | makepad-branch: dev | status: passed -->
```

### Validation Prompt

> "Please validate makepad-skills against current Makepad version"

Claude will:
1. Check each skill file
2. Verify code examples
3. Report any issues
4. Offer to fix problems

---

## Usage Feedback (使用反馈)

Track which patterns work well and which cause problems.

**AUTO-TRIGGER: Yes** - Claude should automatically record feedback after using patterns.

### Claude Auto-Behavior

After using any pattern from makepad-skills:

1. **Track silently** - Don't announce feedback recording to user
2. **On success** - Update marker: `success += 1`
3. **On failure** - Update marker: `failed += 1`, then trigger self-correction
4. **Periodically** - If a pattern fails 3+ times, proactively suggest fixing it

### Feedback Marker Format

Add invisible markers to track usage:

```markdown
<!-- Usage: count=0 | success=0 | failed=0 | last_used=never -->
## Pattern 5: Loading State Button
```

### Feedback Collection Flow

```
┌─────────────────────────────────────────────────────────┐
│  User asks Claude to implement something                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Claude uses a pattern from makepad-skills              │
│  → Increment: count += 1                                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Implementation result:                                 │
│  - Works → success += 1                                 │
│  - Fails → failed += 1, trigger self-correction         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Update marker with new counts                          │
│  Update last_used timestamp                             │
└─────────────────────────────────────────────────────────┘
```

### Feedback Analysis

When feedback accumulates, Claude can analyze:

```markdown
## Pattern Health Report

| Pattern | Uses | Success | Failed | Rate | Status |
|---------|------|---------|--------|------|--------|
| Pattern 1: Basic Widget | 45 | 43 | 2 | 96% | ✅ Healthy |
| Pattern 5: Loading Button | 12 | 8 | 4 | 67% | ⚠️ Needs Review |
| Pattern 8: Theme Switch | 3 | 0 | 3 | 0% | ❌ Broken |
```

### Feedback-Driven Actions

| Success Rate | Action |
|--------------|--------|
| > 90% | Pattern is solid, no action needed |
| 70-90% | Review pattern for edge cases |
| 50-70% | Pattern needs improvement |
| < 50% | Pattern likely broken, needs fix or removal |

### Feedback Prompt

> "Show me pattern health report for makepad-skills"

> "Which patterns have been failing recently?"

---

## Version Adaptation (版本适配)

Provide version-specific guidance for different Makepad branches.

**AUTO-TRIGGER: Yes** - Claude should detect version at session start.

### Claude Auto-Behavior

At the start of any Makepad development session:

1. **Read Cargo.toml** - Look for `makepad-widgets` dependency
2. **Extract branch** - Note `branch = "dev"` or `branch = "rik"` etc.
3. **Set context** - Remember this for all subsequent suggestions
4. **Adapt silently** - Don't announce, just use correct API for that branch
5. **Warn on mismatch** - If user's code uses wrong API, explain the version difference

### Supported Versions

```markdown
| Branch | Status | Notes |
|--------|--------|-------|
| main | Stable | Production ready |
| dev | Active | Latest features, may break |
| rik | Legacy | Older API style |
```

### Version Detection

Claude should detect Makepad version from:

1. **Cargo.toml branch reference**:
   ```toml
   makepad-widgets = { git = "...", branch = "dev" }
   ```

2. **Cargo.lock content**:
   ```
   Check makepad-widgets source revision
   ```

3. **Ask user if unclear**

### Version-Specific Content Format

```markdown
### Timer Setup

<version branch="dev">
```rust
// Makepad dev branch (2024+)
self.timer = cx.start_interval(0.1);
```
</version>

<version branch="rik">
```rust
// Makepad rik branch (legacy)
self.timer.start(cx, 0.1);
```
</version>

<version branch="main">
```rust
// Makepad main branch (stable)
self.timer = cx.start_interval(0.1);
```
</version>
```

### Version Adaptation Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. DETECT: Identify project's Makepad version          │
│     - Read Cargo.toml                                   │
│     - Check branch reference                            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  2. FILTER: Show only relevant version content          │
│     - Hide incompatible examples                        │
│     - Highlight version-specific gotchas                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  3. WARN: Alert about version mismatches                │
│     - "This pattern is for dev branch, you're on rik"   │
│     - "API changed in dev, see updated syntax"          │
└─────────────────────────────────────────────────────────┘
```

### Version Compatibility Table

Maintain in makepad-fundamentals:

```markdown
## API Compatibility

| Feature | main | dev | rik |
|---------|------|-----|-----|
| cx.start_interval() | ✅ | ✅ | ❌ |
| timer.start() | ❌ | ❌ | ✅ |
| AdaptiveView | ✅ | ✅ | ✅ |
| StackNavigation | ✅ | ✅ | ⚠️ |
```

### Version Prompt

> "I'm using Makepad dev branch, adapt your suggestions accordingly"

> "What's different between dev and rik branch for timers?"

---

## Personalization (个性化)

Adapt skill suggestions to project's coding style.

**AUTO-TRIGGER: Yes** - Claude should detect project style on first code generation.

### Claude Auto-Behavior

On first request to generate Makepad code:

1. **Scan quickly** - Read 2-3 existing widget files in the project
2. **Note patterns** - Widget naming, module structure, comment style
3. **Remember** - Store in conversation context
4. **Apply** - All generated code matches project style
5. **Silent** - Don't announce this analysis to user

### Style Detection

Claude analyzes the current project to detect:

| Aspect | Detection Method | Adaptation |
|--------|------------------|------------|
| Naming convention | Scan existing widgets | Match snake_case vs camelCase |
| Code organization | Check module structure | Suggest matching patterns |
| Comment style | Read existing comments | Match documentation style |
| Error handling | Analyze existing code | Match Result vs panic style |
| Widget complexity | Count lines per widget | Suggest appropriate patterns |

### Project Profile

Claude builds a mental profile of the project:

```markdown
## Project Style Profile

- **Widget naming**: snake_case (e.g., `my_button`, `user_card`)
- **Module organization**: Feature-based (`src/features/auth/`)
- **State management**: Centralized AppState
- **Error handling**: Result with custom errors
- **Comments**: Minimal, code is self-documenting
- **Complexity preference**: Simple, small widgets
```

### Personalization Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. SCAN: Analyze existing project code                 │
│     - Read 3-5 representative widget files              │
│     - Note naming patterns                              │
│     - Identify organizational structure                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  2. PROFILE: Build project style profile                │
│     - Naming conventions                                │
│     - Code organization                                 │
│     - Complexity level                                  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  3. ADAPT: Modify skill suggestions to match            │
│     - Rename widgets in examples                        │
│     - Adjust code structure                             │
│     - Match comment style                               │
└─────────────────────────────────────────────────────────┘
```

### Example Personalization

**Skill default**:
```rust
pub struct MyCustomButton {
    #[walk] walk: Walk,
    #[live] label_text: String,
}
```

**Adapted for project using `_view` suffix**:
```rust
pub struct CustomButtonView {
    #[walk] walk: Walk,
    #[live] label_text: String,
}
```

### Personalization Markers

Store detected style in project's `.claude/settings.json`:

```json
{
  "makepad-skills": {
    "style": {
      "widget_suffix": "_view",
      "naming": "snake_case",
      "prefer_simple": true
    }
  }
}
```

### Personalization Prompts

> "Analyze my project style and adapt your Makepad suggestions"

> "My project uses PascalCase for widgets, remember that"

> "Reset personalization to skill defaults"

---

## Combined Self-Improvement Workflow

All mechanisms work together:

```
                    ┌─────────────────┐
                    │  Development    │
                    │  Session        │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Personalize │     │   Use       │     │  Detect     │
│ suggestions │     │   Patterns  │     │  Version    │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Success  │ │ Failure  │ │ New      │
        │ +1       │ │ +1       │ │ Pattern  │
        └──────────┘ └────┬─────┘ └────┬─────┘
                          │            │
                          ▼            ▼
                   ┌──────────┐ ┌──────────┐
                   │ Self-    │ │ Self-    │
                   │ Correct  │ │ Evolve   │
                   └──────────┘ └──────────┘
                          │            │
                          └─────┬──────┘
                                │
                                ▼
                       ┌─────────────┐
                       │  Improved   │
                       │  Skills     │
                       └─────────────┘
```

## References

- [makepad-skills repository](https://github.com/project-robius/makepad-skills)
- [Makepad documentation](https://github.com/makepad/makepad)
- [Project Robius](https://github.com/project-robius)
