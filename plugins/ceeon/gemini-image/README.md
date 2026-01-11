# Gemini Image Skill

Claude Code Skill，通过自然语言生成图片。支持文生图和图生图。

## 获取 API Key

1. 访问 [ismaque.org/register](https://ismaque.org/register?aff=npk7)
2. 注册账号并获取 API Key
3. 将 Key 填入 `secrets.md` 文件中

## 安装

```bash
# 1. 复制到 Claude Code skills 目录
cp -r gemini-image-skill ~/.claude/skills/gemini-image

# 2. 复制模板文件并填入 API Key
cd ~/.claude/skills/gemini-image
cp secrets.example.md secrets.md

# 3. 编辑 secrets.md，填入你的 API Key
nano secrets.md
```

重启 Claude Code 即可使用。

## 使用示例

直接对 Claude 说：

| 说法 | 效果 |
|-----|------|
| "画一只可爱的小猫" | 文生图，标准模型 |
| "用 4K 模型生成日落图片" | 文生图，4K 超清 |
| "画一张 16:9 的山水画" | 文生图，横版宽屏 |
| "根据这张图 URL 画类似的" | 图生图 |

## 文件说明

```
gemini-image/
├── SKILL.md      # Skill 入口和调用指令
├── config.md     # API 配置（模型、尺寸选项）
├── secrets.md    # API Key（需填入你的密钥）
└── README.md     # 说明文档
```

## 支持的模型

| 模型 | 说明 |
|-----|------|
| `gemini-3-pro-image-preview` | 标准版（默认） |
| `gemini-3-pro-image-preview-2k` | 2K 高清 |
| `gemini-3-pro-image-preview-4k` | 4K 超清 |

## 支持的尺寸

`1:1`（默认）、`16:9`、`9:16`、`4:3`、`3:4`、`3:2`、`2:3`、`4:5`、`5:4`、`21:9`
