# 视频加字幕

## 能力用途

将字幕文件或文本内容按自定义样式压制到视频画面中，生成带内嵌字幕的新视频。

## 参数填写规则

- Cloud: subtitle_url参数与subtitles参数两者必须指定一个，且subtitle_url 优先级更高 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 设置 subtitle_pos_preset 或 subtitle_font_size 前，若没有视频宽高，先探测视频元信息。用户未指定位置时：横屏使用 bottom_center，竖屏使用 lower_third。
- 字号不得超过当前位置预设的最大渲染高度（视频原始高度 × height%）；单行字数 × 字号不得超过当前位置预设宽度（视频原始宽度 × width%）。
- 若成片用于短视频或漫剧平台，设置位置前向用户确认，并避开平台操作栏、进度条和互动控件。
- Local: 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。
- Local 仅使用 Local 参数；Cloud-only 或当前未实现字段不得传入。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli --cloud editing add-subtitle-to-video`
- 生命周期：异步
- 返回方式：返回 `task_id`，再查询终态结果。

### 使用指南

- 对象或对象数组参数（`--subtitles`）需传合法 JSON 字符串并整体加单引号，例如 `--subtitles '[{...}]'`；字段名与层级必须与上表“枚举/范围/结构”及子字段说明一致。
- 不要用逗号分隔或裸文本传该参数。

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
 mediakit-cli --cloud editing add-subtitle-to-video \
 --video-url <video_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `callback_args` | `--callback-args` | string | 否 | - | - | 自定义回调参数。任务完成时，您提供的内容会通过事件回调原样返回，便于关联业务；字段长度最大为 512 字节。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `callback_url` | `--callback-url` | string | 否 | - | - | 用于接收该任务结果回调的 URL 地址。提供此参数时，其优先级高于全局回调地址；地址必须以 http:// 或 https:// 开头。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `client_token` | `--client-token` | string | 否 | - | - | 用户请求凭证，用于幂等控制。大小写敏感，不超过 64 个 ASCII 码可打印字符。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `media_output_destination` | `--media-output-destination` | string | 否 | - | - | 指定处理产物的目标存储位置。AI MediaKit 支持将处理产物存储至您的火山引擎视频点播（VOD）空间或对象存储（TOS）桶：存储至 VOD 时设为 vod://<您的空间名>；存储至 TOS 时设为 tos://<您的桶名>。设置后，任务结果中的 url 相关字段将返回 vod:// 或 tos:// 格式的资源地址，不再返回临时下载地址。首次使用前，需要按需授权 AI MediaKit 将文件写入您的 VOD 空间或 TOS 桶。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `subtitle_font_color` | `--subtitle-font-color` | string | 否 | "#FFFFFFFF" | - | subtitle_font_color 非必填，字幕字体颜色采用 RGBA 格式，默认 #FFFFFFFF，表示不透明白色。 |
| `subtitle_font_size` | `--subtitle-font-size` | integer | 否 | 50 | 最小值: 1 | subtitle_font_size 非必填，字幕字体大小单位为 px，默认 50 px。字号不得超过所选位置预设的最大渲染高度，即视频原始高度 × height 百分比（例如 height 为 10% 时，最大字号为视频高度的 10%）；同时单行字数 × 字号不得超过所选位置预设的 width（视频原始宽度 × width 百分比，例如 80%）。 |
| `subtitle_font_type` | `--subtitle-font-type` | string | 否 | "sy_black" | 枚举: ["sy_black","pm_zhengdao","zhanku_kuaile"] | subtitle_font_type 非必填，支持 sy_black（思源黑体，经典无衬线黑体，端正百搭，正文首选）；支持 pm_zhengdao（庞门正道标题体，粗壮有力，适合大标题或封面）；支持 zhanku_kuaile（站酷快乐体，圆润活泼并带手写感，适合轻松搞笑的 Vlog 氛围）；默认 sy_black，即思源黑体。 |
| `subtitle_pos_preset` | `--subtitle-pos-preset` | string | 否 | "bottom_center" | 枚举: ["bottom_center","top_center","center","lower_third"] | subtitle_pos_preset 非必填，通过预设值快速将字幕放到画面常用位置；支持 bottom_center（底部居中，默认，推荐横屏使用）、top_center（顶部居中）、center（画面正中央）、lower_third（偏下三分之一处，推荐竖屏使用）。用户未指定位置时：横屏使用 bottom_center，竖屏使用 lower_third。各预设对应的字幕渲染区域为：top_center 为 width 80%、height 10%、pos_x 10%、pos_y 5%；center 为 width 80%、height 15%、pos_x 10%、pos_y 42.5%；lower_third 为 width 80%、height 10%、pos_x 10%、pos_y 70%；bottom_center 为 width 80%、height 10%、pos_x 10%、pos_y 85%。其中 height 为相对视频原始高度的字体渲染最大高度，width 为相对视频原始宽度的字幕区域最大宽度。若当前没有视频宽高信息，可先探测视频元信息获取宽高后再选择位置与字号。若成片用于短视频或漫剧平台，设置位置前应向用户确认，并避开对应平台的操作栏、进度条和互动控件，避免字幕被遮挡。 |
| `subtitle_url` | `--subtitle-url` | string | 否 | - | - | subtitle_url 非必填，用于提供字幕文件 URL，仅支持公网可访问的 HTTP/HTTPS URL，支持 SRT、VTT、ASS 等常见字幕格式；subtitle_url 与 subtitles 同时存在时，优先使用 subtitle_url 的内容。 |
| `subtitles` | `--subtitles` | array<object> | 否 | - | 最少项数: 0 | subtitles 非必填，是由多个字幕对象组成的字幕内容列表；每个对象包含字幕文本、开始时间和结束时间。 |
| `subtitles[].end_time` | - | number | 是 | - | 最小值: 0 | 该条字幕结束显示的时间，单位为秒。 |
| `subtitles[].start_time` | - | number | 是 | - | 最小值: 0 | 该条字幕开始显示的时间，单位为秒。 |
| `subtitles[].subtitle_text` | - | string | 是 | - | - | 单条字幕的文本内容。 |
| `video_url` | `--video-url` | string | 是 | - | - | video_url 是待添加字幕的视频 URL，支持公网 HTTP/HTTPS、本地文件路径、火山引擎视频点播 vod:// 和火山引擎对象存储 tos:// 四种输入协议，支持 mp4、flv、ts、avi、mov、wmv、mkv 等主流视频格式；最高支持 4K（3840×2160）分辨率；建议输入视频文件大小不超过 10 GB。 |

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `request_id` | string | 否 | Cloud | 请求标识；仅在后端返回时出现。 |
| `task_id` | string | 是 | Cloud | 异步任务的唯一标识，用于查询任务状态并获取最终结果。 |
| `task_type` | string | 否 | Cloud | 任务类型；仅在后端实际返回非空值时出现。 |
| `result.duration` | number | 否 | Cloud 终态 | 输出视频总时长，单位为秒。 |
| `result.resolution` | string | 否 | Cloud 终态 | 输出分辨率支持 240p、360p、480p、540p、720p、1080p、2k、4k。 |
| `result.video_url` | string | 否 | Cloud 终态 | 生成的带内嵌字幕视频地址，文件格式为 MP4。设置 media_output_destination 后，返回 vod://<空间名>/<媒资ID> 或 tos://<桶名>/<对象Key> 格式的存储地址；未设置 media_output_destination 时，返回有效期 24 小时的 HTTPS 临时下载链接，需及时下载保存。 |

Cloud 调用成功后读取 `task_id`，再查询终态结果：

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
 mediakit-cli shared query-task --task-id <task_id> --poll-complete
```

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli --cloud editing add-subtitle-to-video --help
mediakit-cli --cloud editing add-subtitle-to-video --schema
```

## Local

### 命令与生命周期

- 命令：`mediakit-cli --local editing add-subtitle-to-video`
- 生命周期：同步
- 返回方式：直接返回本地结果，不产生 `task_id`。

### 使用指南

- 对象或对象数组参数（`--subtitles`）需传合法 JSON 字符串并整体加单引号，例如 `--subtitles '[{...}]'`；字段名与层级必须与上表“枚举/范围/结构”及子字段说明一致。
- 不要用逗号分隔或裸文本传该参数。

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
 mediakit-cli --local editing add-subtitle-to-video \
 --video-url <video_url> \
 --subtitle-url <subtitle_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `subtitle_font_color` | `--subtitle-font-color` | string | 否 | "#FFFFFFFF" | - | 本地字幕字体颜色，采用 RGBA 格式；默认 #FFFFFFFF，表示不透明白色。 |
| `subtitle_pos_preset` | `--subtitle-pos-preset` | string | 否 | "bottom_center" | 枚举: ["bottom_center","top_center","center","lower_third"] | 本地字幕位置。支持底部居中 bottom_center（推荐横屏）、顶部居中 top_center、画面中央 center、偏下三分之一 lower_third（推荐竖屏）；默认 bottom_center。用户未指定时横屏使用 bottom_center、竖屏使用 lower_third。各预设渲染区域：top_center 为 width 80%、height 10%、pos_x 10%、pos_y 5%；center 为 width 80%、height 15%、pos_x 10%、pos_y 42.5%；lower_third 为 width 80%、height 10%、pos_x 10%、pos_y 70%；bottom_center 为 width 80%、height 10%、pos_x 10%、pos_y 85%。若无视频宽高，可先探测视频元信息。若用于短视频或漫剧平台，应避开平台操作栏、进度条和互动控件。 |
| `subtitle_url` | `--subtitle-url` | string | 否 | - | - | 字幕文件 URL、filename。常见的字幕文件为 SRT、VTT、ASS 等格式。 |
| `subtitles` | `--subtitles` | array<object> | 否 | - | - | 字幕列表，Array<object>类型。<br>子字段说明（JSON 数组每项）:<br>- subtitle_text: 字幕文本，必填<br>- start_time: 字幕开始时间。单位：秒。必填<br>- end_time: 字幕结束时间。单位：秒。必填 |
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
mediakit-cli --local editing add-subtitle-to-video --help
mediakit-cli --local editing add-subtitle-to-video --schema
```
