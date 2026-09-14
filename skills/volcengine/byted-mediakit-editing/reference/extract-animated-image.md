# 视频截取动图

## 能力用途

从视频中按指定开始时间和结束时间截取一段画面，生成 GIF 或 WebP 动图，常用于制作封面动图、营销素材和短预览。

## 参数填写规则

- 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli editing extract-animated-image`
- 生命周期：异步
- 返回方式：返回 `task_id`，再查询终态结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `callback_args` | `--callback-args` | string | 否 | - | - | 自定义回调参数。任务完成时，您提供的内容会通过事件回调原样返回，便于关联业务；字段长度最大为 512 字节。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `callback_url` | `--callback-url` | string | 否 | - | - | 用于接收该任务结果回调的 URL 地址。提供此参数时，其优先级高于全局回调地址；地址必须以 http:// 或 https:// 开头。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `client_token` | `--client-token` | string | 否 | - | - | 用户请求凭证，用于幂等控制。大小写敏感，不超过 64 个 ASCII 码可打印字符。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `end_time` | `--end-time` | number | 是 | - | 最小值: 0 | end_time 表示截取片段的结束时间，单位为秒；end_time 必须大于 start_time；输出动图的时长最大为 60 秒；end_time 支持最多 3 位小数。 |
| `media_output_destination` | `--media-output-destination` | string | 否 | - | - | 指定处理产物的目标存储位置。AI MediaKit 支持将处理产物存储至您的对象存储（TOS）桶，可设为 tos://<您的桶名>。设置后，任务结果中的 url 相关字段将返回 tos:// 格式的资源地址，不再返回临时下载地址。首次使用前，需要授权 AI MediaKit 将文件写入您的 TOS 桶。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `output_format` | `--output-format` | string | 否 | "gif" | 枚举: ["gif","webp"] | output_format 支持 gif 和 webp，默认值为 gif。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `start_time` | `--start-time` | number | 是 | 0 | 最小值: 0 | start_time 表示截取片段的开始时间，单位为秒；start_time 默认为 0，表示从视频开头截取；start_time 支持最多 3 位小数。 |
| `video_url` | `--video-url` | string | 是 | - | - | video_url 指定待截取动图的视频 URL；video_url 支持公网 HTTP/HTTPS URL、本地文件路径、火山引擎视频点播 vod:// 和火山引擎对象存储 tos:// 四种输入协议；输入视频支持 mp4、flv、ts、avi、mov、wmv、mkv 等格式，最高支持 4K（3840×2160）分辨率。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli editing extract-animated-image \
  --video-url <video_url> \
  --start-time <start_time> \
  --end-time <end_time>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `request_id` | string | 否 | Cloud | 请求标识；仅在后端返回时出现。 |
| `task_id` | string | 是 | Cloud | 异步任务的唯一标识，用于查询任务状态并获取最终结果。 |
| `task_type` | string | 否 | Cloud | 任务类型；仅在后端实际返回非空值时出现。 |
| `result.duration` | number | 否 | Cloud 终态 | duration 表示输出动图的时长，单位为秒，根据 min(end_time, 视频总时长) - start_time 计算得出，保留 3 位小数。 |
| `result.image_url` | string | 否 | Cloud 终态 | image_url 是生成的动图文件地址，输出动图的帧率固定为 15 fps。未设置 media_output_destination 时，image_url 返回有效期为 24 小时的 HTTPS 临时下载链接，需及时下载保存；设置 media_output_destination 后，image_url 返回格式为 tos://<桶名>/<对象Key> 的存储地址。 |
| `result.resolution` | string | 否 | Cloud 终态 | 输入视频的分辨率低于 480p 时，输出动图的 resolution 对齐输入视频；输出动图的 resolution 最大为 480p。 |

Cloud 调用成功后读取 `task_id`，再查询终态结果：

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli shared query-task --task-id <task_id> --poll-complete
```

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli editing extract-animated-image --help
mediakit-cli editing extract-animated-image --schema
```
