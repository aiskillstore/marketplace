---
name: yescan-ocr-universal
description: 当用户需要从图片、截图、照片或扫描文档中提取、识别或结构化文本，就使用此技能——包括手写体、表格、数学公式、商品图、各类证件（身份证、社保卡、驾照、行驶证、港澳台通行证、学位证等）、票据（增值税发票、火车票、英文发票等）、医疗报告、药检报告、营业执照、习题以及图片翻译。本技能由夸克扫描王提供支持。即使用户没有明确提到"OCR"或"文字识别"，只要用户的需求涉及从图片中获取文字或关键信息，也应触发此技能。不适用于图像生成、图像编辑或无需从图片中提取文本的任务
license: MIT
compatibility: Requires python3 and the SCAN_WEBSERVICE_KEY environment variable. Performs network calls to scan-business.quark.cn and returns structured OCR text results.
metadata:
  author: yescan-ai
  version: "1.1.4"
  homepage: https://scan.quark.cn/business
  primary-env: SCAN_WEBSERVICE_KEY
---

## 使用前必读（30 秒）

> **隐私与外发提示**：本技能会把图片发送到 `scan-business.quark.cn` 进行识别，识别结果以结构化文本返回。完整数据流向、密钥安全与本地存储说明见 [references/privacy.md](references/privacy.md)。

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

> OCR 识别成功时响应 `data` 中含各场景特定的结构化字段（纯文本、表格、证件信息等），直接返回给用户。`pic-translate` 场景额外生成译图文件，响应含 `translated_image_path`。完整字段说明见 [references/implementation.md](references/implementation.md)。常见错误码与排错见 [references/troubleshooting.md](references/troubleshooting.md)。

## 场景与意图列表（按匹配优先级排序）

1. **手写文档识别**
   - 触发意图：当用户存在识别各类中英文手写内容（如学生作答、作文、会议记录、手写账单等）、将潦草或非标准手写图片转化为高精度可编辑文本，或突破传统 OCR 限制处理复杂手写场景的意图。
   - 场景 scene 标识：`handwritten-ocr`
   - 示例参考：[examples/handwritten-ocr-example.md](examples/handwritten-ocr-example.md)

2. **表格识别**
   - 触发意图：当用户存在识别图片中的各类表格（如 Excel/Word 表格、票据单据、手写表格、检查报告单等）、高精度提取文字内容并精准还原原始表格格式与结构的意图。
   - 场景 scene 标识：`table-ocr`
   - 示例参考：[examples/table-ocr-example.md](examples/table-ocr-example.md)

3. **身份证识别**
   - 触发意图：当用户存在识别身份证图片、提取证件关键信息（包括但不限于姓名、身份证号、地址等字段）、将证件影像转化为结构化数据，或应用于身份核验、实名认证及信息准确性校验等场景的意图。
   - 场景 scene 标识：`idcard-ocr`
   - 示例参考：[examples/idcard-ocr-example.md](examples/idcard-ocr-example.md)

4. **社保卡识别**
   - 触发意图：当用户存在识别社保卡图片、提取证件关键信息（包括但不限于姓名、社会保障号码、卡号、银联号码、性别、民族、发卡日期及有效期限等字段）、将证件影像转化为结构化数据，或应用于社保业务办理、身份核验及政务服务自动化等场景的意图。
   - 场景 scene 标识：`social-security-card-ocr`
   - 示例参考：[examples/social-security-card-ocr-example.md](examples/social-security-card-ocr-example.md)

5. **港澳通行证识别**
   - 触发意图：当用户存在识别港澳通行证（或港澳台通行证）图片、提取证件关键信息（包括但不限于姓名、证件号码、签发机关、有效期限等 11 个字段）、将证件影像转化为结构化数据，或应用于身份核验、出入境管理及政务服务自动化等场景的意图。
   - 场景 scene 标识：`travel-permit-ocr`
   - 示例参考：[examples/travel-permit-ocr-example.md](examples/travel-permit-ocr-example.md)

6. **学位证识别**
   - 触发意图：当用户存在识别学位证书图片、提取证书关键信息（包括但不限于证书名称、学校、姓名、性别、出生日期、学习日期、学制、学历、学位、专业、证书编号及发证日期等 12 个字段）、将证书影像转化为结构化数据，或应用于企业人才信息录入和学历核验等场景的意图。
   - 场景 scene 标识：`degree-certificate-ocr`
   - 示例参考：[examples/degree-certificate-ocr-example.md](examples/degree-certificate-ocr-example.md)

7. **增值税发票识别**
   - 触发意图：当用户存在识别增值税发票图片、提取单据关键信息（包括但不限于销售方、购买方、货物详情、金额等 30 多个字段）、将发票影像转化为结构化数据，或应用于财务报销自动化、税务管理及企业风控等场景的意图。
   - 场景 scene 标识：`vat-invoice-ocr`
   - 示例参考：[examples/vat-invoice-ocr-example.md](examples/vat-invoice-ocr-example.md)

8. **火车票识别**
   - 触发意图：当用户存在识别火车票图片、提取票号/出发站/到达站/车次/开车时间/票价/座位号/座位类型/旅客身份号码/旅客姓名等 10 个关键字段信息、将车票照片转化为结构化文本数据，或应用于企业出行报销场景的意图。
   - 场景 scene 标识：`train-ticket-ocr`
   - 示例参考：[examples/train-ticket-ocr-example.md](examples/train-ticket-ocr-example.md)

