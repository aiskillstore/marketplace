---
name: gke-expert
description: Expert guidance for Google Kubernetes Engine (GKE) operations including cluster management, workload deployment, scaling, monitoring, troubleshooting, and optimization. Use when working with GKE clusters, Kubernetes deployments on GCP, container orchestration, or when users need help with kubectl commands, GKE networking, autoscaling, workload identity, or GKE-specific features like Autopilot, Binary Authorization, or Config Sync.
---

# GKE Expert

Initial Assessment
When user requests GKE help, determine:

Cluster type: Autopilot or Standard?
Task: Create, Deploy, Scale, Troubleshoot, or Optimize?
Environment: Dev, Staging, or Production?

Quick Start Workflows
Create Cluster
Autopilot (recommended for most):
bashgcloud container clusters create-auto CLUSTER_NAME \
  --region=REGION \
  --release-channel=regular
Standard (for specific node requirements):
bashgcloud container clusters create CLUSTER_NAME \
  --zone=ZONE \
  --num-nodes=3 \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=10
Always authenticate after creation:
bashgcloud container clusters get-credentials CLUSTER_NAME --region=REGION
Deploy Application

Create deployment manifest:

yamlapiVersion: apps/v1
kind: Deployment
metadata:
  name: APP_NAME
spec:
  replicas: 3
  selector:
    matchLabels:
      app: APP_NAME
  template:
    metadata:
      labels:
        app: APP_NAME
    spec:
      containers:
      - name: APP_NAME
        image: gcr.io/PROJECT_ID/IMAGE:TAG
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi

Apply and expose:

bashkubectl apply -f deployment.yaml
kubectl expose deployment APP_NAME --type=LoadBalancer --port=80 --target-port=8080
Setup Autoscaling
HPA for pods:
bashkubectl autoscale deployment APP_NAME --cpu-percent=70 --min=2 --max=100
Cluster autoscaling (Standard only):
bashgcloud container clusters update CLUSTER_NAME \
  --enable-autoscaling --min-nodes=2 --max-nodes=10 --zone=ZONE
Configure Workload Identity

Enable on cluster:

bashgcloud container clusters update CLUSTER_NAME \
  --workload-pool=PROJECT_ID.svc.id.goog

Link service accounts:

bash# Create GCP service account
gcloud iam service-accounts create GSA_NAME

## Create K8s service account
kubectl create serviceaccount KSA_NAME

# Bind them
gcloud iam service-accounts add-iam-policy-binding \
  GSA_NAME@PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:PROJECT_ID.svc.id.goog[default/KSA_NAME]"

# Annotate K8s SA
kubectl annotate serviceaccount KSA_NAME \
  iam.gke.io/gcp-service-account=GSA_NAME@PROJECT_ID.iam.gserviceaccount.com
Troubleshooting Guide
Pod Issues
bash# Pod not starting - check events
kubectl describe pod POD_NAME
kubectl get events --field-selector involvedObject.name=POD_NAME

## Common fixes:

### ImagePullBackOff: Check image exists and pull secrets
### CrashLoopBackOff: kubectl logs POD_NAME --previous
### Pending: kubectl describe nodes (check resources)
### OOMKilled: Increase memory limits
Service Issues
bash# No endpoints
kubectl get endpoints SERVICE_NAME
kubectl get pods -l app=APP_NAME  # Check if pods match selector

## Test connectivity
kubectl run test --image=busybox -it --rm -- wget -O- SERVICE_NAME
Performance Issues
bash# Check resource usage
kubectl top nodes
kubectl top pods --all-namespaces

## Find bottlenecks
kubectl describe resourcequotas
kubectl describe limitranges
Production Patterns
Ingress with HTTPS
yamlapiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: APP_NAME-ingress
  annotations:
    networking.gke.io/managed-certificates: "CERT_NAME"
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: APP_NAME
            port:
              number: 80
Pod Disruption Budget
yamlapiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: APP_NAME-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: APP_NAME
Security Context
yamlspec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
Cost Optimization

Use Autopilot for automatic right-sizing
Enable cluster autoscaling with appropriate limits
Use Spot VMs for non-critical workloads:

bashgcloud container node-pools create spot-pool \
  --cluster=CLUSTER_NAME \
  --spot \
  --num-nodes=2

Set resource requests/limits appropriately
Use VPA for recommendations: kubectl describe vpa APP_NAME-vpa

Essential Commands
bash# Cluster management
gcloud container clusters list
kubectl config get-contexts
kubectl cluster-info

## Deployments
kubectl rollout status deployment/APP_NAME
kubectl rollout undo deployment/APP_NAME
kubectl scale deployment APP_NAME --replicas=5

## Debugging
kubectl logs -f POD_NAME --tail=50
kubectl exec -it POD_NAME -- /bin/bash
kubectl port-forward pod/POD_NAME 8080:80

## Monitoring
kubectl top nodes
kubectl top pods
kubectl get events --sort-by='.lastTimestamp'

## External Documentation

For detailed documentation beyond this skill:
- **Official GKE Docs**: https://cloud.google.com/kubernetes-engine/docs
- **kubectl Reference**: https://kubernetes.io/docs/reference/kubectl/
- **GKE Best Practices**: https://cloud.google.com/kubernetes-engine/docs/best-practices
- **Workload Identity**: https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity
- **GKE Pricing Calculator**: https://cloud.google.com/products/calculator

## Cleanup
kubectl delete all -l app=APP_NAME
kubectl drain NODE_NAME --ignore-daemonsets
Advanced Topics Reference

## For complex scenarios, consult:
Stateful workloads: Use StatefulSets with persistent volumes
Batch jobs: Use Jobs/CronJobs with appropriate backoff policies
Multi-region: Use Multi-cluster Ingress or Traffic Director
Service mesh: Install Anthos Service Mesh for advanced networking
GitOps: Implement Config Sync or Flux for declarative management
Monitoring: Integrate with Cloud Monitoring or install Prometheus