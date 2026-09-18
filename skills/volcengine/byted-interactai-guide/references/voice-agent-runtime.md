# Voice Agent 运行时域 — VoiceChat 生命周期与对话链路

**Domain**: voice-agent

本文覆盖对话式 AI 的运行态：VoiceChat 任务生命周期、Agent 进房、目标绑定、
ASR/VAD/LLM/TTS 链路与字幕事件。RTC 媒体侧问题（进房/采集/发布/订阅/播放）不在
本文，见 `references/web-sdk-diagnosis.md`；跨域顺序见
`references/integration-flow.md`。VoiceChat OpenAPI 字段见 `references/voicechat-api.md`。

## 诊断合同

九字段输出、证据强度、标准观察、会话边界与首个故障算法见
`references/integration-flow.md`。本文记录 `voice-agent` 域各阶段的证据和处理动作。错误码用
`vertc explain-error <code>` 查询含义与修复建议。

> **错误码可信状态提醒**：`vertc explain-error` 会为每个条目返回 `source` 和
> `verified`。VoiceChat 对话运行态与 RTC OpenAPI 公共错误码已经过官方文档核验；
> 鉴权/签名类泛化条目为 `curated-seed`，应以官方返回和文档为准。

## 对话链路阶段（本域）

| 阶段 | 关键可观察证据 | 成功判定 |
|------|----------------|----------|
| StartVoiceChat 下发 | 直接 OpenAPI 返回；或 CLI/配套 Server 的成功 envelope 与 typed error | 直接调用为 `Result=ok`；适配层调用为成功状态且无错误。两者都仅表示任务下发成功 |
| 任务初始化 | 已配置的 VoiceChat 回调、AI 状态、Agent 进房或下游事件 | `taskStart` 或任一更强运行态证据；未配置/未收到回调不能单独判失败，显式错误事件则判失败 |
| Agent 进房 | 房间内出现 Agent 这一远端参与者 | Agent 已加入房间 |
| 目标绑定 | Target UID 与用户 User ID 是否一致 | Agent 面向正确用户 |
| ASR/VAD | 识别/断句事件、字幕增量 | 产生识别结果 |
| LLM | 对话事件、服务端返回 | LLM 返回文本 |
| TTS | 合成事件/错误、音频帧产生 | 生成音频 |
| 生命周期 | UpdateVoiceChat / StopVoiceChat 结果、Task 状态 | 任务状态符合预期 |

## 分阶段排查

### 1. StartVoiceChat 下发失败

- **证据**：直接 OpenAPI 调用返回错误或未返回 `Result=ok`；CLI/配套 Server 返回失败
  envelope、typed error 或非成功状态；服务端日志。
- **适配层说明**：CLI/配套 Server 成功响应中的 `task_id` 是调用方 `TaskId` 的回显，只有与
  成功 envelope/无错误状态一起出现时才构成下发证据；它不是 OpenAPI 生成的返回值。
- **常见方向**：鉴权（Signin STS/AK-SK）、必填参数缺失、参数不合法。
- **action**：核对鉴权（`vertc auth login` 重新登录）与场景配置；错误码用
  `vertc explain-error <code>` 反查（注意可信状态）；配置问题 `vertc doctor` 只读定位。
- **结论范式**：`first_failure=StartVoiceChat`、`evidence=OpenAPI 错误码`。

### 2. 下发成功后的任务初始化与 Agent 进房

- **已配置 VoiceChat 回调**：`taskStart` 是任务初始化成功证据；若收到
  `preParamCheck` 等错误事件，使用 `first_failure=任务初始化`，不要归为 Agent 进房失败。
- **未配置或未收到回调**：缺少 `taskStart` 只表示该观测不可用，不能单独判失败。继续检查
  AI 状态、Agent 参与者和 ASR/LLM/TTS 等下游事件；任一更强的运行态证据都可反向确认任务已启动。
- **Agent 进房证据**：房间中出现 Agent 参与者。任务已启动但始终没有 Agent 时，才使用
  `first_failure=Agent 进房`。
