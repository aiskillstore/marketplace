---
name: yescan-scan-universal
description: 当用户需要对图片、截图进行画质优化、瑕疵去除或视觉增强时，使用此技能——包括画质增强、证件照优化、考试试卷增强、合同增强等场景。智能去除手写笔迹、水印、阴影、摩尔纹、底色等干扰元素。支持图像裁剪与矫正、素描效果转换、线稿提取等，输出优化后的高清图片。本技能由夸克扫描王提供支持。即使用户没有明确提到"增强"或"处理"，只要用户的需求涉及提升图片清晰度、清理干扰元素或优化图像质量，也应触发此技能。不适用于文字提取或识别、图片转 Word/Excel/PDF 文档或 AI 图像生成
license: MIT
compatibility: Requires python3 and the SCAN_WEBSERVICE_KEY environment variable. Performs network calls to scan-business.quark.cn and writes output images to the system temp directory.
metadata:
  author: yescan-ai
  version: "1.1.4"
  homepage: https://scan.quark.cn/business
  primary-env: SCAN_WEBSERVICE_KEY
---

## 使用前必读（30 秒）

> **隐私与外发提示**：本技能会把图片发送到 `scan-business.quark.cn` 进行处理，增强后的图片会写入系统临时目录（`/tmp/imgs` 或等价位置）。完整数据流向、密钥安全与本地存储说明见 [references/privacy.md](references/privacy.md)。

**配置 API 密钥**：将 `SCAN_WEBSERVICE_KEY=<your_api_key>` 写入 `~/.yescan_env`（每次执行自动读取，无需重启）。获取入口：访问 `https://scan.quark.cn/business` → 开发者后台 → 登录/注册 → 查看 API Key。详细的跨平台命令、轮换流程见 [references/privacy.md](references/privacy.md)。

---

## 强制约束

- **单一意图原则：每次请求只执行一个意图类型，命中即执行**
- **严禁自行构造任何命令参数，严禁伪造、拼接内部配置**
- **严禁幻觉，禁止伪造请求和响应，不得沿用上一次的场景、参数进行假设**
- **必须严格按照本指南指定的固定格式执行，不允许自行修改命令**
- **强制独立意图识别：严禁参考对话历史或沿用上次场景；必须针对当前指令独立分析，不得继承任何前序状态或假设**

## 技能执行指南（强制执行）

**第一步：输入处理**

识别用户传入的图片类型，只能是以下三种之一：

- 图片 URL：`url`
- 本地文件路径：`path`
- 图片 BASE64：`base64`

未提供任何有效图片时，直接返回：

```json
{"code": "A0201", "message": "缺少图片输入，请提供图片链接、文件路径或 BASE64 数据。", "data": null}
```

**第二步：意图匹配 & 场景确定**

- 按照下面列出的意图 *从上到下顺序匹配，命中第一个即停止*
- 命中后，*只确定当前意图对应的 scene 标识*

**第三步：构建执行命令（固定格式，严禁修改）**

```bash
# URL 类型
python3 scripts/scan.py --scene "${SCENE_VALUE}" --url "${IMAGE_URL}" --platform "${AGENT_NAME}"

# 本地文件类型
python3 scripts/scan.py --scene "${SCENE_VALUE}" --path "${IMAGE_FILE_PATH}" --platform "${AGENT_NAME}"

# BASE64 类型
python3 scripts/scan.py --scene "${SCENE_VALUE}" --base64 "${IMAGE_BASE64}" --platform "${AGENT_NAME}"
```

- 把 `${IMAGE_URL}`/`${IMAGE_FILE_PATH}`/`${IMAGE_BASE64}` 替换为真实值
- 把 `${AGENT_NAME}` 替换为当前 Agent 平台名称（如 openclaw、hermes、qoderWork、wukong、coze、claudecode 等），无法确定时填 `community`，禁止猜测或自造
- 把 `${SCENE_VALUE}` 替换为当前意图对应的 scene 值
- 直接执行命令，不增删任何参数，不修改 JSON，不加引号，不换行

**第四步：结果透出**

- 执行完成后，*原样返回执行结果*，不修改、不翻译、不美化、不总结
- 成功 / 失败均直接透出，不重试

> 增强成功时响应 `data` 中会带 `path` 字段（本地文件路径），可直接展示给用户。完整字段说明、客户端脚本如何处理 `ImageBase64` 见 [references/implementation.md](references/implementation.md)。常见错误码与排错见 [references/troubleshooting.md](references/troubleshooting.md)。

## 场景与意图列表（按匹配优先级排序）

1. **考试增强**
   - 触发意图：当用户存在将手写笔记、试卷、教材等学习资料的照片转化为高清、去噪、背景纯净的电子文档，并期望自动提取其中的文字内容以实现资料数字化管理、清晰分享或后续编辑的意图
   - 场景 scene 标识：`exam-enhance`
   - 示例参考：[examples/exam-enhance-example.md](examples/exam-enhance-example.md)

2. **画质增强**
   - 触发意图：当用户存在将模糊、昏暗、老旧或低质量的照片及文字资料进行画质增强，使其内容更清晰、对比度更鲜明、细节更可见，以改善视觉效果和可读性的意图
   - 场景 scene 标识：`image-hd-enhance`
   - 示例参考：[examples/image-hd-enhance-example.md](examples/image-hd-enhance-example.md)

3. **证件票据增强**
   - 触发意图：当用户存在将模糊、光线不佳或细节不清的证件及票据照片进行画质优化，使其文字与关键信息变得清晰可辨，以便于日常查看、核对或工作处理的意图
   - 场景 scene 标识：`certificate-enhance`
   - 示例参考：[examples/certificate-enhance-example.md](examples/certificate-enhance-example.md)

