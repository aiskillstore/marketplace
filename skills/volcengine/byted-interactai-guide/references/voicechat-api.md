# VoiceChat OpenAPI 摘要（官方链接优先）

**Domain**: voice-agent

VoiceChat OpenAPI 变化较快，本文**只保留最小必要摘要**，字段与取值以火山官方文档为准，
不在此固化易变全文，也不臆造错误码。运行时对话链路排障见
`references/voice-agent-runtime.md`。

## 官方文档（权威来源）

- 产品边界：[AI 音视频互动方案产品简介](https://www.volcengine.com/docs/6348/1310537)
- 当前方案 API：[StartVoiceChat（2025-06-01）](https://www.volcengine.com/docs/6348/2123348)、
  [UpdateVoiceChat](https://www.volcengine.com/docs/6348/2123350)、
  [StopVoiceChat](https://www.volcengine.com/docs/6348/2123349)
- 运行态证据：[事件和错误码](https://www.volcengine.com/docs/6348/1928198)、
  [获取 AI 对话任务事件](https://www.volcengine.com/docs/6348/1798101)

> 维护约定：本文条目应携带来源与时效标记（`source_url` / `source_version` /
> `verified_at` 或等价可信状态）。稳定行为可本地摘要；快变字段以官方链接为准。

## 三个核心动作（必要字段摘要）

| 动作 | 用途 | 关键输入（以官方为准） | 关键输出 |
|------|------|------------------------|----------|
| `StartVoiceChat` | 下发一个对话任务 | `TaskId`、房间/用户标识、Agent 与 VoiceChat 配置 | `Result=ok`（仅表示下发成功） |
| `UpdateVoiceChat` | 对运行中的任务重新下发配置 | `TaskId` + 更新后的配置 | `Result=ok` 或官方定义的错误 |
| `StopVoiceChat` | 结束任务，Agent 离房 | `TaskId` | `Result=ok` 或官方定义的错误 |

- **TaskId**：由调用方在 `StartVoiceChat` 请求中提供；同一 `AppId` + `RoomId` 下必须唯一，
  后续 `Update`/`Stop` 使用同一标识定位任务。它本身不是接口成功或 Agent 已进房的证据。
- **同步返回**：当前接口没有特有返回参数，成功时 `Result=ok`。HTTP 200 仅表示任务下发成功；
  任务是否启动、Agent 是否进房及运行阶段需继续查看 VoiceChat 回调、AI 状态或房间事件。
- **房间/用户绑定**：Start 使用的房间与目标用户须与前端进房参数一致，否则
  Agent 会「进错房/对错人」——排障见 `references/voice-agent-runtime.md` 与
  `references/integration-flow.md`。
- **ASR/LLM/TTS 配置**：位于场景配置（如服务端场景 JSON），具体字段随官方文档演进，
  本文不复制其全文。

## 鉴权

- 服务端管理模式：配套 Server 用 Signin STS（`vertc auth login` 获取）或长期 AK/SK
  调用 OpenAPI。
- 鉴权失败（签名不匹配 / AccessKey 无效）先 `vertc auth login` 重新登录后重试；
  错误码用 `vertc explain-error <code>` 反查。鉴权/签名泛化条目若标记为
  `curated-seed`，应以官方返回和文档为准。

## 与 CLI 的关系

- 快速路径由 `vertc dev` 启动配套 Web 与 Server，Server 负责 VoiceChat 调用。
- 旧版 CLI 管理工程可用内部命令 `vertc agent start` / `vertc agent stop`
  （内部/legacy 路径）。
