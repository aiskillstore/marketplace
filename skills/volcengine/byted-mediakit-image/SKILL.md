---
name: byted-mediakit-image
version: "0.2.1"
license: "MIT"
description: "面向单张或批量图片的视觉处理、质量优化、内容理解与基础编辑目标，适用于图片尺寸缩放与体积治理、元信息探测、裁剪旋转翻转与圆角、颜色与锐化清晰度调整、负片、模糊与打码、水印、背景移除、文字识别、画质评估与智能裁剪等。若对象和目标族已明确属于图片优化、图片理解或图片隐私保护，但具体做法不确定，可先加载本 Skill 探索。"
permissions:
  - shell
metadata:
  requires:
    bins: ["mediakit-cli"]
  cliHelp: "mediakit-cli image --help"
  product: mediakit-cli/skills
  domain: image
  capability_count: 21
---
# image MediaKit Skill

## 使用规则

1. 先读取 `../byted-mediakit-shared/SKILL.md`，执行统一前置检查；该 Skill 缺失时停止并提示安装。
2. 只从下表选择 `image` 域工具；相似能力按各工具“能力描述”和参数边界区分。
3. 执行前按需读取对应 reference；参数与结果说明来自同一份已审核文案，完整机器合同以当前 CLI `--schema` 为准。
4. 缺少必填参数、鉴权环境变量或真实输入资源时，向用户索取；通用可选字段只能透传用户明确提供的值，其他可选字段可由明确意图准确确定，但不得伪造。
5. 执行时设置 `MEDIAKIT_SURFACE=skill`，指定调用来源是 Skill。
6. 执行时把 `MEDIAKIT_RUNTIME` 设置为当前 Agent 宿主，避免 CLI 无法可靠识别父级 Agent。

## 图片体积治理与跨域路由

- 用户强调“尽量不掉画质”“质量优先”“高质量缩小体积”，且没有给出精确体积上限、质量值或格式转换要求时，先读取 [reference/families/image-size-reduction.md](reference/families/image-size-reduction.md)，优先选择 slim-image。
- 用户明确给出 quality、max_size、output_format，要求格式转换，或明确接受 PNG 有损压缩时，按同一 family guide 选择 compress-image。
- 用户只说“压缩”“变小”且无法判断质量优先还是精确体积、质量或格式控制时，先澄清。
- 若只说有图片而未说明业务目标，应先澄清。把多张图片做成视频、给视频叠图或视频画面裁剪应路由到 editing；视频抽帧、视频理解、视频增强或视频字幕擦除应路由到 video。

## 工具列表

