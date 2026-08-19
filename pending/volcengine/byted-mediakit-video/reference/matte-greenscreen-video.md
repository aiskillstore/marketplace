# 视频绿幕抠图

## 能力描述
对以绿幕或纯色为背景的视频进行抠图，自动识别主体（人物、物品、动物等），同时移除背景，生成背景透明的视频。
输出视频格式为 WEBM（默认）或 MOV，分辨率与原片对齐。
支持的格式：主流视频格式如 mp4、flv、ts、avi、mov、mkv、wmv。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `matte-greenscreen-video` |
| 是否异步 | `是` |
| 是否支持 local | `是` |
| 模式说明 | 支持 local / cloud；可通过 `--local` 或 `--cloud` 覆盖当前命令。本地模式使用 ProRes 4444 MOV 透明输出，仅支持 `--format MOV`，WEBM 请使用 cloud |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token` |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_url | `--video-url` | string | 是 | - | 输入视频 Url（需公网可访问） |
| format | `--format` | string | 否 | WEBM | 输出视频格式：MOV / WEBM（默认） |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video matte-greenscreen-video \
  --video-url https://example.com/video_url \
  --format WEBM \
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

- 当前命令：`mediakit-cli video matte-greenscreen-video`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
