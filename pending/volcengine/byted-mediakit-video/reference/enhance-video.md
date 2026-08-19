# 画质增强

## 能力描述
画质增强：针对 AIGC / UGC / 短剧 / 教育 / 游戏 / 老片修复等场景，提供画质提升 + 超分增强一站式解决方案。依托 AI MediaKit 智能媒体处理引擎，融合视频内容理解、画质指标智能决策、多维度增强原子算法，实现画质的全面优化。
支持格式：主流视频格式如mp4、flv、ts、avi、mov、wmv、mkv。
使用限制：单文件大小不超过100G。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `enhance-video` |
| 是否异步 | `是` |
| 是否支持 local | `否` |
| 模式说明 | cloud only；可通过 `--cloud` 强制当前调用。 |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token`。 |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_url | `--video-url` | string | 是 | - | 输入视频。String 类型，支持http://xxx或https://xxx格式 URL |
| scene | `--scene` | string | 否 | common | 场景化模板类型。用于选择一个针对特定业务场景的预设画质增强模板。支持的取值如下：common（默认值）: 通用模板；ugc: UGC 短视频；short_series: 短剧；aigc: AIGC 内容；old_film: 老片修复 |
| tool_version | `--tool-version` | string | 否 | standard | 工具版本，标准版:standard，专业版：professional，默认为标准版 |
| resolution | `--resolution` | string | 否 | - | 目标分辨率。支持的取值如下所示。配置此参数后，不可同时配置resolution_limit字段 |
| resolution_limit | `--resolution-limit` | integer | 否 | - | 目标长宽限制，用于指定输出视频的长边或短边的最大像素值，取值范围为 [64, 2160]。配置此参数后，不可同时配置resolution字段 |
| fps | `--fps` | number | 否 | - | 目标帧率，单位为 fps。取值范围为 (0, 120]。 |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video enhance-video \
  --video-url https://example.com/video_url \
  --scene common \
  --tool-version standard \
  --resolution 240p \
  --resolution-limit 1 \
  --fps 1.0 \
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

- 当前命令：`mediakit-cli video enhance-video`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
