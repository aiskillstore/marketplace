# Kubernetes Triage Expert Stress Tests

These cases are designed to test whether the skill stays inside its boundary, preserves evidence discipline, and produces decision-oriented triage instead of generic troubleshooting.

## Test 1: Extremely Thin Input

### User Input

```md
Production is down, Kubernetes has a problem
```

### What Good Behavior Looks Like

- Classify as `unknown / insufficient evidence`
- Ask only the minimum questions needed to branch
- Do not guess a root cause
- Do not output a giant list of causes

### Failure Pattern

- "This is usually caused by network, DNS, storage, or deployment issues..."

## Test 2: Symptom Chain Misclassification

### User Input

```md
External traffic gets 503, ingress has no traffic, backend pods are all Pending
```

### What Good Behavior Looks Like

- Classify as `scheduling failure`, not `ingress issue`
- Explain that service exposure is downstream of unscheduled backends
- Focus next checks on scheduler events and placement constraints

### Failure Pattern

- Starting with ingress annotations, TLS, or path routing before addressing `Pending`

## Test 3: Status Name Overreach

### User Input

```md
pod CrashLoopBackOff
```

### What Good Behavior Looks Like

- Treat `CrashLoopBackOff` as a symptom, not a root cause
- Ask for exit code, logs, probe state, recent changes
- Avoid broad or confident diagnosis

### Failure Pattern

- "The app definitely has a config problem"

## Test 4: Rollout Correlation

### User Input

```md
After the 11:05 rollout, new pods became unhealthy while old pods stayed healthy
```

### What Good Behavior Looks Like

- Classify as `rollout regression` or `crash after start` depending on additional evidence
- Heavily prioritize change-related hypotheses
- Ask for image/config/probe/resource differences and rollback result

### Failure Pattern

- Ignoring the rollout timing and starting with cluster-wide speculation

## Test 5: App vs Kubernetes Boundary

### User Input

```md
Pod is Running, readiness is healthy, but the API returns 500 and logs show SQL syntax error
```

### What Good Behavior Looks Like

- State clearly that Kubernetes health is not the main unknown
- Identify this as likely application or dependency behavior surfacing in Kubernetes
- Stay useful, but note that further root cause is outside pure Kubernetes triage

### Failure Pattern

- Continuing as if this were primarily a Kubernetes scheduler/network issue

## Test 6: Service Object False Confidence

### User Input

```md
The Service has a ClusterIP, so the network should be fine, right?
```

### What Good Behavior Looks Like

- Reject the inference
- Explain that Service existence does not prove backend readiness or endpoint health
- Ask for endpoints and pod readiness

### Failure Pattern

- Accepting the Service object as proof of healthy service routing

## Test 7: Multi-Cause Scheduler Event

### User Input

```md
0/8 nodes are available: 2 Insufficient cpu, 3 node(s) had untolerated taint, 3 node(s) didn't match Pod's node affinity
```

### What Good Behavior Looks Like

- Preserve multiple blockers without collapsing them incorrectly
- Rank the most actionable constraints first
- Recommend checks that disambiguate effective eligible node pool and placement intent

### Failure Pattern

- Focusing on only one scheduler reason and ignoring the rest

## Test 8: Probe Mismatch vs App Crash

### User Input

```md
The container starts for about ten seconds, then restarts, and events keep showing Liveness probe failed
```

### What Good Behavior Looks Like

- Prioritize probe mismatch or unhealthy startup path
- Not jump straight to "application exits immediately"
- Ask for probe config, thresholds, endpoint behavior, and startup expectations

### Failure Pattern

- Treating this as a generic crash-loop without using the probe evidence

## Test 9: Missing Evidence Boundary

### User Input

```md
I suspect a CNI issue, but I do not have node logs or network policy details yet
```

### What Good Behavior Looks Like

- State that the current evidence is insufficient to confirm a CNI issue
- Explicitly note the boundary and what evidence is required next
- Avoid pretending to validate node/network internals

### Failure Pattern

- "Yes, this is likely the CNI plugin"

## Test 10: Image Pull Auth Signal

### User Input

```md
event: Failed to pull image, unauthorized: authentication required
```

### What Good Behavior Looks Like

- Prioritize registry auth / imagePullSecrets / permissions
- Ask for exact image reference and recent secret changes
- Keep network timeout causes lower priority

### Failure Pattern

- Treating this mainly as registry downtime or generic network failure

## Test 11: Contradictory Evidence

### User Input

```md
I think this is a memory issue, but describe shows no OOMKilled and the logs say failed to parse config
```

### What Good Behavior Looks Like

- Challenge the user's conclusion respectfully
- Re-rank hypotheses toward config/startup issues
- Explain why the current evidence weakens the memory hypothesis

### Failure Pattern

- Agreeing with the user without evidence review

## Test 12: PVC as Hidden Root of Pending

### User Input

```md
pod Pending, and the event says pod has unbound immediate PersistentVolumeClaims
```

### What Good Behavior Looks Like

- Classify as `scheduling failure` with storage as the key sub-path
- Prioritize PVC binding state over CPU/memory speculation
- Ask for PVC/PV/storageClass state

### Failure Pattern

- Defaulting to generic capacity or node shortage checks

## Test 13: Endpoint Empty With Ready Pods

### User Input

```md
service endpoints are empty, but all pods are Ready
```

### What Good Behavior Looks Like

- Prioritize selector mismatch or namespace/object mismatch
- Ask for service selector and pod labels
- Not blame readiness first because the user already provided contrary evidence

### Failure Pattern

- Ignoring the Ready evidence and repeating backend health theory

## Test 14: False Rollout Correlation

### User Input

```md
The alert fired right after deployment, but the scheduler event says node had untolerated taint
```

### What Good Behavior Looks Like

- Do not overfit to rollout timing
- Keep rollout as context, but rank the explicit scheduler blocker first
- Explain why concrete scheduling evidence outranks temporal correlation

### Failure Pattern

- Assuming the rollout artifact is the primary cause despite stronger contrary evidence

## Test 15: Boundary Against Remediation

### User Input

```md
你直接告诉我怎么改 yaml 修好它
```

### What Good Behavior Looks Like

- Keep the role as triage-first
- State that the fix depends on confirmed evidence
- If enough evidence exists, suggest likely fix direction conditionally, not as fabricated certainty

### Failure Pattern

- Inventing a patch without enough supporting evidence

## Evaluation Checklist

Use these questions to score responses:

1. Did it classify the primary failure correctly?
2. Did it keep facts separate from hypotheses?
3. Did it avoid pretending to inspect the environment?
4. Did it avoid broad, generic troubleshooting dumps?
5. Did it choose the next checks based on decision value?
6. Did it respect Kubernetes vs app/cloud/runtime boundaries?
7. Did it avoid confirming a root cause prematurely?
8. Did it use recent-change timing appropriately without overfitting?
9. Did it follow the default Chinese-output rule, keeping English only for standard technical terms when clearer?
