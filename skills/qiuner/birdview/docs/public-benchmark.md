# Public Benchmark Report

[中文](public-benchmark.zh.md)

Status: scoring integration is working and model runs have started. Aggregate results have not been finalized for this report. This report does not establish that Birdview improves coding quality.

Official scoring smoke check passed on 2026-09-17 for `sympy__sympy-20590`: the reference patch resolved the issue; the unmodified source did not. Task image digest: `sha256:3a282752833ce34730ee0621e22033501c993f45742775ca57f04c9ff27178a0`. This is an evaluator check, not a Birdview score. Initial setup failures from network downloads, Windows checkout line endings and a missing Docker CLI are retained as infrastructure records. Evaluation text is normalized to LF before Linux execution; the official grader is unchanged.

## Comparison

| Metric | Without Birdview | Birdview auto | Difference |
| --- | --- | --- | --- |
| Officially resolved issues | Pending / 20 | Pending / 20 | Pending |
| Completed within budget | Pending / 20 | Pending / 20 | Pending |
| Median task time | Pending | Pending | Pending |
| Input / cached / output tokens | Pending | Pending | Pending |
| Monetary cost | Unavailable | Unavailable | Unavailable |

The final report will include a paired outcome chart, per-task results, time and token distributions, concrete successful and failed patches, and links to reproduction artifacts. Fewer lines alone do not establish better code. Official resolution and completion within budget will be reported separately.

## Frozen Design

- Source: [SWE-bench Verified](https://www.swebench.com/), a subset of 20 tasks from 12 repositories. This is not a full leaderboard result or official certification.
- Select before model runs using seed `birdview-swebench-20260917-v1`: sort tasks within each repository by SHA-256 of seed plus instance ID, then select round-robin in repository-name order. Include only Verified test tasks. Exclude the integration task `sympy__sympy-20590`.
- Official harness commit: `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`. A local manifest pins the task repository, source commits, prompts, task hashes and image names. Record image digests before model execution.
- Two arms: the same coding agent without Birdview and with Birdview auto. Initial model configuration: `gpt-5.6-sol`, medium reasoning; one run per task per arm, 40 runs total. The provider exposes an alias, not an immutable model snapshot.
- Preserve the 30-minute task budget, with no token cap. Record infrastructure failures separately and rerun affected pairs with fresh attempt IDs; retain all originals. Do not retry genuine task failures selectively.
- Before measured runs, require the official reference patch to resolve the integration task and the unmodified source to fail it, each in a fresh container.
- Agents receive issue text and clean source only. Reference patches, test patches, test labels, evaluator scripts and Docker socket stay outside their containers. The trusted scorer uses the official evaluation procedure in separate containers.

## Interpretation

The earlier custom-task experiment is a separate pilot and will not be pooled with this public benchmark. Twenty tasks and one repeat provide preliminary evidence, not a universal effect estimate. Public tasks can be present in model training data. Paired success counts, failures and missing measurements must remain visible; report independent code review separately from test outcomes.

Presentation is inspired by [Ponytail's agentic report](https://github.com/DietrichGebert/ponytail/blob/main/benchmarks/results/2026-06-18-agentic.md): real agent sessions, the same-agent baseline, actual patches, cost accounting and explicit limitations. Its published performance numbers are not Birdview results.
