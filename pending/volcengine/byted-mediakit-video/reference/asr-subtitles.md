# 语音转字幕（ASR）

## 能力描述
对输入视频或音频进行语音识别，输出带时间戳的字幕片段。
支持格式：主流音视频格式（如mp4、mov、mp3、m4a、wav等）。
输入：video_url和audio_url二选一。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `asr-subtitles` |
| 是否异步 | `是` |
| 是否支持 local | `否` |
| 模式说明 | cloud only；可通过 `--cloud` 强制当前调用 |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token` |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_url | `--video-url` | string | 否 | - | 输入视频 Url（需公网可访问），与audio_url二选一，都存在时优先取video_url |
| audio_url | `--audio-url` | string | 否 | - | 输入音频 Url（需公网可访问），与video_url二选一，不能都为空 |
| content_type | `--content-type` | string | 否 | - | 识别类型，默认值为空，算法会自动探测类型，speech: 对话，singing: 歌唱 |
| language | `--language` | string | 否 | - | 识别提示语言 ID（默认值为空，算法会自动探测语种）。简体中文：cmn-Hans-CN；英语：eng-US |
| enable_speaker_info | `--enable-speaker-info` | boolean | 否 | false | 是否开启说话人识别 |
| enable_confidence | `--enable-confidence` | boolean | 否 | false | 是否返回置信度 |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video asr-subtitles \
  --video-url https://example.com/video_url \
  --content-type speech \
  --language cmn-Hans-CN \
  --enable-speaker-info \
  --enable-confidence \
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

- 当前命令：`mediakit-cli video asr-subtitles`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
