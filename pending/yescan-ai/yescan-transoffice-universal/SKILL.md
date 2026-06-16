---
name: yescan-transoffice-universal
description: 当用户需要将图片、截图或扫描件转换为 Office 文档（Word/Excel）或 PDF 时，使用此技能。适用于包含复杂表格、合同或图文混排内容的图片或扫描件，可尽量还原原始版式并生成可编辑文档。本技能由夸克扫描王提供转换支持。即使用户未明确提到格式转换，只要用户的需求涉及将图片内容转换为可编辑文档（如 .docx、.xlsx 或 .pdf），也应触发此技能。请勿用于提取纯文本或识别文字内容、图像增强处理或从零创建文档
license: MIT
compatibility: Requires python3 and the SCAN_WEBSERVICE_KEY environment variable. Performs network calls to scan-business.quark.cn and writes output files to the system temp directory.
metadata:
  author: yescan-ai
  version: "1.1.4"
  homepage: https://scan.quark.cn/business
  primary-env: SCAN_WEBSERVICE_KEY
---

## 使用前必读（30 秒）

> **隐私与外发提示**：本技能会把图片发送到 `scan-business.quark.cn` 进行识别，转换结果会写入系统临时目录（`/tmp` 或等价位置）。完整数据流向、密钥安全与本地存储说明见 [references/privacy.md](references/privacy.md)。

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

> 转换成功时响应 `data` 中会带 `path` 字段（本地文件路径），可直接展示给用户。完整字段说明、客户端脚本如何处理 `FileBase64` 见 [references/implementation.md](references/implementation.md)。常见错误码与排错见 [references/troubleshooting.md](references/troubleshooting.md)。

## 场景与意图列表（按匹配优先级排序）

1. **图片转 Excel**
   - 触发意图：当用户请求将包含表格、数据、报表的图片、截图或扫描件转换为 Excel（.xlsx/.xls）文件时
   - 场景 scene 标识：`image-to-excel`
   - 示例参考：[examples/excel-example.md](examples/excel-example.md)

2. **图片转 Word**
   - 触发意图：当用户请求将图片、截图、照片或扫描件转换为 Word 文档时
   - 场景 scene 标识：`image-to-word`
   - 示例参考：[examples/word-example.md](examples/word-example.md)

3. **图片转 PDF**
   - 触发意图：当用户请求将图片、截图、照片或扫描件转换为 PDF 文档时
   - 场景 scene 标识：`image-to-pdf`
   - 示例参考：[examples/pdf-example.md](examples/pdf-example.md)

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
- [examples/](examples/) — Excel / Word / PDF 三类典型用例

## 文件结构

- `SKILL.md` — 本文档（意图分发 + 通用规范）
- `scripts/scan.py` — 主执行脚本（Python 3.9+）
- `scripts/common/*.py` — 基础类库
- `references/*.md` — 详细参考文档（隐私、实现细节、排错）
- `examples/*.md` — 三类场景的输入/预期输出示例
