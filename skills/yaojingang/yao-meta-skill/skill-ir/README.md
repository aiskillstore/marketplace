# Skill IR

Skill IR is the platform-neutral capability contract for Yao Meta Skill 2.0.

The IR keeps core skill semantics stable before any platform-specific packaging:

- job to be done
- trigger surface and exclusions
- workflow steps and failure modes
- references, scripts, assets, and reports
- trigger and output evaluation plan
- risk and governance metadata

Generate the root example:

```bash
python3 scripts/export_skill_ir.py . --output-json skill-ir/examples/yao-meta-skill.json
```

Validate the v0 implementation:

```bash
python3 tests/verify_skill_ir.py
```