- **action**：核对 StartVoiceChat 的房间/用户参数与前端一致，并按当前实际启用的回调、
  AI 状态和房间事件取证；不要要求用户提供未配置的回调。

### 3. 目标绑定错误（Agent 进房但对错人说话）

- **证据**：Agent 已进房，但 Target UID 与实际用户 User ID 不一致。
- **action**：对齐 Agent 目标用户与前端用户 User ID。`vertc doctor` 校验的是配置里
  `agent.target_user_id` 与 `rtc.user_id` 是否一致；运行态 Target UID 需人工核对（查 StartVoiceChat 入参）。

### 4. Agent 已订阅用户音频但 ASR 无结果

- **证据**：无识别事件/字幕增量。
- **常见方向**：用户未真正发布音频（属 `web-sdk` 域，先按 web-sdk 排查）、ASR 配置/鉴权、
  静音或音量过低。
- **action**：先确认用户端已发布音频（见 web-sdk 域）；再核对 ASR 配置与鉴权。
- **结论范式**：`last_success=Agent 订阅用户音频`、`first_failure=ASR/VAD`。

### 5. LLM 无返回

- **证据**：有识别结果但无对话返回；服务端/模型端点日志。
- **常见方向**：模型端点未开通/不可用、配置错误。
- **action**：确认所选模型已开通、场景配置正确；错误码 `vertc explain-error <code>`。

### 6. LLM 有结果但 TTS 或播放失败

- **证据**：有对话文本但无音频。
- **判别**：若 TTS 合成事件报错/缺失 → `first_failure=TTS`（本域，如音色/参数不支持）；
  若 TTS 已产音频但用户听不到 → 属播放问题，转 `web-sdk` 域（订阅/自动播放限制）。
- **action**：TTS 侧更换音色/参数并重试；播放侧见 `references/web-sdk-diagnosis.md`。

### 7. 有声音但无字幕

- **证据**：能听到 Agent 但字幕缺失。
- **action**：核对字幕/对话事件配置与前端字幕渲染日志。

## 生命周期

- **StartVoiceChat**：调用方提供 `TaskId` 并下发对话任务。直接 OpenAPI 同步成功返回
  `Result=ok`；CLI/配套 Server 返回自己的成功 envelope 并回显 `task_id`。运行状态继续通过
  已启用的异步事件、AI 状态或房间/下游证据确认。
- **UpdateVoiceChat**：对运行中的任务重新下发（编辑后的）配置。
- **StopVoiceChat**：结束任务、Agent 离房。
- 服务端管理模式下由配套 Server 编排；旧版 CLI 管理工程可用内部命令
  `vertc agent start` / `vertc agent stop`（内部/legacy 路径，非默认快速路径）。

## 验收场景（本域）

- **StartVoiceChat 失败** → `first_failure=StartVoiceChat`。
- **下发成功后收到异步初始化错误** → `last_success=StartVoiceChat 下发`、`first_failure=任务初始化`。
- **任务已启动但 Agent 未进房** → `last_success=任务初始化`、`first_failure=Agent 进房`。
- **未配置任务回调但 Agent 已进房** → 回调记为「未观测」，继续后续阶段，不得判失败。
- **Agent 已进房但 ASR 无结果** → `last_success=Agent 订阅用户音频`、`first_failure=ASR/VAD`。
- **LLM 有结果但 TTS 失败** → `first_failure=TTS`（播放失败则转 web-sdk 域）。

## 权威来源

- VoiceChat OpenAPI：[StartVoiceChat（2025-06-01）](https://www.volcengine.com/docs/6348/2123348)、
  [UpdateVoiceChat](https://www.volcengine.com/docs/6348/2123350)、
  [StopVoiceChat](https://www.volcengine.com/docs/6348/2123349)
- 运行态证据：[事件和错误码](https://www.volcengine.com/docs/6348/1928198)、
  [获取 AI 对话任务事件](https://www.volcengine.com/docs/6348/1798101)
- 错误码反查：`vertc explain-error <code>`；根据输出中的 `source` 和 `verified`
  判断可信状态，`curated-seed` 条目以官方文档为准。
