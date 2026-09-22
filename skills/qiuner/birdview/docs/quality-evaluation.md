# Coding quality comparison protocol

[中文](quality-evaluation.zh.md)

Status: first automated comparison batch started on 2026-09-17; results and independent review are pending. Measure code outcomes and costs rather than confirm a marketing claim. Tasks are proposed requirements grounded in source interfaces, not confirmed product defects.

## Experiment

- Round one: A loads no Birdview; B uses fixed v0.2.1 in auto mode. Hold exact model version, reasoning effort, host, tools, network policy, OS and dependencies constant. Disable other optional skills in both arms.
- Six tasks, three independent runs per task per arm: 36 runs. First use a separate unscored practice task to validate isolation, logging and scoring; adjust budgets only before scored runs.
- Use clean independent checkouts, fresh sessions, separate user configuration and temporary directories. On-demand mode alone is not a control. Disable shared memory, old maps, other runs' artifacts and external answer searches. Retain identical necessary project instructions.
- B loads its skill from a separate read-only directory, not editable target source. Record skill commit and file hashes; A cannot access that directory.
- Approved execution budget: 30 minutes per run with no token cap; record input, output and cached tokens, including mapping and context reads. Score the last state on timeout and record it; do not silently extend time limits. Unavailable usage is null, never zero. The initial 60,000-token proposal was removed with user authorization after the unscored pilot.
- Freeze identical task prompts without arm labels, implementation locations or hidden tests. Only B's host enables Birdview. Prepare necessary clarification answers in advance, apply identical response rules and retain exchanges.
- Freeze random seed and order before running. Randomize A/B order within each task/repetition and interleave runs. Stop the batch if the model version changes rather than pooling versions.
- This local Codex session already has Birdview exposure through skills and history. It cannot serve as either measured run; validate runner isolation first.

## Source baselines and contamination

| Project | Starting commit | Role |
| --- | --- | --- |
| Birdview | f8b6f372683ee55febaa352b2f150576690df112 | Three harness calibration tasks; report separately, not primary effectiveness evidence |
| DeepSeek Harness | 7a0b7682b6690f0aa2d93438c4d526b38ab45777 | Three external-project tasks; preliminary evidence from only one project |

Birdview contains SKILL.md, workflow references and renderers: not installing the skill cannot remove this contamination. Do not delete essential source to improve results. Add a third project without Birdview content before discussing cross-project effectiveness. Public-source tasks may also have pretraining contamination.

## Six task cards

The requirements below can be given to the model; acceptance outlines are evaluation design, not injected instructions. Implement, freeze and hash real hidden tests on an isolated evaluator. Do not put this protocol in the target checkout.

### B1: CLI help (small-change overhead)

Prompt: Add top-level --help and -h to the Birdview CLI, listing doctor, mode and agent options with successful exit. Unknown commands must still fail. Help must not modify project files.

Acceptance: both aliases exit 0 and list supported commands/agents; temporary project files remain byte-identical; unknown command exits nonzero; existing mode tests pass.
Source basis, withheld from the model: scripts/birdview.mjs and test/mode.test.mjs.

### B2: BOM input compatibility (edge handling)

Prompt: Allow validation and rendering commands to read UTF-8 BOM architecture JSON and activity JSONL with a BOM at the start of the file. Preserve ordinary files and blank-line handling; invalid input still fails and input files remain unchanged.

Acceptance: both commands with/without BOM and with/without activity; CRLF and blank lines; syntax and semantic errors remain nonzero; unchanged input hashes; correct embedded HTML data. Mid-file BOM support is not required.
Source basis: scripts/validate.mjs, scripts/render.mjs and contract/render tests.

### B3: Protect existing render output (filesystem behavior)

Prompt: Add --no-clobber to the rendering command. With this option, create a new HTML output but fail without changing any bytes when the output already exists. Preserve default overwrite behavior, activity input and --simulation compatibility, and automatic creation of parent directories.

Acceptance: successful new output; existing output fails and remains byte-identical; legacy overwrite works; nested output with activity and simulation works; original contract/render tests pass. Source basis: scripts/render.mjs. The original title task was replaced before scored runs because localized project titles already existed.

### D1: Zero source size disables loading (configuration semantics)

Prompt: Allow maxSourceBytes=0 in DeepSeek Harness instruction loading to mean no instruction files are loaded. Preserve positive-integer behavior; configuration validation rejects negatives and fractions. Update relevant documentation.

Acceptance: configuration accepts zero; global/project/local instructions stay out of context; one and default values remain compatible; negatives/fractions rejected; other providers unaffected. Preserve existing maxBytes disabling behavior.
Source basis: packages/context/agent-instructions/src/config.ts, files.ts and corresponding tests.

### D2: Configurable project root markers (configuration and discovery)

