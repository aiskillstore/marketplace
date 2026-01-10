# Code Validation Sandbox v3.0

**Intelligent Docker-based validation with automatic language detection, layer-aware strategies, and reasoning-based error analysis.**

**Version**: 3.0.0 (Reasoning-Activated — Constitution v6.0.0)
**Replaces**: `python-sandbox` v1.0 + `general-sandbox` v1.0
**Pattern**: Persona + Questions + Principles (Research-Grounded)

---

## What Makes This Different

### Traditional Validation (Old Approach)
```bash
# Hardcoded: Extract code → Run → Report errors
find . -name "*.md" -exec extract_python {} \; | python3
```

**Problems**:
- Same validation for all pedagogical contexts
- No adaptation to language ecosystems
- Generic error messages
- No reasoning about "why this matters"

### Intelligent Validation (v3.0 Approach)

**Reasoning Process**:
1. **Analyze Context** → What layer? What language? What audience tier?
2. **Select Strategy** → Appropriate validation depth for pedagogical context
3. **Execute Intelligently** → Language-specific tools with layer-aware checks
4. **Report Actionably** → File:line + fix + "why this matters for THIS layer"

---

## Quick Start

### 1. Setup (One-Time)

```bash
# Create persistent container with Python + Node + tools
bash .claude/skills/code-validation-sandbox/scripts/setup-sandbox.sh
```

**Installs**:
- Python 3.14 + UV + pytest + mypy + ruff
- Node.js 20 + pnpm
- Base tools (curl, git, build-essential)

### 2. Validate a Chapter

```bash
# Auto-detect layer, language, validation strategy
bash .claude/skills/code-validation-sandbox/scripts/validate.sh \
  apps/learn-app/docs/04-Python-Fundamentals/14-data-types
```

**What Happens**:
- Detects Layer 1 (Manual Foundation) from content
- Detects Python from file extensions and keywords
- Applies CRITICAL depth (syntax + runtime + output exact)
- Generates actionable error report

### 3. Review Results

```
=== Code Validation Sandbox v3.0 (Reasoning-Activated) ===

Layer: 1
  → Manual Foundation (zero error tolerance)

Language(s): python
  → Python (AST + runtime validation)

Tier: A2
  → Aspiring/Beginner (heavy scaffolding)

Validation Depth: CRITICAL
  → Syntax + Runtime + Output matching

=== Validation Strategy Selection ===

Strategy: CRITICAL DEPTH
  - Syntax: 100% correct (zero tolerance)
  - Runtime: Must execute without errors
  - Output: Must match expected (if documented)
  - Why: Layer 1 foundation - students type manually

=== Validating python ===

Python Validation (Layer 1, Depth: CRITICAL)

Found 23 Python code blocks

=== CRITICAL Depth Validation ===
- Syntax: 100% correct (zero tolerance)
- Runtime: Must execute successfully
- Output: Must match expected (if documented)

CRITICAL: Syntax error in validation-output/extracted/01-variables_block_7.py
  File "01-variables.py", line 3
    print(count
              ^
SyntaxError: '(' was never closed

=== Python Validation Summary ===
Total blocks: 23
Syntax errors: 1
Runtime errors: 0
❌ CRITICAL errors found (blocks publication)
```

---

## Layer-Aware Validation

### Layer 1: Manual Foundation → CRITICAL Depth

**Context**: Students type code manually, character-by-character

**Validation**:
- ✅ Syntax 100% correct (zero tolerance for typos)
- ✅ Runtime executes successfully
- ✅ Output matches documented examples exactly

**Why**: Errors break learning flow at foundational stage

### Layer 2: AI Collaboration → VERIFICATION Depth

**Context**: Before/after examples showing AI optimization

**Validation**:
- ✅ Baseline implementation works
- ✅ Optimized version works
- ✅ Functional equivalence (same outputs)
- ✅ Performance claims verified (measure if "3x faster")

**Why**: "AI improved this" must be factually accurate

### Layer 3: Intelligence Design → REUSABILITY Depth

