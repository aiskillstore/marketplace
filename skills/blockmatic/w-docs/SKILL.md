---
name: w-docs
description: Document the current code or feature in the owning docs layer.
disable-model-invocation: true
---

Document the current code or feature. Follow the consuming repo's docs and README rules. Do not commit unless asked. Durable information architecture belongs in existing MDX; do not invent a second sitemap.

Write to the layer that owns the change:

| Layer | Role | Update when |
| --- | --- | --- |
| Technical docs (path in `AGENTS.md`) | Architecture, ADRs, how-to | Behavior, architecture, commands, conventions, or workflow changed |
| Agent rules | Short constraints | A convention the agent must not violate changed |
| Nearest README | How to run this app/package; links only | Scripts, setup, or package purpose changed |

Inline comments only when the code is otherwise misleading. Do not copy MDX into rules or READMEs. Do not `@`-attach MDX.

1. Identify the matching docs section, then an existing topic page (create a page only if none fits).
2. Write or patch MDX if the canonical explanation changed.
3. Patch README only for run/setup/scripts; link the MDX.
4. Patch the glob-matched rule only if a constraint changed.
5. For mechanical file or doc moves: propose the smallest from/to list grouped by related files; drop folder-name prefixes inside groups. Save only if the user gave a path. Do not move files unless they also asked to implement.
