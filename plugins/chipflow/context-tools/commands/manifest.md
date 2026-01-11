# Regenerate Project Manifest

Regenerate the project manifest to refresh understanding of this project's structure, build system, and entry points.

Run this command:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate-manifest.py
```

The manifest captures:
- **Languages detected** in the project
- **Build system** and commands (npm, uv, pdm, cargo, cmake, etc.)
- **Entry points** (main scripts, CLI tools)
- **Git activity** summary

The manifest is saved to `.claude/project-manifest.json`.
