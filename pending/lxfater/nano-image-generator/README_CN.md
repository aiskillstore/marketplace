# Nano Image Generator Skill

[English](./README.md)

一个使用 Gemini 3 Pro Preview (Nano Banana Pro) 生成图片的 Claude Code skill。

## 功能特点

- **文字生成图片** - 描述你想要的，生成图片
- **参考图片支持** - 风格迁移、角色一致性（最多 14 张）
- **多种宽高比** - 正方形、竖版、横版、电影比例
- **分辨率选项** - 1K、2K、4K 输出

## 与 [livelabs-ventures/nano-skills](https://github.com/livelabs-ventures/nano-skills) 的区别

| 功能 | 原版 | 本版本 |
|------|------|--------|
| 参考图片 | ❌ 不支持 | ✅ 最多 14 张 |
| API Key 配置 | 环境变量 | 直接改代码 |

## 配置

### 1. 获取 Gemini API Key

访问: https://aistudio.google.com/apikey

### 2. 配置 API Key

编辑 `scripts/generate_image.py`，找到 `get_api_key()` 函数（约第 37 行）：

```python
def get_api_key():
    """
    Get API key.

    ⚠️ SETUP REQUIRED: Replace the placeholder below with your Gemini API key.

    Get your API key from: https://aistudio.google.com/apikey
    """
    return "YOUR_GEMINI_API_KEY_HERE"  # <-- Replace this with your API key
```

将 `YOUR_GEMINI_API_KEY_HERE` 替换为你的实际 API key：

```python
    return "AIzaSy..."  # 你的实际 key
```

## 安装

### 从本地路径安装

```bash
git clone https://github.com/YOUR_USERNAME/nano-image-generator-skill.git
```

添加到你的 `~/.claude/settings.json`：

```json
{
  "skills": [
    "/path/to/nano-image-generator-skill"
  ]
}
```

### 从 GitHub 安装

```bash
claude skill add github:YOUR_USERNAME/nano-image-generator-skill
```

## 插件结构

```
nano-image-generator-skill/
├── SKILL.md                    # Claude Code 的 skill 定义
├── README.md                   # 英文文档
├── README_CN.md                # 中文文档（本文件）
└── scripts/
    └── generate_image.py       # 图片生成脚本（在这里配置 API key）
```

## 使用方法

安装后，当你请求以下操作时，Claude Code 会自动使用此 skill：

- "生成一张...的图片"
- "创建一个...的图标"
- "设计一个 logo..."
- "做一个横幅..."
- "和这张图片一样的风格..."

## 直接使用脚本

### 基础用法

```bash
python scripts/generate_image.py "一个可爱的机器人吉祥物" --output ./robot.png
```

### 指定宽高比

```bash
python scripts/generate_image.py "网站横幅" --aspect 16:9 --output ./banner.png
```

### 使用参考图片

```bash
python scripts/generate_image.py "同一个角色在森林里" --ref ./character.png --output ./forest.png
```

### 多张参考图片

```bash
python scripts/generate_image.py "融合这两种风格" --ref ./img1.png --ref ./img2.png --output ./combined.png
```

## 选项

| 选项 | 可选值 | 默认值 | 说明 |
|------|--------|--------|------|
| `--aspect`, `-a` | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` | `1:1` | 宽高比 |
| `--size`, `-s` | `1K`, `2K`, `4K` | `2K` | 分辨率 |
| `--ref`, `-r` | 图片路径 | - | 参考图片（可重复，最多 14 张） |

## 许可证

MIT
