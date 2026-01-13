---
name: library-detection
description: "Detect project stack from package manifests (package.json, pyproject.toml, go.mod, Cargo.toml, pubspec.yaml, CMakeLists.txt). Auto-identify frameworks, test tools, and build systems for onboarding."
---

# Library Detection Skill

Automatically detect the technology stack of a project by analyzing package manifests and configuration files. Returns structured data for use in onboarding, documentation discovery, and tool configuration.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SCAN_DEPTH | 3 | Max directory depth to search for manifests |
| INCLUDE_DEV_DEPS | true | Include development dependencies in analysis |
| DETECT_FRAMEWORKS | true | Identify frameworks from dependencies |
| DETECT_TEST_TOOLS | true | Identify test frameworks and runners |
| OUTPUT_FORMAT | json | Output format: json, markdown, or toon |

## Instructions

**MANDATORY** - Follow the Workflow steps below in order. Do not skip steps.

1. Scan for package manifests in the project
2. Parse each manifest to extract dependencies
3. Classify dependencies into categories
4. Detect frameworks and test tools from dependency patterns
5. Output structured stack summary

## Red Flags - STOP and Reconsider

If you're about to:
- Assume a framework without checking imports or config files
- Skip manifest files because "the project is simple"
- Hardcode framework versions instead of reading from manifests
- Report a library without verifying it's actually used

**STOP** -> Read the manifest files -> Verify with imports/configs -> Then report

## Workflow

### 1. Discover Manifests

Scan for these files (in order of priority):

| File | Language | Parser |
|------|----------|--------|
| `package.json` | JavaScript/TypeScript | JSON |
| `pyproject.toml` | Python | TOML |
| `requirements.txt` | Python | Line-based |
| `go.mod` | Go | Go mod |
| `Cargo.toml` | Rust | TOML |
| `pubspec.yaml` | Dart/Flutter | YAML |
| `CMakeLists.txt` | C/C++ | CMake |
| `meson.build` | C/C++ | Meson |
| `WORKSPACE` | Bazel | Bazel |
| `pom.xml` | Java | XML |
| `build.gradle` | Java/Kotlin | Gradle DSL |
| `Gemfile` | Ruby | Ruby DSL |
| `composer.json` | PHP | JSON |

Also check for:
- `Dockerfile` - containerization
- `docker-compose.yml` - container orchestration
- `.github/workflows/*.yml` - CI/CD
- `Makefile` - build system
- `tsconfig.json` - TypeScript config
- `vite.config.*` / `webpack.config.*` - bundlers

### 2. Parse Dependencies

For each manifest, extract:
- **Production dependencies**: runtime requirements
- **Development dependencies**: build/test tools
- **Peer dependencies**: expected host environment
- **Optional dependencies**: feature flags

### 3. Classify Stack

Group findings into:

```json
{
  "languages": ["typescript", "python", "go", "rust", "dart", "cpp"],
  "frameworks": [
    {"name": "react", "version": "^18.0.0", "category": "frontend"},
    {"name": "fastapi", "version": "^0.100.0", "category": "backend"}
  ],
  "test_frameworks": [
    {"name": "vitest", "version": "^1.0.0"},
    {"name": "pytest", "version": "^7.0.0"}
  ],
  "build_tools": ["vite", "uv", "docker"],
  "databases": ["postgresql", "redis"],
  "cloud_providers": ["aws", "vercel"],
  "ci_cd": ["github-actions"]
}
```

### 4. Framework Detection Patterns

Use the cookbook for specific detection logic:
- Read `./cookbook/manifest-parsing.md` for parsing rules
- Match dependency names against known framework patterns

### 5. Output

Return the structured stack summary in the requested format.

## Cookbook

### Manifest Parsing
- IF: Parsing any package manifest
- THEN: Read and execute `./cookbook/manifest-parsing.md`

## Quick Reference

### Detection Patterns

| Dependency Pattern | Detected As |
|--------------------|-------------|
| `react`, `react-dom` | React framework |
| `vue`, `@vue/*` | Vue framework |
| `next` | Next.js framework |
| `fastapi` | FastAPI framework |
| `django` | Django framework |
| `flask` | Flask framework |
| `express` | Express.js framework |
| `vitest`, `jest` | JavaScript test framework |
| `pytest` | Python test framework |
| `gtest`, `gmock`, `catch2` | C/C++ test framework |
| `flutter`, `flutter_test` | Flutter framework |
| `@testing-library/*` | Testing utilities |

### Category Mappings

| Category | Examples |
|----------|----------|
| frontend | react, vue, svelte, angular |
| backend | fastapi, django, express, gin |
| database | prisma, sqlalchemy, typeorm |
| testing | vitest, jest, pytest, playwright |
| build | vite, webpack, esbuild, rollup |
| linting | eslint, prettier, ruff, black |
| typing | typescript, mypy, pyright |
| build-native | cmake, meson, bazel |

## Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "project_root": {"type": "string"},
    "scanned_at": {"type": "string", "format": "date-time"},
    "languages": {
      "type": "array",
      "items": {"type": "string"}
    },
    "frameworks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "version": {"type": "string"},
          "category": {"type": "string"}
        }
      }
    },
    "test_frameworks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "version": {"type": "string"}
        }
      }
    },
    "build_tools": {
      "type": "array",
      "items": {"type": "string"}
    },
    "databases": {
      "type": "array",
      "items": {"type": "string"}
    },
    "cloud_providers": {
      "type": "array",
      "items": {"type": "string"}
    },
    "ci_cd": {
      "type": "array",
      "items": {"type": "string"}
    },
    "manifests_found": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

## Integration

Other skills and commands can use this skill for:

1. **Documentation discovery**: Map detected frameworks to doc sources
2. **Onboarding**: Generate quickstart guides tailored to the stack
3. **Tool configuration**: Auto-configure linters, formatters, test runners
4. **Agent routing**: Select appropriate AI providers based on stack

Example usage in another skill:
```markdown
## Prerequisites

Before implementing, run the `library-detection` skill to identify:
- Test frameworks (for writing tests)
- Build tools (for verification)
- Database libraries (for data layer work)
```
