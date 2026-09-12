# 图像人脸打码

## 能力用途

自动检测图片中的所有人脸区域并进行马赛克处理，用于一键保护图片中的人脸隐私。支持社交平台内容审核、街景或监控画面脱敏、新闻媒体素材处理以及 AI 训练数据集脱敏等批量人脸隐私保护场景。

## 参数填写规则

- 提交一张公网可访问图片 Url，自动检测并对图中所有人脸做马赛克打码；可选配置打码形状、像素格大小、检测置信度阈值与输出格式。 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli image face-blur-image`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `blur_shape` | `--blur-shape` | string | 否 | "circle" | 枚举: ["circle","rectangle"] | 人脸模糊区域的形状，支持 circle 或 rectangle：circle 表示圆形，rectangle 表示矩形；默认 circle。 |
| `face_detect_thresh` | `--face-detect-thresh` | number | 否 | 0.9 | 大于: 0；小于: 1 | 人脸检测置信度阈值必须大于 0 且小于 1；越高过滤越严格，过低可能误判非人脸区域，过高可能漏检人脸；默认 0.9。 |
| `image_url` | `--image-url` | string | 是 | - | - | 待打码的图像 URL，支持公网 HTTP/HTTPS URL、本地文件路径和火山引擎对象存储 tos:// 三种输入协议；支持 .png、.jpg、.jpeg、.webp、.avif 等主流图像格式，不支持动图。建议图像文件大小不超过 35 MB；图片文件过大可能导致处理失败；图片宽度和高度的乘积不得超过 4 亿像素。 |
| `mosaic_step` | `--mosaic-step` | integer | 否 | 12 | 最小值: 5；最大值: 100 | 马赛克像素格大小，单位 px，必须为正整数；越大，马赛克颗粒越大且脱敏强度越高；建议范围为 [5, 100]；默认 12。 |
| `output_format` | `--output-format` | string | 否 | "webp" | 枚举: ["png","jpeg","webp"] | 输出图片格式，支持 png、jpeg 或 webp；默认 webp。 |

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli image face-blur-image \
  --image-url <image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `face_count` | integer | 否 | Cloud | 检测到并已打码的人脸数量；为 0 表示未检测到人脸且原图未做处理；大于 0 表示已对对应数量的人脸完成打码。 |
| `face_location` | array<object> | 否 | Cloud | 每张检测出的人脸信息对象数组；未检测到人脸时为空数组。 |
| `face_location[].bottom_right_x` | integer | 否 | Cloud | 人脸检测框右下角横坐标，单位 px。 |
| `face_location[].bottom_right_y` | integer | 否 | Cloud | 人脸检测框右下角纵坐标，单位 px。 |
| `face_location[].confidence` | number | 否 | Cloud | 人脸检测置信度，必须大于 0 且小于 1。 |
| `face_location[].top_left_x` | integer | 否 | Cloud | 人脸检测框左上角横坐标，单位 px。 |
| `face_location[].top_left_y` | integer | 否 | Cloud | 人脸检测框左上角纵坐标，单位 px。 |
| `image_format` | string | 否 | Cloud | 处理后图片格式。 |
| `image_height` | integer | 否 | Cloud | 处理后图片高度，单位 px。 |
| `image_size` | integer | 否 | Cloud | 处理后图片大小，单位字节。 |
| `image_url` | string | 否 | Cloud | 人脸打码后的图片文件下载地址，有效期为 24 小时，务必及时保存对应的产物。 |
| `image_width` | integer | 否 | Cloud | 处理后图片宽度，单位 px。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli image face-blur-image --help
mediakit-cli image face-blur-image --schema
```
