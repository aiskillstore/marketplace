# 视频画面裁剪

## 能力用途

按指定的矩形区域裁剪视频画面，裁剪结果仅保留指定的需要区域。

## 参数填写规则

- 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli editing crop-video`
- 生命周期：异步
- 返回方式：返回 `task_id`，再查询终态结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `bottom_right_x` | `--bottom-right-x` | integer | 是 | - | 最小值: 1 | 裁剪矩形右下角的 X 坐标，单位为像素。bottom_right_x 必须大于 top_left_x，且 bottom_right_x 与 top_left_x 的差值不得小于 16px。建议裁剪矩形不要超出原始画面边界；当 bottom_right_x 超过视频宽度或 bottom_right_y 超过视频高度时，裁剪结果的相应维度会截断至画面边界。 |
| `bottom_right_y` | `--bottom-right-y` | integer | 是 | - | 最小值: 1 | 裁剪矩形右下角的 Y 坐标，单位为像素。bottom_right_y 必须大于 top_left_y，且 bottom_right_y 与 top_left_y 的差值不得小于 16px。建议裁剪矩形不要超出原始画面边界；当 bottom_right_x 超过视频宽度或 bottom_right_y 超过视频高度时，裁剪结果的相应维度会截断至画面边界。 |
| `callback_args` | `--callback-args` | string | 否 | - | - | 自定义回调参数。任务完成时，您提供的内容会通过事件回调原样返回，便于关联业务；字段长度最大为 512 字节。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `callback_url` | `--callback-url` | string | 否 | - | - | 用于接收该任务结果回调的 URL 地址。提供此参数时，其优先级高于全局回调地址；地址必须以 http:// 或 https:// 开头。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `client_token` | `--client-token` | string | 否 | - | - | 用户请求凭证，用于幂等控制。大小写敏感，不超过 64 个 ASCII 码可打印字符。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `media_output_destination` | `--media-output-destination` | string | 否 | - | - | 指定处理产物的目标存储位置。AI MediaKit 支持将处理产物存储至您的火山引擎视频点播（VOD）空间或对象存储（TOS）桶：存储至 VOD 时设为 vod://<您的空间名>；存储至 TOS 时设为 tos://<您的桶名>。设置后，任务结果中的 url 相关字段将返回 vod:// 或 tos:// 格式的资源地址，不再返回临时下载地址。首次使用前，需要按需授权 AI MediaKit 将文件写入您的 VOD 空间或 TOS 桶。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `top_left_x` | `--top-left-x` | integer | 是 | - | 最小值: 0 | top_left_x 是裁剪矩形左上角的水平方向 X 坐标，单位为像素。top_left_x 必须为非负整数。 |
| `top_left_y` | `--top-left-y` | integer | 是 | - | 最小值: 0 | top_left_y 是裁剪矩形左上角的垂直方向 Y 坐标，单位为像素。top_left_y 必须为非负整数。 |
| `video_url` | `--video-url` | string | 是 | - | - | 待裁剪视频的 URL。支持 mp4、flv、ts、avi、mov、wmv、mkv 等主流视频格式；支持公网 HTTP/HTTPS、本地文件路径、火山引擎视频点播 vod:// 和对象存储 tos:// 四种输入协议。输入视频最高支持 4K（3840×2160）分辨率，建议输入文件大小不超过 10 GB。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli editing crop-video \
  --video-url <video_url> \
  --top-left-x <top_left_x> \
  --top-left-y <top_left_y> \
  --bottom-right-x <bottom_right_x> \
  --bottom-right-y <bottom_right_y>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `request_id` | string | 否 | Cloud | 请求标识；仅在后端返回时出现。 |
| `task_id` | string | 是 | Cloud | 异步任务的唯一标识，用于查询任务状态并获取最终结果。 |
| `task_type` | string | 否 | Cloud | 任务类型；仅在后端实际返回非空值时出现。 |
| `result.duration` | number | 否 | Cloud 终态 | 输出视频的总时长，单位为秒。 |
| `result.resolution` | string | 否 | Cloud 终态 | 输出视频的分辨率，支持 240p、360p、480p、540p、720p、1080p、2k、4k。 |
| `result.video_url` | string | 否 | Cloud 终态 | 生成的裁剪后视频文件地址。生成的裁剪后视频文件格式为 MP4。未设置 media_output_destination 时，返回有效期 24 小时的 HTTPS 临时下载链接，需要及时下载保存；设置 media_output_destination 后，返回 vod://<空间名>/<媒资ID> 或 tos://<桶名>/<对象Key> 格式的存储地址。 |

Cloud 调用成功后读取 `task_id`，再查询终态结果：

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli shared query-task --task-id <task_id> --poll-complete
```

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli editing crop-video --help
mediakit-cli editing crop-video --schema
```
