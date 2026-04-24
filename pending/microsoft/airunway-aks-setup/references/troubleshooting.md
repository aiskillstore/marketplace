# Troubleshooting & Rollback

## Error Handling

| Error / Symptom | Likely Cause | Remediation |
|-----------------|--------------|-------------|
| No kubeconfig context | Not connected to a cluster | Run `az aks get-credentials` or equivalent |
| `make: *** No rule to make target` | Not in AI Runway repo root | `cd` to repo root and retry |
| Controller in CrashLoopBackOff | Config or RBAC issue | `kubectl logs -n airunway-system -l control-plane=controller-manager --previous` |
| Provider not ready | Image pull or RBAC issue | `kubectl describe pod` for the provider pod |
| ModelDeployment stuck in Pending | GPU scheduling failure or provider not ready | `kubectl describe modeldeployment` events |
| Pod shows ImagePullBackOff | Wrong image reference or missing pull secret | `kubectl describe pod` for the model pod |
| 401 from HuggingFace at model load | Gated model, token secret not wired into CR | Ensure `huggingFaceTokenSecretRef` is set in the CR |
| `bfloat16` errors at inference | T4 or V100 lacks bfloat16 support | Add `--dtype float16` to serving args |

## Rollback

If a step fails and you need to undo a partial setup, work backwards through the steps:

| What to undo | Command |
|--------------|---------|
| Model deployment | `kubectl delete modeldeployment <model-name> -n <namespace>` |
| HuggingFace token secret | `kubectl delete secret hf-token -n <namespace>` |
| Provider | `cd providers/<provider> && make undeploy` (from repo root) |
| Controller | `make controller-undeploy && make controller-uninstall` (from repo root) |
