# Benchmark Methodology

This report makes Yao Meta Skill benchmark claims auditable. It distinguishes self-eval evidence from release gates and names the limits of every comparison.

## Benchmark Types

| Type | Purpose | Evidence |
| --- | --- | --- |
| Self-eval | Fast local regression signal during authoring | Trigger suites, output eval cases, packaging checks |
| Internal blind eval | Guard against tuning only visible cases | Blind holdout, adversarial holdout, route confusion |
| External review | Check whether the workflow holds up outside the author context | Human review notes, benchmark scans, release snapshots |

## Sample Sources

- Public fixtures that can be committed and rerun.
- Real but anonymized cases when user content can be safely reduced to metadata or synthetic prompts.
- Failure library entries from prior regressions.
- Near-neighbor prompts that should not trigger the skill.
- Output cases with without-skill and with-skill artifacts.

## Evaluation Dimensions

| Dimension | Evidence |
| --- | --- |
| Trigger reliability | should-trigger, should-not-trigger, near-neighbor, route confusion |
| Output effectiveness | with-skill vs baseline delta, v1 vs v2 delta, assertion grading |
| Context efficiency | entrypoint size, references split, resource-boundary score |
| Runtime compatibility | target package structure, metadata, degradation notes |
| Trust and security | script interface, dependency pinning, permissions, secret scan, package hash |
| Governance and drift | owner, maturity, review cadence, regression history, promotion decisions |
| UX and adoption | quickstart, review viewer, report readability, reviewer handoff |

## Weighting Rule

Any weighted public score must publish:

- exact sample count
- case families
- weights per dimension
- commands used to reproduce results
- failing cases and excluded cases
- commit hash and generated artifact paths

If a score is based on local self-eval only, label it as project-level self-eval rather than external benchmark proof.

## Failure Disclosure

Every release should keep at least one representative failure when failures exist. The release note should say:

- what failed
- why it mattered
- whether the fix was trigger, output, runtime, trust, or governance related
- which test now prevents recurrence

## Reproduction

Recommended release evidence:

```bash
git rev-parse HEAD
python3 scripts/run_output_eval.py
python3 scripts/export_skill_ir.py . --output-json skill-ir/examples/yao-meta-skill.json
python3 scripts/yao.py benchmark-reproducibility .
make ci-test
```

Record generated artifacts in `reports/` and avoid comparing different runtime targets as if their capabilities were identical.
