# 音频转码

## 能力用途

音频转码将一个音频码流转换为另一个音频码流，通常涉及编码格式、编码参数和封装格式的转换，用于适应不同业务场景、播放终端和网络环境。

## 参数填写规则

- 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli audio transcode-audio`
- 生命周期：异步
- 返回方式：返回 `task_id`，再查询终态结果。

### 使用指南

- 数组参数（`--metadata-keep-tags`）传多个值时用逗号分隔并整体加引号，例如 `--metadata-keep-tags "url1,url2"`。
- 单个值中的文件名或 URL 不能包含逗号（`,`），否则会被 CLI 当成多个元素拆开。遇到这种情况时，先向用户澄清，请其提供不含逗号的文件名或对应 URL 后再调用。
- 对象或对象数组参数（`--audio`、`--metadata-add-tags`）需传合法 JSON 字符串并整体加单引号，例如 `--audio '[{...}]'`；字段名与层级必须与上表“枚举/范围/结构”及子字段说明一致。
- 不要用逗号分隔或裸文本传该参数。

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli audio transcode-audio \
  --audio '[{...}]'
  --container-format <container_format> \
  --audio <audio>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `audio` | `--audio` | object | 是 | - | - | audio 提供音频参数配置。 |
| `audio.bitrate_kbps` | - | integer | 是 | 128 | 最小值: 10；最大值: 500 | bitrate_kbps 指定音频码率，单位为 Kbps，范围 10 至 500，默认值为 128；为空时，输出音频码率与原始音频保持一致。 |
| `audio.bitrate_mode` | - | string | 是 | "cbr" | 枚举: ["cbr","cae"] | bitrate_mode 指定音频码率控制模式，支持 cbr 和 cae，默认 cbr。cbr 是恒定码率模式，编码器会尝试让音频流每秒严格保持 bitrate_kbps 设定的码率，使文件大小可以被精确预测，适合带宽稳定性要求高的流式传输。cae 仅在 container_format 为 M4A 时支持，会根据音频内容复杂度动态调整瞬时码率，并确保整个文件平均码率接近 bitrate_kbps 目标值。 |
| `audio.channels` | - | integer | 否 | - | 枚举: [1,2] | channels 指定音频声道数，支持 1 和 2，默认 2；1 表示单声道，2 表示双声道。 |
| `audio.sample_rate` | - | integer | 是 | 48000 | 枚举: [8000,11025,12000,16000,22050,24000,32000,44100,48000,64000,88200,96000] | sample_rate 指定音频采样率，单位为 Hz，默认 48000。建议根据目标编码器填写：MP3 支持 8000、11025、12000、16000、22050、24000、32000、44100、48000；AAC 支持 8000、11025、12000、16000、22050、24000、32000、44100、48000、64000、88200、96000；Opus 支持 48000。 |
| `audio.volume_integrated_loudness` | - | number | 否 | -12 | 最小值: -70；最大值: -5 | volume_integrated_loudness 用于设定音频整体感知音量的目标综合响度，单位为 LUFS，范围 -70 至 -5，默认值为 -12。 |
| `audio.volume_loudness_range` | - | number | 否 | 7 | 最小值: 1；最大值: 20 | volume_loudness_range 调节音频最响亮和最安静部分之间的差异，单位为 LU，范围 1 至 20，默认值为 7；volume_method 为 2Pass 时生效。 |
| `audio.volume_method` | - | string | 否 | - | 枚举: ["2Pass"] | volume_method 是音量均衡算法开关；不设置时不处理音量。支持将 volume_method 设置为 2Pass 启用两阶段响度分析与处理，此时 volume_integrated_loudness、volume_true_peak 和 volume_loudness_range 生效。 |
| `audio.volume_true_peak` | - | number | 否 | 0 | 最小值: -9；最大值: 0 | volume_true_peak 设置音频信号的真实峰值最高上限，以防止削波失真，单位为 dBTP，范围 -9 至 0，默认值为 0。 |
| `audio_url` | `--audio-url` | string | 是 | - | - | audio_url 是待转码音频的 URL，支持公网 HTTP/HTTPS URL、本地文件路径、视频点播 vod:// 和对象存储 tos:// 四种输入协议；输入支持 mp3、m4a、wav、wma、amr、aac、ogg、flac 等音频格式。 |
| `callback_args` | `--callback-args` | string | 否 | - | - | 自定义回调参数。任务完成时，您提供的内容会通过事件回调原样返回，便于关联业务；字段长度最大为 512 字节。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `callback_url` | `--callback-url` | string | 否 | - | - | 用于接收该任务结果回调的 URL 地址。提供此参数时，其优先级高于全局回调地址；地址必须以 http:// 或 https:// 开头。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `client_token` | `--client-token` | string | 否 | - | - | 用户请求凭证，用于幂等控制。大小写敏感，不超过 64 个 ASCII 码可打印字符。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `container_format` | `--container-format` | string | 是 | "MP3" | 枚举: ["MP3","M4A","OGG"] | container_format 指定目标封装格式，建议填写，默认 MP3；系统根据封装格式自动选择对应编码器：MP3 封装格式使用 MP3 编码器，M4A 封装格式使用 AAC 编码器，OGG 封装格式使用 Opus 编码器。 |
| `media_output_destination` | `--media-output-destination` | string | 否 | - | - | 指定处理产物的目标存储位置。AI MediaKit 支持将处理产物存储至您的火山引擎视频点播（VOD）空间或对象存储（TOS）桶：存储至 VOD 时设为 vod://<您的空间名>；存储至 TOS 时设为 tos://<您的桶名>。设置后，任务结果中的 url 相关字段将返回 vod:// 或 tos:// 格式的资源地址，不再返回临时下载地址。首次使用前，需要按需授权 AI MediaKit 将文件写入您的 VOD 空间或 TOS 桶。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `metadata_add_tags` | `--metadata-add-tags` | array<object> | 否 | - | - | metadata_add_tags 指定为输出音频新增的元信息标签；新增标签与保留标签同名时，新增标签设置覆盖源文件的值。 |
| `metadata_add_tags[].key` | - | string | 否 | - | - | 标签键。 |
| `metadata_add_tags[].value` | - | string | 否 | - | - | 标签值。 |
| `metadata_keep_tags` | `--metadata-keep-tags` | array<string> | 否 | - | - | metadata_keep_tags 指定从源音频保留的元信息标签键；默认情况下，转码会丢弃大部分元信息，例如标题和艺术家。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `request_id` | string | 否 | Cloud | 请求标识；仅在后端返回时出现。 |
| `task_id` | string | 是 | Cloud | 异步任务的唯一标识，用于查询任务状态并获取最终结果。 |
| `task_type` | string | 否 | Cloud | 任务类型；仅在后端实际返回非空值时出现。 |
| `result.audio_url` | string | 否 | Cloud 终态 | audio_url 是输出音频的地址。未设置 media_output_destination 时，返回 HTTPS 临时下载链接，有效期为 24 小时；设置 media_output_destination 后，返回 vod://<空间名>/<媒资ID> 或 tos://<桶名>/<对象Key> 格式的存储地址。 |
| `result.duration` | number | 否 | Cloud 终态 | duration 表示音频时长，单位为秒。 |

Cloud 调用成功后读取 `task_id`，再查询终态结果：

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli shared query-task --task-id <task_id> --poll-complete
```

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli audio transcode-audio --help
mediakit-cli audio transcode-audio --schema
```
