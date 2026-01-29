---
name: tts-skill
description: 多引擎文本转语音技能，支持Qwen3-TTS本地音色克隆、VoiceCraft在线TTS和OpenAI TTS。使用自然语言指令即可生成高质量语音，支持通过assets下的文件名前缀选择音色。指令模式：/tts-skill [引擎] [文本内容] --voice [音色关键词]
---

# 🎙️ TTS-Skill - 多引擎文本转语音技能

一个功能强大的多引擎TTS技能，支持本地音色克隆、在线TTS服务和商业API，为用户提供完整的语音生成解决方案。

## ✨ 核心功能

### 🚀 多引擎支持
- **🔊 Qwen3-TTS** - 本地音色克隆，支持自定义参考音频
- **🌐 VoiceCraft** - 在线Microsoft Edge TTS，20+种中文语音
- **🎯 OpenAI TTS** - 商业级高质量语音生成

### 🎨 智能特性
- **🧠 语义理解** - 支持自然语言指令，自动匹配音色
- **🌍 语言检测** - 智能识别中英文，自动选择合适引擎
- **🎭 音色匹配** - 通过文件名前缀智能匹配参考音色
- **⚡ 一键生成** - 简化操作流程，快速生成高质量语音

## 📁 文件结构

```
tts-skill/
├── assets/                    # 参考音色文本（音频文件通常被 .gitignore 忽略）
│   ├── Lei.txt
│   ├── 寒冰射手.txt
│   ├── 布里茨.txt
│   └── 赵信.txt
├── engines/                   # 引擎脚本与配置
│   ├── edge-tts-cli.py
│   ├── edge-tts.config
│   ├── openai-tts-cli.py
│   ├── openai-tts.config
│   ├── qwen3-tts-cli.py
│   └── qwen3-tts.config
├── input/
│   └── text.txt               # 示例输入
├── output/                    # 默认输出目录
├── tts-skill.py               # 主入口
├── SKILL.md                   # 英文技能说明
└── SKILL.zh-CN.md             # 中文技能说明
```

## 🎯 使用方法

### 📝 基本语法

```
/tts-skill [引擎] [文本内容] --voice [音色关键词] [其他参数]
```

### 📄 从文件读取文本（--text-file / -f）

当文本较长时，推荐把内容放到文件里，然后通过 `--text-file` 读取。

**主入口用法（推荐）：**

```bash
python tts-skill.py qwen3-tts --text-file "input\\text.txt" --voice 寒冰射手
```

**说明：**

- `--text-file` 支持相对路径与绝对路径；相对路径以你执行命令时的当前目录为基准
- 如果同时传了「位置参数文本」和 `--text-file`，会优先使用 `--text-file` 的内容
- 建议文本文件使用 UTF-8 编码（支持 UTF-8 BOM）；遇到编码异常会自动尝试 GBK
- Windows 路径建议用双引号包住，并使用 `\\` 或直接用 `\`（PowerShell 下也可正常工作）

**引擎脚本直调用法（可选）：**

```bash
python engines/qwen3-tts-cli.py --text-file "input\\text.txt" --voice 寒冰射手
python engines/edge-tts-cli.py --text-file "input\\text.txt" --voice xiaoxiao
python engines/openai-tts-cli.py --text-file "input\\text.txt" --voice alloy
```

### 🎭 引擎选择

| 引擎 | 指令 | 特点 | 适用场景 |
|------|------|------|----------|
| Qwen3-TTS | `qwen3-tts` | 本地音色克隆 | 个性化语音、参考音色 |
| VoiceCraft | `edge-tts` | 在线多语音 | 快速生成、多种选择 |
| OpenAI TTS | `openai-tts` | 商业级质量 | 专业应用、高质量需求 |

### 🗣️ 自然语言指令示例

```
# 使用赵信音色生成语音
/tts-skill qwen3-tts 胜利在呼唤，勇往直前 --voice 赵信

