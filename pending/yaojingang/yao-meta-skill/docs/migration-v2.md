# Migration To Skill OS 2.0

This document tracks the first migration path from Yao Meta Skill 1.x to the Skill OS 2.0 architecture.

## 1.x To 2.0 Mapping

| 1.x Asset | 2.0 Role |
| --- | --- |
| `SKILL.md` frontmatter | `skill-ir.trigger_surface.description` |
| `reports/intent-context.json` | `skill-ir.job_to_be_done` and input/output assumptions |
| `evals/trigger_cases.json` | `skill-ir.trigger_surface` samples and Trigger Eval Lab |
| `reports/baseline-compare.*` | legacy baseline evidence for Output Eval Lab |
| `reports/output-risk-profile.*` | failure taxonomy seed for Output Eval Lab |
| `agents/interface.yaml` | target compatibility seed for runtime conformance |
| `manifest.json` | governance and registry metadata seed |

## Migration Steps

1. Export Skill IR:

   ```bash
   python3 scripts/export_skill_ir.py . --output-json skill-ir/examples/yao-meta-skill.json
   ```

2. Run Output Eval Lab:

   ```bash
   python3 scripts/run_output_eval.py
   ```

3. Run runtime conformance and trust checks:

   ```bash
   python3 scripts/run_conformance_suite.py .
   python3 scripts/trust_check.py .
   ```

4. For library or team workspaces, build the Skill Atlas:

   ```bash
   python3 scripts/build_skill_atlas.py --workspace-root . --output-dir skill_atlas --report-html reports/skill_atlas.html --report-json reports/skill_atlas.json
   ```

   This also writes `skill_atlas/drift_signals.json` from aggregate `reports/adoption_drift_report.json` files. Do not migrate or publish raw `reports/telemetry_events.jsonl` logs.

5. Keep legacy trigger eval gates intact while output eval coverage grows.

6. Move adapter-specific logic toward future compiler commands after IR fields are stable.

7. Treat new 2.0 checks as tiered gates: scaffold stays light, production adds output eval, library adds conformance and atlas, governed adds trust and release evidence.

## Compatibility Strategy

No existing 1.x command is removed in the v0 migration. New commands produce additional artifacts and should become release gates only after their cases and schemas stabilize.

## Deprecation Notes

- Legacy baseline compare remains useful but should not be treated as full output quality proof.
- Platform packaging should continue to work directly until compiler-based packaging is introduced.
- Review Studio 2.0 should aggregate existing reports before replacing any current report.
- Conformance v0 is a structural and metadata gate; it does not yet simulate each client runtime.
- Trust v0 blocks obvious secret and remote-inline-execution risks, while surfacing script and dependency warnings for reviewer judgment.
- Skill Atlas v0 is local-first portfolio analysis; avoid committing reports generated from private parent workspaces unless the names and routes are intended to be shared.
