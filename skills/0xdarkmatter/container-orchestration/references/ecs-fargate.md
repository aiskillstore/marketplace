# Amazon ECS on AWS Fargate

The rest of this skill covers Docker and Kubernetes. ECS on Fargate is a distinct
orchestrator: AWS-native, serverless containers — no nodes to patch, no kubelet, no
control plane to run. Reach here for production-grade Fargate workloads.

Verify specifics against the canonical sources (links per section); ECS features move
across platform versions.

## ECS vs Kubernetes — when to pick Fargate

| | ECS on Fargate | Kubernetes (EKS / self-managed) |
|---|---|---|
| Ops burden | None — no nodes, no control plane | You run/patch nodes (EKS manages the control plane) |
| Portability | AWS-only | Portable across clouds |
| Ecosystem | AWS-native (ALB, IAM, CloudWatch, Secrets Manager) | Huge CNCF ecosystem, Helm, operators |
| Learning curve | Low | High |
| Best for | AWS-committed teams wanting minimal infra ops | Multi-cloud, complex scheduling, existing k8s investment |

Pick Fargate when you're AWS-committed and want to stop managing container hosts.
Pick Kubernetes when you need portability, advanced scheduling, or already run k8s.
Note **EKS can also run on Fargate** — that's k8s pods on serverless capacity, a
different product from the ECS-on-Fargate covered here.

## Core building blocks

- **Task definition** — the blueprint: container image(s), CPU/memory at the task
  level (Fargate requires valid CPU/memory pairs, e.g. 0.25 vCPU / 0.5 GB up to
  16 vCPU / 120 GB), `awsvpc` network mode (mandatory on Fargate), log config, the
  two IAM roles (below), and `secrets` mappings.
- **Service** — keeps N task copies running, registers them with a load balancer,
  handles rolling or blue/green deploys, and integrates Service Auto Scaling and
  Service Connect / service discovery.
- **Cluster** — logical grouping; with Fargate it's effectively just a namespace
  plus a capacity-provider strategy.
- **Capacity providers** — `FARGATE` (on-demand) and `FARGATE_SPOT` (interruptible,
  up to ~70% cheaper). Mix them with a strategy (e.g. a base of FARGATE plus a
  weighted FARGATE_SPOT layer) to cut cost while protecting a reliable baseline.

Architecting for AWS Fargate:
https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html ·
ECS Developer Guide:
https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html

## Networking (awsvpc)

Every Fargate task gets its own ENI with a private IP — security groups attach to the
*task*, not a shared host.

- Run tasks in **private subnets**; reach the internet via a NAT Gateway, or skip NAT
  with **VPC interface endpoints** (ECR, Secrets Manager, CloudWatch Logs, etc.) to
  cut NAT cost and keep traffic on the AWS backbone.
- **Security groups**: the task SG is the source. Common gotcha — a task can't reach
  RDS even though SGs "look right": the RDS SG must allow inbound *from the task's SG*
  (reference the SG id, not a CIDR), and the task must be in a subnet with a route to
  RDS.
- **Load balancing**: **ALB** for HTTP/HTTPS (path/host routing, TLS termination) —
  the default for web services; **NLB** for TCP/UDP, ultra-low latency, or a static
  IP. The service registers task ENIs into the target group as `ip` targets.
- **Service Connect** (preferred) or ECS Service Discovery for service-to-service
  communication with built-in naming and health.

## IAM — two distinct roles

| Role | Used by | Grants |
|------|---------|--------|
| **Task execution role** | the ECS agent, at launch | Pull the image from ECR, write logs, fetch `secrets` from Secrets Manager / SSM |
| **Task role** | your application, at runtime | The app's own AWS permissions (S3, DynamoDB, SQS…) |

Keep them separate and least-privilege. Don't grant the app's S3 access on the
execution role, and don't put image-pull permission on the task role.

## Secrets

Inject via the task definition `secrets` block from **Secrets Manager** or **SSM
Parameter Store** — values land as env vars at start, never baked into the image or
committed. The *execution role* needs read access to the secret (and to the KMS key
if the secret is CMK-encrypted).

## Scaling & cost

- **Service Auto Scaling** via Application Auto Scaling: target tracking (e.g. hold
  CPU at 60%, or scale on ALB requests-per-target), step scaling, or scheduled
  scaling for known peaks.
- **Cost levers**: FARGATE_SPOT for fault-tolerant/stateless work, right-size task
  CPU/memory (Container Insights shows actual utilization), Compute Savings Plans for
  steady baseline load, VPC endpoints to drop NAT data charges.

## Observability & deploys

- **Logging** — `awslogs` driver to CloudWatch is the simple default; **FireLens**
  (Fluent Bit sidecar) when you need to route/transform logs to a third party or
  multiple sinks.
- **Metrics** — CloudWatch Container Insights for per-task CPU/memory/network;
  alarm on those.
- **Debugging** — **ECS Exec** opens an interactive shell into a running task (no SSH,
  no public IP). Needs ECS Exec enabled on the service and the SSM permissions on the
  task role.
- **Deploys** — rolling (built-in, `minimumHealthyPercent` / `maximumPercent`) or
  **blue/green** via CodeDeploy (shift traffic, auto-rollback on alarm). Always wire
  container **health checks** so a bad revision fails the deployment instead of
  serving errors.

## Deployment tooling

| Tool | Best for |
|------|----------|
| **AWS Copilot** | Fastest path — opinionated, generates the VPC/ALB/service for you. Great for getting a service live and managing environments. |
| **AWS CDK** | Real IaC with `ecs-patterns` L3 constructs (e.g. `ApplicationLoadBalancedFargateService`); programmable, testable. |
| **CloudFormation** | Declarative, no extra runtime; verbose. |
| **Terraform** | When the org standardizes on Terraform across clouds. |

Copilot to start fast; CDK/Terraform when you need full control and review.

## Common failure modes

| Symptom | Likely cause |
|---------|--------------|
| Task can't reach RDS (timeout) | RDS SG doesn't allow the task SG; or task subnet has no route |
| `CannotPullContainerError` | Execution role lacks ECR pull, or no route to ECR (no NAT / no VPC endpoint) |
| Secret injection fails at start | Execution role missing Secrets Manager / SSM (and KMS) read permission |
| Tasks killed under load | Task CPU/memory under-provisioned — check Container Insights, right-size |
| Spot tasks vanish | FARGATE_SPOT interruption — add a FARGATE base in the capacity strategy |

## Canonical references

- AWS Fargate architecture: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html
- ECS Developer Guide: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html
- ECS Best Practices: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-best-practices.html
- Getting started with Fargate: https://aws.amazon.com/fargate/getting-started/
