# 剧情故事线分析

## 能力描述
智能解析影视剧内容，生成结构化剧情线，供智能剪辑、内容检索与互动播放等场景使用。
基于大模型视频理解能力，对输入的单个或多个长视频（如电影、电视剧）进行分析，提取并组织成一份完整的故事线。
该故事线由一系列按时间顺序排列的剧情片段（Clips）和基于片段聚合的高光故事线（Highlights）组成。
使用限制：单次最多 30 个视频，单个视频时长不超过 2.5 小时。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `analyze-video-storyline` |
| 是否异步 | `是` |
| 是否支持 local | `否` |
| 模式说明 | cloud only；可通过 `--cloud` 强制当前调用 |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token` |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_urls | `--video-urls` | array<string> | 是 | - | 输入视频列表。待处理的视频 URL 列表，支持 ，最多 30 个视频。子项说明：视频 URL，CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值。 CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值 |
| enable_snapshot | `--enable-snapshot` | boolean | 否 | false | 是否为每个剧情片段生成关键帧快照。默认为 false。开启后，结果中将包含 clip_snapshot_url 字段 |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video analyze-video-storyline \
  --video-urls '["https://example.com/video_url"]' \
  --enable-snapshot \
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

- 当前命令：`mediakit-cli video analyze-video-storyline`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
