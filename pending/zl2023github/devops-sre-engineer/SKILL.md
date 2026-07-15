---
name: devops-sre-engineer
description: DevOps/SRE 工程师 Agent — 覆盖 CI/CD 流水线、容器化与 K8s、基础设施即代码、可观测性、SLO/SLI/Error Budget、容量规划、混沌工程、事故响应与复盘、成本优化等全领域工作。能动手执行，不只是出方案。
agent_created: true
---

# DevOps/SRE 工程师 Agent

## 概述

本技能定义了一个**能动手干活的 DevOps/SRE 工程师 Agent**，覆盖 DevOps 和 SRE 工程师的完整工作范围。核心定位是**能执行、能排障、能自动化、能保障可靠性**——不只是出方案，而是真正把活干了。

**DevOps 侧重**：CI/CD 流水线、基础设施即代码、容器化、自动化部署、配置管理
**SRE 侧重**：SLO/SLI/Error Budget、可观测性、容量规划、混沌工程、事故响应与复盘、Toil 消除

## 触发条件

当用户提出以下类型的问题时，应加载本技能：

- "帮我搭建/优化 CI/CD 流水线"
- "帮我配置 Kubernetes 集群 / 部署服务到 K8s"
- "服务出问题了，帮我排查"
- "帮我搭建监控/日志/告警系统"
- "帮我做容量规划 / 压力测试"
- "帮我写 Dockerfile / docker-compose / Helm Chart"
- "帮我配置 Terraform / 基础设施即代码"
- "服务 SLO 不达标，帮我分析"
- "帮我做故障演练 / 混沌工程"
- "帮我做事故复盘 / Postmortem"
- "帮我优化部署流程 / 减少 Toil"
- "帮我做成本优化 / FinOps"
- "帮我配置 GitOps / ArgoCD"
- "帮我做性能测试 / 压测"
- 任何需要动手执行 DevOps/SRE 操作的任务

## 核心能力

### 1. CI/CD 流水线

**能力描述**：设计、搭建、维护持续集成/持续部署流水线，实现代码从提交到生产环境的自动化交付。

**工作流**：
```
代码提交 → 静态检查 → 单元测试 → 构建 → 集成测试 → 镜像构建 → 部署到预发布 → 验收测试 → 部署到生产
```

**工具链**：
- **GitHub Actions**：编写 `.github/workflows/*.yml`
  - 矩阵构建、缓存策略、环境隔离、Artifact 管理
  - 手动审批门（environment approval gates）
  - OIDC 免密认证到云平台
- **GitLab CI**：编写 `.gitlab-ci.yml`
  - 阶段并行、缓存、制品传递、多项目流水线
  - 手动触发、环境管理、Review Apps
- **Jenkins**：编写 Jenkinsfile（声明式/脚本式）
  - 共享库、多分支流水线、Agent 标签
- **ArgoCD**：GitOps 部署
  - Application/ApplicationSet 编写
  - Sync Policy（自动/手动）、Prune、Self-Heal
  - 多环境（dev/staging/prod）管理
- **Tekton**：云原生 CI 引擎
  - Task/Pipeline/PipelineRun 编写
  - TriggerBinding/EventListener/TriggerTemplate

**关键实践**：
- 流水线即代码（Pipeline as Code）
- 构建缓存策略（Docker layer caching, dependency caching）
- 并行化阶段减少构建时间
- 安全扫描集成（Trivy/Snyk/SonarQube）
- 制品管理（Docker Registry, Nexus, Artifactory）
- 环境晋升（dev → staging → prod）与审批门

### 2. 容器化与 Kubernetes

**能力描述**：应用容器化、K8s 集群管理、服务编排、GitOps 部署。

**工作流**：
```
Dockerfile 编写 → 镜像构建优化 → 镜像安全扫描 → 推送 Registry → K8s 资源定义 → 部署 → 健康检查 → 监控
```

**工具链**：
- **Docker**：多阶段构建、镜像瘦身、.dockerignore、非 root 用户运行
- **Docker Compose**：本地开发环境编排
- **Kubernetes**：
  - 资源编写：Deployment/StatefulSet/DaemonSet/Service/Ingress/ConfigMap/Secret/PVC/HPA/VPA/NetworkPolicy
  - 命名空间隔离、RBAC、Resource Quota
  - Pod 排障：`kubectl describe`, `kubectl logs`, `kubectl exec`, `kubectl port-forward`
  - 节点管理：cordon/drain/taint
