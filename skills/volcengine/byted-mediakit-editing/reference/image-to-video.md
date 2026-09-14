# 图片转视频

## 能力用途

将多张图片按顺序组合成动态视频，可配置转场动画和镜头内动画；仅把现有图片做成带动效的视频，不支持根据参考图生成新的画面内容。

## 参数填写规则

- 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli editing image-to-video`
- 生命周期：异步
- 返回方式：返回 `task_id`，再查询终态结果。

### 使用指南

- 数组参数（`--transitions`）传多个值时用逗号分隔并整体加引号，例如 `--transitions "url1,url2"`。
- 单个值中的文件名或 URL 不能包含逗号（`,`），否则会被 CLI 当成多个元素拆开。遇到这种情况时，先向用户澄清，请其提供不含逗号的文件名或对应 URL 后再调用。
- 对象或对象数组参数（`--images`）需传合法 JSON 字符串并整体加单引号，例如 `--images '[{...}]'`；字段名与层级必须与上表“枚举/范围/结构”及子字段说明一致。
- 不要用逗号分隔或裸文本传该参数。

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli editing image-to-video \
  --images '[{...}]'
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `callback_args` | `--callback-args` | string | 否 | - | - | 自定义回调参数。任务完成时，您提供的内容会通过事件回调原样返回，便于关联业务；字段长度最大为 512 字节。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `callback_url` | `--callback-url` | string | 否 | - | - | 用于接收该任务结果回调的 URL 地址。提供此参数时，其优先级高于全局回调地址；地址必须以 http:// 或 https:// 开头。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `client_token` | `--client-token` | string | 否 | - | - | 用户请求凭证，用于幂等控制。大小写敏感，不超过 64 个 ASCII 码可打印字符。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `images` | `--images` | array<object> | 是 | - | 最少项数: 1；最多项数: 100 | 图片对象列表，用于定义视频的每一帧内容；单次任务支持最少 1 个、最多 100 个图片对象。 |
| `images[].animation_in` | - | number | 否 | - | - | 仅在设置了 animation_type 后生效；动画开始时间点相对于该图片片段的起始，单位：秒；默认值为 0，表示动画从图片展示的第一帧开始。 |
| `images[].animation_out` | - | number | 否 | - | - | 仅在设置了 animation_type 后生效；动画结束时间点相对于该图片片段的起始，单位：秒；默认值为图片的 duration 值，表示动画在图片展示的最后一帧结束。 |
| `images[].animation_type` | - | string | 否 | - | - | 图片展示期间的镜头内动画类型；默认无动画；可使用 move_up、move_down、move_left、move_right、zoom_in、zoom_out。 |
| `images[].duration` | - | number | 否 | - | - | 图片展示时长，单位：秒；默认值为 3；支持最多两位小数。 |
| `images[].image_url` | - | string | 是 | - | - | 图片的 URL；支持公网 HTTP/HTTPS URL、本地文件路径、对象存储 tos:// 三种输入协议；支持 jpg、png 等主流静态图片格式。 |
| `media_output_destination` | `--media-output-destination` | string | 否 | - | - | 指定处理产物的目标存储位置。AI MediaKit 支持将处理产物存储至您的火山引擎视频点播（VOD）空间或对象存储（TOS）桶：存储至 VOD 时设为 vod://<您的空间名>；存储至 TOS 时设为 tos://<您的桶名>。设置后，任务结果中的 url 相关字段将返回 vod:// 或 tos:// 格式的资源地址，不再返回临时下载地址。首次使用前，需要按需授权 AI MediaKit 将文件写入您的 VOD 空间或 TOS 桶。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `transitions` | `--transitions` | array<string> | 否 | - | 元素枚举: ["1182359","1182360","1182358","1182365","1182367","1182368","1182369","1182370","1182373","1182374","1182375","1182378"] | 图片间的转场效果 ID 列表；默认无转场（硬切）；如果列表长度小于所需转场数（图片数量 - 1），将循环使用列表中的效果。 转场效果 ID 分类：交替出场，ID：1182359 分类：旋转放大，ID：1182360 分类：泛开，ID：1182358 分类：六角形，ID：1182365 分类：故障转换，ID：1182367 分类：飞眼，ID：1182368 分类：梦幻放大，ID：1182369 分类：开门展现，ID：1182370 分类：立方转换，ID：1182373 分类：透镜变换，ID：1182374 分类：晚霞转场，ID：1182375 分类：圆形交替，ID：1182378 CLI 传参时可使用逗号分隔多个值，或重复传递该 flag；不要传 JSON 数组字符串。 |

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `request_id` | string | 否 | Cloud | 请求标识；仅在后端返回时出现。 |
| `task_id` | string | 是 | Cloud | 异步任务的唯一标识，用于查询任务状态并获取最终结果。 |
| `task_type` | string | 否 | Cloud | 任务类型；仅在后端实际返回非空值时出现。 |
| `result.duration` | number | 否 | Cloud 终态 | 输出视频的总时长，单位：秒 |
| `result.resolution` | string | 否 | Cloud 终态 | 输出视频的分辨率 |
| `result.video_url` | string | 否 | Cloud 终态 | 生成的视频文件地址，视频文件格式为 MP4；设置 media_output_destination 后返回存储地址，格式为 vod://<空间名>/<媒资ID> 或 tos://<桶名>/<对象Key>；未设置 media_output_destination 时默认返回 HTTPS 临时下载链接，有效期为 24 小时。 |

Cloud 调用成功后读取 `task_id`，再查询终态结果：

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli shared query-task --task-id <task_id> --poll-complete
```

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli editing image-to-video --help
mediakit-cli editing image-to-video --schema
```
