# 集成诊断完整阶段与深挖路由

**Domain**: integration

先读 `references/integration-flow.md`。请求涉及全链路、跨域归因、具体阶段检查或较长的错误映射时，
再读本文。单个事件的证据边界由 `integration-flow.md` 直接处理。

## 完整阶段模型

```text
鉴权 → Demo 配置 → Web SDK 初始化 → 用户进房 → 麦克风采集与发布
→ StartVoiceChat 下发 → 任务初始化 → Agent 进房 → Agent 订阅用户音频
→ ASR/VAD → LLM → TTS / Agent 音频发布
→ 用户收到远端音频 → 用户播放并可听
```

| 阶段 | domain | 充分成功证据 |
|---|---|---|
| 鉴权 | auth | 有效且未过期的 Signin STS |
| Demo 配置 | integration | 场景配置语义校验通过 |
| Web SDK 初始化 | web-sdk | Engine 就绪回调 |
| 用户进房 | web-sdk | join 成功回调 |
| 麦克风采集与发布 | web-sdk | 发布成功回调；服务端用户 ASR 结果可作发布的因果证据 |
| StartVoiceChat 下发 | voice-agent | OpenAPI `Result=ok`；或适配层成功 envelope 且无 typed error |
| 任务初始化 | voice-agent | `taskStart`；Agent 进房或任一下游运行态事实也可反向确认 |
| Agent 进房 | voice-agent | 房间成员或 AI 状态明确出现 Agent |
| Agent 订阅用户音频 | integration | 目标用户订阅/收音事件，或 Agent 侧目标远端音量大于 0 |
| ASR/VAD | voice-agent | 对应 ASR/断句事件；开始说话不等于识别完成 |
| LLM | voice-agent | `llmOutput` 或明确的模型输出事件 |
| TTS / Agent 音频发布 | voice-agent / integration | `answerStart`、TTS 产帧或 Agent 发布成功，按来源归域 |
| 用户收到远端音频 | web-sdk | 订阅端收到并解码远端音频首帧，或目标远端音量大于 0 |
| 用户播放并可听 | web-sdk | 播放成功/出声事实或用户确认听到 |

`StartVoiceChat` 同步成功表示请求已下发。缺少未配置的 `taskStart` 回调不构成失败；
Agent 进房或任一下游对话事件可反向确认任务已初始化。

## VoiceChat 事件与错误映射

官方 VoiceChat 回调中，`EventType=1` 表示错误：

- `RunStage=preParamCheck` → 任务初始化；
- `RunStage=asr` → ASR/VAD；
- `RunStage=llm` → LLM；
- `RunStage=tts` → TTS。

正向阶段事件包括 `taskStart`、`asrFinish`、`llmOutput`、`answerStart`、`answerFinish`；
`beginAsking` 只表示用户开始说话，不能当识别完成。

错误定位先看显式 `source/stage/errorCode`。注册错误码或明确错误族
`ASR`、`LLM/MODEL`、`TTS`、`AUTH`、`JOIN/RTC` 可用于阶段归类；精确含义和修复采用
`vertc explain-error` 返回的 `source/verified/meaning/fix`。无来源的 `timeout` 保持
`domain=unknown,first_failure=null`。负数码调用时把 `--format json` 放在前面，在
`explain-error` 后用参数终止符 `--` 再传负数，避免被解析为 flag。

## 深挖路由

| 首个失败或缺证据阶段 | 下一份 reference / 最小方向 | 验证 |
|---|---|---|
| 鉴权 | 重新登录；通用就绪检查用 `vertc doctor` | STS 有效 |
| Demo 配置 | 配置语义见 `references/voice-agent-config.md` | 目标配置校验通过 |
| Web SDK 初始化 / 用户进房 | `references/web-sdk-diagnosis.md` | Engine / join 成功回调 |
| 麦克风采集与发布 | 授予权限、确认本地音轨与发布 | 发布成功回调 |
| StartVoiceChat / 任务初始化 | `references/voice-agent-runtime.md` | 下发成功后出现任务或更强下游事实 |
| Agent 进房 / 目标绑定 | 对齐房间、Agent 与 Target UID | Agent 在正确房间面向正确用户 |
| Agent 订阅用户音频 | 开启目标用户的 Agent 侧订阅/远端音量日志 | 目标 UID 音量大于 0 或明确收音 |
| ASR/VAD | 核对 ASR 配置与错误事件 | 新的识别结果到达 |
| LLM | 核对模型开通、配置和模型错误事件 | 明确模型文本输出 |
| TTS / Agent 音频发布 | 核对 TTS 错误；音色问题交配置能力验证兼容组合 | 远端音频首帧到达 |
| 用户收到音频但不可听 | `references/web-sdk-diagnosis.md`，检查自动播放、输出设备和播放音量 | 播放成功或用户实际听到 |

常见边界：Token 无效导致进房失败归 `web-sdk:用户进房`；纯 Web SDK 远端音频无法播放归
`web-sdk:用户播放并可听`。TTS 音色不兼容时，先核对音色、`ResourceId`、`Provider` 的兼容关系；
没有已验证的替代值时不生成 patch。

## 权威来源与时效

- VoiceChat：[事件和错误码](https://www.volcengine.com/docs/6348/1928198)、
  [获取 AI 对话任务事件](https://www.volcengine.com/docs/6348/1798101)
- 远端音量：官方 RTC「音频音量」（`vertc docs` id `6a79684f4bdbc784e3895ac1`）
- Web SDK：[实现音视频通话](https://www.volcengine.com/docs/6348/106914)

上述 VoiceChat 事件和远端音量正文已于 **2026-08-18** 通过
`vertc docs search → fetch` 核验；快变事件名仍以当前官方正文为准。
