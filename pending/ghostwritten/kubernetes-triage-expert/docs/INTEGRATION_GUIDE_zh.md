# 集成指南

本文档定义 `Kubernetes Triage Expert` 应该如何接入更大的排障工作流，同时不破坏它原本的边界。

核心原则很简单：这个 skill 是推理层，不是执行层。

## 目的

使用这份文档是为了回答下面几类问题：

- 什么时候应该把这个 skill 接进工作流
- 责任应该如何拆分
- 外部工具应该以什么方式提供证据
- 什么接法能保持 skill 的设计初衷

这不是安装文档。安装和首次使用请看：

- [../README.md](../README.md)
- [README_zh.md](./README_zh.md)

## 集成原则

所有集成方式都应遵守这些原则：

- 输入的是证据，输出的是推理
- 不暗示环境访问能力
- skill 负责请求证据，外部系统负责提供证据
- 执行和修复不属于 skill
- 下一步动作应当收敛、可审计、能改变判断

## 责任模型

当这个 skill 与其他工具一起使用时，责任分工应保持稳定。

### Skill

- 识别故障类型
- 规范化故障描述
- 区分事实与推测
- 排序高概率假设
- 请求下一步最高价值检查项
- 明确指出何时已经超出 Kubernetes 初筛边界

### 操作者

- 执行命令
- 获取日志、Events、Metrics、Manifest、发布记录
- 把关键证据贴回或总结回对话
- 决定是否实施修复

### 外部系统

- 提供原始运维证据
- 不替代推理
- 只回答 skill 提出的具体诊断问题

## 适用场景

当你需要以下能力时，适合接入这个 skill：

- 结构化多轮 triage
- 基于证据逐步收敛假设
- 明确区分“谁负责推理、谁负责执行”
- 规范地使用日志、events、metrics 和 rollout 信息

当你主要需要以下能力时，它不适合作为主层：

- 直接执行命令
- 自动采集证据
- 无人参与的实时环境验证
- 自动修复
- 以应用内部逻辑或云平台底层排查为主任务

## 集成模式

### Codex

如果你想要一个结构化、多轮推进的排障过程，Codex 是很自然的使用环境。

推荐模式：

1. 安装或加载这个 skill。
2. 显式调用 skill，或用与 skill 描述高度匹配的方式描述任务。
3. 提供故障对象、症状、时间线和最强证据。
4. 让 skill 给出下一步检查项。
5. 你自己执行检查，再把结果返回给 skill。

示例提示：

```text
Use the kubernetes-triage-expert skill and stay within skill boundaries only.

namespace=prod
deployment=checkout-api
pods are CrashLoopBackOff
started after today's rollout
log excerpt: failed to load config: missing REDIS_URL
```

### 普通聊天界面

在普通聊天 UI 中，这个 skill 应当被视为“带强约束的推理助手”。

推荐模式：

- 把 [../PROMPT.md](../PROMPT.md) 的内容贴进去
- 明确要求 assistant 严格遵守 skill 边界
- 结构化提供证据

避免：

- 让它“直接检查集群”
- 在证据不足时要求直接给修复方案
- 只给一个状态名就让它确认根因

### `kubectl`

这是最常见的协作模式。

推荐闭环：

1. 先把问题描述给 skill。
2. 让 skill 指定下一步最值得检查的内容。
3. 你手动执行相应的 `kubectl` 命令。
4. 把输出结果或精确摘要贴回对话。
5. 让 skill 更新假设和下一步动作。

好的模式：

- skill 要 scheduler event
- 操作者执行 `kubectl describe pod ...`
- 返回关键 event 行
- skill 收敛到调度约束路径

坏的模式：

- 一上来问“你直接告诉我执行什么命令可以修好”

### 日志

日志是证据提供层，不是诊断替代品。

适合提供的内容包括：

- 启动失败日志
- 终止原因
- 探针相关错误
- 外部依赖连接失败
- 与发布时间相关的异常日志

最佳实践：

- 给短而精确的日志片段，不要给模糊总结
- 带上时间信息
- 标明是当前容器还是 previous container 的日志

### 指标与仪表盘

指标主要用于回答 skill 提出的具体诊断问题，例如：

- 是否存在 OOM 证据
- 是否有 CPU 饱和
- 副本健康是否明显下降
- 延迟或错误率是否与 rollout 强相关

不要把整页 dashboard 总结直接塞进对话，除非它明确对应某个假设。

### 告警与 Incident 系统

告警最适合作为 triage 的入口。

有价值的输入包括：

- 什么告警触发了
- 什么时候开始
- 影响了哪个服务或 namespace
- 影响面有多大
- 附近是否有发布或配置变更

skill 应该把这些输入转化为：

- 一个主要故障类型
- 初始假设
- 下一步要收集的证据

### Runbook

Runbook 和这个 skill 的职责不同。

- runbook 负责沉淀已知处理流程
- skill 负责判断当前证据更接近哪条 runbook，或当前是否还没到直接套 runbook 的阶段

skill 不应假装执行 runbook。

## 推荐工作流

推荐使用这个闭环：

1. 从症状、时间、对象和最强证据开始。
2. 让 skill 归类主要故障类型。
3. 让 skill 要求接下来 1 到 3 个最关键的检查项。
4. 使用 `kubectl`、日志、仪表盘、告警或 runbook 去收集这些证据。
5. 把证据返回给 skill。
6. 重复这个过程，直到根因被确认、问题明显超出 Kubernetes 初筛范围，或需要进入修复决策阶段。

## 环境说明

不同环境主要影响 skill 的发现和触发方式，不改变它的边界。

- Codex：显式点名 skill 往往最清晰
- Claude Code：当任务与 skill 描述匹配时，可能自动发现
- OpenClaw：skill 的加载方式可能取决于 skill 目录和工作区配置
- 普通聊天界面：通常最稳定的方式是直接粘贴 prompt

## 反模式

不要把这个 skill 当成：

- 已接入集群的 agent
- 自动 incident commander
- 自动修复引擎
- Kubernetes 百科机器人
- 应用代码排错替代品

典型错误用法：

- “你检查下我的集群哪里有问题。”
- “你直接告诉我怎么修。”
- “现在是 CrashLoopBackOff，所以根因是什么？”
- “我贴一张 dashboard 截图，你把所有问题都诊断出来。”

## 示例交互模式

### 第一步

用户：

```text
Use the kubernetes-triage-expert skill.
服务不可达
namespace=prod
deployment=checkout-api
started after rollout
```

### 第二步

skill：

- 先归类可能的故障族群
- 要求补充下一步缺失证据

### 第三步

用户：

```text
service endpoints are empty
one pod is Running but not Ready
one pod is CrashLoopBackOff
```

### 第四步

skill：

- 如果需要，重新定位主要故障
- 收敛假设
- 给出下一步最高价值检查项

## 总结

用这个 skill 来推理。
用外部工具来取证。
用操作者来执行命令和做变更。

只要这三者边界不混，这个 skill 才会持续保持诚实且有价值。
