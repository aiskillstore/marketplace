# 图像元信息获取

## 能力用途

支持查询 metadata、avghue、alpha、blurhash 四种图像信息。

## 参数填写规则

- 提交一张公网可访问图片 URL，并指定查询信息类型；未传 info_type 时默认返回 metadata。 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli image probe-image-metadata`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `image_url` | `--image-url` | string | 是 | - | - | 待探测的图片 URL。支持公网 HTTP/HTTPS URL、本地文件路径 与火山引擎对象存储 tos:// 三种输入协议；支持 .png、.jpg、.jpeg、.webp 等主流图像格式。图片输入分辨率的宽和高均不得超过 10000 像素，建议单张图片文件大小不超过 35 MB。 |
| `info_type` | `--info-type` | string | 否 | "metadata" | 枚举: ["metadata","avghue","alpha","blurhash"] | 查询信息类型。metadata 获取图像的基本元信息；avghue 提取图像的主题色；alpha 分析图像的 Alpha 透明通道；blurhash 生成图像的 BlurHash 值。默认 metadata。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli image probe-image-metadata \
  --image-url <image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `aigc` | object / null | 否 | Cloud | AIGC 元数据。 |
| `alpha_ratio` | number | 否 | Cloud | Alpha 像素（完全透明或半透明）在整张图片中的占比。 |
| `blurhash` | string | 否 | Cloud | BlurHash 编码字符串。 |
| `color` | string | 否 | Cloud | 十六进制格式的主题色，例如 #RRGGBB。 |
| `color_model` | string | 否 | Cloud | 色彩模型，例如 yuv420p。 |
| `duration` | number | 否 | Cloud | 动图时长，单位为秒；静态图此字段可能不存在。 |
| `exif` | object / null | 否 | Cloud | EXIF 元数据。 |
| `format` | string | 否 | Cloud | 图片格式，例如 jpeg。 |
| `frame_count` | number | 否 | Cloud | 图片帧数，对于静态图通常为 1。 |
| `has_alpha` | boolean | 否 | Cloud | 是否包含 Alpha 透明通道。 |
| `height` | number | 否 | Cloud | 图片高度，单位为 px。 |
| `is_animation` | boolean | 否 | Cloud | 是否为动图。 |
| `md5` | string | 否 | Cloud | 图片的 MD5 值。 |
| `orientation` | object / array / string / number / boolean / null | 否 | Cloud | 图片方向信息。 |
| `quality` | number | 否 | Cloud | 压缩质量参数。 |
| `size` | number | 否 | Cloud | 图片大小，单位为 Byte。 |
| `width` | number | 否 | Cloud | 图片宽度，单位为 px。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli image probe-image-metadata --help
mediakit-cli image probe-image-metadata --schema
```
