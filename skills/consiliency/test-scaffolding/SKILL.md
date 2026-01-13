---
name: test-scaffolding
description: "Generate test file scaffolds from source analysis with language-appropriate templates."
---

# Test Scaffolding Skill

Generate test file scaffolds for source files, enabling TDD workflows. Scaffolds contain TODO stubs that the test-engineer agent fills during lane execution.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SOURCE_FILES | [] | List of source files to scaffold tests for |
| TEST_FRAMEWORK | auto | Framework to use (auto-detects from manifest) |
| OUTPUT_DIR | tests/ | Where to place generated test files |
| NAMING_CONVENTION | language-default | Test file naming pattern |
| INCLUDE_FIXTURES | true | Generate fixture stubs |
| STUB_STYLE | todo | `todo` (TODO comments) or `skip` (skip markers) |

## Workflow (Mandatory)

1. **Detect stack**: Read package manifest (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`)
2. **Identify framework**: Match test dependencies (pytest, vitest, jest, testing, cargo test)
3. **Analyze sources**: Extract public functions, classes, methods from each source file
4. **Map to tests**: Apply naming convention to determine test file paths
5. **Generate scaffolds**: Use language template, insert TODO stubs for each testable unit
6. **Return manifest**: JSON with generated files, skipped files, and unit counts

## Supported Frameworks

| Language | Frameworks | Detection |
|----------|------------|-----------|
| Python | pytest, unittest | `pyproject.toml` → `[tool.pytest]` or `pytest` in deps |
| TypeScript | vitest, jest | `package.json` → `vitest` or `jest` in devDeps |
| JavaScript | vitest, jest | `package.json` → `vitest` or `jest` in devDeps |
| Go | testing | `go.mod` → built-in testing package |
| Rust | cargo test | `Cargo.toml` → built-in test harness |
| Dart | flutter_test, test | `pubspec.yaml` → `flutter_test` or `test` in dev_deps |

## Naming Conventions

| Language | Source | Test File |
|----------|--------|-----------|
| Python | `src/auth/login.py` | `tests/auth/test_login.py` |
| TypeScript | `src/auth/login.ts` | `src/auth/login.test.ts` or `tests/auth/login.test.ts` |
| Go | `pkg/auth/login.go` | `pkg/auth/login_test.go` |
| Rust | `src/auth/login.rs` | inline `#[cfg(test)]` module |
| Dart | `lib/auth/login.dart` | `test/auth/login_test.dart` |

## Source Analysis Heuristics

### Python
- Detect `def function_name(` where name doesn't start with `_`
- Detect `class ClassName:` for public classes
- Extract method signatures within classes
- Skip `__init__`, `__str__`, etc. (dunder methods)

### TypeScript/JavaScript
- Detect `export function`, `export const`, `export class`
- Detect `export default function/class`
- Parse JSDoc/TSDoc for parameter types

### Go
- Detect exported functions (capitalized names)
- Detect exported methods on structs
- Detect exported types

### Rust
- Detect `pub fn`, `pub struct`, `pub enum`
- Detect `impl` blocks with public methods

## Output Schema

```json
{
  "format": "scaffold-manifest/v1",
  "generated_at": "<ISO-8601 UTC>",
  "framework": "pytest",
  "generated": [
    {
      "source": "src/auth/login.py",
      "test": "tests/auth/test_login.py",
      "units": ["login", "logout", "refresh_token"],
      "unit_count": 3
    }
  ],
  "skipped": [
    {
      "source": "src/auth/utils.py",
      "reason": "test file exists"
    }
  ],
  "total_units": 12
}
```

## Red Flags (Stop & Verify)

- No package manifest found → prompt user for framework
- Source file has no public functions → skip with warning
- Test file already exists → skip unless `--force` specified
- Unable to parse source file → log warning, continue with others

## Integration Points

### With `/ai-dev-kit:plan-phase`
- Called to auto-populate `Tests Owned Files` column
- Uses `Owned Artifacts` from impl tasks as source files

### With `/ai-dev-kit:execute-lane`
- Called before test-engineer agent runs
- Scaffolds committed with `chore(P{n}-{lane}): scaffold test files`

### With `test-engineer` agent
- Agent detects TODO markers in scaffolds
- Fills in test implementations
- Removes TODO markers when complete

## Provider Notes

- Use this skill when `/ai-dev-kit:scaffold-tests` is invoked
- Prefer TODO-style stubs over skip markers for visibility
- Preserve source file structure in test organization
- Include proper imports based on detected framework
