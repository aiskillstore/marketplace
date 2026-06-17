# yescan-scan-universal

[English](README.md) | **简体中文**

对图片进行画质增强、去噪、去瑕疵（手写、水印、阴影、摩尔纹、底色）以及裁剪矫正、素描转换等视觉优化，由[夸克扫描王](https://scan.quark.cn/business)提供处理能力。

## 功能简介

向夸克扫描王服务 API 发送单张图片（URL / 本地路径 / BASE64），返回增强后的图片并保存到系统临时目录。面向 AI Agent（Claude / Codex / Claude Code / Coze 等）作为技能调用。

| 场景 scene | 能力说明 |
|---|---|
| `exam-enhance` | 试卷/手写笔记转高清电子文档，去噪、背景纯净化 |
| `image-hd-enhance` | 模糊、昏暗、老旧照片一键画质增强 |
| `certificate-enhance` | 证件票据智能清晰化，关键信息清晰可辨 |
| `remove-handwriting` | 精准去除手写笔迹，完整还原印刷原件 |
| `remove-watermark` | 去除文字/Logo/标记水印，不损伤背景 |
| `remove-shadow` | 去除拍摄阴影，还原均匀亮度 |
| `remove-screen-pattern` | 去除屏幕摩尔纹与反光，文字清晰可读 |
| `remove-background-color` | 去底色，彩色文档转纯白背景黑字 |
| `image-crop-rectify` | 自动裁边 + 透视矫正，歪斜照片秒变规整 |
| `sketch-drawing` | 照片转素描/速写艺术风格 |
| `extract-lineart` | 提取纯净线稿，用于创作或设计 |
| `scan-contract` | 合同/协议画质优化，清晰归档 |
| `scan-document` | 通用文档扫描增强（兜底场景） |

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
4. 对 Agent 说：*「帮我增强这张模糊的文档照片：/path/to/image.png」*

## 目录结构

```
yescan-scan-universal/
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
    ├── exam-enhance-example.md
    ├── image-hd-enhance-example.md
    ├── certificate-enhance-example.md
    ├── remove-handwriting-example.md
    ├── remove-watermark-example.md
    ├── remove-shadow-example.md
    ├── remove-screen-pattern-example.md
    ├── remove-background-color-example.md
    ├── image-crop-rectify-example.md
    ├── sketch-drawing-example.md
    ├── extract-lineart-example.md
    ├── scan-contract-example.md
    └── scan-document-example.md
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
- [examples/](examples/) — 13 个场景的典型输入/预期输出示例

## 安全

本技能会将用户提供的图片发送到第三方 API。处理敏感数据前，请阅读 [SECURITY.md](SECURITY.md) 与 [references/privacy.md](references/privacy.md)。

## 许可

[MIT](LICENSE)

## 作者

[yescan-ai](https://github.com/yescan-ai)