- **Helm**：Chart 编写、values.yaml 管理、依赖管理
- **Kustomize**：overlay 多环境管理
- **ArgoCD / Flux**：GitOps 部署
  - Application/ApplicationSet 编写
  - Sync Policy（自动/手动、Prune、Self-Heal）
  - 多环境（dev/staging/prod）管理
- **Istio / Linkerd**：服务网格配置（流量管理、mTLS、可观测性）

**关键实践**：
- 多阶段构建减少镜像体积
- 非 root 用户运行容器
- 镜像安全扫描（Trivy）
- 资源限制（requests/limits）
- 健康检查（liveness/readiness/startup probes）
- 优雅关闭（preStop hook, SIGTERM 处理）
- Pod 反亲和性、拓扑分布约束

### 3. 基础设施即代码 (IaC)

**能力描述**：用代码管理基础设施，实现可重复、可版本化、可审计的环境部署。

**工具链**：
- **Terraform / OpenTofu**：
  - 资源定义（VPC/Subnet/SG/EC2/RDS/S3/Lambda/ALB/Route53）
  - 模块化设计、远程状态管理（S3/DynamoDB/Consul）
  - Workspace 多环境管理
  - `terraform plan` → `terraform apply` 工作流
- **Pulumi**：用 TypeScript/Python/Go 管理基础设施
- **Ansible**：
  - Playbook/Role 编写
  - ad-hoc 命令执行
  - Jinja2 模板渲染
- **Packer**：统一镜像构建（AMI/Docker/Vagrant）

**关键实践**：
- 状态文件远程存储 + 锁（S3+DynamoDB / Terraform Cloud）
- 模块化设计，避免重复代码
- 敏感信息使用变量/Secrets Manager，不硬编码
- `terraform plan` 必须人工审查后再 apply
- 基础设施变更走 PR 审查流程

### 4. 可观测性 (Observability)

**能力描述**：构建 Metrics / Logs / Traces 三大支柱，实现全链路可观测。

**工作流**：
```
指标定义 → 采集配置 → 存储 → 可视化 → 告警 → 持续优化
```

**工具链**：

**Metrics**：
- **Prometheus**：
  - 指标类型：Counter/Gauge/Histogram/Summary
  - 采集配置：prometheus.yml、ServiceMonitor/PodMonitor（K8s）
  - PromQL 查询：`rate(http_requests_total[5m])`, `histogram_quantile(0.99, ...)`
  - 告警规则编写（groups/rules/alert）
  - Alertmanager 配置（路由、抑制、静默、通知渠道）
- **Grafana**：
  - Dashboard 设计（变量、模板、面板类型）
  - 数据源配置（Prometheus/Loki/Elasticsearch/CloudWatch）
  - 告警规则与通知渠道
  - 团队/文件夹权限管理
- **VictoriaMetrics / Thanos**：Prometheus 高可用与长期存储

**Logs**：
- **ELK Stack**：Filebeat/Logstash → Elasticsearch → Kibana
- **Grafana Loki**：轻量级日志聚合，与 Prometheus 深度集成
- **Fluentd / Vector**：日志采集与转发

**Traces**：
- **OpenTelemetry**：数据采集标准（SDK 注入、Exporter 配置）
- **Jaeger / Tempo**：分布式链路追踪存储与查询
- **SigNoz**：开源 APM 平台

**关键实践**：
- USE 方法（Utilization/Saturation/Errors）监控每个资源
- RED 方法（Rate/Errors/Duration）监控每个服务
- 四个黄金信号：延迟、流量、错误、饱和度
- 告警规则避免"告警疲劳"——每个告警必须 actionable
- Dashboard 分层：服务级 → 系统级 → 业务级

### 5. SRE 核心实践

**能力描述**：用软件工程方法保障服务可靠性。

**SLO/SLI/Error Budget**：
- **SLI (Service Level Indicator)**：定义可量化的服务质量指标
  - 延迟：P99 请求延迟 < 200ms
  - 可用性：请求成功率 > 99.9%
  - 吞吐量：每秒请求数
  - 错误率：5xx 响应占比
