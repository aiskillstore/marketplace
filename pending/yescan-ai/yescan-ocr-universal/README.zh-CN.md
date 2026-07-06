# yescan-ocr-universal

[English](README.md) | **简体中文**

从图片中提取、识别或结构化文本——覆盖手写体、表格、证件、票据、公式、医疗报告、药检报告、营业执照、商品图、图片翻译等 19 种场景，由[夸克扫描王](https://scan.quark.cn/business)提供识别能力。

## 功能简介

向夸克扫描王服务 API 发送单张图片（URL / 本地路径 / BASE64），返回结构化 JSON 识别结果。面向 AI Agent（Claude / Codex / Claude Code / Coze 等）作为技能调用。

| 场景 scene | 能力说明 |
|---|---|
| `handwritten-ocr` | 手写中英文识别，潦草笔迹转高精度文本 |
| `table-ocr` | 表格识别，还原行列结构与单元格内容 |
| `idcard-ocr` | 身份证识别，提取姓名、证号、地址等 |
| `social-security-card-ocr` | 社保卡识别，提取姓名、社保号、银联号等 |
| `travel-permit-ocr` | 港澳通行证识别，提取证件号、有效期等 |
| `degree-certificate-ocr` | 学位证识别，提取学校、专业、证书编号等 |
| `vat-invoice-ocr` | 增值税发票识别，提取销售方、金额等 30+ 字段 |
| `train-ticket-ocr` | 火车票识别，提取车次、票价、座位等 |
| `formula-ocr` | 数学/化学公式识别，输出 LaTeX |
| `question-ocr` | 题目识别，仅提取题干文本 |
| `driver-license-ocr` | 驾驶证识别，提取证号、姓名、准驾车型等 |
| `vehicle-license-ocr` | 行驶证识别，提取号牌、车辆类型等 |
| `commercial-invoice-ocr` | 英文商业发票识别，提取买卖方、明细等 |
| `medical-report-ocr` | 医疗报告单识别，提取检验项目与结果 |
| `pharmaceutical-inspection-report` | 药检报告识别，提取药品名称、检验结果等 |
| `business-license-ocr` | 营业执照识别，提取信用代码、法人等 |
| `product-image-ocr` | 商品图文字识别，提取品名、规格、成分等 |
| `pic-translate` | 图片翻译，生成保留排版的译文图片 |
| `general-ocr` | 通用文字提取（兜底场景） |

## 快速开始

1. 在 `https://scan.quark.cn/business` 开发者后台创建应用、获取 API Key
2. 配置 API 密钥（任选其一）：
   - **方式一：环境变量**（推荐）
     ```bash
     export SCAN_WEBSERVICE_KEY=<你的密钥>
     ```
   - **方式二：配置文件**
     ```bash
     echo 'SCAN_WEBSERVICE_KEY=<你的密钥>' > ~/.yescan_env
     chmod 600 ~/.yescan_env
     ```
   > 优先读取环境变量，未设置时自动从 `~/.yescan_env` 文件加载。
3. 将本技能安装到你的 Agent 运行时（参考各平台的技能安装文档）
4. 对 Agent 说：*「帮我识别这张发票图片：/path/to/invoice.png」*

## 目录结构

```
yescan-ocr-universal/
├── SKILL.md                 # 面向 Agent 的技能定义（意图分发）
├── README.md                # 英文说明
├── README.zh-CN.md          # 中文说明
├── LICENSE                  # MIT
├── SECURITY.md              # 安全说明与数据流向
├── scripts/
│   ├── scan.py              # 入口脚本
│   └── common/              # 扫描王 API 客户端、文件保存、参数校验等
├── references/
│   ├── privacy.md           # 数据流向、密钥配置、轮换
│   ├── implementation.md    # 客户端脚本行为、响应字段
│   └── troubleshooting.md   # 错误码与常见问题
└── examples/
    ├── handwritten-ocr-example.md
    ├── table-ocr-example.md
    ├── idcard-ocr-example.md
    ├── social-security-card-ocr-example.md
    ├── travel-permit-ocr-example.md
    ├── degree-certificate-ocr-example.md
    ├── vat-invoice-ocr-example.md
    ├── train-ticket-ocr-example.md
    ├── formula-ocr-example.md
    ├── question-ocr-example.md
    ├── driver-license-ocr-example.md
    ├── vehicle-license-ocr-example.md
    ├── commercial-invoice-ocr-example.md
    ├── medical-report-ocr-example.md
    ├── pharmaceutical-inspection-report-example.md
    ├── business-license-ocr-example.md
    ├── product-image-ocr-example.md
    ├── pic-translate-example.md
    └── general-ocr-example.md
```

## 运行要求

- Python 3.9+
- 配置 `SCAN_WEBSERVICE_KEY` 环境变量（或 `~/.yescan_env`）
- 网络可访问 `scan-business.quark.cn`
- 单张图片 ≤ 5 MB，格式限 jpg/jpeg/png/gif/bmp/webp/tiff/wbmp
- 不支持视频、批量、实时摄像头流

## 详细文档

- [SKILL.md](SKILL.md) — 意图分发 + 执行规范
- [SECURITY.md](SECURITY.md) / [references/privacy.md](references/privacy.md) — 数据流向与密钥管理
- [references/implementation.md](references/implementation.md) — 客户端脚本行为与响应字段
- [references/troubleshooting.md](references/troubleshooting.md) — 错误码与排错
- [examples/](examples/) — 19 个场景各自的输入/预期输出示例

## 安全

本技能会将用户提供的图片发送到第三方 API。处理敏感数据前，请阅读 [SECURITY.md](SECURITY.md) 与 [references/privacy.md](references/privacy.md)。

## 许可

[MIT](LICENSE)

## 作者

[yescan-ai](https://github.com/yescan-ai)