**Context**: Creating reusable skills/agents

**Validation**:
- ✅ Persona+Questions+Principles pattern present
- ✅ Works with multiple scenarios (not hardcoded)
- ✅ Tested across 3+ use cases

**Why**: Intelligence must generalize, not overfit

### Layer 4: Orchestration → INTEGRATION Depth

**Context**: Multi-component system integration

**Validation**:
- ✅ All services start (docker-compose up)
- ✅ Health checks pass
- ✅ End-to-end scenarios work
- ✅ Graceful degradation on failures

**Why**: Production systems need resilience

---

## Multi-Language Support

### Auto-Detection

**Python** (detected from):
- `.py` files
- Keywords: `import`, `def`, `class`, `pip`, `uv`

**Node.js** (detected from):
- `package.json`
- `.js` / `.ts` files
- Keywords: `npm`, `pnpm`, `require`, `import ... from`

**Rust** (detected from):
- `Cargo.toml`
- `.rs` files
- Keywords: `cargo`, `fn`, `impl`

**Multi-Language**:
- Validates each independently
- Then integration testing (if docker-compose.yml)

### Language-Specific Tools

**Python**: AST syntax check + pytest + mypy + ruff
**Node.js**: tsc + npm test + npm build
**Rust**: cargo check + cargo test

---

## Actionable Error Reports

### Generic Error (Anti-Pattern)
```
Error in file: line 23
```

### Actionable Error (v3.0 Pattern)
```
CRITICAL: Layer 1 Manual Foundation
File: 02-variables.md:145 (code block 7)
Error: NameError: name 'count' is not defined

Context (lines 142-145):
  142: def increment():
  143:     global counter  # ← Typo detected
  144:     counter += 1
  145:     print(counter)  # ← Fails here

Root Cause: Variable declared as 'count' but referenced as 'counter'

Fix: Line 143: global counter → global count

Why this matters (Layer 1):
  - Students typing manually will hit confusing error
  - Breaks learning flow at foundational stage
  - Variable names must match declarations exactly
  - Zero tolerance for errors in foundation

Validation: python3 -m ast fixed.py && python3 fixed.py
```

---

## Usage Examples

### Basic Validation
```bash
bash .claude/skills/code-validation-sandbox/scripts/validate.sh \
  apps/learn-app/docs/04-Python-Fundamentals/14-data-types
```

### Force Layer
```bash
# Override auto-detection
bash .claude/skills/code-validation-sandbox/scripts/validate.sh \
  apps/learn-app/docs/04-Python-Fundamentals/14-data-types \
  --layer 1
```

### Verbose Output
```bash
bash .claude/skills/code-validation-sandbox/scripts/validate.sh \
  apps/learn-app/docs/04-Python-Fundamentals/14-data-types \
  --verbose
```

### Custom Output Directory
```bash
bash .claude/skills/code-validation-sandbox/scripts/validate.sh \
  apps/learn-app/docs/04-Python-Fundamentals/14-data-types \
  --output audit-results
```

### Validate Multiple Chapters
```bash
for chapter in apps/learn-app/docs/04-Python-Fundamentals/*/; do
  bash .claude/skills/code-validation-sandbox/scripts/validate.sh "$chapter"
done
```

---

## Architecture

### Files

```
code-validation-sandbox/
├── SKILL-REDESIGN-v3.md     # Main skill (Persona+Questions+Principles)
├── metadata.yaml             # Skill configuration
├── README.md                 # This file
└── scripts/
    ├── detect-context.sh     # Intelligent context detection
    ├── validate.sh           # Main orchestrator
    ├── validate-python.sh    # Python-specific validation
    ├── setup-sandbox.sh      # Container setup
    └── (validate-node.sh)    # TODO: Node.js validation
```

### Context Detection (Reasoning-Based)