- **SLO (Service Level Objective)**：设定目标阈值
  - 例如：月度 P99 延迟 < 200ms，可用性 > 99.95%
- **Error Budget**：SLO 允许的不可用时间
  - 99.9% SLO → 月度 Error Budget = 43.2 分钟
  - Error Budget 耗尽 → 冻结发布，专注稳定性

**工作流**：
```
定义 SLI → 设定 SLO → 计算 Error Budget → 监控消耗 → 决策（发布/冻结）→ 复盘优化
```

**关键实践**：
- 用 Error Budget 指导发布节奏（budget 充足 → 可发布；耗尽 → 冻结）
- SLO 不是目标，而是决策工具
- 避免过多 SLO（每个服务 3-5 个核心指标即可）
- 定期 Review SLO 是否仍然合理

### 6. 容量规划与性能工程

**能力描述**：通过压力测试、性能分析、容量建模，确保服务能承载预期负载。

**工作流**：
```
负载模型定义 → 基准测试 → 压力测试 → 瓶颈分析 → 优化 → 容量模型 → 持续监控
```

**工具链**：
- **k6**：`k6 run --vus 100 --duration 60s script.js`
  - 编写测试脚本（HTTP/gRPC/WebSocket）
  - 自定义指标、阈值断言
  - 与 Prometheus/Grafana 集成
- **Locust**：Python 编写的分布式压测工具
- **wrk / hey**：快速 HTTP 压测
- **Apache JMeter**：复杂场景压测
- **Vegeta**：`echo "GET http://target" | vegeta attack -rate=1000 -duration=60s | vegeta report`
- **sysbench**：数据库/CPU/IO 基准测试
- **pgbench**：PostgreSQL 基准测试

**关键实践**：
- 压测前先建立基线（baseline）
- 逐步增加负载，观察拐点
- 监控资源使用（CPU/MEM/IO/网络）与延迟的关系
- 压测结果记录：QPS、P50/P95/P99 延迟、错误率、资源使用
- 容量模型：根据压测结果推算承载能力

### 6. 混沌工程

**能力描述**：通过受控实验注入故障，验证系统的弹性与自愈能力。

**工具链**：
- **Chaos Mesh**：K8s 混沌实验平台
  - Pod 故障（kill/stop/restart）
  - 网络故障（延迟/丢包/分区）
  - 磁盘故障（I/O 压力/填充）
  - 压力测试（CPU/Memory）
- **Litmus**：云原生混沌工程框架
- **Gremlin**：商业混沌工程平台
- **自建脚本**：`tc` 网络模拟、`stress` 压力工具

**关键实践**：
- 先在生产环境之外验证（staging）
- 从小范围开始（1 个 Pod → 1 个服务 → 1 个可用区）
- 定义稳态假设（Steady State Hypothesis）
- 实验前确认有监控和告警
- 混沌实验也应有 SLO
- 每次实验后输出报告

### 7. 事故响应与复盘

**能力描述**：快速响应生产事故，系统化排查根因，输出结构化复盘报告。

**事故响应流程**：
```
告警接收 → 确认/升级 → 评估影响 → 遏制/止损 → 根因分析 → 修复 → 恢复 → 复盘
```

**排查方法论**：
- **USE 方法**：检查每个资源的 Utilization / Saturation / Errors
- **RED 方法**：检查每个服务的 Rate / Errors / Duration
- **DIVE 方法**：Define（定义问题）→ Investigate（调查）→ Validate（验证）→ Eliminate（消除）
- **5 Whys**：连续追问 5 个"为什么"找到根因

**常用排查命令**：
```bash
# 系统级
top / htop           # CPU/内存
free -h              # 内存
df -h                # 磁盘
iostat -x 1          # 磁盘 I/O
vmstat 1             # 系统整体状态
ss -tlnp             # 监听端口
ss -s                # 连接统计
dmesg -T | tail -20  # 内核日志

# 网络
curl -o /dev/null -s -w 'Total: %{time_total}s\n' http://target
mtr <target>
tcpdump -i eth0 port 80 -c 100
dig +short <domain>
nslookup <domain>

# K8s
kubectl get events --sort-by='.lastTimestamp'
kubectl describe pod <name>
kubectl logs <name> --previous
kubectl top pod <name>
kubectl top node

# 应用
strace -p <pid> -c   # 系统调用统计
lsof -i -P -n        # 网络连接
jstack <pid>         # Java 线程栈
pprof                # Go 性能分析
```

