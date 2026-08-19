# 视频元信息获取

## 能力描述
对输入视频 Url（需公网可访问） 进行探测，输出标准化媒资元信息，覆盖容器层（format_meta）、视频流层（video_stream_meta）与音频流层（audio_stream_meta）。
字段分类参考 ffprobe，并对 VOD 原始返回做精简与统一，便于上层做分辨率/帧率/码率/编码等策略判断。
使用限制：仅支持公网 HTTP/HTTPS URL；输入视频分辨率最高支持 4K。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `probe-video-metadata` |
| 是否异步 | `是` |
| 是否支持 local | `是` |
| 模式说明 | 支持 local / cloud；可通过 `--local` 或 `--cloud` 覆盖当前命令 |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token` |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_url | `--video-url` | string | 是 | - | 输入视频。待探测的视频 |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video probe-video-metadata \
  --video-url https://example.com/video_url \
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

- 当前命令：`mediakit-cli video probe-video-metadata`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
