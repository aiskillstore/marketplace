# Dependency Mapper - Quick Start Guide

## What is Dependency Mapper?

A comprehensive tool for analyzing, visualizing, and auditing software dependencies across multiple programming languages and package managers.

## When to Use

- Before major releases to audit dependencies
- When investigating build issues or conflicts
- For security vulnerability assessments
- When optimizing bundle sizes
- To detect circular dependencies
- For license compliance auditing
- When debugging version conflicts

## Quick Start

### 1. Basic Usage

```bash
# Analyze current project
/dep-map .

# Analyze specific project
/dep-map /path/to/project

# With security audit
/dep-map . --security

# With circular dependency detection
/dep-map . --circular

# Generate HTML visualization
/dep-map . --format html
```

### 2. Using the Subagent

```javascript
Task("Dependency Mapper",
  "Analyze dependencies in ./my-app with full security audit and visualization",
  "code-analyzer")
```

### 3. Using MCP Tool

```javascript
mcp__dependency-mapper__analyze({
  project_path: "./my-app",
  include_security: true,
  detect_circular: true,
  check_outdated: true,
  visualization_format: "html"
})
```

## Output Examples

### Console Output
```
📦 Dependency Analysis Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project: my-app
Package Manager: npm v9.5.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Statistics:
  ├─ Total Dependencies: 847
  ├─ Direct Dependencies: 23
  ├─ Dev Dependencies: 15
  ├─ Transitive Dependencies: 809
  └─ Max Depth: 8 levels

🔒 Security:
  ├─ Critical: 0
  ├─ High: 2 ⚠️
  ├─ Medium: 5
  └─ Low: 12

🔄 Circular Dependencies: 0 ✓

📦 Outdated Packages: 15
  ├─ Major updates: 3
  ├─ Minor updates: 7
  └─ Patch updates: 5

⚖️  License Issues: 0 ✓

✅ Recommendations:
  1. Update lodash to fix high-severity vulnerability
  2. Update axios to patch medium-severity issue
  3. Consider updating react to latest major version
  4. Remove unused dependency: moment (use date-fns instead)
```

### JSON Report Structure
```json
{
  "metadata": {
    "project_name": "my-app",
    "package_manager": "npm",
    "analysis_date": "2025-10-30T14:23:45Z",
    "analysis_duration_ms": 1847
  },
  "statistics": {
    "total": 847,
    "direct": 23,
    "dev": 15,
    "transitive": 809,
    "max_depth": 8
  },
  "security": {
    "vulnerabilities": {
      "critical": 0,
      "high": 2,
      "medium": 5,
      "low": 12
    },
    "affected_packages": [...]
  },
  "circular_dependencies": [],
  "outdated_packages": [...],
  "license_analysis": {...},
  "dependency_tree": {...}
}
```

## Common Workflows

### Workflow 1: Pre-Release Security Audit
```bash
# 1. Run full security scan
/dep-map . --security --format json > security-report.json

# 2. Review critical and high vulnerabilities
cat security-report.json | jq '.security.vulnerabilities'

# 3. Update vulnerable packages
npm audit fix

# 4. Verify fixes
/dep-map . --security
```

### Workflow 2: Bundle Size Optimization
```bash
# 1. Generate dependency visualization
/dep-map . --format html

# 2. Open visualization in browser
# Identify large/duplicate dependencies

# 3. Replace heavy dependencies
# Example: Replace moment with date-fns

# 4. Verify size reduction
/dep-map . --format json | jq '.statistics'
```

### Workflow 3: Circular Dependency Resolution
```bash
# 1. Detect circular dependencies
/dep-map . --circular

# 2. Review circular paths
# Output shows: A → B → C → A

# 3. Refactor to break cycles
# Move shared code to new module

# 4. Verify resolution
/dep-map . --circular
```

## Integration Examples

### CI/CD Integration (GitHub Actions)
```yaml
name: Dependency Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: /dep-map . --security --format json > report.json
      - run: |
          CRITICAL=$(jq '.security.vulnerabilities.critical' report.json)
          if [ "$CRITICAL" -gt 0 ]; then
            echo "Critical vulnerabilities found!"
            exit 1
          fi
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

if git diff --cached --name-only | grep -q "package.json\|package-lock.json"; then
  echo "📦 Running dependency analysis..."
  /dep-map . --security --circular

  if [ $? -ne 0 ]; then
    echo "❌ Dependency issues detected. Fix before committing."
    exit 1
  fi
fi
```

## Command Reference

| Command | Description |
|---------|-------------|
| `/dep-map [path]` | Basic dependency analysis |
| `/dep-map [path] --security` | Include security audit |
| `/dep-map [path] --circular` | Detect circular dependencies |
| `/dep-map [path] --outdated` | Check for outdated packages |
| `/dep-map [path] --format json` | Output as JSON |
| `/dep-map [path] --format html` | Generate HTML visualization |
| `/dep-map [path] --format svg` | Export SVG diagram |
| `/dep-map [path] --max-depth N` | Limit tree depth |
| `/dep-map [path] --cache` | Use cached results |

## Configuration

Create `.dependency-mapper.json` in project root:

```json
{
  "exclude_patterns": [
    "node_modules/**/test/**",
    "**/examples/**"
  ],
  "security_scan": {
    "enabled": true,
    "sources": ["npm", "snyk", "github"],
    "fail_on_severity": "high"
  },
  "circular_detection": {
    "enabled": true,
    "max_path_length": 10
  },
  "outdated_check": {
    "enabled": true,
    "include_dev_dependencies": true
  },
  "visualization": {
    "default_format": "html",
    "max_nodes": 1000,
    "highlight_vulnerabilities": true
  }
}
```

## Troubleshooting

### Problem: "Package manager not detected"
**Solution**: Ensure lock files are present (package-lock.json, yarn.lock, etc.)

### Problem: "Analysis timeout"
**Solution**: Use `--max-depth 5` or `--cache` flag

### Problem: "Cannot generate visualization"
**Solution**: Install graphviz: `apt-get install graphviz` or `brew install graphviz`

### Problem: "Security scan fails"
**Solution**: Check internet connection or use offline mode

## Performance Tips

1. Use caching for repeated analyses
2. Limit depth for large projects
3. Run security scans asynchronously
4. Use incremental analysis for CI/CD
5. Cache vulnerability databases locally

## Support

- Full Documentation: See SKILL.md
- Process Details: See PROCESS.md
- Technical Implementation: See subagent-dependency-mapper.md
- Issues: Report at project repository

## License

MIT - Part of Claude Code Skills Collection