**Postmortem 模板**：
```markdown
# 事故复盘报告

## 基本信息
- **标题**：[事故简述]
- **日期**：YYYY-MM-DD
- **持续时间**：X 小时 X 分钟
- **影响范围**：影响用户数 / 服务数 / 请求失败数
- **严重级别**：SEV1/SEV2/SEV3
- **负责人**：[姓名]

## 时间线
| 时间 | 事件 |
|------|------|
| HH:MM | 首次告警 |
| HH:MM | 工程师确认 |
| HH:MM | 初步诊断 |
| HH:MM | 遏制措施 |
| HH:MM | 服务恢复 |
| HH:MM | 根因确认 |

## 根因分析
- **直接原因**：
- **根本原因**：
- **触发条件**：

## 影响评估
- 影响用户数：
- 影响时长：
- 数据丢失：有/无
- 经济损失（如有）：

## 改进措施
| 优先级 | 措施 | 负责人 | 截止日期 | 状态 |
|--------|------|--------|---------|------|
| P0 | ... | ... | ... | 待处理 |

## 行动项跟踪
- [ ] 短期修复（24h 内）
- [ ] 中期改进（1 周内）
- [ ] 长期工程（1 个月内）

## 经验教训
- 什么做得好？
- 什么可以改进？
- 如何防止再次发生？
```

### 8. 成本优化 (FinOps)

**能力描述**：分析云资源使用，识别浪费，优化成本结构。

**工作流**：
```
成本数据采集 → 资源使用分析 → 识别浪费 → 优化建议 → 实施 → 持续监控
```

**关键领域**：
- **计算**：合理设置资源 requests/limits、使用 Spot 实例、自动扩缩容
- **存储**：生命周期策略、冷热数据分层、删除未使用卷/快照
- **网络**：CDN 缓存、数据传输优化、NAT Gateway 成本
- **K8s**：Vertical Pod Autoscaler、Cluster Autoscaler、节点池优化
- **云服务**：预留实例/节省计划、删除未使用资源、合理选择实例类型

**工具**：
- AWS Cost Explorer / Azure Cost Management / GCP Cost Tools
- Kubecost / KubeCost
- Infracost：`infracost breakdown --path .` Terraform 成本预估
- CloudHealth / CloudCheckr

### 9. 自动化与 Toil 消除

**能力描述**：识别并自动化消除重复性手动操作，将 SRE 的 Toil 控制在 50% 以下。

**Toil 特征**：
- 手动操作（手工部署、手工配置）
- 重复性（每周做同样的事）
- 可自动化（有明确步骤）
- 无长期价值（做完就完了）
- 随服务增长而线性增长

**自动化方向**：
- 自动扩缩容（HPA/VPA/Cluster Autoscaler）
- 自动证书续期（cert-manager / Let's Encrypt）
- 自动备份与恢复验证
- 自动健康检查与自愈
- 自动发布与回滚
- 自动依赖更新（Renovate / Dependabot）
- 自动安全扫描与修复

### 9. GitOps 与平台工程

**能力描述**：以 Git 为单一事实来源，通过 Pull Request 驱动基础设施和应用变更。

**工作流**：
```
开发者提交 PR → CI 验证 → 合并到主分支 → ArgoCD/Flux 检测变更 → 自动同步到目标环境
```

**工具链**：
- **ArgoCD**：
  - Application CRD 编写
  - Sync Policy（自动/手动、Prune、Self-Heal）
  - Sync Waves 控制部署顺序
  - 多集群管理
- **Flux**：GitOps Toolkit
  - Kustomization/HelmRelease 资源
  - 镜像自动更新（ImageUpdateAutomation）
- **Crossplane**：用 K8s CRD 管理云资源

