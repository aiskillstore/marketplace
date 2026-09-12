# 视频画面翻转

## 能力用途

用于视频画面翻转，对指定视频进行上下或左右镜像翻转。

## 参数填写规则

- 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。
- Local 仅使用 Local 参数；Cloud-only 或当前未实现字段不得传入。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli --cloud editing flip-video`
- 生命周期：异步
- 返回方式：返回 `task_id`，再查询终态结果。

### 使用指南

- 布尔参数（`--is-flip-horizontal`、`--is-flip-vertical`）只能写成 `--is-flip-horizontal=true` 或 `--is-flip-horizontal=false`，也可用裸 `--is-flip-horizontal`（等价 true）；禁止空格传值 `--is-flip-horizontal true`，否则该值会被当作位置参数。
- 布尔参数取默认值时直接省略，不要显式重复默认值。

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli --cloud editing flip-video \
  --video-url <video_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `callback_args` | `--callback-args` | string | 否 | - | - | 自定义回调参数。任务完成时，您提供的内容会通过事件回调原样返回，便于关联业务；字段长度最大为 512 字节。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `callback_url` | `--callback-url` | string | 否 | - | - | 用于接收该任务结果回调的 URL 地址。提供此参数时，其优先级高于全局回调地址；地址必须以 http:// 或 https:// 开头。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `client_token` | `--client-token` | string | 否 | - | - | 用户请求凭证，用于幂等控制。大小写敏感，不超过 64 个 ASCII 码可打印字符。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `is_flip_horizontal` | `--is-flip-horizontal` | boolean | 否 | false | - | 可省略，用于控制是否进行水平（左右）翻转，默认值为 false。 |
| `is_flip_vertical` | `--is-flip-vertical` | boolean | 否 | false | - | 可省略，用于控制是否进行垂直（上下）翻转，默认值为 false。is_flip_vertical 和 is_flip_horizontal 两个参数至少需要将其中一个设置为 true，否则处理后的视频与原视频没有区别；如果两个参数都设置为 true，效果等同于将画面旋转 180 度。 |
| `media_output_destination` | `--media-output-destination` | string | 否 | - | - | 指定处理产物的目标存储位置。AI MediaKit 支持将处理产物存储至您的火山引擎视频点播（VOD）空间或对象存储（TOS）桶：存储至 VOD 时设为 vod://<您的空间名>；存储至 TOS 时设为 tos://<您的桶名>。设置后，任务结果中的 url 相关字段将返回 vod:// 或 tos:// 格式的资源地址，不再返回临时下载地址。首次使用前，需要按需授权 AI MediaKit 将文件写入您的 VOD 空间或 TOS 桶。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `video_url` | `--video-url` | string | 是 | - | - | 待翻转的视频 URL，支持公网 HTTP/HTTPS URL、本地文件路径、火山引擎视频点播 (vod://) 和火山引擎对象存储 (tos://) 四种输入协议；支持 mp4、flv、ts、avi、mov、wmv、mkv 等主流视频格式；最高支持 4K (3840×2160) 分辨率；建议输入文件大小不超过 10 GB。 |

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `request_id` | string | 否 | Cloud | 请求标识；仅在后端返回时出现。 |
| `task_id` | string | 是 | Cloud | 异步任务的唯一标识，用于查询任务状态并获取最终结果。 |
| `task_type` | string | 否 | Cloud | 任务类型；仅在后端实际返回非空值时出现。 |
| `result.duration` | number | 否 | Cloud 终态 | 输出视频的总时长，单位为秒。 |
| `result.resolution` | string | 否 | Cloud 终态 | 输出视频的分辨率，可能为 240p、360p、480p、540p、720p、1080p、2k 或 4k。 |
| `result.video_url` | string | 否 | Cloud 终态 | 生成的翻转后视频文件地址，文件格式为 MP4。未设置 media_output_destination 时返回一个 HTTPS 临时下载链接，有效期为 24 小时；设置 media_output_destination 后返回存储地址，格式为 vod://<空间名>/<媒资ID> 或 tos://<桶名>/<对象Key>。 |

Cloud 调用成功后读取 `task_id`，再查询终态结果：

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli shared query-task --task-id <task_id> --poll-complete
```

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli --cloud editing flip-video --help
mediakit-cli --cloud editing flip-video --schema
```

## Local

### 命令与生命周期

- 命令：`mediakit-cli --local editing flip-video`
- 生命周期：同步
- 返回方式：直接返回本地结果，不产生 `task_id`。

### 使用指南

- 布尔参数（`--is-flip-horizontal`、`--is-flip-vertical`）只能写成 `--is-flip-horizontal=true` 或 `--is-flip-horizontal=false`，也可用裸 `--is-flip-horizontal`（等价 true）；禁止空格传值 `--is-flip-horizontal true`，否则该值会被当作位置参数。
- 布尔参数取默认值时直接省略，不要显式重复默认值。

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli --local editing flip-video \
  --video-url <video_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `is_flip_horizontal` | `--is-flip-horizontal` | boolean | 否 | false | - | 是否进行水平翻转。Boolean 类型，默认值为 false， 表示不翻转。 |
| `is_flip_vertical` | `--is-flip-vertical` | boolean | 否 | false | - | 是否进行垂直翻转。Boolean 类型，默认值为 false， 表示不翻转。 |
| `video_url` | `--video-url` | string | 是 | - | - | 输入视频。String 类型，支持http://xxx或https://xxx格式 URL |

### Local CLI 选项

| CLI flag | 必填 | 说明 |
| --- | --- | --- |
| `--output-path` | 否 | 本地文件输出目录或完整输出文件路径；仅在用户明确指定输出位置时传递。 |

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `duration` | number | 否 | Local | 视频时长，单位：秒 |
| `resolution` | string | 否 | Local | 视频分辨率档位（如 360p, 480p, 720p, 1080p, 2k, 4k） |
| `video_url` | string | 否 | Local | 输出视频文件路径或 URL |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli --local editing flip-video --help
mediakit-cli --local editing flip-video --schema
```
