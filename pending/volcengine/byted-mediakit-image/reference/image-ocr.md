# 图像文字识别OCR

## 能力用途

用于通用印刷体文字识别（OCR），识别图片中的简体中文和英文，并提供文本块位置坐标与置信度参考。

## 参数填写规则

- 提交一张包含通用印刷体文字的公网可访问图片 URL，识别图片中的简体中文和英文文本。 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli image image-ocr`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 使用指南

- `image_url` 有宽高与体积限制：长边不得超过 3840 px，短边不得超过 2160 px，单张文件大小不得超过 10 MB。为避免超限导致调用失败，提交 OCR 前可先用本域能力做前置探测与治理：
  1. 用 `probe-image-metadata`（默认 `info_type=metadata`）探测宽高与文件大小，判断是否可能超限；
  2. 若宽高超限，先用 `resize-image` 等比缩放到合规尺寸；详见 [resize-image.md](resize-image.md)；
  3. 若体积超限，先用 `compress-image` 压缩到 10 MB 以内；详见 [compress-image.md](compress-image.md)；
  4. 将预处理返回的 `image_url` 再作为本工具的 `--image-url` 输入。探测详见 [probe-image-metadata.md](probe-image-metadata.md)。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `image_url` | `--image-url` | string | 是 | - | - | 待识别的图像 URL。图像来源支持公网 HTTP/HTTPS URL、本地文件路径、火山引擎对象存储 (tos://) 三种输入协议；图像长边不得超过 3840 px，短边不得超过 2160 px，单张图片文件大小不得超过 10 MB；支持 .png、.jpg、.jpeg、.webp、.tiff、.bmp 和 .heic 格式。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli image image-ocr \
  --image-url <image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `ocr_result` | array<object> | 否 | Cloud | 通用印刷体文字识别结果列表，每个元素代表一个识别出的文本块。 |
| `ocr_result[].bottom_right_x` | number | 否 | Cloud | 文字框右下角横坐标，单位 px。 |
| `ocr_result[].bottom_right_y` | number | 否 | Cloud | 文字框右下角纵坐标，单位 px。 |
| `ocr_result[].confidence` | number | 否 | Cloud | 识别置信度，取值范围 [0,1]。 |
| `ocr_result[].content` | string | 否 | Cloud | 识别出的文字内容。 |
| `ocr_result[].top_left_x` | number | 否 | Cloud | 文字框左上角横坐标，单位 px。 |
| `ocr_result[].top_left_y` | number | 否 | Cloud | 文字框左上角纵坐标，单位 px。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli image image-ocr --help
mediakit-cli image image-ocr --schema
```
