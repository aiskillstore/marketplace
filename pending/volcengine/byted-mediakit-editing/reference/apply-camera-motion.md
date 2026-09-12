# 视频添加运镜

## 能力用途

对输入视频在指定时间段内添加一种运镜特效，常用于素材二次创作、营销片头、短剧动效等场景。

## 参数填写规则

- 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli editing apply-camera-motion`
- 生命周期：异步
- 返回方式：返回 `task_id`，再查询终态结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `callback_args` | `--callback-args` | string | 否 | - | - | 自定义回调参数；任务完成时会通过事件回调原样返回，用于关联业务；字段长度最大为 512 字节。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `callback_url` | `--callback-url` | string | 否 | - | - | 用于接收该任务结果回调的 URL 地址；提供后优先级高于全局回调地址；地址必须以 http:// 或 https:// 开头。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `client_token` | `--client-token` | string | 否 | - | - | 用户请求凭证，用于幂等控制；大小写敏感，长度不超过 64 个 ASCII 可打印字符。 默认不传。用户明确指定时原样使用；用户明确要求重试时，同一逻辑请求的重试链必须复用同一 token。已有 token 时必须复用原值；此前请求未带 token 时，可从本次重试开始创建一次并持续复用，但该 token 不对此前请求提供追溯幂等。业务参数变化视为新请求，不得复用旧 token。不得为每次尝试生成不同值。CLI/MCP runtime 不判断重试意图，也不自动生成 token。 |
| `end_time` | `--end-time` | number | 否 | - | 最小值: 0 | 运镜结束时间，单位为秒，支持设置为 2 位小数，需大于 start_time；默认到视频结尾；仅传 start_time 时会运镜到视频结尾；若填写值超过视频实际时长，将自动按视频时长处理。 |
| `motion_style` | `--motion-style` | string | 否 | "zoom" | 枚举: ["zoom","pan-zoom","orbit-360","bounce"] | 运镜风格，支持 zoom、pan-zoom、orbit-360、bounce 几种预设效果，默认值为 zoom。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID；不传时默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以按队列对应的项目进行分账。队列可创建和管理，系统会自动分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `start_time` | `--start-time` | number | 否 | 0 | 最小值: 0 | 运镜开始时间，单位为秒，支持设置为 2 位小数，不得小于 0；默认值为 0，0 表示从视频片头开始；仅传 end_time 时按 0 作为开始时间。 |
| `video_url` | `--video-url` | string | 是 | - | - | 待处理的视频 URL。支持公网 HTTP/HTTPS URL、本地文件路径、火山引擎视频点播 vod:// 和火山引擎对象存储 tos:// 四种输入协议；支持 mp4、flv、ts、avi、mov、wmv、mkv 等格式；最高支持 1080p 分辨率；视频时长不得超过 5 分钟。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli editing apply-camera-motion \
  --video-url <video_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 任务结果查询

提交成功后会返回 `task_id`，再执行 `mediakit-cli shared query-task --task-id <task_id>` 查询。

- 当前命令：`mediakit-cli editing apply-camera-motion`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli editing apply-camera-motion --help
mediakit-cli editing apply-camera-motion --schema
```
