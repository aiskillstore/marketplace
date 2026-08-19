# 生成式画质增强

## 能力描述
生成式视频增强修复（generative_video_restoration）是基于扩散大模型（Diffusion-based Large Model）的生成式视频修复技术。不仅可以还原被破坏的像素，更借助大规模预训练积累的丰富视觉先验，主动补全细节、理解语义，生成真实、自然、高保真的视频内容。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `enhance-video-generative` |
| 是否异步 | `是` |
| 是否支持 local | `否` |
| 模式说明 | cloud only；可通过 `--cloud` 强制当前调用 |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token` |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_url | `--video-url` | string | 是 | - | 输入视频。String 类型，支持http://xxx或https://xxx格式 URL |
| resolution | `--resolution` | string | 否 | 720p | 目标分辨率。支持的取值：720p / 1080p |
| bitrate_level | `--bitrate-level` | string | 否 | medium | 码率档位。输出视频的目标平均码率。取值：low（低码率）/ medium（中码率，推荐）/ high（高码率）。默认为 medium |
| fps | `--fps` | number | 否 | - | 目标帧率，单位为 fps。若未指定，输出视频将保持与原始片源一致的帧率。取值范围为 [15, 120]，建议不超过原片的 4 倍 |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video enhance-video-generative \
  --video-url https://example.com/video_url \
  --resolution 720p \
  --bitrate-level medium \
  --fps 30 \
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

- 当前命令：`mediakit-cli video enhance-video-generative`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
