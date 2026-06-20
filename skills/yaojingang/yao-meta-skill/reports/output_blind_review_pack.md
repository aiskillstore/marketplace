# Output Blind A/B Review Pack

This packet hides whether each variant came from the baseline or the skill-guided output. Use the separate answer key only after review.

- Pairs: `5`
- Seed: `yao-output-eval-blind-v1`
- Answer key separate: `True`

## Case: skill-package-contract

Prompt: Turn this repeated workflow into a reusable team skill package.

Rubric:
- `has-entrypoint` (1.0): Output names the routeable Skill entrypoint.
- `has-interface` (1.0): Output includes neutral interface metadata.
- `has-report` (1.0): Output points reviewer to generated overview report.
- `has-resource-boundary` (1.0): Output preserves entrypoint/resource separation.

### Variant A

Create a routeable SKILL.md, agents/interface.yaml, reports/skill-overview.html, and a focused eval plan. Keep the root entrypoint lean, move durable guidance into references/, scripts into scripts/, and evidence into reports/.

### Variant B

I can write a prompt for that workflow and include a short checklist.

## Case: output-eval-expectation

Prompt: Upgrade this production skill so we know whether the generated output is better than baseline.

Rubric:
- `has-baseline-comparison` (1.0): Output explicitly compares with-skill and baseline outputs.
- `has-assertion-grading` (1.0): Output includes objective assertion grading.
- `has-scorecard` (1.0): Output produces a scorecard report path.
- `has-failure-taxonomy` (1.0): Output records failure taxonomy.

### Variant A

Add Output Eval Lab cases with baseline_output and with_skill_output, run assertion grading, report with-skill vs baseline pass-rate delta, and record failure taxonomy plus next fixes in reports/output_quality_scorecard.md.

### Variant B

Add more examples and run the trigger eval again.

## Case: ir-before-packaging

Prompt: Package this skill for OpenAI, Claude, Agent Skills, and generic targets.

Rubric:
- `has-ir-first` (1.0): Output requires Skill IR before packaging.
- `has-core-ir-fields` (1.0): Output lists core IR contract fields.
- `has-targets` (1.0): Output names requested runtime targets.
- `has-semantic-preservation` (1.0): Output says targets must preserve the capability contract.

### Variant A

Export folders for each platform and adjust files as needed.

### Variant B

Export Skill IR first with job_to_be_done, trigger_surface, workflow, resources, eval_plan, risk, and governance. Then compile or package targets from the IR so OpenAI, Claude, Agent Skills, and generic packages preserve the same capability contract.

## Case: near-neighbor-boundary

Prompt: I only need a one-off summary of these notes, not a reusable process.

Rubric:
- `declines-skill` (1.0): Output refuses unnecessary skill creation for one-off work.
- `names-near-neighbor` (1.0): Output labels the request as near-neighbor instead of owned work.
- `requires-reuse-signal` (1.0): Output asks for repeat-use evidence before packaging.

### Variant A

Create a SKILL.md and a reusable workflow anyway so future notes can use it.

### Variant B

Do not create a skill for this one-off request. Treat it as a near-neighbor: answer the summary directly unless the user confirms repeated use, shared ownership, or a reusable output contract.

## Case: file-backed-governed-package

Prompt: Turn the attached release brief source into a governed skill package.

Rubric:
- `uses-file-backed-evidence` (1.0): Output names file-backed source evidence.
- `has-governance` (1.0): Output preserves governed ownership metadata.
- `has-output-contract` (1.0): Output preserves output and rollback boundaries.
- `has-trust-and-scorecard` (1.0): Output requires trust and output scorecard artifacts.
- `does-not-invent-evidence` (1.0): Output forbids invented launch evidence.

### Variant A

Draft a release announcement with the changelog, support notes, and owner name.

### Variant B

Use the file-backed fixture as source evidence, then create a governed skill package with SKILL.md, agents/interface.yaml, owner, review cadence, input_files, output contract, rollback boundary, trust report, and reports/output_quality_scorecard.md. Mark missing launch metrics as missing evidence instead of inventing them.
