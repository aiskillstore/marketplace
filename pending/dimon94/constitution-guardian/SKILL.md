---
name: constitution-guardian
description: Real-time Constitution compliance checker for devflow documents. Blocks partial implementations and hardcoded secrets during file editing.
---

# Constitution Guardian

## Purpose
Enforce CC-DevFlow Constitution compliance by detecting violations in real-time during document editing, preventing non-compliant content from being saved.

**Trigger**: PreToolUse hook when editing devflow documents (PRD.md, EPIC.md, TASKS.md, TECH_DESIGN.md)

## Enforcement Scope

**Focus Articles** (Real-time prevention):
- **Article I.1**: Quality First - No Partial Implementation
- **Article III.1**: Security First - No Hardcoded Secrets

**Note**: Full Constitution has 10 Articles. This guardrail focuses on the most critical real-time violations. Batch validation by `validate-constitution.sh` covers all Articles.

## Violation Patterns

### Article I.1: No Partial Implementation

#### Pattern 1: TODO placeholders
```markdown
# ❌ BLOCKED
## User Stories
### US1: User Registration
TODO later: Add email verification flow
FIXME: Implement password strength validation
```

**Regex Patterns**:
- `TODO.*later`
- `FIXME`
- `\[placeholder\]`
- `// TODO:.*later`
- `# FIXME:.*`

#### Pattern 2: Simplified/Partial notes
```markdown
# ❌ BLOCKED
## Implementation Notes
This is simplified for now, complete implementation would require...
```

**Regex Pattern**: `simplified for now`

#### Pattern 3: Version deferral
```markdown
# ❌ BLOCKED
## Acceptance Criteria
- [ ] Basic login (v1)
- [ ] Remember me (defer to v2)
```

**Regex Pattern**: `defer to v\d|will complete in v\d`

### Article III.1: No Hardcoded Secrets

#### Pattern 1: Environment variables with secrets
```markdown
# ❌ BLOCKED
## Configuration
API_KEY=sk-abc123def456
JWT_SECRET=mysecretkey123
PASSWORD=admin123
```

**Regex Patterns**:
- `API_KEY\s*=\s*['"]?[a-zA-Z0-9_-]{10,}`
- `SECRET\s*=\s*['"]?[a-zA-Z0-9_-]+`
- `PASSWORD\s*=\s*['"]?[^\s]+`
- `TOKEN\s*=\s*['"]?[a-zA-Z0-9_-]{10,}`

#### Pattern 2: Code snippets with hardcoded secrets
```typescript
// ❌ BLOCKED
const config = {
  apiKey: "sk-abc123def456",
  dbPassword: "postgres123"
};
```

**Regex Patterns**:
- `apiKey:\s*['"][^'"]+['"]`
- `password:\s*['"][^'"]+['"]`
- `secret:\s*['"][^'"]+['"]`

## Blocking Message

When violation detected, PreToolUse hook returns **exit code 2** (blocks file save):

```
⚠️ BLOCKED - Constitution Violation

Detected:
- [Line 42] TODO placeholder (Article I.1 - No Partial Implementation)
- [Line 58] Hardcoded API key (Article III.1 - No Hardcoded Secrets)

📋 ACTION:
1. Complete all TODOs/FIXMEs before saving
2. Move secrets to environment variables (.env, not committed)
3. Review `.claude/rules/project-constitution.md` v2.0.0
4. Run /flow-verify for comprehensive check

Source: Constitution Articles I.1, III.1
File: {file_path}

Constitutional Basis:
  Article I.1: "NO PARTIAL IMPLEMENTATION: Complete implementation or no implementation"
  Article III.1: "NO HARDCODED SECRETS: Use environment variables or secret management"

💡 SKIP: Add `@constitution-verified` comment or set SKIP_CONSTITUTION_CHECK=1
```

## Constitutional Basis

### Article I: Quality First

```yaml
I.1 Complete Implementation Mandate:
  Prohibition: Any form of partial implementation or placeholder code
  Requirement: Complete implementation or no implementation
  Examples:
    ❌ Forbidden: "// TODO: Implement this later"
    ❌ Forbidden: "// Simplified for now, will complete in v2"
    ✅ Required: Fully functional, production-ready code
```

**Enforcement**:
- **Generation time**: prd-writer, tech-architect, planner agents check output
- **Edit time**: constitution-guardian guardrail blocks save (this skill)
- **Phase completion**: validate-constitution.sh batch validation

### Article III: Security First

```yaml
III.1 No Hardcoded Secrets:
  Prohibited:
    ❌ API_KEY = "sk-abc123..." in source code
    ❌ PASSWORD = "admin123" in config files
    ❌ JWT_SECRET embedded in code

  Required:
    ✅ Environment variables (.env files, not committed)
    ✅ Secret management services (AWS Secrets Manager, etc.)
    ✅ Configuration injection at runtime

  Detection: Pre-push guard scans for secret patterns
```

**Enforcement**:
- **Generation time**: All agents avoid secrets in generated docs
- **Edit time**: constitution-guardian guardrail blocks save (this skill)
- **Pre-push**: Git pre-push hook scans for secrets

## Skip Conditions

Users can bypass Constitution guardian in specific scenarios:

### 1. Session Skip (One-time per session)
- **Mechanism**: `sessionSkillUsed: true` in skill-rules.json
- **Behavior**: Guardrail only triggers once per Claude session
- **Use case**: User acknowledged violation, working on fix

