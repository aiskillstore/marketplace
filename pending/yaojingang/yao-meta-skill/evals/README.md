# Evals

This directory makes trigger quality and packaging quality more reproducible.

Contents:

- `trigger_cases.json`: full regression set with `family` labels
- `train/`, `dev/`, `holdout/`: split trigger suites for iterative tuning and final verification
- `blind_holdout/`: description-optimization acceptance prompts that do not participate in candidate ranking
- `adversarial/`: harder route-collision prompts for description optimization, including noisy positives and deceptive non-trigger requests
- `confusion/`: sibling-skill routing prompts used to catch route theft and false `no_route` decisions
- `semantic_config.json`: local semantic-intent concepts, exclusions, and weights
- `promotion_policy.md`: formal rules for when a route is promotable
- `baseline_description.txt`: intentionally weaker trigger description
- `improved_description.txt`: current stronger trigger description
- `../reports/description_optimization*.{json,md}`: generated route-optimization reports for the root skill
- `failure-cases.md`: current weak spots and regression targets
- `packaging_expectations.json`: required packaging behaviors for supported targets, including IR provenance, compiler contracts, and semantic parity fields
- `output/`: Output Eval Lab cases, fixtures, and schema for with-skill vs baseline assertion grading
- registry audit tests verify package metadata, compatibility, checksum, owner, license, and Skill IR provenance
- package verification tests verify generated manifests, target adapters, zip archive safety, archive checksum, and registry parity
- install simulation tests verify archive extraction, entrypoint loading, manifest/interface readability, adapter loading, and unsafe zip blocking
- upgrade check tests verify version-bump recommendations, target diff detection, compatibility regression blocking, and release-note evidence
- adoption drift tests verify metadata-only telemetry aggregation, privacy-field blocking, and exclusion of raw local telemetry logs from zip packages
- review waiver tests verify reviewer, reason, expiry, active coverage, expired records, invalid records, and Review Studio integration
- compiler tests verify Skill IR target contracts, adapter modes, generated-file mappings, unsupported targets, and markdown/json report artifacts
- `../reports/`: generated suite JSON plus the homepage-visible family summary panel source

Use:

```bash
python3 scripts/trigger_eval.py --description-file evals/improved_description.txt --cases evals/trigger_cases.json
python3 scripts/trigger_eval.py --description-file evals/improved_description.txt --cases evals/trigger_cases.json --baseline-description-file evals/baseline_description.txt
python3 scripts/run_eval_suite.py
python3 scripts/judge_blind_eval.py --description-file SKILL.md --cases evals/blind_holdout/trigger_cases.json --semantic-config evals/semantic_config.json
python3 scripts/run_description_optimization_suite.py --history-snapshot-output evals/history/description_optimization/YYYY-MM-DD-adversarial-calibration-and-family-drift.json --snapshot-date YYYY-MM-DD --snapshot-id adversarial-calibration-and-family-drift --snapshot-label "Adversarial Calibration And Family Drift"
python3 scripts/build_confusion_matrix.py --history-snapshot-output evals/history/YYYY-MM-DD-route-scorecard-foundation.json --snapshot-date YYYY-MM-DD --snapshot-id route-scorecard-foundation --snapshot-label "Route Scorecard Foundation"
python3 scripts/render_eval_dashboard.py
python3 scripts/render_description_drift_history.py
python3 scripts/render_iteration_ledger.py
python3 tests/verify_description_optimization.py
python3 tests/verify_route_confusion.py
python3 tests/verify_failure_regressions.py
python3 scripts/compile_skill.py . --target openai --target claude --target generic
python3 tests/verify_compile_skill.py
python3 scripts/cross_packager.py . --platform openai --platform claude --expectations evals/packaging_expectations.json --zip
python3 scripts/verify_package.py . --package-dir dist --require-zip
python3 tests/verify_packager_failures.py
python3 tests/verify_package_verification.py
python3 scripts/simulate_install.py . --package-dir dist
python3 tests/verify_install_simulation.py
python3 scripts/run_output_eval.py
python3 tests/verify_output_eval_lab.py
python3 scripts/registry_audit.py .
python3 tests/verify_registry_audit.py
python3 scripts/upgrade_check.py . --previous-package-json registry/examples/yao-meta-skill-1.0.0.json
python3 tests/verify_upgrade_check.py
python3 scripts/render_adoption_drift_report.py . --record-event skill_activation --activation-type explicit --outcome accepted
python3 tests/verify_adoption_drift.py
python3 scripts/render_review_waivers.py .
python3 tests/verify_review_waivers.py
```

Regression scope now includes:

- direct positives
- direct negatives
- near neighbors
- long-context positives
- mixed-intent negatives
- explicit "do not build a skill" negatives
- semantic exclusion cases such as one-off, document-only, and future-outline prompts
- paraphrase families that avoid the original wording while preserving the same trigger intent
- long-context contamination cases where build intent or no-build intent appears after unrelated setup text
- family-based reporting across workflow-to-skill, iterate-existing-skill, document-only, one-off, and future-outline cases
- holdout verification
- description optimization reports that compare baseline, current, and optimized route wording across dev, holdout, blind holdout, and adversarial holdout gates
- judge-backed blind-holdout verification that adds a rubric-based second opinion for blind prompts
- calibration summaries that surface score gaps, threshold margins, and risk bands for each acceptance gate
- family-level drift history that records which blind and adversarial families stay clean over time
- output-quality scorecards that compare without-skill and with-skill artifacts through assertion grading, including near-neighbor and file-backed governed cases
- install-simulation checks that prove generated archives can be extracted into a temporary local skill root and loaded without touching the active global skills directory
- upgrade-readiness checks that compare registry package baselines, recommend semver bumps, and block breaking changes without an adequate declared version
- local-first adoption drift checks that turn accepted, edited, missed, rejected, script-error, and review-overdue metadata into next iteration candidates without storing raw prompts or outputs
- reviewer-waiver checks that keep warning acceptance explicit, expiring, and separate from non-waivable blockers
- compiler checks that turn Skill IR into reviewable target contracts before packaging embeds those contracts into adapters
