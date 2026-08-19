# 高光智剪-小游戏

## 能力描述
识别小游戏录屏视频中的核心玩法与高光事件（如连击、通关、极限操作等），
快速生成用于买量的视频素材。支持提供游戏名称、玩法描述、高光定义以辅助模型更精准识别。
使用限制：本期仅支持单视频输入。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `generate-highlights-minigame` |
| 是否异步 | `是` |
| 是否支持 local | `否` |
| 模式说明 | cloud only；可通过 `--cloud` 强制当前调用 |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token` |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_urls | `--video-urls` | array<string> | 是 | - | 输入视频列表。 CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值 |
| mode | `--mode` | string | 否 | HighlightExtract | 高光提取模式，本期支持 HighlightExtract |
| enable_generate_video | `--enable-generate-video` | boolean | 否 | true | 是否生成混剪成片视频。true（默认）= 同时输出混剪视频与高光片段信息；false = 仅输出高光片段信息（clips），底层请求不携带 Edit 字段，也不会生成任何混剪视频 |
| minigame_info | `--minigame-info` | object | 否 | - | 小游戏描述信息，建议填写以辅助模型更精准识别高光内容。CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值 |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video generate-highlights-minigame \
  --video-urls '["https://example.com/video_url"]' \
  --mode HighlightExtract \
  --enable-generate-video \
  --minigame-info '{"game_name": "demo"}' \
  --callback-args sample-callback-args \
  --client-token demo-client-token
```

## 输出格式
```json
{
  "task_id": "task_demo_001",
  "request_id": "req_demo_001"
}
```

## 任务结果查询
提交成功后会返回 `task_id`，再执行 `mediakit-cli shared query-task --task-id <task_id>` 查询。

- 当前命令：`mediakit-cli video generate-highlights-minigame`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
