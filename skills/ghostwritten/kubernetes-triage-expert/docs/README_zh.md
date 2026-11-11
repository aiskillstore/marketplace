# Kubernetes Triage Expert

`Kubernetes Triage Expert` 是一个面向 Kubernetes 故障场景的 prompt-first skill 规范仓库。它的目标不是模拟一个“已经接入集群”的系统，而是在没有任何工具执行能力的前提下，仍然把故障分析过程做得专业、克制、结构化。

这个仓库定义的是一种严格受限的排障工作方式：只基于用户已经提供的证据进行 Kubernetes 初筛与诊断推进。

## 快速安装

如果你使用 OpenClaw / ClawHub，可以直接安装已发布版本：

```bash
clawhub install kubernetes-triage-expert
```

查看已发布包信息：

```bash
clawhub inspect kubernetes-triage-expert
```

## 文档入口

如果你想快速上手，请先看：

- [../README.md](../README.md)

如果你想看详细规范，请继续阅读：

- [../SKILL.md](../SKILL.md)
- [skill_zh.md](./skill_zh.md)
- [INTEGRATION_GUIDE_zh.md](./INTEGRATION_GUIDE_zh.md)

## 概述

很多通用对话式 AI 在 Kubernetes 排障中会出现几个典型问题：

- 过早猜测根因
- 把症状和根因混在一起
- 输出大而全、没有优先级的原因列表
- 说话方式像是已经检查过集群

这个项目就是为了解决这些问题。它定义了一套更严格的 skill 行为模型，使回答更接近专业 SRE 的初筛逻辑，而不是泛化问答。

## 目标

- 为 Kubernetes 故障初筛建立一套专业规范。
- 保证所有结论都受证据约束。
- 提升“下一步排查动作”的质量，而不是只提升解释质量。
- 避免 prompt 常见失真，例如过度确定、泛化建议堆砌、伪装环境可见性。
- 通过示例和压力测试让 skill 行为可验证、可审计。

## 非目标

- 执行 `kubectl` 或其他命令
- 接入 Kubernetes、云平台、CI/CD 或观测系统
- 扩展成 agent、MCP、tool 或自动化工作流
- 自动修复问题或生成未经验证的修复方案
- 替代应用代码、运行时内部机制、云厂商底层基础设施的深度排查

## 适用对象

本仓库适合以下人群使用或参考：

- SRE 工程师
- DevOps 工程师
- 平台工程师
- 设计运维类 AI prompt 的工程师
- 希望验证“无工具能力的 skill 是否仍然有价值”的团队

## 仓库内容

- [SKILL.md](../SKILL.md)：完整 skill 规范与行为约束
- [PROMPT.md](../PROMPT.md)：可直接投喂模型的精简 prompt
- [EXAMPLES.md](./EXAMPLES.md)：英文示例集
- [EXAMPLES_zh.md](./EXAMPLES_zh.md)：中文示例集
- [STRESS_TESTS.md](./STRESS_TESTS.md)：英文压力测试用例
- [STRESS_TESTS_zh.md](./STRESS_TESTS_zh.md)：中文压力测试用例
- [EVALUATION_RUBRIC.md](./EVALUATION_RUBRIC.md)：评估与回归测试评分标准
- [EVALUATION_RUBRIC_zh.md](./EVALUATION_RUBRIC_zh.md)：中文评分标准
- [REVIEW_TEMPLATE.md](./REVIEW_TEMPLATE.md)：评审模板
- [MULTI_TURN_REVIEW_TEMPLATE.md](./MULTI_TURN_REVIEW_TEMPLATE.md)：多轮评审模板
- [MULTI_TURN_REVIEW_TEMPLATE_zh.md](./MULTI_TURN_REVIEW_TEMPLATE_zh.md)：中文多轮评审模板
- [skill_zh.md](./skill_zh.md)：`SKILL.md` 的中文翻译

## 规范主文件

- [SKILL.md](../SKILL.md) 是行为、结构和约束的主规范。
- [PROMPT.md](../PROMPT.md) 是面向运行时的精简 prompt，应与 [SKILL.md](../SKILL.md) 保持一致。
- 其他文档都应服从 [SKILL.md](../SKILL.md) 中定义的边界、语言和输出规则。

## 设计原则

- 证据优先：没有证据，不确认根因。
- 最早故障优先：排障应从故障链中最早断开的地方开始。
- 下一步最小化：只推荐能改变诊断方向的检查项。
- 边界诚实：绝不暗示自己能看见环境或能执行命令。
- 推理可审计：明确区分已确认、高概率、已排除、仍缺失。
- 收敛优先于百科：目标是缩小搜索空间，而不是罗列所有知识。

## 工作模型

这个 skill 被刻意设计得很窄。

它可以：

- 分析用户提供的状态、日志、事件和变更信息
- 识别故障类型
- 排序最可能的假设
- 推荐接下来 1-3 个最高价值的检查项
- 明确指出何时已经超出 Kubernetes 初筛边界

它不能：

- 检查集群
- 执行命令
- 主动拉取遥测数据
- 独立验证实时环境状态
- 在证据不足时制造确定性结论

## 重点覆盖的故障类型

本 skill 主要针对高频 Kubernetes 故障族群进行优化，包括：

- `CrashLoopBackOff`
- `Pending`
- `ImagePullBackOff` / `ErrImagePull`
- Service 不可达
- 发布后回归
- 探针相关异常
- PVC / 存储导致的调度阻塞

它的职责不是一次性解决全部问题，而是给出“当前最正确的下一步排查动作”。

## 推荐使用顺序

1. 先阅读 [SKILL.md](../SKILL.md)，理解完整约束和设计逻辑。
2. 使用 [PROMPT.md](../PROMPT.md) 作为运行时 prompt。
3. 通过 [EXAMPLES_zh.md](./EXAMPLES_zh.md) 或 [EXAMPLES.md](./EXAMPLES.md) 观察好输出与坏输出的差异。
4. 使用 [STRESS_TESTS_zh.md](./STRESS_TESTS_zh.md) 或 [STRESS_TESTS.md](./STRESS_TESTS.md) 做稳定性与边界测试。
5. 使用 [EVALUATION_RUBRIC.md](./EVALUATION_RUBRIC.md) 对输出做评分、回归评审或模型对比。

## 输出结构示例

```md
故障判断
- 类型:
- 严重性初判:
- 当前阶段:

已确认事实
- ...

主要假设
1. ...
2. ...
3. ...

下一步检查
1. 检查项:
   原因:
   如果成立:
   如果不成立:

当前结论
- 已确认:
- 高概率:
- 已排除:
- 仍需证据:
```

## 评估标准

一个高质量回答应当：

- 正确识别主要故障类型
- 有效减少不确定性
- 避免过度下结论
- 把下一步检查控制在少而精准的范围内
- 正确区分 Kubernetes 问题、应用问题、运行时问题和云平台问题

一个低质量回答通常会：

- 一次性列太多原因
- 在证据不足时猜测
- 把下游症状误当成主要故障
- 说得像已经检查过环境

## 路线图

当前范围：

- skill 规范
- 运行时 prompt
- 示例集
- 压力测试集

后续可扩展方向：

- 更细的回答评分标准
- 按故障类型拆分的 prompt 变体
- 便于横向对比的基准对话集
- 用于 prompt 回归评审的检查清单

## 当前状态

当前仓库已经具备一套较完整的 Kubernetes 排障 skill 设计包，适合做 prompt 评审、行为测试、质量对比和后续迭代。它仍然保持为纯 skill 设计，不包含任何运行时集成能力。