```bash
# detect-context.sh analyzes:

1. Layer Detection
   - Explicit metadata (chapter-meta.yaml)
   - Content patterns ("first time" → L1, "optimize" → L2, etc.)

2. Language Detection
   - File extensions (.py, .js, .rs)
   - Manifest files (package.json, Cargo.toml)
   - Keywords in markdown

3. Tier Detection (CEFR-aligned)
   - Part number (Parts 1-3 → A2, 4-5 → B1, 6-13 → C2)

4. Validation Depth
   - Layer → Depth mapping (L1 → CRITICAL, L2 → VERIFICATION, etc.)

Output (machine-readable):
LAYER=1
LANGUAGES=python
TIER=A2
DEPTH=CRITICAL
```

---

## Reasoning Pattern (Research-Grounded)

### Persona
"Validation intelligence architect" who reasons about test strategy

### Questions
- What layer? (Determines validation depth)
- What language? (Selects appropriate tools)
- What severity? (Prioritizes fixes)

### Principles
- IF Layer 1 → THEN zero tolerance (CRITICAL depth)
- IF Layer 2 → THEN verify claims (VERIFICATION depth)
- IF Layer 3 → THEN test reusability (multi-scenario)
- IF Layer 4 → THEN integration testing (end-to-end)

### Anti-Convergence
Self-monitoring prevents generic validation:
- Did I analyze layer context?
- Did I select language-appropriate tools?
- Did I provide actionable diagnostics?

---

## Exit Codes

- `0` - All validations passed ✅
- `1` - Validation errors found (review recommended) ⚠️
- `2` - Critical errors (blocks publication) ❌
- `3` - Invalid arguments

---

## Migration from Old Skills

### python-sandbox → code-validation-sandbox

**Old**:
```bash
bash .claude/skills/python-sandbox/scripts/validate-in-sandbox.sh \
  apps/learn-app/docs/04-Python-Fundamentals/14-data-types
```

**New**:
```bash
bash .claude/skills/code-validation-sandbox/scripts/validate.sh \
  apps/learn-app/docs/04-Python-Fundamentals/14-data-types
```

**Improvements**:
- Auto-detects layer (no manual specification)
- Layer-aware validation depth
- Actionable error reports
- Self-monitoring anti-convergence

### general-sandbox → code-validation-sandbox

**Old** (required manual language config):
```bash
bash .claude/skills/general-sandbox/scripts/install-in-sandbox.sh "
  apt-get install -y nodejs
  npm install -g pnpm
"
bash .claude/skills/general-sandbox/scripts/validate-in-sandbox.sh ...
```

**New** (auto-detects language):
```bash
# Just run - it figures out Node.js automatically
bash .claude/skills/code-validation-sandbox/scripts/validate.sh \
  apps/learn-app/docs/02-Part-2-Tools/05-npm-chapter
```

**Improvements**:
- No manual installation scripting
- Persistent container (pre-installed Python + Node)
- Language auto-detection
- Unified interface

---

## Constitutional Alignment

✅ **Validation-First Safety** (Philosophy #5): Never trust code without testing
✅ **Evals-First Development** (Philosophy #4): Success = 0 errors
✅ **Layer Awareness**: Validates appropriately for pedagogical context
✅ **Reasoning Activation**: Persona+Questions+Principles pattern throughout
✅ **Anti-Convergence**: Self-monitoring prevents generic validation

---

## Research Foundation

Based on: "Activating Reasoning Mode in Large Language Models"

**Key patterns applied**:
1. **Persona** → Cognitive stance (validation intelligence architect)
2. **Questions** → Systematic analysis (What layer? What language?)
3. **Principles** → Decision frameworks (IF Layer 1 → THEN zero tolerance)
4. **Right Altitude** → Balance specificity and flexibility
5. **Anti-Convergence** → Self-monitoring prevents generic patterns

**Result**: Validation that REASONS about context, not just EXECUTES scripts

---

## Status

✅ **Core Complete**: Persona+Questions+Principles pattern implemented
✅ **Python Validation**: Layer-aware validation working
✅ **Context Detection**: Intelligent layer/language detection
⏳ **Node.js Validation**: TODO (similar to Python pattern)
⏳ **Rust Validation**: TODO (similar to Python pattern)

**Ready for production use with Python chapters.**
