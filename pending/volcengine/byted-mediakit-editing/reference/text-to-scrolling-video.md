# 文字生成滚屏视频

## 能力用途

将指定文本内容转换为文字滚屏视频，输出视频为固定 9:16 竖版，常用于小说推文、内容讲解和歌词视频等场景。

## 参数填写规则

- 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli editing text-to-scrolling-video`
- 生命周期：异步
- 返回方式：返回 `task_id`，再查询终态结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `audio_url` | `--audio-url` | string | 否 | - | - | 背景音乐 URL。支持公网 HTTP/HTTPS URL、本地文件路径、vod:// 火山引擎视频点播和 tos:// 火山引擎对象存储四种输入协议，支持 mp3、m4a、wav 等主流音频格式。建议单个输入音频文件不超过 10 GB。提供背景音乐后，会无缝循环播放并覆盖整个视频时长，直到视频结束；若背景音乐时长超过视频时长，超出部分会自动截断。 |
| `callback_args` | `--callback-args` | string | 否 | - | - | 自定义回调参数。任务完成时，您提供的内容会通过事件回调原样返回，便于关联业务；字段长度最大为 512 字节。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `callback_url` | `--callback-url` | string | 否 | - | - | 用于接收该任务结果回调的 URL 地址。提供此参数时，其优先级高于全局回调地址；地址必须以 http:// 或 https:// 开头。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `client_token` | `--client-token` | string | 否 | - | - | 用户请求凭证，用于幂等控制。大小写敏感，不超过 64 个 ASCII 码可打印字符。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `end_hold_duration` | `--end-hold-duration` | number | 否 | 2 | 最小值: 0；最大值: 60 | 视频结束时，文字在结束位置静止停留的时长，单位为秒，范围 0 到 60，默认 2。 |
| `font_color` | `--font-color` | string | 否 | "#1F1F1FFF" | 格式: "^#[0-9A-Fa-f]{8}$" | 字体颜色必须采用 8 位 RGBA 十六进制 RRGGBBAA 格式，默认 #1F1F1FFF，表示不透明深灰色。使用深色背景图时，建议传入浅色字体（如 #FFFFFFFF）以保证可读性。 |
| `font_type` | `--font-type` | string | 否 | "sy_black" | 枚举: ["sy_black","pm_zhengdao","zhanku_kuaile"] | 滚屏文本字体支持 sy_black、pm_zhengdao、zhanku_kuaile，默认 sy_black。sy_black 表示思源黑体，风格经典、端正、百搭；pm_zhengdao 表示庞门正道标题体，风格粗壮、有力；zhanku_kuaile 表示站酷快乐体，风格圆润、活泼。 |
| `image_url` | `--image-url` | string | 是 | - | - | 背景图片 URL。支持公网 HTTP/HTTPS URL、本地文件路径和 tos:// 火山引擎对象存储三种输入协议，支持 jpg、png 等主流静态图片格式。建议背景图片宽高比为 9:16，与输出视频一致；建议背景图片分辨率尽量与 resolution 选择的输出视频分辨率一致；建议背景图片整体基调与 font_color 形成足够对比度。系统自动裁切背景图片顶部 10% 和底部 10% 区域，裁切区域作为半透明遮罩叠加在视频顶部和底部，增强滚屏文字可读性；建议背景图片顶部和底部各 10% 区域不包含关键信息。 |
| `media_output_destination` | `--media-output-destination` | string | 否 | - | - | 指定处理产物的目标存储位置。AI MediaKit 支持将处理产物存储至您的火山引擎视频点播（VOD）空间或对象存储（TOS）桶：存储至 VOD 时设为 vod://<您的空间名>；存储至 TOS 时设为 tos://<您的桶名>。设置后，任务结果中的 url 相关字段将返回 vod:// 或 tos:// 格式的资源地址，不再返回临时下载地址。首次使用前，需要按需授权 AI MediaKit 将文件写入您的 VOD 空间或 TOS 桶。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `resolution` | `--resolution` | string | 否 | "720p" | 枚举: ["360p","480p","720p","1080p"] | 输出分辨率选择固定 9:16 的竖版规格，支持 360p、480p、720p、1080p，默认 720p。360p 对应 360 × 640 像素输出尺寸，480p 对应 480 × 854 像素输出尺寸，720p 对应 720 × 1280 像素输出尺寸且为默认档位，1080p 对应 1080 × 1920 像素输出尺寸。字体大小随 resolution 档位线性缩放，以保持视觉效果一致；在 720p 分辨率下，字号约为 36px。 |
| `single_roll_duration` | `--single-roll-duration` | number | 否 | 3 | 最小值: 0.5；最大值: 60 | 单页文字从进入画面到完全滚出画面所需时间，也表示单页文字完全滚过屏幕的时长，单位为秒，范围 0.5 到 60，默认 3。single_roll_duration 越小，滚动速度越快。 |
| `start_hold_duration` | `--start-hold-duration` | number | 否 | 2 | 最小值: 0；最大值: 60 | 视频开始时，文字在起始位置静止停留的时长，单位为秒，范围 0 到 60，默认 2。 |
| `text` | `--text` | string | 是 | - | 最短长度: 1 | 滚屏文本内容，支持使用 \n 强制换行；未包含 \n 时，文本会按画布宽度自动换行。文本横排、左对齐显示。若要显示单个斜杠 /，传入 text 时需输入两个斜杠 //。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
 mediakit-cli editing text-to-scrolling-video \
 --text <text> \
 --image-url <image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `request_id` | string | 否 | Cloud | 请求标识；仅在后端返回时出现。 |
| `task_id` | string | 是 | Cloud | 异步任务的唯一标识，用于查询任务状态并获取最终结果。 |
| `task_type` | string | 否 | Cloud | 任务类型；仅在后端实际返回非空值时出现。 |
| `result.duration` | number | 否 | Cloud 终态 | 输出视频总时长，单位为秒。 |
| `result.resolution` | string | 否 | Cloud 终态 | 输出视频分辨率。 |
| `result.video_url` | string | 否 | Cloud 终态 | 生成的文字滚屏视频文件地址，视频文件格式为 MP4。设置 media_output_destination 后，为 vod://<空间名>/<媒资ID> 或 tos://<桶名>/<对象Key> 存储地址；未设置 media_output_destination 时，为有效期 24 小时的 HTTPS 临时下载链接。 |

Cloud 调用成功后读取 `task_id`，再查询终态结果：

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
 mediakit-cli shared query-task --task-id <task_id> --poll-complete
```

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli editing text-to-scrolling-video --help
mediakit-cli editing text-to-scrolling-video --schema
```