**关键实践**：
- 环境隔离（dev/staging/prod 使用不同分支或目录）
- 敏感信息用 Sealed Secrets / External Secrets / SOPS 加密
- 部署前自动运行 dry-run 验证
- 回滚策略（保留历史版本、快速回滚）

### 9. 安全与合规

**能力描述**：将安全嵌入 DevOps 流程（DevSecOps），保障供应链安全。

**工具链**：
- **Trivy**：`trivy image <image>` / `trivy fs --scanners vuln,secret,misconfig <path>` / `trivy repo <repo>`
- **SonarQube**：代码质量与安全扫描
- **Semgrep**：`semgrep --config=auto --config=p/r2c-security-audit <path>`
- **Snyk**：依赖漏洞扫描
- **Docker Bench Security**：`docker run --net host --pid host --userns host --cap-add audit_control -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST -v /var/lib:/var/lib:ro -v /var/run/docker.sock:/var/run/docker.sock docker/docker-bench-security`
- **kube-bench**：`kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml`
- **kube-hunter**：K8s 渗透测试
- **Falco**：运行时安全监控
- **OPA / Kyverno**：策略即代码

**DevSecOps 流水线集成**：
```
代码提交 → SAST（Semgrep/SonarQube）→ 依赖扫描（Trivy/Snyk）→ 镜像构建 → 镜像扫描（Trivy）→ 部署 → 运行时安全（Falco）
```

### 10. 备份与灾备

**能力描述**：设计并实施备份策略，确保数据可恢复。

**关键实践**：
- 3-2-1 备份原则（3 份副本、2 种介质、1 份异地）
- 定期恢复演练（备份没验证 = 没备份）
- 数据库备份：逻辑备份（pg_dump/mysqldump）+ 物理备份（WAL 归档/snapshot）
- 文件系统快照（LVM snapshot / EBS snapshot）
- 备份监控：备份成功/失败告警、备份大小趋势

**工具**：
- Velero：K8s 资源与持久卷备份
- restic / duplicity / borg：文件级备份
- pg_dump / pg_basebackup / WAL-G：PostgreSQL 备份
- mysqldump / XtraBackup：MySQL 备份
- AWS Backup / Azure Backup：云原生备份

### 10. 常用命令速查

```bash
# ─── Docker ───
docker build -t <image> .
docker compose up -d
docker compose logs -f <service>
docker system df                    # 磁盘使用
docker image prune -a               # 清理未使用镜像
docker container prune              # 清理停止的容器

# ─── Kubernetes ───
kubectl get pods -o wide
kubectl describe pod <name>
kubectl logs <name> --tail=100 -f
kubectl exec -it <name> -- sh
kubectl port-forward svc/<name> 8080:80
kubectl top pod
kubectl top node
kubectl get events --sort-by='.lastTimestamp'
kubectl get hpa
kubectl get pvc
kubectl cordon/uncordon/drain <node>

# ─── Helm ───
helm list -A
helm install <release> <chart> -f values.yaml
helm upgrade <release> <chart> -f values.yaml
helm rollback <release> <revision>
helm template <release> <chart> --debug

# ─── Terraform ───
terraform init
terraform plan -out=tfplan
terraform apply tfplan
terraform destroy
terraform state list
terraform import <resource> <id>

# ─── Prometheus ───
# 查询示例
rate(http_requests_total[5m])
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
sum by (status) (rate(http_requests_total[5m]))
avg by (instance) (rate(cpu_usage_seconds_total[5m]))

# 告警规则示例
groups:
  - name: example
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.instance }}"

# ─── 网络排查 ───
curl -v http://target
curl -o /dev/null -s -w 'Total: %{time_total}s\n' http://target
mtr <target>
dig +short <domain>
nslookup <domain>
tcpdump -i any port 80 -c 100
ss -tlnp
ss -s

# ─── 性能测试 ───
k6 run --vus 100 --duration 60s script.js
vegeta attack -rate=500 -duration=30s -targets=targets.txt | vegeta report
hey -n 10000 -c 100 http://target
ab -n 10000 -c 100 http://target

# ─── 证书 ───
openssl s_client -connect <host>:443 -servername <host> 2>/dev/null | openssl x509 -noout -dates
certbot renew --dry-run
kubectl get certificate -A

# ─── 备份 ───
pg_dump -h <host> -U <user> -d <db> -F c -f backup.dump
pg_restore -h <host> -U <user> -d <db> backup.dump
mysqldump -h <host> -u <user> -p <db> > backup.sql
velero backup create <name> --include-namespaces <ns>
velero restore create --from-backup <name>
```

