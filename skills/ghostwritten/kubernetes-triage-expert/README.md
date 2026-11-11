# Kubernetes Triage Expert

Kubernetes Triage Expert is a prompt-first troubleshooting skill specification for Kubernetes incidents. It is built to help engineers reason about faults using only the evidence already present in the conversation, without pretending to be an agent, a tool runner, or a live cluster observer.

This repository defines a narrow and deliberate operating model: structured Kubernetes triage with hard boundaries.

[中文说明](./docs/README_zh.md)

## Quick Start

Pick the environment you use and install the skill there.

### Codex

```bash
mkdir -p "$CODEX_HOME/skills/kubernetes-triage-expert"
cp ./SKILL.md "$CODEX_HOME/skills/kubernetes-triage-expert/SKILL.md"
```

If `CODEX_HOME` is not set in your shell, use the concrete path instead:

```bash
mkdir -p /Users/zongxun/.codex/skills/kubernetes-triage-expert
cp ./SKILL.md /Users/zongxun/.codex/skills/kubernetes-triage-expert/SKILL.md
```

### Claude Code

For a personal Claude Code skill:

```bash
mkdir -p ~/.claude/skills/kubernetes-triage-expert
cp ./SKILL.md ~/.claude/skills/kubernetes-triage-expert/SKILL.md
```

For a project-scoped Claude Code skill:

```bash
mkdir -p ./.claude/skills/kubernetes-triage-expert
cp ./SKILL.md ./.claude/skills/kubernetes-triage-expert/SKILL.md
```

Claude Code discovers skills automatically when the request matches the skill description.

### OpenClaw

For a personal OpenClaw skill:

```bash
mkdir -p ~/.openclaw/skills/kubernetes-triage-expert
cp ./SKILL.md ~/.openclaw/skills/kubernetes-triage-expert/SKILL.md
```

For a workspace-scoped OpenClaw skill:

```bash
mkdir -p ./skills/kubernetes-triage-expert
cp ./SKILL.md ./skills/kubernetes-triage-expert/SKILL.md
```

If your OpenClaw setup uses agent-compatible skill folders, you can also place it in `~/.agents/skills/` or `<workspace>/.agents/skills/`.

### ClawHub

Install directly from ClawHub:

```bash
clawhub install kubernetes-triage-expert
```

Inspect the published package:

```bash
clawhub inspect kubernetes-triage-expert
```

### First Run

Then start a conversation and invoke or describe the task clearly:

```text
Use the kubernetes-triage-expert skill and stay within skill boundaries only.

namespace=prod
deployment=checkout-api
pods are CrashLoopBackOff
started after today's rollout
log excerpt: failed to load config: missing REDIS_URL
```

The skill will not run commands. It will classify the fault, rank likely hypotheses, and ask for the next 1-3 checks.

## Install Options

- Codex skill install: copy [SKILL.md](./SKILL.md) into your Codex skills directory.
- Claude Code skill install: copy [SKILL.md](./SKILL.md) into `~/.claude/skills/` or `.claude/skills/`.
- OpenClaw skill install: copy [SKILL.md](./SKILL.md) into `~/.openclaw/skills/` or `./skills/`.
- ClawHub install: run `clawhub install kubernetes-triage-expert`.
- Prompt-only use: paste [PROMPT.md](./PROMPT.md) into a constrained chat or evaluation environment.
- Repo review: read [SKILL.md](./SKILL.md), [docs/EXAMPLES.md](./docs/EXAMPLES.md), and [docs/STRESS_TESTS.md](./docs/STRESS_TESTS.md) before integrating it into a workflow.

## When To Use

Use this skill when you want:

- structured Kubernetes incident triage without fake environment access
- evidence-based narrowing instead of generic troubleshooting dumps
- the next highest-value checks rather than broad remediation advice
- a prompt/skill behavior contract that can be reviewed and tested

Do not use it as:

- a cluster-connected operator
- a command runner
- an automatic remediation engine
- a replacement for application debugging or cloud-internal investigation

## Overview

General-purpose conversational AI often underperforms in Kubernetes troubleshooting because it tends to:

- guess too early
- confuse symptoms with root causes
- produce long generic cause lists
- speak as if it has already inspected the environment

This project exists to correct that behavior. It specifies a disciplined skill that:

- classifies fault types
- normalizes incident reports
- separates facts from hypotheses
- ranks the most likely causes
- recommends the next highest-value checks
- remains honest about what a skill can and cannot do

## Goals

- Provide a professional specification for Kubernetes fault triage.
- Preserve evidence discipline in every response.
- Improve the quality of the next troubleshooting step, not just the explanation.
- Prevent common prompt failures such as overclaiming, generic advice dumping, and fake environment awareness.
- Make behavior testable through examples and stress cases.

## Non-Goals

- Running `kubectl` or any cluster command
- Integrating with Kubernetes, cloud providers, CI/CD, or observability backends
- Acting as an agent, MCP server, or automation workflow
- Applying remediation or generating unaudited fixes
- Replacing deep investigation of application code, runtime internals, or cloud-provider infrastructure

## Intended Audience

This repository is aimed at:

- SRE engineers
- DevOps engineers
- platform engineers
- prompt designers working on operational AI behavior
- teams evaluating whether a Kubernetes troubleshooting skill can stay useful without tool access

## Repository Contents

