# 图像智能裁剪

## 能力用途

自动识别图像中的主体人脸区域，并适配指定尺寸进行裁剪；支持普通人脸和动漫人脸场景。未识别到人脸时，可按预设的降级策略输出结果。

## 参数填写规则

- 提交一张公网可访问图片 URL，并指定目标宽高、裁剪场景和未找到人脸时的降级裁剪策略。 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli image smart-crop-image`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `crop_strategy` | `--crop-strategy` | string | 否 | "top_crop" | 枚举: ["top_crop","center_crop","frosted_glass_fill"] | 可选。裁剪后图片与目标宽高比例不一致时，使用降级裁剪策略；支持三种策略：top_crop（从图像顶部开始并水平居中裁剪，默认）、center_crop（从图像正中心开始向四周裁剪）、frosted_glass_fill（保持原图完整，并在两侧或上下添加毛玻璃背景以达到目标尺寸）。 |
| `frosted_glass_strength` | `--frosted-glass-strength` | number | 否 | 100 | 最小值: 1 | 可选。毛玻璃填充的模糊强度，数值越大，模糊效果越强；仅在 crop_strategy 为 frosted_glass_fill 时生效。默认 100，推荐取值范围为 [10, 100]。 |
| `image_url` | `--image-url` | string | 是 | - | - | 待处理图片的 URL。支持公网 HTTP/HTTPS URL、本地文件路径和火山引擎对象存储 tos:// 三种输入协议；支持 .png、.jpg、.jpeg、.webp、.tiff、.bmp、.heic 等主流图像格式。图片宽和高均不得超过 6000 px，建议单张输入图片不超过 10 MB。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `scene` | `--scene` | string | 否 | "person_face" | 枚举: ["person_face","cartoon_face"] | 可选。用于指定识别主体的裁剪场景模型；支持 person_face 和 cartoon_face 两种场景。person_face 表示普通人脸裁剪；cartoon_face 表示动漫人脸裁剪。默认 person_face。 |
| `target_height` | `--target-height` | integer | 否 | 100 | 最小值: 1 | 可选。裁剪后的目标高度，单位 px；默认 100。 |
| `target_width` | `--target-width` | integer | 否 | 100 | 最小值: 1 | 可选。裁剪后的目标宽度，单位 px；默认 100。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli image smart-crop-image \
  --image-url <image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `image_format` | string | 否 | Cloud | 生成图像的格式。 |
| `image_height` | integer | 否 | Cloud | 生成图像的高度，单位 px。 |
| `image_size` | integer | 否 | Cloud | 生成图像的大小，单位字节。 |
| `image_url` | string | 否 | Cloud | 智能裁剪后图片文件的下载地址，有效期为 24 小时，务必及时保存指向的产物。 |
| `image_width` | integer | 否 | Cloud | 生成图像的宽度，单位 px。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli image smart-crop-image --help
mediakit-cli image smart-crop-image --schema
```