| 工具 | 说明 | 支持模式 | 命令 | 参考 |
| --- | --- | --- | --- | --- |
| add-image-watermark | 为图片添加图文明水印，适用于版权标识与素材分发防盗链场景。 | Cloud | `mediakit-cli image add-image-watermark` | [reference/add-image-watermark.md](reference/add-image-watermark.md) |
| adjust-image-color | 对输入图像的亮度、对比度和饱和度进行调整，支持调亮、调暗、增强对比度、减弱对比度、增强饱和度、减弱饱和度共 6 种快速调整效果。适用于素材基础优化、统一内容视觉风格、营造庄重、复古等特殊氛围等场景。 | Cloud | `mediakit-cli image adjust-image-color` | [reference/adjust-image-color.md](reference/adjust-image-color.md) |
| compress-image | 有损图像压缩与格式转换工具；用户明确给出 quality、max_size、output_format、要求格式转换，或明确接受 PNG 有损压缩时选择。若用户强调尽量不掉画质、质量优先或高质量缩小体积，应优先选择 slim-image。 | Cloud | `mediakit-cli image compress-image` | [reference/compress-image.md](reference/compress-image.md) |
| crop-image | 对输入图像进行多模式裁剪，可执行方向裁剪、定向裁剪、自定义裁剪或内切圆裁剪，适用于多端尺寸适配、主体保留、商品图去边和指定区域截取。 | Cloud | `mediakit-cli image crop-image` | [reference/crop-image.md](reference/crop-image.md) |
| enhance-image | 基于图像内容理解进行智能决策，提升图片的分辨率、清晰度与色彩表现。 | Cloud | `mediakit-cli image enhance-image` | [reference/enhance-image.md](reference/enhance-image.md) |
| erase-image | 可按不同场景控制自动检测并擦除图片中的文字或常见图标，擦除后的区域通过智能填充技术进行修复，修复后的区域与背景自然融合。 | Cloud | `mediakit-cli image erase-image` | [reference/erase-image.md](reference/erase-image.md) |
| evaluate-image-quality | 用于图像画质评估，对输入图片进行主客观画质和美学评分，适用于质量监控、低质图筛查、内容审核、推荐排序和训练数据清洗。 | Cloud | `mediakit-cli image evaluate-image-quality` | [reference/evaluate-image-quality.md](reference/evaluate-image-quality.md) |
| face-blur-image | 自动检测图片中的所有人脸区域并进行马赛克处理，用于一键保护图片中的人脸隐私。支持社交平台内容审核、街景或监控画面脱敏、新闻媒体素材处理以及 AI 训练数据集脱敏等批量人脸隐私保护场景。 | Cloud | `mediakit-cli image face-blur-image` | [reference/face-blur-image.md](reference/face-blur-image.md) |
| flip-image | 支持对单张图片执行水平或竖直翻转。 | Cloud | `mediakit-cli image flip-image` | [reference/flip-image.md](reference/flip-image.md) |
| gaussian-blur-image | 用于图像高斯模糊；通过设定模糊强度快速对图片进行模糊处理，适用于隐私信息弱化、背景氛围化、生成预览图及封面背景等场景。 | Cloud | `mediakit-cli image gaussian-blur-image` | [reference/gaussian-blur-image.md](reference/gaussian-blur-image.md) |
| image-ocr | 用于通用印刷体文字识别（OCR），识别图片中的简体中文和英文，并提供文本块位置坐标与置信度参考。 | Cloud | `mediakit-cli image image-ocr` | [reference/image-ocr.md](reference/image-ocr.md) |
| invert-image | 用于图像负片，对输入图像执行负片（反相）效果，将图像的明暗关系与颜色映射为原图的相反效果，即明暗反转、色彩转为补色。 | Cloud | `mediakit-cli image invert-image` | [reference/invert-image.md](reference/invert-image.md) |
| mosaic-image | 支持对整张图像或指定矩形区域进行马赛克打码，可调整像素格形状与大小。支持用于遮挡人脸、证件信息、车牌、聊天记录等敏感内容。 | Cloud | `mediakit-cli image mosaic-image` | [reference/mosaic-image.md](reference/mosaic-image.md) |
| probe-image-metadata | 支持查询 metadata、avghue、alpha、blurhash 四种图像信息。 | Cloud | `mediakit-cli image probe-image-metadata` | [reference/probe-image-metadata.md](reference/probe-image-metadata.md) |
| remove-image-background | 自动识别并保留图像主体，移除背景后生成背景透明的图片，用于图像背景移除（抠图）。 | Cloud | `mediakit-cli image remove-image-background` | [reference/remove-image-background.md](reference/remove-image-background.md) |
| resize-image | 用于图像缩放，支持按指定宽高精确缩放，也可按长边、短边或等比模式缩放，适用于多端素材适配、封面与缩略图生成及批量图片预处理。 | Cloud | `mediakit-cli image resize-image` | [reference/resize-image.md](reference/resize-image.md) |
| rotate-image | 通过设置旋转角度和旋转背景样式对图片进行旋转处理，适用于图片方向校正、创意编辑和批量图像处理。 | Cloud | `mediakit-cli image rotate-image` | [reference/rotate-image.md](reference/rotate-image.md) |
| round-corner-image | 为图片四角快速添加正圆或椭圆圆角，适用于头像、卡片、电商主图等常见视觉编辑场景。 | Cloud | `mediakit-cli image round-corner-image` | [reference/round-corner-image.md](reference/round-corner-image.md) |
| sharpen-image | 用于图像锐化，通过对输入图像进行锐化处理，有效增强图像的边缘细节与整体清晰度。适用于电商素材优化、UGC 画质增强、封面海报二创等场景。 | Cloud | `mediakit-cli image sharpen-image` | [reference/sharpen-image.md](reference/sharpen-image.md) |
| slim-image | 质量优先的图片瘦身工具；用户强调尽量不掉画质、质量优先或高质量缩小体积，且未要求精确体积上限、质量值或格式转换时优先选择。 | Cloud | `mediakit-cli image slim-image` | [reference/slim-image.md](reference/slim-image.md) |
| smart-crop-image | 自动识别图像中的主体人脸区域，并适配指定尺寸进行裁剪；支持普通人脸和动漫人脸场景。未识别到人脸时，可按预设的降级策略输出结果。 | Cloud | `mediakit-cli image smart-crop-image` | [reference/smart-crop-image.md](reference/smart-crop-image.md) |
