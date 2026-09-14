# 图像画质增强

## 能力用途

基于图像内容理解进行智能决策，提升图片的分辨率、清晰度与色彩表现。

## 参数填写规则

- 必须至少传入 multiple 或 target_width / target_height，指定倍率或宽高。如果同时传入 multiple 和 target_width / target_height，则 multiple 生效。若不设置则默认倍率为2 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli image enhance-image`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `image_url` | `--image-url` | string | 是 | - | - | image_url 是待增强图像的 URL，支持公网 HTTP/HTTPS URL、本地文件路径和火山引擎对象存储 tos:// 三种输入协议；单张输入图片不得超过 10 MB；输入和输出尺寸范围随 tool_version 而不同；支持 .png、.jpg、.jpeg、.webp 等常见主流图像格式。 |
| `multiple` | `--multiple` | number | 否 | - | 最小值: 1；最大值: 30 | multiple 为非必选参数，表示图像处理后相对原图的放大倍数，支持 2 位小数；tool_version 为 standard 时，multiple 的范围是 [1, 8]；tool_version 为 professional 时，multiple 的范围是 [1, 30]；最终生成图像的宽度和高度不能超过所选模型版本支持的最大分辨率。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `target_height` | `--target-height` | integer | 否 | - | 最小值: 64；最大值: 10240 | target_height 为非必选参数，表示处理后的目标高度，单位为 px；可选，通常与 target_width 配合使用，也可单独设置以保持原图宽高比；tool_version 为 standard 时，target_height 的范围是 [原图高度, 6144]，且最终放大倍数不能超过 8 倍；tool_version 为 professional 时，target_height 的范围是 [64, 10240]。 |
| `target_width` | `--target-width` | integer | 否 | - | 最小值: 64；最大值: 10240 | target_width 为非必选参数，表示处理后的目标宽度，单位为 px；target_height 与 target_width 可选搭配使用，也可单独设置以保持原图宽高比；tool_version 为 standard 时，target_width 的范围是 [原图宽度, 6144]，且最终放大倍数不能超过 8 倍；tool_version 为 professional 时，target_width 的范围是 [64, 10240]。 |
| `tool_version` | `--tool-version` | string | 否 | "standard" | 枚举: ["standard","professional"] | tool_version 为非必选参数，用于选择画质增强模型版本，不同版本在效果、处理范围和价格上有所差异；默认是 standard；standard 是标准版，平衡处理速度与画质效果；professional 是专业版，提供发丝级画质增强，效果更佳。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli image enhance-image \
  --image-url <image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `image_format` | string | 否 | Cloud | tool_version 为 standard 时，输出图像格式固定为 png；tool_version 为 professional 时，输出图像格式与输入图像格式保持一致。 |
| `image_height` | integer | 否 | Cloud | 生成图像的高度，单位为 px。 |
| `image_size` | integer | 否 | Cloud | 生成图像的大小，单位为字节。 |
| `image_url` | string | 否 | Cloud | image_url 是增强后图片文件的下载地址，有效期为 24 小时，必须及时保存产物。 |
| `image_width` | integer | 否 | Cloud | 生成图像的宽度，单位为 px。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli image enhance-image --help
mediakit-cli image enhance-image --schema
```
