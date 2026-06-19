# Runtime Conformance

Runtime Conformance verifies that a skill package can be consumed by target clients without silently losing its core contract.

The v0 suite checks:

- frontmatter `name` and `description`
- description length for Agent Skills / VS Code style clients
- `manifest.json` governance metadata
- `agents/interface.yaml` compatibility metadata
- Skill IR semantic alignment
- target degradation notes
- relative resource paths in IR

Run:

```bash
python3 scripts/run_conformance_suite.py .
```
