# 视频识别字幕（OCR）

## 能力描述
识别视频画面中的字幕/文字内容，输出带时间戳的字幕片段。
支持格式：主流视频格式如 mp4、flv、ts、avi、mov、wmv、mkv。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `video-ocr` |
| 是否异步 | `是` |
| 是否支持 local | `否` |
| 模式说明 | cloud only；可通过 `--cloud` 强制当前调用 |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token` |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_url | `--video-url` | string | 是 | - | 输入视频 Url（需公网可访问） |
| mode | `--mode` | string | 否 | Subtitle | 工作模式（Subtitle: 识别字幕文本；Detailed: 识别更详细文本信息） |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video video-ocr \
  --video-url https://example.com/video_url \
  --mode Subtitle \
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

- 当前命令：`mediakit-cli video video-ocr`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
