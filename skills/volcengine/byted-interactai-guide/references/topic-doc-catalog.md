# AI 音视频互动精确文档路由

**Domain**: product-capability

本表把常见意图路由到标题明确的专题文档，表内不记录产品事实。先用 `list_query` 定位当前
索引中的 `documents[].id`，确认标题与 `expected_title` 一致后再定向 fetch。网页 URL 的数字
ID 不能作为 CLI `doc-id`。

| 主题 | 触发词示例 | list_query | expected_title |
|---|---|---|---|
| 产品简介 | 方案介绍、是否支持 | `AI 音视频互动方案 产品简介` | `产品简介` |
| 发版说明 | 最近变化、新增能力 | `AI 音视频互动方案 发版说明` | `发版说明` |
| 当前计费 | Token 计费、智能体计费 | `AI 音视频互动方案 计费` | 当前方案计费文档 |
| StartVoiceChat | 开启 AI 对话、2025-06-01 | `StartVoiceChat` | 当前版本 `StartVoiceChat` |
| ASR | 语音识别、识别配置 | `配置语音识别 ASR` | `配置语音识别 ASR` |
| LLM | 大模型、SystemMessages | `配置大模型 LLM` | `配置大模型 LLM` |
| TTS | 语音合成、音色、语速 | `配置语音合成 TTS` | `配置语音合成 TTS` |
| 视觉理解 | 图片理解、视频理解 | `视觉理解` | 视觉理解专题 |
| 字幕 | 实时字幕、对话记录 | `字幕` | 字幕专题 |
| 上下文 | 短期记忆、历史轮数 | `上下文管理` | `上下文管理（短期记忆）` |
| 打断 | 允许打断、禁止打断 | `打断 AI` | 打断专题 |
| 判停 | VAD、语义断句 | `判停` | 判停专题 |
| Function Calling | 函数调用、工具调用 | `Function Calling` | Function Calling 专题 |
| MCP | MCP 工具、MCP 服务 | `配置 MCP` | MCP 专题 |
| RAG | 知识库、检索增强 | `接入知识库 RAG` | `接入知识库 RAG` |
| 第三方模型 | 自定义模型、第三方 Agent | `接入第三方大模型或 Agent` | `接入第三方大模型或 Agent` |
| 端到端模型 | 实时语音大模型 | `接入端到端实时语音大模型` | `接入端到端实时语音大模型` |
| 文本提问 | 文字提问、TextQuestion | `文本提问` | 文本提问专题 |
| 自定义播报 | 指定文本播报、CustomSpeech | `自定义文本播报` | 自定义文本播报专题 |
| 自定义指令 | 发送指令、CustomCommand | `自定义指令` | 自定义指令专题 |
| AI 状态 | 智能体状态、任务状态 | `AI 状态` | AI 状态专题 |
| 任务事件 | 回调事件、任务报错 | `任务事件` | 任务事件专题 |
| 错误 | 错误码、报错信息 | `AI 音视频互动 错误码` | AI 音视频互动错误专题 |

查询示例：

```bash
vertc docs list --query "StartVoiceChat" --limit 10 --format json
vertc docs fetch <documents[].id> --match "StartVoiceChat" --match "2025-06-01" --match "目标字段" --format json
```

AibotCreate/AibotUpdate 配置请求也使用 StartVoiceChat 路由：先验证统一核心配置，再由
`voice-agent-config-output.md` 生成创建结构或更新 patch。该流程无需读取两者的接口文档。

标题没有唯一精确匹配时，按 [documentation-retrieval.md](documentation-retrieval.md) 执行一次
`search → fetch`，并使用返回的 ID。专题文档较长时，用 `--match` 返回相关完整章节。用户明确
要求全文，或 matched excerpt 无法回答时，再读取全文。