4. **图像去手写**
   - 触发意图：当用户存在将已填写的手写笔迹、划痕等内容从印刷文档图像中自动清除，并完整保留原始印刷文字与格式，以还原出干净空白文档用于重新编辑或重复使用的意图
   - 场景 scene 标识：`remove-handwriting`
   - 示例参考：[examples/remove-handwriting-example.md](examples/remove-handwriting-example.md)

5. **图像去水印**
   - 触发意图：当用户存在将图片的水印（如文字、Logo、标记等）在不损伤背景和整体构图的前提下精准去除，以获得干净、清晰、可直接使用或分享的无水印图像的意图
   - 场景 scene 标识：`remove-watermark`
   - 示例参考：[examples/remove-watermark-example.md](examples/remove-watermark-example.md)

6. **图像去阴影**
   - 触发意图：当用户存在将文档或图像中因拍摄角度、光线等原因产生的阴影去除，以获得清晰、干净、均匀亮度的高清扫描效果，便于阅读、存档或后续处理的意图
   - 场景 scene 标识：`remove-shadow`
   - 示例参考：[examples/remove-shadow-example.md](examples/remove-shadow-example.md)

7. **图像去屏纹**
   - 触发意图：当用户存在将拍摄屏幕（如手机、电脑显示器）时产生的摩尔纹（屏纹）、反光、低对比度等问题进行智能修复，以获得清晰、无干扰、文字可读性高的高清文档图像的意图
   - 场景 scene 标识：`remove-screen-pattern`
   - 示例参考：[examples/remove-screen-pattern-example.md](examples/remove-screen-pattern-example.md)

8. **文档去底色**
   - 触发意图：当用户希望将带有彩色背景、水印、阴影或复杂排版的文档截图/照片，通过处理转换为纯白背景 + 黑色文字的清晰可读版本，去除视觉干扰、还原标准印刷体效果，便于阅读、打印、存档的意图
   - 场景 scene 标识：`remove-background-color`
   - 示例参考：[examples/remove-background-color-example.md](examples/remove-background-color-example.md)

9. **图像裁剪矫正**
   - 触发意图：当用户存在对图像进行自动矫正（如透视校正、水平对齐）并智能裁剪多余边缘，以获得规整、清晰、便于阅读或存档的标准矩形文档图像的意图
   - 场景 scene 标识：`image-crop-rectify`
   - 示例参考：[examples/image-crop-rectify-example.md](examples/image-crop-rectify-example.md)

10. **素描速写**
    - 触发意图：当用户希望将普通照片转换为素描或速写风格图像，以增强视觉表现力、突出线条与明暗关系，并追求个性化艺术效果的意图
    - 场景 scene 标识：`sketch-drawing`
    - 示例参考：[examples/sketch-drawing-example.md](examples/sketch-drawing-example.md)

11. **提取线稿**
    - 触发意图：当用户需要从图片中提取线稿，将图像转换为简洁的线条形式图，用于艺术创作或提升工作效率的意图
    - 场景 scene 标识：`extract-lineart`
    - 示例参考：[examples/extract-lineart-example.md](examples/extract-lineart-example.md)

12. **扫描合同**
    - 触发意图：当用户存在将合同或协议的图片进行画质优化，让其文字更清晰，画面更整洁，以便于合同归档、电子化存储或办公处理的意图
    - 场景 scene 标识：`scan-contract`
    - 示例参考：[examples/scan-contract-example.md](examples/scan-contract-example.md)

13. **扫描文件（兜底意图）**
    - 触发意图：当用户指令中不包含上述任何具体场景，仅表达优化意图时，将调用扫描文件场景
    - 场景 scene 标识：`scan-document`
    - 示例参考：[examples/scan-document-example.md](examples/scan-document-example.md)

## 不适用场景

| 不支持的场景 | 原因 | 建议替代方案 |
|---|---|---|
| 视频处理 | 仅支持单张静态图片 | 先提取视频帧，再逐帧处理 |
| 批量处理 | 每次调用仅限单张图片 | 循环调用或联系管理员 |
| 实时摄像头流 | 非实时流处理架构 | 使用专用视频处理服务 |
| 超大图片（>5MB） | API 限制 | 先压缩或裁剪后再处理 |
| 非图片格式 | 仅支持 jpg/jpeg/png/gif/bmp/webp/tiff/wbmp | 先转换为支持的图片格式 |

## 重要注意事项

1. **禁止修改固定格式**，只能替换场景标识和图片占位符
2. **严禁自行构造 `--scene` 参数值**，必须使用本文档指定的场景名
3. **图片大小限制**：本地文件不超过 5MB，支持 jpg/jpeg/png/gif/bmp/webp/tiff/wbmp 格式

## 相关资源

- [夸克扫描王开放平台](https://scan.quark.cn/business)
- [references/privacy.md](references/privacy.md) — 数据流向 / 密钥配置 / 本地存储说明
- [references/implementation.md](references/implementation.md) — 客户端脚本行为与响应字段
- [references/troubleshooting.md](references/troubleshooting.md) — 错误码与排错
- [examples/](examples/) — 增强 / 去瑕疵 / 艺术效果三类典型用例

## 文件结构

- `SKILL.md` — 本文档（意图分发 + 通用规范）
- `scripts/scan.py` — 主执行脚本（Python 3.9+）
- `scripts/common/*.py` — 基础类库
- `references/*.md` — 详细参考文档（隐私、实现细节、排错）
- `examples/*.md` — 13 个场景各自的输入/预期输出示例