### 2. File Marker (Permanent skip for specific file)
- **Marker**: Add `@constitution-verified` comment in document
- **Example**:
  ```markdown
  <!-- @constitution-verified: Legacy doc migration, compliance review completed -->
  ```
- **Use case**: Legacy documentation, special cases

### 3. Environment Variable (Temporary global skip)
- **Variable**: `SKIP_CONSTITUTION_CHECK=1`
- **Scope**: Current terminal session
- **Use case**: Bulk imports, automated migrations

## Relationship with Other Components

### validate-constitution.sh (Script)
- **Purpose**: Batch validation of all 10 Constitutional Articles
- **Scope**: Complete document/codebase scan
- **Timing**: Phase completion (e.g., /flow-prd Exit Gate)
- **Articles**: I, II, III, IV, V, VI, VII, VIII, IX, X

### constitution-guardian (Guardrail)
- **Purpose**: Real-time prevention of critical violations
- **Scope**: Single document being edited
- **Timing**: During file editing (PreToolUse hook)
- **Articles**: Focus on I.1, III.1 (most critical for documents)

**Relationship**: **Complementary (互补)**
- Guardrail: Real-time prevention (write-time, partial Articles)
- Script: Batch validation (phase-time, all Articles)
- Double insurance: Guardrail catches most issues, Script catches remaining

### Constitution Document
- **Source of Truth**: `.claude/rules/project-constitution.md` v2.0.0
- **Contains**: All 10 Articles with detailed rules
- **This guardrail**: Extracts Articles I.1, III.1 prohibition rules only

## Configuration

In `.claude/skills/skill-rules.json`:

```json
{
  "constitution-guardian": {
    "type": "guardrail",
    "enforcement": "block",
    "priority": "critical",
    "description": "Real-time Constitution compliance, extracted from Constitution v2.0.0",
    "fileTriggers": {
      "pathPatterns": [
        "devflow/requirements/**/PRD.md",
        "devflow/requirements/**/EPIC.md",
        "devflow/requirements/**/TASKS.md",
        "devflow/requirements/**/TECH_DESIGN.md",
        "devflow/requirements/**/contracts/**/*.yaml",
        "devflow/requirements/**/data-model.md"
      ],
      "contentPatterns": [
        "TODO.*later",
        "FIXME",
        "\\[placeholder\\]",
        "simplified for now",
        "defer to v\\d",
        "API_KEY\\s*=\\s*['\"]?[a-zA-Z0-9_-]{10,}",
        "SECRET\\s*=\\s*['\"]?[a-zA-Z0-9_-]+",
        "PASSWORD\\s*=\\s*['\"]?[^\\s]+",
        "TOKEN\\s*=\\s*['\"]?[a-zA-Z0-9_-]{10,}",
        "apiKey:\\s*['\"][^'\"]+['\"]",
        "password:\\s*['\"][^'\"]+['\"]"
      ]
    },
    "blockMessage": "⚠️ BLOCKED - Constitution Violation\n\nDetected:\n- Partial implementation (Article I.1)\n- Hardcoded secrets (Article III.1)\n\n📋 ACTION:\n1. Complete all TODOs/FIXMEs\n2. Move secrets to config system\n3. Run /flow-verify\n\nSource: .claude/rules/project-constitution.md v2.0.0",
    "skipConditions": {
      "sessionSkillUsed": true,
      "fileMarkers": ["@constitution-verified"],
      "envOverride": "SKIP_CONSTITUTION_CHECK"
    }
  }
}
```

## Line Number Reporting (Enhancement)

**Goal**: Precise violation location reporting

**Implementation** (in PreToolUse hook):
```typescript
function detectViolations(content: string, patterns: string[]) {
  const lines = content.split('\n');
  const violations: Array<{line: number, pattern: string, text: string}> = [];

  lines.forEach((line, index) => {
    patterns.forEach(pattern => {
      if (new RegExp(pattern, 'i').test(line)) {
        violations.push({
          line: index + 1,
          pattern: pattern,
          text: line.trim()
        });
      }
    });
  });

  return violations;
}
```

**Enhanced Blocking Message**:
```
⚠️ BLOCKED - Constitution Violation

Detected 3 violations:
  [Line 42] TODO placeholder (Article I.1)
    → "TODO later: Add email verification"

  [Line 58] Hardcoded API key (Article III.1)
    → "API_KEY=sk-abc123def456"

  [Line 73] FIXME comment (Article I.1)
    → "FIXME: Complete error handling"

📋 ACTION: ...
```

## Design Principle

**This guardrail does NOT contain**:
- ❌ Complete Constitution (all 10 Articles are in project-constitution.md)
- ❌ All violation patterns (only Articles I.1, III.1)
- ❌ Batch validation logic (that's in validate-constitution.sh)

**This guardrail ONLY contains**:
- ✅ Articles I.1, III.1 prohibition rule extraction
- ✅ Real-time violation detection (content pattern matching)
- ✅ Blocking mechanism (PreToolUse hook, exit code 2)
- ✅ Precise line number reporting
- ✅ Links to full Constitution document

**Rationale**: Avoid duplication ("不重不漏" principle). Constitution document owns full text, guardrail owns real-time enforcement of critical rules.