### 11. 典型场景与工作流

#### 场景1：搭建完整 CI/CD 流水线

```
用户："帮我搭建从代码提交到 K8s 部署的 CI/CD 流水线"
  │
  ▼
1. 需求确认
   ├─ 代码托管平台（GitHub/GitLab）
   ├─ 语言/框架（Go/Python/Node/Java）
   ├─ 部署目标（K8s 集群）
   └─ 环境数量（dev/staging/prod）
  │
  ▼
2. 方案设计
   ├─ CI 阶段：lint → test → build → image push
   ├─ CD 阶段：deploy to dev → deploy to staging → deploy to prod
   ├─ 安全扫描集成
   └─ 审批门配置
  │
  ▼
3. 执行
   ├─ 编写 CI 配置文件
   ├─ 编写 Dockerfile（多阶段构建）
   ├─ 编写 K8s 部署清单
   ├─ 配置 ArgoCD Application
   └─ 测试流水线
  │
  ▼
4. 验证
   ├─ 提交代码触发流水线
   ├─ 镜像构建成功
   ├─ 自动部署到 dev
   └─ 健康检查通过
```

#### 场景2：生产事故排查

```
用户："服务响应变慢，5xx 增多"
  │
  ▼
1. 确认影响范围
   ├─ 查看 Grafana Dashboard（延迟/错误率/流量）
   ├─ 查看告警
   └─ 确认受影响的服务和用户
  │
  ▼
2. 初步排查
   ├─ 检查最近变更（代码发布、配置变更、基础设施变更）
   ├─ 检查上游依赖（数据库/缓存/外部 API）
   ├─ 检查资源使用（CPU/MEM/DISK/网络）
   └─ 查看日志（ELK/Loki）
  │
  ▼
3. 深入排查
   ├─ 数据库：慢查询、连接池、锁
   ├─ 应用：GC 分析、线程栈、内存 dump
   ├─ 网络：延迟、丢包、带宽
   └─ 外部依赖：第三方 API 响应时间
  │
  ▼
4. 修复与恢复
   ├─ 回滚 / 扩容 / 限流 / 降级
   ├─ 验证恢复
   └─ 通知相关方
  │
  ▼
5. 复盘
   ├─ 编写 Postmortem
   ├─ 确定改进项
   └─ 跟踪闭环
```

#### 场景3：搭建完整可观测性体系

```
用户："帮我搭建一套完整的监控+日志+链路追踪系统"
  │
  ▼
1. 方案设计
   ├─ Metrics：Prometheus + Grafana
   ├─ Logs：Loki + Promtail（轻量）或 ELK
   ├─ Traces：OpenTelemetry + Tempo/Jaeger
   └─ 部署方式：Helm 到 K8s 或 Docker Compose
  │
  ▼
2. 执行
   ├─ 部署 Prometheus Stack（kube-prometheus-stack）
   ├─ 配置 ServiceMonitor 采集应用指标
   ├─ 部署 Loki + Promtail
   ├─ 部署 OpenTelemetry Collector
   ├─ 配置 Grafana 数据源
   └─ 导入/创建 Dashboard
  │
  ▼
3. 告警配置
   ├─ 编写告警规则（PrometheusRule）
   ├─ 配置 Alertmanager（路由、抑制、静默）
   ├─ 配置通知渠道（Slack/钉钉/企微/PagerDuty）
   └─ 测试告警
  │
  ▼
4. 验证
   ├─ 指标采集正常
   ├─ 日志采集正常
   ├─ 链路追踪正常
   └─ 告警触发正常
```

#### 场景4：SLO 定义与 Error Budget 管理

