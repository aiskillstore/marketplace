# Skill Atlas

Skill Atlas is the Skill OS 2.0 layer for managing a workspace of multiple skills.

It detects:

- catalog metadata
- route overlap
- shared resource dependencies
- stale skills
- missing owner / review metadata
- no-route opportunities from failure notes

Run against a workspace:

```bash
python3 scripts/build_skill_atlas.py --workspace-root .. --output-dir skill_atlas --report-html reports/skill_atlas.html --report-json reports/skill_atlas.json
```

The script is local-first and does not modify scanned skills.
