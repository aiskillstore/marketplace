# 添加图文水印

## 能力用途

为图片添加图文明水印，适用于版权标识与素材分发防盗链场景。

## 参数填写规则

- 提交一张公网可访问图片 URL，并配置文字或图片水印。watermark_type=image 时必须提供 watermark_image_url；watermark_type=text 时建议提供 watermark_text。 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli image add-image-watermark`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 使用指南

- 布尔参数（`--enable-tile`）只能写成 `--enable-tile=true` 或 `--enable-tile=false`，也可用裸 `--enable-tile`（等价 true）；禁止空格传值 `--enable-tile true`，否则该值会被当作位置参数。
- 布尔参数取默认值时直接省略，不要显式重复默认值。

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli image add-image-watermark \
  --image-url <image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `enable_tile` | `--enable-tile` | boolean | 否 | false | - | 默认 false。开启后水印将以固定的间距重复平铺在整个图片上；对于文字水印，会额外应用逆时针 30 度的旋转；对于图片水印，仅进行平铺，不应用旋转。 |
| `image_url` | `--image-url` | string | 是 | - | - | 待处理的图片 URL，支持公网 HTTP/HTTPS URL、本地文件路径、对象存储 tos:// 三种输入协议；仅支持处理静图；建议单张图片不超过 35 MB；支持 .png、.jpg、.jpeg、.webp 等主流图像格式；输入图片宽和高均不得超过 10000 像素。 |
| `output_format` | `--output-format` | string | 否 | "original" | 枚举: ["original","png","jpeg","webp"] | 输出图片格式可为 original、png、jpeg、webp；original 表示保持与原图一致的格式；默认 original。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `watermark_image_opacity` | `--watermark-image-opacity` | integer | 否 | 100 | 最小值: 0；最大值: 100 | 图片水印透明度范围为 [0,100]；值越小越透明；默认 100。 |
| `watermark_image_url` | `--watermark-image-url` | string | 否 | - | - | 图片水印的 URL，必须为公网可访问的 HTTP 或 HTTPS URL；不是无条件必填；建议不超过 5 MB；支持 .jpg、.jpeg、.webp 等常见图像格式。 |
| `watermark_position` | `--watermark-position` | string | 否 | "bottom_right" | 枚举: ["top_left","top_right","bottom_left","bottom_right","left_center","right_center","top_center","bottom_center","center"] | 水印在图片上的九宫格布局位置，可为 top_left、top_center、top_right、left_center、center、right_center、bottom_left、bottom_center、bottom_right；默认 bottom_right；当使用包含 center 的值时，watermark_position_offset_x 和 watermark_position_offset_y 将不生效。 |
| `watermark_position_offset_x` | `--watermark-position-offset-x` | integer | 否 | 0 | 最小值: 0 | 水印在 watermark_position 基础上沿 X 轴的微调距离，单位为像素；默认 0；仅在 watermark_position 取值不包含 center 时生效。 |
| `watermark_position_offset_y` | `--watermark-position-offset-y` | integer | 否 | 0 | 最小值: 0 | 水印在 watermark_position 基础上沿 Y 轴的微调距离，单位为像素；默认 0；仅在 watermark_position 取值不包含 center 时生效。 |
| `watermark_text` | `--watermark-text` | string | 否 | - | 最长长度: 64 | 水印文字内容，不是无条件必填。 |
| `watermark_text_color` | `--watermark-text-color` | string | 否 | "#FFFFFF" | 格式: "^#[0-9a-fA-F]{6}$" | 文字颜色支持十六进制、RGB 等格式；默认 #FFFFFF。 |
| `watermark_text_font` | `--watermark-text-font` | string | 否 | "SourceHanSans-Regular.ttf" | 枚举: ["SourceHanSans-Regular.ttf","SourceHanSans-Bold.ttf","SourceHanSans-ExtraLight.ttf","SourceHanSans-Heavy.ttf","SourceHanSans-Light.ttf","SourceHanSans-Medium.ttf","SourceHanSans-Normal.ttf","SourceHanSerifCN-Regular.ttf","SourceHanSerifCN-Bold.ttf","SourceHanSerifCN-ExtraLight.ttf","SourceHanSerifCN-Heavy.ttf","SourceHanSerifCN-Light.ttf","SourceHanSerifCN-SemiBold.ttf","zcool-heiti.ttf","zcool_gaoduanhei.ttf","zcool_kuaileti.ttf","zcool_huangyou.ttf","FZLTHK.TTF"] | 文字字体支持思源黑体、思源宋体、站酷、方正兰亭黑等系列字体；默认 SourceHanSans-Regular.ttf（思源黑体）。 |
| `watermark_text_font_size` | `--watermark-text-font-size` | integer | 否 | 30 | 最小值: 1；最大值: 200 | 文字字号单位为像素；默认 30。 |
| `watermark_text_opacity` | `--watermark-text-opacity` | integer | 否 | 30 | 最小值: 0；最大值: 100 | 文字水印透明度范围为 [0,100]；值越小越透明；默认 30。 |
| `watermark_type` | `--watermark-type` | string | 否 | "text" | 枚举: ["text","image"] | 水印类型可为 text 和 image；text 表示文字水印，image 表示图片水印；默认 text。 |

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `image_format` | string | 否 | Cloud | 生成图像的格式。 |
| `image_height` | integer | 否 | Cloud | 生成图像的高度，单位 px。 |
| `image_size` | integer | 否 | Cloud | 生成图像的大小，单位字节。 |
| `image_url` | string | 否 | Cloud | 处理后的图片文件下载地址，有效期为 24 小时。 |
| `image_width` | integer | 否 | Cloud | 生成图像的宽度，单位 px。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli image add-image-watermark --help
mediakit-cli image add-image-watermark --schema
```
