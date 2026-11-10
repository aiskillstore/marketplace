# Kubernetes Triage Expert Examples

These examples are meant to validate realistic skill behavior, not to provide generic troubleshooting encyclopedias.

The set is intentionally small and representative:

- one low-evidence intake case
- one strong-evidence infrastructure case
- one rollout-driven workload case
- one clear boundary case

## Example 1: Low-Evidence Intake

### User

```md
My pod is not coming up.
```

### Good Response

```md
Assessment
- Fault class: startup failure or crash after start
- Initial severity: unknown
- Current stage: intake

Confirmed Facts
- A workload is unhealthy, but the failure stage is still unclear.

Leading Hypotheses
1. The workload is failing during startup, but the exact cause is not yet visible.
2. The workload may be blocked earlier by scheduling or image pull issues.

Next Checks
1. Check: Provide the namespace, workload kind, workload name, and current Pod status.
   Why it matters: This identifies the failing object and distinguishes startup, crash, or scheduling paths.
   If yes: The triage can branch on the real failure stage.
   If no: The issue remains too broad to classify correctly.

2. Check: Provide the start time and whether there was a recent rollout, image, ConfigMap, or Secret change.
   Why it matters: Time correlation is one of the highest-value branching signals.
   If yes: Change-related hypotheses can be ranked early.
   If no: The analysis stays broader and less certain.

3. Check: Provide one exact error line, preferably from Events or container logs.
   Why it matters: Exact error text is often the fastest way to avoid generic guessing.
   If yes: The next hypothesis set becomes more specific.
   If no: The skill should stay in low-evidence mode.

Current Conclusion
- Confirmed: Only that the workload is unhealthy.
- Likely: Evidence is still too thin to rank causes confidently.
- Ruled out: None.
- Still needed: Pod status, timeline, recent changes, and exact error text.
```

### Why This Is Good

- It does not pretend to know the cause.
- It asks only for the minimum evidence needed to branch.
- It stays in low-evidence mode instead of dumping generic Kubernetes advice.

## Example 2: Calico RBAC Degradation

### User

```md
Help me analyze this error.

Cluster environment:
$ kubectl get node
NAME       STATUS   ROLES           AGE   VERSION
master01   Ready    control-plane   70d   v1.33.7
worker01   Ready    <none>          70d   v1.33.7
worker02   Ready    <none>          70d   v1.33.7
worker03   Ready    <none>          67d   v1.33.7

Command:
$ kubectl logs -n kube-system calico-kube-controllers-8445577b47-25gtz --tail 200

Latest error:
failed to list *v1.Service: services is forbidden: User "system:serviceaccount:kube-system:calico-kube-controllers" cannot list resource "services" in API group "" at the cluster scope
```

### Good Response

```md
Assessment
- Fault class: network or DNS problem, more precisely a control-plane permission fault affecting Calico
- Initial severity: medium
- Current stage: active triage

Confirmed Facts
- All nodes are currently `Ready`.
- The failing identity is `system:serviceaccount:kube-system:calico-kube-controllers`.
- The denied action is cluster-scoped `list` on core `services`.
- The error comes from a client-go reflector during `list/watch` cache sync.
- The process is still running, so this looks like degraded controller behavior rather than a crashing Pod.

Leading Hypotheses
1. The `ClusterRole` or `ClusterRoleBinding` for `calico-kube-controllers` is missing, broken, or no longer grants the required `services` permissions.
2. The running Calico controller version expects `services` permissions, but the currently applied RBAC is older or incomplete.
3. A recent Calico reinstall, upgrade, backup restore, or manual RBAC change caused drift between the `ServiceAccount`, binding, and role.

Next Checks
1. Check: Inspect the `ServiceAccount`, `ClusterRoleBinding`, and `ClusterRole` associated with `calico-kube-controllers`.
   Why it matters: This directly tests whether the identity is missing the required RBAC grant.
   If yes: If the role lacks `get/list/watch` on `services`, or the binding does not point to `kube-system:calico-kube-controllers`, the root cause is nearly confirmed.
   If no: If the binding and role look correct, compare the deployed Calico version and manifest state.

2. Check: Run `kubectl auth can-i list services --as=system:serviceaccount:kube-system:calico-kube-controllers`.
   Why it matters: This is the fastest way to confirm whether the current identity really has the required permission.
   If yes: Re-check whether the logs came from an older container instance or whether another identity is actually in use.
   If no: Keep the diagnosis centered on RBAC drift.

3. Check: Compare the deployed `calico-kube-controllers` image version with the currently applied Calico RBAC manifest.
   Why it matters: Version drift is a common reason why the controller expects permissions that the cluster no longer grants.
   If yes: Reconcile the deployed version with the matching official RBAC manifest.
   If no: Prioritize manual RBAC drift or partial restore scenarios.

Current Conclusion
- Confirmed: `calico-kube-controllers` is being denied cluster-scoped access to core `Service` objects.
- Likely: RBAC drift or a Calico version-to-manifest mismatch is the main fault path.
- Ruled out: There is no current evidence of a node-wide outage, and the controller process is not simply crash-looping.
- Still needed: The actual `ClusterRole`, `ClusterRoleBinding`, `kubectl auth can-i` result, and deployed Calico image version.

If you share the outputs of these three commands, the next turn can usually narrow the issue down to the exact missing RBAC rule and the minimum repair path:

kubectl auth can-i list services --as=system:serviceaccount:kube-system:calico-kube-controllers
kubectl get clusterrolebinding,clusterrole | grep -i calico
kubectl get deploy -n kube-system calico-kube-controllers -o yaml
```