# 使用微软晓晓朗读
/tts-skill edge-tts 你好，这是一个测试 --voice xiaoxiao

# 使用OpenAI语音生成
/tts-skill openai-tts Hello, this is a test --voice alloy
```

### 🎨 音色选择

**智能匹配规则：**
- 支持通过assets目录下的文件名前缀选择音色
- 当用户说"用赵信的声音"，自动匹配到`assets/赵信.mp3`
- 支持模糊匹配，如"温柔女声"匹配到晓晓音色

**常用音色关键词：**

#### Qwen3-TTS (本地音色)
- `赵信` - 英雄联盟赵信角色音色
- `寒冰射手` - 英雄联盟艾希角色音色
- `Lei` - Lei角色音色
- `布里茨` - 机器人布里茨音色

#### VoiceCraft (微软语音)
**女声：**
- `xiaoxiao` - 晓晓 (温柔)
- `xiaoyi` - 晓伊 (甜美)
- `xiaochen` - 晓辰 (知性)
- `xiaohan` - 晓涵 (优雅)

**男声：**
- `yunxi` - 云希 (清朗)
- `yunyang` - 云扬 (阳光)
- `yunjian` - 云健 (稳重)

#### OpenAI TTS
- `alloy` - 中性平衡
- `echo` - 深沉磁性
- `nova` - 温暖女性

## 🔧 安装配置

### Qwen3-TTS 环境配置

```bash
# 检测是否已配置qwen3-tts环境
micromamba activate qwen3-tts

# 如果未配置，运行安装脚本
python engines/qwen3-tts-cli.py --install
```

### VoiceCraft 配置

```bash
# 查看可用语音
python engines/edge-tts-cli.py --list-voices

# 查看语音风格
python engines/edge-tts-cli.py --list-styles
```

### OpenAI TTS 配置

```bash
[DEFAULT]
api_key = your_openai_api_key
api_url = https://api.openai.com/v1/audio/speech
voice = alloy
model = tts-1
speed = 1.0
```

## 🎮 详细指令

### Qwen3-TTS 引擎

```bash
# 基本使用
python engines/qwen3-tts-cli.py "要转换的文本" --voice 赵信

# 从文件读取
python engines/qwen3-tts-cli.py --text-file input.txt --voice 寒冰射手

# 指定输出路径
python engines/qwen3-tts-cli.py "测试文本" --voice 赵信 --output test.wav

# 列出可用音色
python engines/qwen3-tts-cli.py --list-voices

# 安装环境
python engines/qwen3-tts-cli.py --install
```

### VoiceCraft 引擎

```bash
# 基本使用
python engines/edge-tts-cli.py "测试文本" --voice xiaoxiao

# 调整参数
python engines/edge-tts-cli.py "测试文本" --voice yunxi --speed 1.2 --pitch 5 --style cheerful

# 从文件读取
python engines/edge-tts-cli.py --text-file script.txt --voice xiaohan
```

### OpenAI TTS 引擎

```bash
# 基本使用
python engines/openai-tts-cli.py "Hello World" --voice alloy

# 使用高质量模型
python engines/openai-tts-cli.py "测试文本" --voice nova --model tts-1-hd --speed 1.5
```

## 🎯 参数说明

### 通用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--voice` | 音色选择 | `--voice 赵信` |
| `--output` | 输出文件路径 | `--output speech.mp3` |
| `--text-file` | 文本文件输入 | `--text-file script.txt` |

## 🔧 故障排除

### 常见问题

**Q: Qwen3-TTS环境配置失败？**
A: 确保已安装Python 3.12+和Micromamba，检查网络连接，可能需要科学上网下载模型。

**Q: VoiceCraft API调用失败？**
A: 检查网络连接，确认API地址正确，尝试使用备用API端点。

**Q: OpenAI TTS认证失败？**
A: 确认API密钥正确，检查账户余额和权限设置。

---

**🎙️ TTS-Skill** - 让文字拥有声音，让创意更有温度！