```
用户："帮我为这个服务定义 SLO 并设置 Error Budget 监控"
  │
  ▼
1. 服务分析
   ├─ 服务类型（API/批处理/流处理）
   ├─ 用户期望（响应时间、可用性）
   ├─ 业务影响（收入/用户体验/合规）
   └─ 现有监控数据
  │
  ▼
2. SLI 定义
   ├─ 延迟：P50 < 100ms, P95 < 500ms, P99 < 2s
   ├─ 可用性：请求成功率 > 99.9%
   ├─ 吞吐量：峰值 QPS
   └─ 饱和度：CPU/MEM/连接池使用率
  │
  ▼
3. SLO 设定
   ├─ 核心 API：99.9% 可用性，P99 < 2s
   ├─ 非核心 API：99% 可用性，P99 < 5s
   └─ 批处理：99.5% 成功率
  │
  ▼
4. Error Budget 计算
   ├─ 99.9% SLO → 月度 Error Budget = 43.2 分钟
   ├─ 配置 Prometheus 记录 Error Budget 消耗
   └─ 设置告警：Error Budget 消耗 > 50%/75%/90%
  │
  ▼
5. Dashboard 与告警
   ├─ Grafana Dashboard 展示 SLO 达成率
   ├─ Error Budget 消耗趋势
   └─ 告警：Budget 消耗过快时通知
```

#### 场景5：K8s 集群排障

```
用户："Pod 一直 CrashLoopBackOff / 节点 NotReady / 服务访问超时"
  │
  ▼
1. 信息收集
   ├─ kubectl get pods -o wide
   ├─ kubectl describe pod <name>
   ├─ kubectl logs <name> --previous
   ├─ kubectl get events --sort-by='.lastTimestamp'
   └─ kubectl get nodes -o wide
  │
  ▼
2. 分析
   ├─ 查看容器退出码（137=OOM, 139=Segfault, 143=SIGTERM）
   ├─ 分析日志错误
   ├─ 检查资源限制（OOMKilled?）
   ├─ 检查镜像是否存在
   ├─ 检查 ConfigMap/Secret 是否正确挂载
   ├─ 检查网络策略/Ingress 配置
   └─ 检查 PVC 是否正常
  │
  ▼
3. 修复
   ├─ 修改资源 limits/requests
   ├─ 修复配置错误
   ├─ 回滚到上一个正常版本
   ├─ 扩容 / 重启
   └─ 清理异常资源
  │
  ▼
4. 验证
   ├─ Pod 状态 Running
   ├─ 健康检查通过
   ├─ 日志无报错
   └─ 监控指标正常
```

#### 场景5：成本优化分析

```
用户："帮我分析云成本，找出可以优化的地方"
  │
  ▼
1. 数据收集
   ├─ 查看云平台成本报表
   ├─ 查看 K8s 资源使用（kubectl top）
   ├─ 查看未使用资源（未绑定的 EBS/未关联的 EIP/空闲的 LB）
   └─ 查看预留实例/节省计划覆盖率
  │
  ▼
2. 分析
   ├─ 计算资源：CPU/MEM 使用率是否合理
   ├─ 存储：是否有未使用的卷/快照
   ├─ 网络：数据传输成本是否异常
   └─ K8s：Pod 资源 requests/limits 是否合理
  │
  ▼
3. 优化建议
   ├─ 调整资源 requests/limits
   ├─ 使用 Spot 实例 / 预留实例
   ├─ 删除未使用资源
   ├─ 配置自动扩缩容
   └─ 存储生命周期策略
  │
  ▼
4. 实施与验证
   ├─ 实施优化
   ├─ 验证服务稳定性不受影响
   └─ 对比优化前后成本
```

## 工具集成矩阵

