# yescan

夸克扫描王一站式图片处理技能。支持 36 个场景，覆盖 OCR 识别、图像增强、文档转换、AIGC 生成四大能力。

## 能力概览

| 类别 | 场景数 | 典型用途 |
|---|---|---|
| OCR 识别 | 19 | 身份证、发票、表格、手写体、公式等文字提取 |
| 图像增强 | 13 | 去水印、去阴影、去手写、矫正裁剪、画质增强等 |
| 文档转换 | 3 | 图片转 Word / Excel / PDF |
| AIGC 生成 | 1 | 证件照生成 |

## 快速开始

### 1. 安装

```bash
pip3 install yescan
```

### 2. 配置 API Key

```bash
yescan config set SCAN_WEBSERVICE_KEY <your_api_key>
```

> 获取 API Key：https://scan.quark.cn/business → 开发者后台

### 3. 使用

```bash
# 查看所有场景
yescan --list-scenes

# OCR 识别
yescan --scene idcard-ocr --path ./idcard.jpg

# 图像增强
yescan --scene remove-watermark --path ./img.jpg

# 文档转换
yescan --scene image-to-excel --path ./table.jpg

# 查看单个场景的参数
yescan --list-scenes id-photo
```

## 设计理念

- **CLI-first**：CLI 自解释，`--list-scenes` 输出包含意图描述和参数详情
- **Agent-native**：SKILL.md 定义 PEV 协议（Plan → Execute → Verify）与约束，Agent 自主决策场景匹配
- **动态发现**：所有场景和参数通过 CLI 动态查询，不硬编码

## 文件结构

```
yescan-universal/
├── SKILL.md                        ← Agent 技能契约（PEV 协议 + 约束）
├── references/
│   ├── privacy.md                  ← 隐私、数据流向与密钥安全
│   ├── troubleshooting.md          ← 错误码与排错
│   └── implementation.md           ← 实现细节：CLI 行为与响应字段
├── SECURITY.md                     ← 安全策略
├── README.md                       ← 本文档
└── README.en.md                    ← English README
```

## 相关链接

- [夸克扫描王开放平台](https://scan.quark.cn/business)
- [SKILL.md](SKILL.md) — Agent 技能契约
- [SECURITY.md](SECURITY.md) — 安全策略
