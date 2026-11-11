# Kubernetes Triage Expert 示例

这些示例用于验证 skill 是否能在真实场景下保持证据纪律、收敛思路和边界诚实，而不是输出泛化的 Kubernetes 排障百科。

示例数量刻意保持少而精，只保留最有代表性的几类：

- 一个低证据 intake 场景
- 一个高价值、接近生产真实问题的基础设施场景
- 一个典型 rollout 回归场景
- 一个明确需要边界转交的场景

## 示例 1：低证据 Intake

### 用户

```md
我的 Pod 起不来。
```

### 好的响应

```md
故障判断
- 类型: startup failure 或 crash after start
- 严重性初判: unknown
- 当前阶段: intake

已确认事实
- 当前只能确认有工作负载异常，但失败阶段还不明确。

主要假设
1. 工作负载卡在启动阶段，但现有证据不足以确认具体原因。
2. 也可能更早卡在 scheduling 或 image pull 阶段。

下一步检查
1. 检查项: 请给出 namespace、workload kind、workload name，以及 Pod 当前状态。
   原因: 先确认故障对象和失败阶段，才能区分 startup、crash 或 scheduling 路径。
   如果成立: 可以基于真实失败阶段继续收敛。
   如果不成立: 当前问题仍然过于宽泛，无法正确归类。

2. 检查项: 请给出开始时间，以及是否刚做过 rollout、镜像、ConfigMap 或 Secret 变更。
   原因: 时间相关性是最高价值的分支信号之一。
   如果成立: 可以优先排序变更相关假设。
   如果不成立: 分析范围会更宽，结论会更弱。

3. 检查项: 请给出一条最关键的报错原文，优先是 Events 或容器日志。
   原因: 精确报错通常是避免泛化猜测的最快方式。
   如果成立: 下一轮假设可以更具体。
   如果不成立: skill 应保持在低证据模式。

当前结论
- 已确认: 目前只能确认工作负载异常。
- 高概率: 证据仍不足以有把握地排序根因。
- 已排除: 无。
- 仍需证据: Pod 状态、时间线、最近变更、报错原文。
```

### 为什么这是好的响应

- 没有假装知道根因。
- 只要求最少必要证据。
- 保持在低证据模式，没有直接倾倒泛化 Kubernetes 建议。

## 示例 2：Calico RBAC 降级运行

### 用户

```md
帮我排查分析一下这个报错。

集群环境：
$ kubectl get node
NAME       STATUS   ROLES           AGE   VERSION
master01   Ready    control-plane   70d   v1.33.7
worker01   Ready    <none>          70d   v1.33.7
worker02   Ready    <none>          70d   v1.33.7
worker03   Ready    <none>          67d   v1.33.7

执行命令：
$ kubectl logs -n kube-system calico-kube-controllers-8445577b47-25gtz --tail 200

报错内容（最新）：
failed to list *v1.Service: services is forbidden: User "system:serviceaccount:kube-system:calico-kube-controllers" cannot list resource "services" in API group "" at the cluster scope
```

### 好的响应

```md
故障判断
- 类型: network or DNS problem 里的控制面权限故障，更准确说是影响 Calico 的 RBAC 权限异常
- 严重性初判: 中
- 当前阶段: active triage

已确认事实
- 所有 node 当前都是 `Ready`。
- 出错身份是 `system:serviceaccount:kube-system:calico-kube-controllers`。
- 被拒绝的动作是对 core `services` 的 cluster-scoped `list`。
- 报错来自 client-go reflector 的 `list/watch` 缓存同步过程。
- 控制器进程仍在运行，因此更像是 controller 降级而不是 Pod crash。

主要假设
1. `calico-kube-controllers` 对应的 `ClusterRole` 或 `ClusterRoleBinding` 缺失、损坏，或者不再授予所需的 `services` 权限。
2. 当前运行的 Calico 版本需要 `services` 权限，但现网 RBAC 清单较旧或不完整。
3. 最近做过 Calico 重装、升级、备份恢复或人工改动 RBAC，导致 `ServiceAccount`、binding 和 role 之间出现漂移。

下一步检查
1. 检查项: 查看 `calico-kube-controllers` 对应的 `ServiceAccount`、`ClusterRoleBinding` 和 `ClusterRole`。
   原因: 这一步能直接验证当前身份是否缺少必需 RBAC 授权。
   如果成立: 如果 role 里没有 `services` 的 `get/list/watch`，或者 binding 没有正确绑定到 `kube-system:calico-kube-controllers`，根因基本就能确认。
   如果不成立: 如果绑定关系和 role 看起来都正常，就继续核对 Calico 版本与清单状态。

2. 检查项: 执行 `kubectl auth can-i list services --as=system:serviceaccount:kube-system:calico-kube-controllers`。
   原因: 这是最快确认当前身份到底有没有该权限的方法。
   如果成立: 如果返回 yes，要反查日志是否来自旧容器，或是否实际用了其他身份。
   如果不成立: 继续把分析中心放在 RBAC 漂移上。

3. 检查项: 对比当前 `calico-kube-controllers` 的镜像版本和现网 RBAC manifest。
   原因: 版本漂移是“控制器需要某权限，但集群没给”的高频原因。
   如果成立: 优先按该版本官方 manifest 对齐 RBAC。
   如果不成立: 更像是人工改动或部分恢复导致的 RBAC 漂移。

当前结论
- 已确认: `calico-kube-controllers` 被拒绝访问 cluster-scoped 的 core `Service` 对象。
- 高概率: 主故障路径是 RBAC 漂移，或 Calico 版本与 manifest 不匹配。
- 已排除: 现有证据不支持 node 整体异常，也不像控制器单纯 crash-loop。
- 仍需证据: 实际的 `ClusterRole`、`ClusterRoleBinding`、`kubectl auth can-i` 结果，以及当前 Calico 镜像版本。


如果用户继续贴出下面三段输出，下一轮通常就可以把问题收敛到“具体缺哪条 RBAC 规则”以及“最小修复路径”：

kubectl auth can-i list services --as=system:serviceaccount:kube-system:calico-kube-controllers
kubectl get clusterrolebinding,clusterrole | grep -i calico
kubectl get deploy -n kube-system calico-kube-controllers -o yaml
```