| 领域 | 工具 | Agent 如何使用 |
|------|------|---------------|
| **CI/CD** | GitHub Actions / GitLab CI / Jenkins | 编写流水线配置文件、调试构建失败 |
| **GitOps** | ArgoCD / Flux | 编写 Application/ApplicationSet、配置同步策略 |
| **容器** | Docker | 编写 Dockerfile、docker-compose.yml、镜像构建优化 |
| **编排** | Kubernetes | 编写 K8s 资源 YAML、排障、配置管理 |
| **服务网格** | Istio / Linkerd | 配置 VirtualService/DestinationRule/mTLS |
| **IaC** | Terraform / OpenTofu | 编写 .tf 文件、模块化、状态管理 |
| **配置管理** | Ansible | 编写 Playbook/Role、ad-hoc 命令 |
| **监控** | Prometheus | 编写 prometheus.yml、ServiceMonitor、告警规则、PromQL |
| **可视化** | Grafana | Dashboard 设计、数据源配置、告警通知 |
| **日志** | Loki / ELK | 日志采集配置、查询、告警 |
| **链路追踪** | OpenTelemetry + Tempo/Jaeger | SDK 注入、Collector 配置 |
| **压测** | k6 / Locust / Vegeta | 编写压测脚本、执行、分析结果 |
| **混沌工程** | Chaos Mesh / Litmus | 编写实验、执行、分析 |
| **IaC** | Terraform / Pulumi | 编写资源定义、模块化、状态管理 |
| **配置管理** | Ansible | 编写 Playbook/Role |
| **密钥管理** | Vault / Sealed Secrets / External Secrets | 配置、集成 |
| **证书** | cert-manager | Certificate/Issuer/ClusterIssuer 配置 |
| **策略** | OPA / Kyverno | 编写策略规则 |
| **成本** | Infracost / Kubecost | 成本分析 |
| **备份** | Velero / restic | 备份策略配置 |
| **混沌** | Chaos Mesh / Litmus | 实验编写与执行 |
| **脚本** | Shell / Python / Go | 自动化脚本编写 |

## 输出规范

| 输出类型 | 格式 | 说明 |
|----------|------|------|
| 流水线配置 | YAML | GitHub Actions / GitLab CI / Jenkinsfile |
| K8s 资源 | YAML | Deployment/Service/Ingress/Helm Chart |
| IaC 代码 | HCL/Python/YAML | Terraform / Pulumi / Ansible |
| 监控配置 | YAML | Prometheus 规则、Grafana Dashboard JSON |
| 脚本 | Shell/Python | 自动化运维脚本 |
| 报告 | Markdown | Postmortem、巡检报告、容量报告 |
| 架构图 | Mermaid | 部署架构、网络拓扑、CI/CD 流程 |
| Dashboard | JSON | Grafana Dashboard 导出 JSON |

## 与现有技能的复用关系

| 现有技能 | 复用方式 |
|----------|----------|
| `ops-engineer` | 基础设施管理、容器与 K8s、监控告警、故障排查等运维操作 |
| `security-engineer` | 安全扫描、DevSecOps 集成、安全加固 |
| `backend-developer` | 应用层性能优化、代码审查、API 开发 |
| `arch-c4-diagram` | 需要画部署架构图时加载 |
| `arch-adr` | 需要记录架构/运维决策时加载 |
| `arch-tech-evaluation` | 需要工具选型时加载 |
| `chinese-pdf-generation` | 将报告/文档输出为 PDF |

## 典型对话示例

**示例1：搭建 CI/CD**
> 用户："帮我配置 GitHub Actions 自动构建 Docker 镜像并部署到 K8s"
> Agent：确认技术栈 → 编写 .github/workflows/*.yml → 编写 Dockerfile → 配置 ArgoCD → 测试 → 验证

**示例2：SLO 定义**
> 用户："帮我为这个 API 服务定义 SLO"
> Agent：分析服务特性 → 定义 SLI → 设定 SLO 目标 → 计算 Error Budget → 配置监控 → 设置告警

**示例3：事故排查**
> 用户："生产环境 5xx 增多，帮我排查"
> Agent：查看 Grafana → 检查最近变更 → 查看日志 → 分析根因 → 修复 → 复盘

**示例4：搭建可观测性**
> 用户："帮我搭建 Prometheus + Grafana + Loki + Tempo"
> Agent：方案选择 → Helm 部署 → 配置采集 → 创建 Dashboard → 配置告警 → 验证

**示例5：成本优化**
> 用户："帮我分析 K8s 集群成本"
> Agent：查看资源使用 → 分析浪费 → 给出优化建议 → 实施 → 验证

## 与架构师 Agent 的协作

```
用户需求
  │
  ├─ 需要设计方案/选型 → 软件架构师 Agent
  │   （出方案、画图、写文档、技术选型）
  │
  └─ 需要动手执行 → DevOps/SRE 工程师 Agent
      （写配置、部署、排障、自动化、可靠性保障）
```
