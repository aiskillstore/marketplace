# 语音端点识别

## 能力用途

用于语音端点识别。自动定位音频或视频文件中有效语音的起止时间。将人声和静音、背景噪声等无效片段区分开来。返回包含所有有效人声片段起止时间戳的列表。

## 参数填写规则

- 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli audio detect-voice-activity`
- 生命周期：异步
- 返回方式：返回 `task_id`，再查询终态结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `audio_url` | `--audio-url` | string | 否 | - | - | audio_url 为待处理的音频 URL，是条件必填项；支持公网可访问的 http/https 直链或 mediakit/tos/vod 平台资源链接；audio_url 与 video_url 二选一，必须且只能提供其中一个。支持 mp3、m4a、wav、wma、amr、aac、ogg、flac 等主流音频格式。 |
| `callback_args` | `--callback-args` | string | 否 | - | - | 自定义回调参数。任务完成时，您提供的内容会通过事件回调原样返回，便于关联业务；字段长度最大为 512 字节。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `callback_url` | `--callback-url` | string | 否 | - | - | 用于接收该任务结果回调的 URL 地址。提供此参数时，其优先级高于全局回调地址；地址必须以 http:// 或 https:// 开头。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `client_token` | `--client-token` | string | 否 | - | - | 用户请求凭证，用于幂等控制。大小写敏感，不超过 64 个 ASCII 码可打印字符。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `video_url` | `--video-url` | string | 否 | - | - | video_url 为待处理的视频 URL，是条件必填项；支持公网可访问的 http/https 直链或 mediakit/tos/vod 平台资源链接；video_url 与 audio_url 二选一，必须且只能提供其中一个。支持 mp4、flv、ts、avi、mov、wmv、mkv 等主流视频格式。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli audio detect-voice-activity \
  --video-url <video_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `request_id` | string | 否 | Cloud | 请求标识；仅在后端返回时出现。 |
| `task_id` | string | 是 | Cloud | 异步任务的唯一标识，用于查询任务状态并获取最终结果。 |
| `task_type` | string | 否 | Cloud | 任务类型；仅在后端实际返回非空值时出现。 |
| `result.duration` | number | 否 | Cloud 终态 | 输入媒体文件的总时长，单位为秒。 |
| `result.segment_count` | integer | 否 | Cloud 终态 | 检测到的人声片段数量；未检测到人声片段时为 0。 |
| `result.voice_segments` | array<object> | 否 | Cloud 终态 | 有效人声片段列表；未检测到有效人声时返回空数组。 |
| `result.voice_segments[].end_time` | number | 否 | Cloud 终态 | 片段结束时间，单位为秒，精确到小数点后两位。 |
| `result.voice_segments[].start_time` | number | 否 | Cloud 终态 | 片段开始时间，单位为秒，精确到小数点后两位。 |

Cloud 调用成功后读取 `task_id`，再查询终态结果：

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli shared query-task --task-id <task_id> --poll-complete
```

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli audio detect-voice-activity --help
mediakit-cli audio detect-voice-activity --schema
```
