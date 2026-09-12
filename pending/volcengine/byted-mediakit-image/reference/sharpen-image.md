# 图像锐化

## 能力用途

用于图像锐化，通过对输入图像进行锐化处理，有效增强图像的边缘细节与整体清晰度。适用于电商素材优化、UGC 画质增强、封面海报二创等场景。

## 参数填写规则

- 输入一张图片并指定锐化强度档位。锐化强度 sharpen_level 支持 low / medium / high 三档，默认 low。output_format 默认 original 表示保持原图格式。 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli image sharpen-image`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `image_url` | `--image-url` | string | 是 | - | - | 待处理图片 URL，支持 .png、.jpg、.jpeg、.webp 等主流图像格式；支持公网 HTTP/HTTPS URL、本地文件路径、火山引擎对象存储 tos:// 三种输入协议；仅支持处理静图；输入图像的宽和高均不得超过 10000 像素；建议单张图片不超过 35 MB。 |
| `output_format` | `--output-format` | string | 否 | "original" | 枚举: ["original","png","jpeg","webp"] | 输出图片格式，默认并支持 original，表示保持与原图一致的格式；也支持 png、jpeg、webp。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `sharpen_level` | `--sharpen-level` | string | 否 | "low" | 枚举: ["low","medium","high"] | 锐化强度档位，支持 low（轻度锐化）、medium（中度锐化）和 high（重度锐化），默认 low。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli image sharpen-image \
  --image-url <image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `image_format` | string | 否 | Cloud | 生成图像的格式。 |
| `image_height` | integer | 否 | Cloud | 生成图像的高度，单位为 px。 |
| `image_size` | integer | 否 | Cloud | 生成图像的大小，单位为字节。 |
| `image_url` | string | 否 | Cloud | 处理后的图片文件下载地址，有效期为 24 小时。 |
| `image_width` | integer | 否 | Cloud | 生成图像的宽度，单位为 px。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli image sharpen-image --help
mediakit-cli image sharpen-image --schema
```
