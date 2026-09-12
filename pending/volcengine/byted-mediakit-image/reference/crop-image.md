# 图像裁剪

## 能力用途

对输入图像进行多模式裁剪，可执行方向裁剪、定向裁剪、自定义裁剪或内切圆裁剪，适用于多端尺寸适配、主体保留、商品图去边和指定区域截取。

## 参数填写规则

- 输入图片并指定裁剪模式。仅支持公网 URL。未传 crop_mode 时默认 directional，且方向裁剪默认位置为 center。 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli image crop-image`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `crop_height` | `--crop-height` | integer | 否 | - | 最小值: 0 | directional 模式下，crop_height 表示裁剪后图像的目标高度，单位为 px，且 crop_mode 为 directional 时必须提供 crop_height。crop_mode 为 origin 时，crop_height 表示目标高度，单位为 px。crop_height 为 0 时，高度根据 crop_width 按原图比例自适应。 |
| `crop_mode` | `--crop-mode` | string | 否 | "directional" | 枚举: ["directional","origin","custom","circle"] | 支持 directional、origin、custom、circle 四种模式。directional 根据指定宽度、高度和位置进行方向裁剪；origin 根据指定宽高、偏移量和锚点进行定向裁剪；custom 根据指定左上角和右下角坐标进行自定义裁剪；circle 执行最大内切圆裁剪，无需配置其他参数。裁剪模式决定裁剪行为及所需参数，默认 directional。 |
| `crop_position` | `--crop-position` | string | 否 | "center" | 枚举: ["center","up","down","left","right"] | 指定裁剪区域的位置。支持 center、up、down、left、right，分别表示居中、顶部、底部、左侧、右侧，默认 center。 |
| `crop_width` | `--crop-width` | integer | 否 | - | 最小值: 0 | directional 模式下，crop_width 表示裁剪后图像的目标宽度，单位为 px，且 crop_mode 为 directional 时必须提供 crop_width。crop_mode 为 origin 时，crop_width 表示目标宽度，单位为 px。crop_width 为 0 时，宽度根据 crop_height 按原图比例自适应。directional 模式下，crop_width 与 crop_height 不得同时为 0。 |
| `custom_x1` | `--custom-x1` | integer | 否 | - | - | crop_mode 为 custom 时，custom_x1 表示裁剪区域左上角横坐标（X 轴），单位为 px。 |
| `custom_x2` | `--custom-x2` | integer | 否 | - | - | crop_mode 为 custom 时，custom_x2 表示裁剪区域右下角横坐标（X 轴），单位为 px。 |
| `custom_y1` | `--custom-y1` | integer | 否 | - | - | crop_mode 为 custom 时，custom_y1 表示裁剪区域左上角纵坐标（Y 轴），单位为 px。 |
| `custom_y2` | `--custom-y2` | integer | 否 | - | - | crop_mode 为 custom 时，custom_y2 表示裁剪区域右下角纵坐标（Y 轴），单位为 px。 |
| `image_url` | `--image-url` | string | 是 | - | - | 待处理图片的 URL，仅支持处理静图。支持公网 HTTP/HTTPS URL、本地文件路径和火山引擎对象存储 tos:// 三种输入协议，支持 .png、.jpg、.jpeg、.webp 等主流图像格式。建议单张图片不超过 35 MB。crop_mode 为 circle 时，原图最短边不得超过 2048 px。 |
| `origin_gravity` | `--origin-gravity` | string | 否 | "northwest" | 枚举: ["northwest","north","northeast","west","center","east","southwest","south","southeast"] | 指定定向裁剪的锚点（起始点）。支持 northwest、north、northeast、west、center、east、southwest、south、southeast，默认 northwest，表示左上角。 |
| `origin_x` | `--origin-x` | integer | 否 | - | - | crop_mode 为 origin 时，origin_x 表示相对锚点水平偏移量，单位为 px；正值向右，负值向左。 |
| `origin_y` | `--origin-y` | integer | 否 | - | - | crop_mode 为 origin 时，origin_y 表示相对锚点垂直偏移量，单位为 px；正值向下，负值向上。 |
| `output_format` | `--output-format` | string | 否 | "original" | 枚举: ["original","png","jpeg","webp"] | 指定输出图片格式，默认 original，表示保持原图格式。circle 模式下，为确保背景透明，建议输出为 png 或 webp；输出 jpeg 时，非圆形区域填充为白色。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli image crop-image \
  --image-url <image_url> \
  --crop-width <crop_width> \
  --crop-height <crop_height>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `image_format` | string | 否 | Cloud | 生成图像的格式。 |
| `image_height` | integer | 否 | Cloud | 生成图像的高度，单位为 px。 |
| `image_size` | integer | 否 | Cloud | 生成图像的大小，单位为字节。 |
| `image_url` | string | 否 | Cloud | 处理后图片的下载地址，有效期为 24 小时，请及时保存产物。 |
| `image_width` | integer | 否 | Cloud | 生成图像的宽度，单位为 px。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli image crop-image --help
mediakit-cli image crop-image --schema
```
