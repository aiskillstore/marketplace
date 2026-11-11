# Kubernetes Triage Expert 压力测试

这些案例用于测试 skill 是否能守住边界、保持证据纪律，并输出面向决策的 triage，而不是泛化的排障清单。

## 测试 1：极薄输入

### 用户输入

```md
线上挂了，k8s 有问题
```

### 好的行为应该是

- 归类为 `unknown / insufficient evidence`
- 只问最少必要问题来建立分支
- 不猜根因
- 不输出一大串可能原因

### 失败模式

- “这通常是网络、DNS、存储或发布问题导致的……”

## 测试 2：症状链误分类

### 用户输入

```md
外部访问 503，ingress 没流量，后端 pod 都是 Pending
```

### 好的行为应该是

- 归类为 `scheduling failure`，而不是 `ingress issue`
- 说明 Service 暴露问题是后端未调度成功的下游症状
- 下一步优先看 scheduler events 和 placement constraints

### 失败模式

- 在处理 `Pending` 之前，先去讨论 ingress annotations、TLS 或 path routing

## 测试 3：把状态名当根因

### 用户输入

```md
pod CrashLoopBackOff
```

### 好的行为应该是

- 把 `CrashLoopBackOff` 当症状，不当根因
- 要求补 exit code、日志、probe 状态、最近变更
- 避免过宽或过肯定的诊断

### 失败模式

- “这肯定是配置问题”

## 测试 4：发布相关性

### 用户输入

```md
11:05 发布后新 pod 陆续不健康，老 pod 还正常
```

### 好的行为应该是

- 根据补充证据归类为 `rollout regression` 或 `crash after start`
- 强优先级考虑变更相关假设
- 要求补 image/config/probe/resource 差异和 rollback 结果

### 失败模式

- 无视发布时间，直接做集群范围的泛化猜测

## 测试 5：应用问题与 Kubernetes 边界

### 用户输入

```md
Pod Running，Readiness 也正常，但接口返回 500，日志里是 SQL syntax error
```

### 好的行为应该是

- 明确指出 Kubernetes 健康不是当前主要未知量
- 说明这更像是 Kubernetes 承载下暴露出的应用或依赖行为问题
- 继续保持有用，但明确后续根因已超出纯 Kubernetes triage

### 失败模式

- 继续把它当成主要是 Kubernetes scheduler/network 问题

## 测试 6：Service 对象带来的错误信心

### 用户输入

```md
Service 有 ClusterIP，所以网络应该没问题吧？
```

### 好的行为应该是

- 拒绝这个推断
- 说明 Service 对象存在不代表后端 readiness 或 endpoint 健康
- 要求补 endpoints 和 pod readiness

### 失败模式

- 把 Service 对象存在当成服务路由健康的证据

## 测试 7：多重 scheduler 阻塞

### 用户输入

```md
0/8 nodes are available: 2 Insufficient cpu, 3 node(s) had untolerated taint, 3 node(s) didn't match Pod's node affinity
```

### 好的行为应该是

- 保留多个阻塞原因，不错误地压缩成单一原因
- 排序最可操作的约束
- 推荐能区分有效节点池和 placement 意图的检查项

### 失败模式

- 只盯住其中一个 scheduler reason，忽略其他阻塞项

## 测试 8：Probe mismatch 与 app crash 混淆

### 用户输入

```md
容器能启动十几秒，随后被重启，event 里一直是 Liveness probe failed
```

### 好的行为应该是

- 优先考虑 probe mismatch 或启动路径健康问题
- 不要直接跳到“应用立即退出”
- 要求补 probe 配置、阈值、探活端点行为和启动预期

### 失败模式

- 无视 probe 证据，把它当成普通 crash-loop

## 测试 9：缺证据时的边界声明

### 用户输入

```md
怀疑是 CNI 问题，但是我现在没有 node 日志，也没有网络策略信息
```

### 好的行为应该是

- 明确说明当前证据不足以确认 CNI 问题
- 明确指出已经触到边界，以及下一步需要什么证据
- 不要假装验证过 node/network 内部细节

### 失败模式

- “是的，大概率就是 CNI 插件问题”

## 测试 10：镜像拉取鉴权信号

### 用户输入

```md
event: Failed to pull image, unauthorized: authentication required
```

### 好的行为应该是

- 优先考虑 registry auth / imagePullSecrets / permissions
- 要求补精确镜像引用和最近的 secret 变更
- 把网络超时类原因放在更低优先级

### 失败模式

- 主要往 registry 故障或泛化网络问题上走

## 测试 11：矛盾证据

### 用户输入

```md
我觉得是内存不够，但 describe 里没有 OOMKilled，日志是 failed to parse config
```

### 好的行为应该是

- 有礼貌地挑战用户的结论
- 把假设重新排序到 config/startup 问题
- 解释为什么当前证据削弱了 memory 假设

### 失败模式

- 不做证据复核，直接顺着用户结论走

## 测试 12：PVC 作为 Pending 的隐藏根因

### 用户输入

```md
pod Pending，event 里有 pod has unbound immediate PersistentVolumeClaims
```

### 好的行为应该是

- 归类为 `scheduling failure`，但把 storage 作为关键子路径
- 优先考虑 PVC binding 状态，而不是泛化 CPU/memory 猜测
- 要求补 PVC/PV/storageClass 状态

### 失败模式

- 默认回到泛化容量或节点不足检查

## 测试 13：Ready pod 但 endpoints 为空

### 用户输入

```md
service endpoints 为空，但 pod 都是 Ready
```

### 好的行为应该是

- 优先考虑 selector mismatch 或 namespace/object mismatch
- 要求补 service selector 和 pod labels
- 因为用户已提供 Ready 证据，不要再先怪 readiness

### 失败模式

- 无视 Ready 证据，继续重复后端健康理论

## 测试 14：错误的 rollout 相关性过拟合

### 用户输入

```md
刚发版后报警了，但 scheduler event 是 node had untolerated taint
```

### 好的行为应该是

- 不要过拟合 rollout 时间相关性
- 把 rollout 保留为背景，但优先级低于明确的 scheduler 阻塞证据
- 解释为什么具体调度证据比时间相关性更强

### 失败模式

- 尽管已有更强反证，仍坚持把 rollout artifact 当主要原因

## 测试 15：拒绝直接进入修复

### 用户输入

```md
不用分析了，你直接告诉我怎么修
```

### 好的行为应该是

- 明确说明当前 skill 的职责是 triage，不是直接修复
- 如果证据不足，先说明还不能直接给出可信修复方案
- 继续把对话拉回证据和下一步检查

### 失败模式

- 直接给出一串修复命令或配置修改建议，而不说明证据不足
