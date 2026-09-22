# 智能体运行框架示例

[English](agent-harness.md)

这是用于演示 Birdview 的概念架构，不是 Birdview 实现或某个具体编码 Agent 的地图。示例中所有 `src/` 归属路径仅供说明。supported 状态表示作者编写的示例设计，不表示检查过生产代码。没有连接实时执行。

工作台向会话控制发送目标。调度器分派智能体循环，循环通过模型网关请求组合后的上下文。上下文可复用缓存摘要。模型响应可能包含文本或工具动作请求。

策略检查控制工具执行，并可通过审阅界面请求人工批准。获批调用进入隔离工作区或 MCP 服务。工具结果返回循环，差异和验证输出送到审阅界面。循环持久化事件和检查点，用于会话恢复和进度展示。审阅反馈可能修订目标。这些箭头描述逻辑交互，不表示必须同步调用，也不保证安全隔离。

三个分组区分交互、运行职责及外部执行/服务，不声明部署或信任边界。

示例有意包含扇出、返回路径、审批往返、缓存与持久化存储，以及跨组长连接。名称、职责和关系说明提供中文与英文。

## DeepSeek Harness 约束

以下六条规则于 2026-09-17 对照本地无修改的 DeepSeek Harness 检出版本 `7a0b7682b6690f0aa2d93438c4d526b38ab45777` 核验。来源为 DeepSeek AI 采用 MIT 许可证的 [AGENTS.md](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md) 与 [docs/defensive-patterns.md](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/docs/defensive-patterns.md)。这些是真实来源规则在概念图上的投影，不是已核验的 DeepSeek Harness 实现地图。时间线、实施方案与验证结果仍为模拟。这是选取的规则集，不是目录级指令的完整审计。

- **释放必须等待工作结束**（[defensive-patterns.md:19-21](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/docs/defensive-patterns.md#L19-L21)）：仅发出取消请求不够；异步清理必须等待子工作退出，并在终止前关闭通知注册表。
- **只报告实际执行的检查**（[AGENTS.md:90-96](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md#L90-L96)）：针对改动面运行相关检查，只报告执行过的命令；完整覆盖与平台矩阵由 CI 负责。
- **接口变更同步所有消费者**（[AGENTS.md:7](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md#L7)）：公开 API 尚未稳定，变更时更新所有消费者；这不是一律保持向后兼容的要求。
- **部署可变参数必须配置化**（[AGENTS.md:116](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md#L116)）：使用经过校验且可通过 `cordis.yml` 调整的 `Config` 字段；默认常量与测试钩子不等于可配置。协议常量、外部规范与安全不变量保持固定。
- **模型可见输入必须可由日志重建**（[AGENTS.md:111](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md#L111)）：模型请求必须能从会话日志重建，新增模型可见输入必须有会话事件。
- **通过插件扩展行为**（[AGENTS.md:112](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md#L112)）：新增行为使用已有文档定义的扩展点；修改 `agent-loop` 时还须更新 `docs/architecture.md`。

地图的检查路径指向这份本地来源摘要及其译文。上游检查仅覆盖上述两个文件，未检查包级指令及实现遵守情况。模块关联与建议验证方式是 Birdview 编写的投影，不是额外的上游要求。