- [SKILL.md](./SKILL.md): full behavioral contract and troubleshooting specification
- [PROMPT.md](./PROMPT.md): compact runtime prompt suitable for direct deployment
- [docs/EXAMPLES.md](./docs/EXAMPLES.md): English examples
- [docs/EXAMPLES_zh.md](./docs/EXAMPLES_zh.md): Chinese examples
- [docs/STRESS_TESTS.md](./docs/STRESS_TESTS.md): English adversarial evaluation cases
- [docs/STRESS_TESTS_zh.md](./docs/STRESS_TESTS_zh.md): Chinese adversarial evaluation cases
- [docs/EVALUATION_RUBRIC.md](./docs/EVALUATION_RUBRIC.md): evaluation rubric for review and regression testing
- [docs/EVALUATION_RUBRIC_zh.md](./docs/EVALUATION_RUBRIC_zh.md): Chinese evaluation rubric
- [docs/REVIEW_TEMPLATE.md](./docs/REVIEW_TEMPLATE.md): reusable review template
- [docs/MULTI_TURN_REVIEW_TEMPLATE.md](./docs/MULTI_TURN_REVIEW_TEMPLATE.md): multi-turn review template
- [docs/MULTI_TURN_REVIEW_TEMPLATE_zh.md](./docs/MULTI_TURN_REVIEW_TEMPLATE_zh.md): Chinese multi-turn review template
- [docs/README_zh.md](./docs/README_zh.md): Chinese quick-start and documentation index
- [docs/skill_zh.md](./docs/skill_zh.md): Chinese translation of the skill
- [docs/INTEGRATION_GUIDE.md](./docs/INTEGRATION_GUIDE.md): integration principles, scenarios, and patterns

## Source of Truth

- [SKILL.md](./SKILL.md) is the primary source of truth for behavior, structure, and guardrails.
- [PROMPT.md](./PROMPT.md) is the runtime-oriented condensed prompt and must stay aligned with [SKILL.md](./SKILL.md).
- Supporting docs must follow the behavior defined in [SKILL.md](./SKILL.md), especially language policy, evidence thresholds, and boundary rules.

## Design Principles

- Evidence first. No root-cause claim without user-supplied evidence.
- Earliest failure first. Triage starts at the first real break in the failure chain.
- Minimal next step. Recommend only the checks that materially change diagnosis.
- Boundary honesty. Never imply environment access or execution capability.
- Auditable reasoning. Keep confirmed facts, likely hypotheses, ruled-out paths, and missing evidence separate.
- Triage over encyclopedias. The skill should narrow the search space, not recite everything it knows.

## Operating Model

The skill is intentionally narrow.

It may:

- analyze user-provided statuses, logs, events, and change context
- classify incident types
- rank likely hypotheses
- recommend the next 1-3 checks
- state when the problem likely exceeds Kubernetes triage scope

It may not:

- inspect the cluster
- run commands
- fetch telemetry
- verify live state independently
- fabricate certainty where evidence is missing

## Supported Fault Families

The skill is optimized for high-frequency Kubernetes fault classes, including:

- `CrashLoopBackOff`
- `CreateContainerConfigError`
- `CreateContainerError`
- `ContainerCreating`
- `Pending`
- `ImagePullBackOff` and `ErrImagePull`
- DNS and connection failures such as `no such host`, `connection refused`, and `i/o timeout`
- service reachability failures
- rollout regressions
- probe-related instability
- storage-related scheduling blockers

Its responsibility is not to solve every incident end to end. Its responsibility is to produce the next correct troubleshooting move.

## Recommended Reading Order

1. Use the Quick Start section above to install and try the skill.
2. Read [SKILL.md](./SKILL.md) for the full design contract.
3. Use [PROMPT.md](./PROMPT.md) as the deployment-ready prompt.
4. Review [docs/EXAMPLES.md](./docs/EXAMPLES.md) to understand expected good and bad behavior.
5. Use [docs/STRESS_TESTS.md](./docs/STRESS_TESTS.md) or [docs/STRESS_TESTS_zh.md](./docs/STRESS_TESTS_zh.md) to evaluate robustness and boundary discipline.
6. Use [docs/EVALUATION_RUBRIC.md](./docs/EVALUATION_RUBRIC.md) when scoring outputs or running regressions.
7. Read [docs/INTEGRATION_GUIDE.md](./docs/INTEGRATION_GUIDE.md) when wiring the skill into a broader tool flow.

## Example Output Shape

The skill uses one output language per response, follows the user's current language, and keeps technical identifiers in their original form.

```md
Assessment
- Fault class:
- Initial severity:
- Current stage:

Confirmed Facts
- ...

Leading Hypotheses
1. ...
2. ...
3. ...

Next Checks
1. Check:
   Why it matters:
   If yes:
   If no:

Current Conclusion
- Confirmed:
- Likely:
- Ruled out:
- Still needed:
```

## Evaluation Criteria

A strong response should:

- classify the primary fault correctly
- reduce uncertainty
- avoid overclaiming
- keep the next checks limited and high-value
- adapt output language without switching to bilingual output unless requested
- calibrate depth to low, medium, or high evidence situations
- distinguish Kubernetes-level problems from application, runtime, or cloud-provider problems

A weak response usually:

- lists too many causes
- guesses without evidence
- confuses downstream symptoms with the primary failure
- speaks as if it already inspected the environment

## Roadmap

Current scope:

- skill specification
- runtime prompt
- example set
- stress-test set

Possible next steps:

- tighter response rubrics for evaluation
- fault-family-specific prompt variants
- benchmark conversations for side-by-side prompt comparison
- review checklists for prompt regressions

## Status

This repository currently contains the design package for a Kubernetes troubleshooting skill. It is suitable for prompt review, evaluation, iteration, and controlled testing.