Prompt: Add projectRootMarkers configuration to DeepSeek Harness filesystem skill discovery, defaulting to only .git. Select the nearest matching ancestor; markers may be files or directories. Fall back to cwd with no match; an empty list disables upward search. Preserve skill source priority and document the behavior.

Acceptance: defaults, file/directory markers, nearest nested ancestor, no match, empty list; skills come from the selected project root; user/custom priorities unchanged; working directories do not contaminate each other.
Source basis: roots/findProjectRoot in packages/skill/skill-filesystem/src/index.ts and tests. Check for equivalent existing support before freezing.

### D3: Same-directory instruction deduplication (seeded regression)

Prompt: Fix an instruction loading regression: same-directory candidates whose bodies match after trimming should load only the earliest candidate. Equal bodies in different directories must both remain. Local overlays and base candidates share same-directory deduplication without changing order.

Acceptance: duplicate base candidates, overlay/base duplicates, equal bodies across directories, reordered candidates and distinct content; existing instruction tests pass.
Source basis: discovery/deduplication and tests in packages/context/agent-instructions. The baseline already documents correct behavior: prepare a minimal faulty seed patch first and use the identical patch hash for both arms. This task is not runnable until the seed is verified. It is evaluation-only, not an upstream product change.

## Acceptance and scoring

1. Before running, establish reproducible baselines, hidden tests and a human-reviewed reference fix for each task. The baseline must fail new requirement assertions and the reference fix must pass. Original regression checks must pass on the unmutated baseline. Otherwise repair or replace the task and refreeze, never select tasks after seeing outcomes.
2. Inject hidden tests into a separate evaluation copy after the model exits, using trusted tests/dependencies to prevent score gaming. Assert publicly specified behavior, not reference implementation structure. Classify all failures.
3. Primary metric: strict task success = runs passing every required acceptance check with no new failures in agreed regression checks / all valid runs. Tasks have equal weight regardless of assertion counts. Report partial acceptance separately.
4. Timeouts, model errors, incomplete work and test tampering count as failures. Log-confirmed runner infrastructure failures are invalid, retained and rerun as pairs. Product build failures are not infrastructure failures.
5. Anonymous code review sees product patches and test outcomes, not arm, maps or sessions. Two reviewers independently score scope control, responsibility/interface clarity, unnecessary complexity and behavioral verification 0/1/2 (material problem/adequate/evidenced strength), citing files/symbols. Preserve initial scores when resolving disagreement. Style may reveal the arm; anonymity is not perfect blinding.
6. Separately report wall time, input/output/cached tokens, tool calls, cost and product diff size, with identical dependency warmup policy. Maps/activity count toward process cost, not unrelated product-code penalties or quality bonuses.
7. For B, record actual skill reads, pre-edit maps, source evidence/scope and truthful checks. Keep noncompliant runs in B's primary outcomes; report adherence separately rather than selecting only successfully activated runs.
8. Report per-task successes out of three, paired wins/ties/losses, review scores and median/range costs. Separate project tables; 18 runs per arm are not 18 independent tasks. Do not claim significance or universal benefit from this small sample. Publish failures and extra costs too.

## Records and execution gates

Record runId, taskId, repeat, anonymous arm key, baseCommit, seedPatchHash, skillCommit/hash (null for A), model/version, reasoning, hostVersion, environment/lock hashes, budgets, randomized order, start/end times, termination reason, dialogue/tool log paths, patch hash, hidden-test hash/results, regression outcomes, costs and review scores/reasons. Store the arm mapping separately from reviewers.

Execution configuration: gpt-5.6-sol, medium reasoning, Codex CLI 0.151.0, isolated Linux Docker containers. The configured provider exposes a model alias, not a verifiable immutable backend snapshot; record returned model names and disclose this reproducibility limit. Pricing is unavailable, so monetary cost remains null. Code-generating containers have no hidden tests, reference fixes or host skills, and use an internal network with a model-only relay. Scoring runs separately without network access and restores trusted baseline tests.

Before scoring, validate each task's baseline/reference pair on the execution platform, freeze prompts and artifact hashes, and verify isolation with the unscored pilot. Reference fixes are agent-authored and inspected, not independently human-approved; blind maintainability review remains separate from automated correctness. This protocol produces no quality scores itself.

Local execution checkpoint: all six baseline/reference acceptance pairs were verified. DeepSeek Harness's unchanged and reference regression suites each passed 177/177 tests with the same dropped Linux capabilities used by scored runs; an earlier unrestricted-root run invalidated a file-permission assertion and is retained as an environment diagnostic. Both isolated practice arms completed and passed independent behavior assertions. The 36-run batch freezes image IDs, source commits, evaluator/skill hashes, seed data and paired order before execution. These checks validate the runner, not a coding-quality improvement; independent review is still outstanding.

In round two, compare v0.2.0 with v0.2.1 on frozen tasks, adding an explicitly requested architecture-review task to exercise the new instructions. Ordinary coding outcomes cannot establish the benefit of a review route that never activated.