### Why This Is Good

- It uses the exact evidence the user supplied.
- It identifies the issue as a permission fault without pretending to inspect unseen resources.
- It separates confirmed impact from likely root cause.
- It asks for the next 1-3 checks that can directly confirm or reject the RBAC hypothesis.

## Example 3: Rollout Regression With Strong Startup Signal

### User

```md
namespace=prod
deployment=checkout-api
The issue started right after today's rollout.
Pods are CrashLoopBackOff.
The startup log says: failed to load config: missing REDIS_URL
```

### Good Response

```md
Assessment
- Fault class: crash after start
- Initial severity: medium to high if all replicas are affected
- Current stage: active triage

Confirmed Facts
- Workload: `prod` / `Deployment` / `checkout-api`
- The issue began around the latest rollout
- Pods are in `CrashLoopBackOff`
- Startup log includes `failed to load config: missing REDIS_URL`

Leading Hypotheses
1. The new rollout is missing required environment configuration.
2. A `Secret` or `ConfigMap` reference changed and no longer injects `REDIS_URL`.
3. The application now expects a new variable that the previous configuration did not provide.

Next Checks
1. Check: Compare the old and new Pod env or config sources for `REDIS_URL`.
   Why it matters: The log already points to a concrete startup dependency.
   If yes: The rollout or config change is the primary fault path.
   If no: Re-check whether the variable name or config source changed.

2. Check: Inspect whether the referenced `Secret`, `ConfigMap`, or key actually exists and contains `REDIS_URL`.
   Why it matters: A missing key and a broken reference are different failure modes.
   If yes: Focus on app expectation or env mapping.
   If no: Focus on broken config wiring.

3. Check: Confirm whether rollback to the previous version restores health.
   Why it matters: This separates rollout-caused regression from unrelated background issues.
   If yes: Prioritize release artifact or config regression.
   If no: Expand to non-release causes.

Current Conclusion
- Confirmed: The container is failing during startup, and the visible error points to missing `REDIS_URL`.
- Likely: The latest rollout introduced a config or env regression.
- Ruled out: There is no current evidence of a cluster-wide scheduling or networking issue.
- Still needed: Old vs new env/config comparison and rollback result.
```

## Example 4: Clear Boundary Handoff

### User

```md
The Pod is Running, readiness is healthy, but the API returns 500.
The app log shows SQL syntax error.
```

### Good Response

```md
Assessment
- Fault class: unknown / insufficient evidence for a Kubernetes fault
- Initial severity: medium
- Current stage: evidence review

Confirmed Facts
- The Pod is `Running`.
- Readiness is healthy.
- The request fails with `500`.
- The visible app log contains `SQL syntax error`.

Leading Hypotheses
1. The primary fault is in application behavior or database interaction, not in Kubernetes health.
2. Kubernetes is only the execution environment in which the application error is surfacing.

Next Checks
1. Check: Confirm the failing SQL statement or the application change that introduced it.
   Why it matters: The visible evidence points to app or dependency logic, not cluster scheduling or readiness.
   If yes: Hand off to application or database investigation.
   If no: Keep reviewing app-level logs and recent code or config changes.

Current Conclusion
- Confirmed: Kubernetes readiness and basic Pod health are not the main unknowns here.
- Likely: This is an application or dependency fault surfacing through a healthy workload.
- Ruled out: A primary scheduling or startup failure.
- Still needed: App-level query context, recent app change history, and database-side evidence.

Boundary Handoff
- boundary reached: pure Kubernetes triage
- why this is beyond Kubernetes triage: the strongest evidence points to application or database behavior rather than cluster health
- likely owning area: application or database layer
- missing evidence needed from that area: exact failing query, recent code or config change, and database-side error context
- what remains valid from current triage: the workload is running and passing readiness, so the failure is not currently explained by basic Pod lifecycle health
```

### Why This Is Good

- It remains useful without pretending the fault is still mainly Kubernetes-level.
- It states the boundary clearly and tells the operator what evidence is needed next.
