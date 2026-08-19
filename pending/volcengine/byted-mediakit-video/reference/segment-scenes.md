# 场景切分

## 能力描述
依据视频转场与画面变化自动切分场景，输出切片时间轴和（可选）切片文件。
支持格式：MP4、FLV、ASF、RM、RMVB、MPEG、MOV、AVI、MPEGTS、M4S、WMV、3GP、TS、MPG、WEBM、MKV、WM、MPE、VOB、DAT、MP4V、M4V、F4V、MXF、QT 等主流视频格式。
使用限制：单个视频时长不超过 2 小时。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `segment-scenes` |
| 是否异步 | `是` |
| 是否支持 local | `否` |
| 模式说明 | cloud only；可通过 `--cloud` 强制当前调用 |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token` |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_url | `--video-url` | string | 是 | - | 待处理视频 Url，必须是公网可直接访问的 HTTP/HTTPS 链接 |
| enable_clip_fade | `--enable-clip-fade` | boolean | 否 | false | 是否将检测到的淡入/淡出片段作为独立切片输出 |
| segment_threshold | `--segment-threshold` | number | 否 | - | 场景切分敏感度阈值，范围 [0, 100)，100 不可取。数值越低切得越细，参考经验值10 |
| min_duration | `--min-duration` | number | 否 | - | 单个切片最小时长（秒），参考经验值3，应小于等于max_duration |
| max_duration | `--max-duration` | number | 否 | - | 单个切片最大时长（秒），参考经验值30，应大于等于min_duration |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video segment-scenes \
  --video-url https://example.com/video_url \
  --enable-clip-fade \
  --segment-threshold 10 \
  --min-duration 3 \
  --max-duration 30 \
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

- 当前命令：`mediakit-cli video segment-scenes`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
