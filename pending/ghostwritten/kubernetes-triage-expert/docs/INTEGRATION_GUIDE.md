# Integration Guide

This document defines how `Kubernetes Triage Expert` should be integrated into broader troubleshooting workflows without breaking its intended boundary.

The core rule is simple: this skill is a reasoning layer, not an execution layer.

## Purpose

Use this guide to decide:

- when the skill belongs in a workflow
- how responsibility should be split
- how surrounding tools should provide evidence
- what usage patterns preserve the skill's design intent

This is not the installation guide. For setup and first-run steps, use:

- [../README.md](../README.md)
- [README_zh.md](./README_zh.md)

## Integration Principles

All integrations should preserve these principles:

- evidence in, reasoning out
- no implied environment access
- the skill requests evidence; external systems provide it
- execution and remediation stay outside the skill
- the next step should be narrow, high-value, and auditable

## Responsibility Model

When the skill is used with other tools, the split should stay stable.

### Skill

- classifies the fault
- normalizes the incident
- separates facts from guesses
- ranks likely hypotheses
- requests the next highest-value checks
- states when the issue exceeds Kubernetes triage scope

### Operator

- runs commands
- retrieves logs, events, metrics, manifests, and rollout history
- pastes or summarizes evidence back into the conversation
- decides whether to apply remediation

### External Systems

- expose raw operational evidence
- do not replace reasoning
- should answer the specific diagnostic questions raised by the skill

## Supported Integration Scenarios

The skill is a good fit when you need:

- structured multi-turn triage
- evidence-driven narrowing of hypotheses
- a clean split between reasoning and execution
- disciplined use of logs, events, metrics, and rollout context

It is not a good fit when you need:

- direct command execution
- automatic evidence collection
- live state validation without a human in the loop
- remediation automation
- deep application or cloud-provider debugging as the primary task

## Integration Patterns

### Codex

Codex is a natural environment for this skill when you want a structured multi-turn diagnosis loop.

Recommended pattern:

1. Install or load the skill definition.
2. Invoke the skill explicitly or describe the task in terms that match the skill.
3. Provide the fault object, symptom, time context, and strongest evidence.
4. Let the skill request the next checks.
5. Run those checks yourself and return the evidence.

Example prompt:

```text
Use the kubernetes-triage-expert skill and stay within skill boundaries only.

namespace=prod
deployment=checkout-api
pods are CrashLoopBackOff
started after today's rollout
log excerpt: failed to load config: missing REDIS_URL
```

### Generic Chat Interfaces

In a regular chat UI, the skill should be treated as a constrained reasoning assistant.

Recommended pattern:

- paste [../PROMPT.md](../PROMPT.md)
- state that the assistant must stay inside the skill boundary
- provide evidence in a structured way

Avoid:

- asking the assistant to "check the cluster"
- asking for direct fixes before evidence is sufficient
- providing only a status label and expecting a confirmed root cause

### `kubectl`

This is the most common collaboration pattern.

Recommended loop:

1. Describe the problem to the skill.
2. Let the skill request the next most useful checks.
3. Run the corresponding `kubectl` commands manually.
4. Paste the output or a precise summary back into the conversation.
5. Let the skill update hypotheses and next steps.

Good pattern:

- skill asks for scheduler event text
- operator runs `kubectl describe pod ...`
- operator returns the relevant scheduler event line
- skill narrows the fault path

Bad pattern:

- operator asks "what command should I run to fix this immediately?"

### Logs

Logs are evidence providers, not a substitute for diagnosis.

Useful inputs include:

- startup failures
- termination messages
- probe-related errors
- dependency connection failures
- rollout-time regressions

Best practice:

- provide a short, exact excerpt instead of a vague summary
- include timing context
- include whether the log comes from the current or previous container attempt

### Metrics and Dashboards

Metrics are useful when the skill asks a specific diagnostic question, such as:

- whether OOM evidence exists
- whether CPU saturation is present
- whether replica health dropped sharply
- whether latency or error rates correlate with a rollout

Do not dump large dashboard summaries into the conversation without tying them to a hypothesis.

### Alerts and Incident Systems

Alerts work best as the entry point to triage.

Useful inputs include:

- what fired
- when it started
- affected service or namespace
- blast radius
- whether a rollout or config change happened nearby

The skill should convert the alert into:

- a primary fault classification
- initial hypotheses
- the next evidence to collect

### Runbooks

Runbooks and this skill serve different roles.

- runbooks encode known procedures
- the skill helps determine which runbook path is most relevant, or whether the situation is still too ambiguous for a runbook jump

The skill should not pretend to execute runbooks.

## Recommended Workflow

Use this closed loop:

1. Start with the symptom, time, object, and strongest evidence.
2. Let the skill classify the primary fault.
3. Let the skill request the next 1-3 checks.
4. Use `kubectl`, logs, dashboards, alerts, or runbooks to gather only that evidence.
5. Return the evidence to the skill.
6. Repeat until the root cause is confirmed, the issue moves outside Kubernetes triage, or remediation decision-making begins.

## Environment Notes

Environment differences mainly affect discovery and invocation, not the skill boundary.

- Codex: explicit skill naming is often the clearest trigger
- Claude Code: skill discovery may be automatic when the task matches the skill
- OpenClaw: skill loading may depend on the chosen skill directory and workspace configuration
- generic chat: prompt pasting is usually the most reliable integration pattern

## Anti-Patterns

Do not use the skill as if it were:

- a cluster-connected agent
- an automated incident commander
- a remediation engine
- a generic Kubernetes encyclopedia
- a substitute for application debugging when the evidence already points to app-level failure

Specific anti-patterns:

- "Check my cluster and tell me the issue."
- "Just give me the fix."
- "This is CrashLoopBackOff, so what is the root cause?"
- "Here is a screenshot of a dashboard, diagnose everything."

## Example Interaction Pattern

### Step 1

User:

```text
Use the kubernetes-triage-expert skill.
service unreachable
namespace=prod
deployment=checkout-api
started after rollout
```

### Step 2

Skill:

- classifies the likely fault family
- asks for the next missing evidence

### Step 3

User:

```text
service endpoints are empty
one pod is Running but not Ready
one pod is CrashLoopBackOff
```

### Step 4

Skill:

- reclassifies the primary fault if needed
- narrows hypotheses
- asks for the next highest-value check

## Summary

Use this skill to reason.
Use tools to gather evidence.
Use operators to execute commands and make changes.

If those roles stay separate, the skill remains honest and useful.