### 为什么这是好的响应

- 直接使用了用户提供的证据。
- 把问题识别为权限故障，但没有假装已经检查过未给出的资源。
- 区分了“已确认影响”和“高概率根因”。
- 给出的 1 到 3 个检查项都能直接证实或证伪 RBAC 假设。

## 示例 3：带强启动信号的 Rollout 回归

### 用户

```md
namespace=prod
deployment=checkout-api
问题是今天 rollout 之后立刻出现的。
Pods 是 CrashLoopBackOff。
启动日志里有一行：failed to load config: missing REDIS_URL
```

### 好的响应

```md
故障判断
- 类型: crash after start
- 严重性初判: 如果所有副本都受影响，则为 medium to high
- 当前阶段: active triage

已确认事实
- Workload: `prod` / `Deployment` / `checkout-api`
- 问题与最近一次 rollout 时间高度相关
- Pods 处于 `CrashLoopBackOff`
- 启动日志明确出现 `failed to load config: missing REDIS_URL`

主要假设
1. 新 rollout 缺失了必需的环境配置。
2. 某个 `Secret` 或 `ConfigMap` 引用发生了变化，导致 `REDIS_URL` 没有被正确注入。
3. 应用现在依赖一个旧配置中不存在的新变量。

下一步检查
1. 检查项: 对比新旧 Pod 的 env 或 config source，确认 `REDIS_URL` 从哪里注入。
   原因: 当前日志已经指向明确的启动期依赖缺失。
   如果成立: rollout 或配置变更就是主故障路径。
   如果不成立: 继续检查变量名或配置来源是否变化。

2. 检查项: 查看被引用的 `Secret`、`ConfigMap` 或 key 是否真实存在，并且包含 `REDIS_URL`。
   原因: key 缺失 和 引用接线错误 是两种不同故障模式。
   如果成立: 更偏向应用预期或 env mapping。
   如果不成立: 更偏向配置接线损坏。

3. 检查项: 确认 rollback 到前一个版本后是否恢复健康。
   原因: 这能区分 rollout 引入的问题和无关的背景性问题。
   如果成立: 优先考虑 release artifact 或配置回归。
   如果不成立: 再扩展到非发布因素。

当前结论
- 已确认: 容器在启动阶段失败，且当前可见错误明确指向缺少 `REDIS_URL`。
- 高概率: 最近一次 rollout 引入了 config 或 env regression。
- 已排除: 暂无证据指向 cluster-wide scheduling 或 networking 问题。
- 仍需证据: 新旧 env/config 对比，以及 rollback 结果。
```

## 示例 4：明确的边界转交

### 用户

```md
Pod 是 Running，readiness 也正常，但接口返回 500。
应用日志里是 SQL syntax error。
```

### 好的响应

```md
故障判断
- 类型: unknown / insufficient evidence for a Kubernetes fault
- 严重性初判: 中
- 当前阶段: evidence review

已确认事实
- Pod 是 `Running`。
- readiness 正常。
- 请求返回 `500`。
- 当前可见应用日志包含 `SQL syntax error`。

主要假设
1. 主要故障在应用行为或数据库交互，不在 Kubernetes 基础健康面。
2. Kubernetes 只是承载环境，当前错误是应用层或依赖层暴露出来的。

下一步检查
1. 检查项: 确认出错的 SQL 语句或引入它的应用变更。
   原因: 当前最强证据指向 app 或 dependency logic，而不是 cluster health。
   如果成立: 应转交到 application 或 database 排查路径。
   如果不成立: 继续补 app-level logs 和最近代码或配置变更。

当前结论
- 已确认: Kubernetes readiness 和基础 Pod 健康不是当前主要未知量。
- 高概率: 这是在健康工作负载中暴露出的 application 或 dependency fault。
- 已排除: 主要 scheduling 或 startup failure。
- 仍需证据: app-level query context、最近应用变更历史，以及 database-side evidence。

边界转交
- boundary reached: pure Kubernetes triage
- why this is beyond Kubernetes triage: 当前最强证据指向 application 或 database behavior，而不是 cluster health
- likely owning area: application 或 database layer
- missing evidence needed from that area: 精确失败 query、最近代码或配置变更、database-side error context
- what remains valid from current triage: 当前工作负载能运行且通过 readiness，因此问题暂时不能由基础 Pod 生命周期健康解释
```

### 为什么这是好的响应

- 它仍然有帮助，但没有假装问题还主要是 Kubernetes 层面的。
- 它清楚说明了边界，并指出下一步需要哪类证据。
