# Kubernetes Operations

Use these rules only when the repository actually deploys to Kubernetes. Treat manifests, Helm values, and GitOps state as desired intent; verify the running workload before diagnosing or declaring success.

## Inspect desired and live state

Establish:

- cluster/context, namespace, workload kind, release/GitOps owner, and deployed revision;
- rendered manifests and effective configuration, not values files alone;
- Deployment/StatefulSet/Job status, ReplicaSets, Pods, events, EndpointSlices, Services, and ingress/gateway state;
- running image digest, environment/config mounts, service account, security context, resources, probes, and termination settings;
- current logs, metrics, traces, queue lag, dependency status, and recent changes.

Do not diagnose a running Pod solely from source YAML. A stale image, unrolled ConfigMap, admission mutation, failed mount, scheduling event, or old ReplicaSet can make live state differ from repository intent.

## Choose the workload deliberately

- Use a Deployment for replaceable stateless HTTP, message-consumer, or worker replicas.
- Use a Job for finite work and a CronJob or platform scheduler for scheduled work that should not run once per web replica.
- Use a StatefulSet only when stable identity/storage or ordered lifecycle is required; a database being stateful does not automatically make the application a StatefulSet.
- Separate web and worker Deployments when traffic, scaling, shutdown, or resource profiles differ.
- Keep durable state outside replaceable application Pods unless the workload has an explicit stateful design.

## Configure probes by semantics

- **Startup probe:** protect a genuinely slow or variable initialization from premature liveness failure.
- **Liveness probe:** detect an unrecoverable local inability to make progress. Keep it cheap and independent of ordinary downstream outages.
- **Readiness probe:** answer whether this instance should receive new traffic or work now; it may include critical local/dependency state with bounded checks.

Do not point all three probes at one expensive endpoint without understanding the consequences. A broad liveness dependency can turn a database outage into a restart storm. Tune period, timeout, failure threshold, and startup budget from observed timings.

Use Nest Terminus when it fits the installed application, but the contract matters more than the package. Restrict health details from leaking internal topology or credentials.

## Drain and terminate safely

1. Ensure the Node process receives the termination signal and Nest shutdown hooks are enabled when needed.
2. Stop accepting new application work; terminating Kubernetes endpoints become not-ready, but consumers and custom routing may need explicit pause behavior.
3. Stop schedulers and queue intake.
4. Finish, checkpoint, or safely requeue in-flight HTTP requests, streams, sockets, and jobs.
5. Flush bounded telemetry and close broker, cache, database, server, and worker resources.
6. Exit before `terminationGracePeriodSeconds`; measure the real worst-case drain time.

Use a `preStop` hook only for a concrete ordering or compatibility need. It consumes the same termination grace period and cannot replace application shutdown behavior. Test deletion during real traffic/work, not only a direct lifecycle-method call.

## Resources and autoscaling

- Set CPU and memory requests from measured steady and peak usage so scheduling and utilization-based autoscaling have meaningful inputs.
- Set limits with runtime behavior understood: CPU limits can throttle; memory limits can lead to OOM termination.
- Account for sidecars and for total database, HTTP, cache, and broker connections across maximum replicas.
- Give Node.js memory configuration headroom below the container limit and observe heap, RSS, native buffers, and GC.
- Scale on a signal connected to demand or saturation: CPU for CPU-bound work, queue age/depth for workers, concurrency or latency only when the control loop is stable.
- Configure minimum/maximum replicas, scale-up/down behavior, and stabilization so an HPA does not oscillate or exceed downstream capacity.
- Prove per-instance capacity and startup/readiness timing before enabling aggressive autoscaling.

## Availability and rollout

- Configure rolling `maxUnavailable` and `maxSurge` from capacity and dependency headroom.
- Use readiness, minimum ready time, and a progress deadline to detect a stalled rollout.
- Keep old/new API, message, schema, cache, and configuration contracts compatible during overlap.
- Use a PodDisruptionBudget for voluntary disruptions only when multiple healthy replicas and workload semantics justify it; it does not protect against node failure or a broken rollout.
- Spread replicas across failure domains when availability requirements and cluster topology justify it.
- Use canary or progressive delivery only with trustworthy metrics, automated/manual abort criteria, and enough traffic for a decision.

## Security and configuration

- Use a dedicated service account with least-privilege RBAC; disable token automount when the Pod does not call the Kubernetes API.
- Run as non-root, disallow privilege escalation, use a read-only root filesystem, drop capabilities, and select seccomp/pod-security controls where compatible.
- Use ConfigMaps for non-secret configuration. Kubernetes Secret values are not safe merely because they are base64-encoded; use encryption, access control, or an external secret workflow appropriate to the threat model.
- Prefer immutable artifact/config references or deliberate restart automation so operators know when a change reaches Pods.
- Restrict ingress and egress with network policy where the cluster networking and threat model support it.
- Never place credentials in images, manifests committed in plaintext, annotations, command arguments, or logs.

## Runtime verification

For every deployment, verify:

```text
revision/digest -> rollout status -> ready endpoints -> representative traffic/work
-> error/latency/saturation -> dependency and queue health -> drain/rollback readiness
```

For an incident, compare desired revision with the running digest, then inspect events and container termination/restart reasons before changing configuration. Preserve evidence and prefer reversible changes.

See official Kubernetes guidance for [probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/), [Pod lifecycle and termination](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/), [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), [resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/), [horizontal autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/), [disruption budgets](https://kubernetes.io/docs/tasks/run-application/configure-pdb/), and [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/).
