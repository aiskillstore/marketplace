# 高光片段提取

## 能力描述
智能捕捉视频"情绪波峰"与"关键动作"，输出精准时间戳、高光打分、OCR 文本和画面描述等元数据，供下游进行更灵活的二次开发。
支持短剧（Miniseries）和小游戏（Game）两种分析模型。
使用限制：单次最多 100 个视频，累计时长不超过 300 分钟。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `analyze-video-highlights` |
| 是否异步 | `是` |
| 是否支持 local | `否` |
| 模式说明 | cloud only；可通过 `--cloud` 强制当前调用 |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token` |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_urls | `--video-urls` | array<string> | 是 | - | 输入视频列表。待处理的视频 URL 列表，支持 1-100 个视频。子项说明：视频 URL，CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值。 CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值 |
| model | `--model` | string | 是 | - | 分析场景模型，Miniseries（短剧）或 Game（小游戏） |
| mode | `--mode` | string | 是 | - | 高光提取模式。固定组合为：model=Miniseries 时 mode 只能传 StorylineCuts；model=Game 时 mode 只能传 HighlightExtract |
| minigame_info | `--minigame-info` | object | 否 | - | 小游戏描述信息，当 model=Game 时可选填，可辅助模型更精准识别高光内容。CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值 |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video analyze-video-highlights \
  --video-urls '["https://example.com/video_url"]' \
  --model Miniseries \
  --mode StorylineCuts \
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

- 当前命令：`mediakit-cli video analyze-video-highlights`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
