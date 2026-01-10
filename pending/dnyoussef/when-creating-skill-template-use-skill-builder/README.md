# Skill Builder - Quick Start

## Purpose
Generate Claude Code Skills with proper YAML frontmatter, structure, and documentation.

## When to Use
- Creating new skills
- Standardizing skill format
- Building skill libraries

## Quick Start

```bash
npx claude-flow@alpha skill-run skill-builder \
  --name "my-skill" \
  --category "utilities" \
  --agents "coder,tester"
```

## 5-Phase Process

1. **Design Structure** (5 min) - Define metadata and phases
2. **Generate Template** (5 min) - Create 4 core files
3. **Implement** (8 min) - Add code and examples
4. **Test** (5 min) - Validate syntax and execution
5. **Document** (2 min) - Add usage guide

## Output Files

- `SKILL.md` - Main skill specification
- `README.md` - Quick start guide
- `PROCESS.md` - Detailed workflow
- `process-diagram.gv` - Visual diagram

## Success Criteria

- Valid YAML frontmatter
- All 4 files created
- Passes validation
- Executable skill

For detailed documentation, see SKILL.md