9. **公式识别**
   - 触发意图：当用户存在识别数学/化学公式图片、高精度解析分数、矩阵、分段函数及化学方程式等复杂结构、将图像公式转化为可编辑的 LaTeX 代码或结构化数据，或应用于智能试卷自动批改、学术论文数字化归档、在线教育题目解析及科研文献深度分析等场景的意图。
   - 场景 scene 标识：`formula-ocr`
   - 示例参考：[examples/formula-ocr-example.md](examples/formula-ocr-example.md)

10. **题目识别**
    - 触发意图：当用户上传包含习题/考题的图片，需**仅提取题目文本**（不含解答、批注或无关内容），并保留题号、题干结构，用于教育题库构建或题目检索。
    - 场景 scene 标识：`question-ocr`
    - 示例参考：[examples/question-ocr-example.md](examples/question-ocr-example.md)

11. **驾驶证识别**
    - 触发意图：当用户存在识别驾驶证图片、提取证件关键信息（如证号、姓名、住址、有效期等）、将非结构化图像转化为结构化数据，或应用于身份核验、交通管理等场景的意图。
    - 场景 scene 标识：`driver-license-ocr`
    - 示例参考：[examples/driver-license-ocr-example.md](examples/driver-license-ocr-example.md)

12. **行驶证识别**
    - 触发意图：当用户存在识别行驶证图片、提取证件关键信息（包括但不限于证号、姓名、住址、有效期、准驾车型等）、将行驶证影像转化为结构化数据，或应用于身份核验、交通管理及汽车租赁等场景的意图。
    - 场景 scene 标识：`vehicle-license-ocr`
    - 示例参考：[examples/vehicle-license-ocr-example.md](examples/vehicle-license-ocr-example.md)

13. **英文发票识别**
    - 触发意图：当用户存在识别英文商业发票图片、提取单据关键信息（包括但不限于发票号、日期、买卖双方信息、商品明细、金额及税额等）、将非结构化英文单据转化为结构化数据，或应用于跨境贸易单证处理、海外费用报销及国际化财务自动化审核等场景的意图。
    - 场景 scene 标识：`commercial-invoice-ocr`
    - 示例参考：[examples/commercial-invoice-ocr-example.md](examples/commercial-invoice-ocr-example.md)

14. **医疗报告单识别**
    - 触发意图：当用户存在识别医疗报告单图片、提取报告关键信息（包括但不限于检验项目、结果、参考值等）、将医疗报告影像转化为结构化数据，或应用于电子病历归档、健康数据分析及远程医疗辅助诊断等场景的意图。
    - 场景 scene 标识：`medical-report-ocr`
    - 示例参考：[examples/medical-report-ocr-example.md](examples/medical-report-ocr-example.md)

15. **药检报告识别**
    - 触发意图：当用户存在识别药品检验报告单图片、提取药品名称、批号、检验项目、检验结果、标准值及结论等关键信息、将药检报告影像转化为结构化数据，或应用于药品质量追溯、GMP 合规审计及药品监管等场景的意图。
    - 场景 scene 标识：`pharmaceutical-inspection-report`
    - 示例参考：[examples/pharmaceutical-inspection-report-example.md](examples/pharmaceutical-inspection-report-example.md)

16. **营业执照识别**
    - 触发意图：当用户存在识别营业执照图片、提取证件关键信息（包括但不限于统一社会信用代码、名称、类型、法定代表人、经营范围等）、将执照影像转化为结构化数据，或应用于企业身份核验、工商注册自动化、供应链准入审核及金融风控等场景的意图。
    - 场景 scene 标识：`business-license-ocr`
    - 示例参考：[examples/business-license-ocr-example.md](examples/business-license-ocr-example.md)

17. **商品图片识别**
    - 触发意图：当用户存在识别商品图片或商品包装中的文字信息、提取包装或标签上的内容（包括但不限于商品名称、品牌、规格、成分、生产信息、使用说明、条码等）、将商品包装图片转化为文字或结构化数据，或应用于商品信息录入、商品上架、商品检索及商品信息分析等场景的意图。
    - 场景 scene 标识：`product-image-ocr`
    - 示例参考：[examples/product-image-ocr-example.md](examples/product-image-ocr-example.md)

18. **图片翻译**
    - 触发意图：当用户存在将图片中的文字翻译为其他语言、生成保留原图排版的译文图片，或应用于多语言文档翻译、跨语言沟通等场景的意图。
    - 场景 scene 标识：`pic-translate`
    - 示例参考：[examples/pic-translate-example.md](examples/pic-translate-example.md)

19. **通用文字提取（兜底意图）**
    - 触发意图：当用户指令中不包含上述任何具体场景，仅表达提取纯文字意图时。
    - 场景 scene 标识：`general-ocr`
    - 示例参考：[examples/general-ocr-example.md](examples/general-ocr-example.md)

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
- [examples/](examples/) — 19 个场景各自的输入/预期输出示例

## 文件结构

- `SKILL.md` — 本文档（意图分发 + 通用规范）
- `scripts/scan.py` — 主执行脚本（Python 3.9+）
- `scripts/common/*.py` — 基础类库
- `references/*.md` — 详细参考文档（隐私、实现细节、排错）
- `examples/*.md` — 19 个场景各自的输入/预期输出示例
