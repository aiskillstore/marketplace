# 视频加图片

## 能力用途

支持将指定图片（如 Logo、水印等）叠加到视频画面上。

## 参数填写规则

- 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。
- Local 仅使用 Local 参数；Cloud-only 或当前未实现字段不得传入。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli --cloud editing add-image-to-video`
- 生命周期：异步
- 返回方式：返回 `task_id`，再查询终态结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `callback_args` | `--callback-args` | string | 否 | - | - | 自定义回调参数。任务完成时，您提供的内容会通过事件回调原样返回，便于关联业务；字段长度最大为 512 字节。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `callback_url` | `--callback-url` | string | 否 | - | - | 用于接收该任务结果回调的 URL 地址。提供此参数时，其优先级高于全局回调地址；地址必须以 http:// 或 https:// 开头。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `client_token` | `--client-token` | string | 否 | - | - | 用户请求凭证，用于幂等控制。大小写敏感，不超过 64 个 ASCII 码可打印字符。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `end_time` | `--end-time` | number | 否 | - | 最小值: 0 | 图片结束显示的时间，单位为秒。默认与视频结束时间一致。如果 end_time 超出原始视频时长，输出视频长度将延长至该 end_time，超出部分将以黑屏形式延续，图片会继续显示在黑屏上。 |
| `media_output_destination` | `--media-output-destination` | string | 否 | - | - | 指定处理产物的目标存储位置。AI MediaKit 支持将处理产物存储至您的火山引擎视频点播（VOD）空间或对象存储（TOS）桶：存储至 VOD 时设为 vod://<您的空间名>；存储至 TOS 时设为 tos://<您的桶名>。设置后，任务结果中的 url 相关字段将返回 vod:// 或 tos:// 格式的资源地址，不再返回临时下载地址。首次使用前，需要按需授权 AI MediaKit 将文件写入您的 VOD 空间或 TOS 桶。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `start_time` | `--start-time` | number | 否 | - | 最小值: 0 | 图片开始显示的时间，单位为秒。默认与视频开始时间一致。 |
| `sub_image_height` | `--sub-image-height` | string | 否 | "5%" | 格式: "^(\\d{1,4}\|\\d{1,3}%)$" | 图片高度支持像素值或相对于视频高度的百分比，默认值为 "5%"。 |
| `sub_image_pos_x` | `--sub-image-pos-x` | string | 否 | "85%" | 格式: "^(\\d{1,4}\|\\d{1,3}%)$" | 图片左上角在水平方向（X 轴）的位置，以视频左上角 "0" 为原点，支持像素值或百分比，默认值为 "85%"。 |
| `sub_image_pos_y` | `--sub-image-pos-y` | string | 否 | "90%" | 格式: "^(\\d{1,4}\|\\d{1,3}%)$" | 图片左上角在垂直方向（Y 轴）的位置，以视频左上角 "0" 为原点，支持像素值或百分比，默认值为 "90%"。 |
| `sub_image_url` | `--sub-image-url` | string | 是 | - | - | 待添加的图片 URL。图片来源仅支持公网可访问的 HTTP/HTTPS URL。建议使用 PNG、JPG、JPEG 等常见图片格式；推荐使用带透明通道的 PNG 格式以获得最佳水印效果。 |
| `sub_image_width` | `--sub-image-width` | string | 否 | "10%" | 格式: "^(\\d{1,4}\|\\d{1,3}%)$" | 图片宽度支持像素值或相对于视频宽度的百分比，默认值为 "10%"。 |
| `video_url` | `--video-url` | string | 是 | - | - | 待添加图片的视频 URL。视频来源支持公网 HTTP/HTTPS URL、本地文件路径、视频点播 vod:// 和对象存储 tos:// 四种输入协议。支持 mp4、flv、ts、avi、mov、wmv、mkv 等主流视频格式，最高支持 4K（3840×2160）分辨率。建议输入文件大小不超过 10 GB。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli --cloud editing add-image-to-video \
  --video-url <video_url> \
  --sub-image-url <sub_image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `request_id` | string | 否 | Cloud | 请求标识；仅在后端返回时出现。 |
| `task_id` | string | 是 | Cloud | 异步任务的唯一标识，用于查询任务状态并获取最终结果。 |
| `task_type` | string | 否 | Cloud | 任务类型；仅在后端实际返回非空值时出现。 |
| `result.duration` | number | 否 | Cloud 终态 | 输出视频总时长，单位为秒。 |
| `result.resolution` | string | 否 | Cloud 终态 | 输出视频分辨率，支持 240p、360p、480p、540p、720p、1080p、2k 或 4k。 |
| `result.video_url` | string | 否 | Cloud 终态 | 添加图片后的视频文件地址。结果视频文件格式为 MP4。未设置 media_output_destination 时返回 HTTPS 临时下载链接，有效期为 24 小时；设置 media_output_destination 后返回 vod://<空间名>/<媒资ID> 或 tos://<桶名>/<对象Key> 格式的存储地址。 |

Cloud 调用成功后读取 `task_id`，再查询终态结果：

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli shared query-task --task-id <task_id> --poll-complete
```

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli --cloud editing add-image-to-video --help
mediakit-cli --cloud editing add-image-to-video --schema
```

## Local

### 命令与生命周期

- 命令：`mediakit-cli --local editing add-image-to-video`
- 生命周期：同步
- 返回方式：直接返回本地结果，不产生 `task_id`。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `end_time` | `--end-time` | number | 否 | - | - | 图片的结束时间，单位：秒。注意：如果设置的开始/结束时间超出原始视频时长，输出视频长度将以该结束时间为准，超出部分以黑屏形式延续。不传默认同视频结束时间 |
| `start_time` | `--start-time` | number | 否 | - | - | 图片的开始时间，单位：秒。不传默认同视频开始时间 |
| `sub_image_height` | `--sub-image-height` | string | 否 | "5%" | - | 图片的高度，字符串类型，支持具体像素值（如 '100'）或百分比（如 '20%'，相对于视频高度）。 |
| `sub_image_pos_x` | `--sub-image-pos-x` | string | 否 | "85%" | - | 图片在水平方向（X 轴）的位置，以视频左上角为原点，字符串类型，支持具体像素值（如 '100'）或百分比（如 '20%'）。例如值为 '0' 时，表示处于最左侧。 |
| `sub_image_pos_y` | `--sub-image-pos-y` | string | 否 | "90%" | - | 图片在垂直方向（Y 轴）的位置，以视频左上角为原点，字符串类型，支持具体像素值（如 '100'）或百分比（如 '20%'）。例如值为 '0' 时，表示处于最上侧。 |
| `sub_image_url` | `--sub-image-url` | string | 是 | - | - | 图片URL。支持http://xxx或https://xxx格式 URL |
| `sub_image_width` | `--sub-image-width` | string | 否 | "10%" | - | 图片的宽度，字符串类型，支持具体像素值（如 '100'）或百分比（如 '20%'，相对于视频高度）。 |
| `video_url` | `--video-url` | string | 是 | - | - | 输入视频。String 类型，支持http://xxx或https://xxx格式 URL |

### Local CLI 选项

| CLI flag | 必填 | 说明 |
| --- | --- | --- |
| `--output-path` | 否 | 本地文件输出目录或完整输出文件路径；仅在用户明确指定输出位置时传递。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli --local editing add-image-to-video \
  --video-url <video_url> \
  --sub-image-url <sub_image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `duration` | number | 否 | Local | 视频时长，单位：秒 |
| `resolution` | string | 否 | Local | 视频分辨率档位（如 360p, 480p, 720p, 1080p, 2k, 4k） |
| `video_url` | string | 否 | Local | 输出视频文件路径或 URL |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli --local editing add-image-to-video --help
mediakit-cli --local editing add-image-to-video --schema
```
