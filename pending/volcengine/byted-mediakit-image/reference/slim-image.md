# 集智瘦身

## 能力用途

集智瘦身通过 AI 大幅缩小图片体积，修复毛刺、彩噪和块效应等问题，增强图像边缘与纹理细节，输出更轻量且更清晰的图片。用户强调尽量不掉画质、质量优先或高质量缩小体积，且未要求精确体积上限、质量值或格式转换时，优先选择本工具。

## 相近能力选择

缩小图片文件体积时，先读取 [图片体积治理选择指南](families/image-size-reduction.md)，再决定使用 slim-image 或 compress-image。

## 参数填写规则

- 提交一张公网可访问的图片 URL 并指定输出格式。当前版本仅开放 URL 输入 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 与 `compress-image` 的边界：本工具用于质量优先的图片瘦身；若用户明确给出 `quality`、`max_size`、`output_format`，要求格式转换，或明确接受 PNG 有损压缩，应改用 `compress-image`；若只说压缩或变小且无法判断目标，先澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli image slim-image`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `image_url` | `--image-url` | string | 是 | - | - | 待处理图片 URL，支持公网 HTTP/HTTPS URL、本地文件路径和火山引擎对象存储 tos:// 三种输入协议。输入图片支持 jpeg、jpg、png、heic、avif 和 webp 格式，暂不支持动图输入。建议单张输入图片不超过 50 MB；输入图像的宽度不得超过 10000 像素，高度不得超过 10000 像素。当输入图像格式为 avif 时，建议宽与高的乘积不要超过 100,000；当 avif 输入图像的宽与高乘积超过建议的 100,000 时，处理可能失败。 |
| `output_format` | `--output-format` | string | 否 | "original" | 枚举: ["original","png","jpeg","webp"] | 输出图片格式，默认 original；original 表示输出保持与原图一致的格式，支持 original、png、jpeg 或 webp。输入和输出格式均为 JPEG 时，部分已高度压缩的源文件处理后体积可能无明显变化；JPEG 输入输出时体积可能不降或略增，与原图压缩参数及 JPEG 重新编码特性有关，属于正常现象；输入和输出格式均为 JPEG 时，少数情况下处理后体积甚至会略微增大。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli image slim-image \
  --image-url <image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `image_format` | string | 否 | Cloud | 生成图像的格式。 |
| `image_height` | integer | 否 | Cloud | 生成图像的高度，单位为 px。 |
| `image_size` | integer | 否 | Cloud | 生成图像的大小，单位为字节。 |
| `image_url` | string | 否 | Cloud | 集智瘦身后的结果图片下载 URL，有效期 24 小时，必须及时保存指向的产物。 |
| `image_width` | integer | 否 | Cloud | 生成图像的宽度，单位为 px。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli image slim-image --help
mediakit-cli image slim-image --schema
```
