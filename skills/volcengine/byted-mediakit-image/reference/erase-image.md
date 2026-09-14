# 图像擦除修复

## 能力用途

可按不同场景控制自动检测并擦除图片中的文字或常见图标，擦除后的区域通过智能填充技术进行修复，修复后的区域与背景自然融合。

## 参数填写规则

- 提交一张公网可访问图片 URL，可选择标准版擦除修复；标准版支持自动检测、bbox、遮罩和文字擦除。 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli image erase-image`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `image_url` | `--image-url` | string | 是 | - | - | 待处理图像的 URL；图像来源支持公网 HTTP/HTTPS URL、本地文件路径和火山引擎对象存储 tos:// 三种输入协议；输入图像分辨率不得小于 10x10 像素，且不得超过 2560x1440 像素，顺序为宽x高；单张输入图片大小不得超过 10 MB；输入图片支持 .png、.jpg、.jpeg、.webp、.tiff、.bmp 和 .heic 格式。 |
| `output_format` | `--output-format` | string | 否 | "webp" | 枚举: ["png","jpeg","webp"] | 输出图片的格式，支持 webp、png 和 jpeg；默认 webp。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `standard_erase_text` | `--standard-erase-text` | string | 否 | - | - | standard_erase_text 指定需要擦除的文字内容；仅当 standard_scene 为 full_screen_text_erase 时生效；不提供 standard_erase_text 时会擦除识别到的所有文字。 |
| `standard_scene` | `--standard-scene` | string | 否 | "full_screen_text_erase" | 枚举: ["full_screen_text_erase","full_screen_icon_erase"] | standard_scene 表示标准版擦除场景；仅当 tool_version 为 standard 时生效；支持 full_screen_text_erase 和 full_screen_icon_erase；默认 full_screen_text_erase；full_screen_text_erase 表示全屏文字擦除，在 full_screen_text_erase 场景中，可选用 standard_erase_text 指定要擦除的文字，不指定 standard_erase_text 时默认擦除所有文字内容；full_screen_icon_erase 表示全屏图标擦除。 |
| `tool_version` | `--tool-version` | string | 否 | "standard" | 枚举: ["standard"] | 图像擦除修复选用的模型版本；当前仅支持 standard（标准版）；standard 标准版适用于简单、明确的擦除任务。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli image erase-image \
  --image-url <image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `image_format` | string | 否 | Cloud | 生成图像的格式。 |
| `image_height` | integer | 否 | Cloud | 生成图像的高度，单位为像素（px）。 |
| `image_size` | integer | 否 | Cloud | 生成图像的大小，单位为字节。 |
| `image_url` | string | 否 | Cloud | 擦除修复后的图片下载 URL，有效期为 24 小时，必须及时保存对应的产物。 |
| `image_width` | integer | 否 | Cloud | 生成图像的宽度，单位为像素（px）。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli image erase-image --help
mediakit-cli image erase-image --schema
```
