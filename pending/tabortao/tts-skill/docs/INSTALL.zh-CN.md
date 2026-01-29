# 🔧 TTS-Skill 安装指南

## 📋 系统要求

- **操作系统**: Windows 10+, macOS 10.15+, Linux
- **Python**: 3.8+
- **内存**: 4GB+ RAM
- **存储**: 10GB+ 可用空间
- **网络**: 需要网络连接 (VoiceCraft和OpenAI需要)
- **GPU**: 推荐4GB+显存 (仅Qwen3-TTS需要)

## 🚀 快速安装

### 1. 基础环境

```bash
# 克隆项目
git clone <your-repo>/tts-skill.git
cd tts-skill

# 验证Python版本
python --version  # 需要3.8+
```

### 2. Qwen3-TTS 环境配置

```bash
# 使用自动安装脚本
python tts-skill.py --install

# 或者手动安装
python engines/qwen3-tts-cli.py --install
```

### 3. 验证安装

```bash
# 检查所有引擎
python tts-skill.py --list-engines

# 查看可用音色
python tts-skill.py --list-voices

# 显示帮助
python tts-skill.py --help
```

## 🔧 详细配置

### Qwen3-TTS 手动配置

Qwen3-TTS支持通过配置文件自定义设置。首先创建配置文件：

```bash
# 创建或编辑配置文件
nano engines/qwen3-tts.config

# 主要配置项示例:
[Qwen3-TTS]
model_dir = ./Qwen3-TTS-12Hz-0.6B-Base
default_voice = 赵信
output_format = wav
device = auto
```

#### Windows 用户

```powershell
# 1. 安装Python 3.12+
# 下载地址: https://www.python.org/downloads/

# 2. 安装Micromamba
Invoke-Expression ((Invoke-WebRequest -Uri https://micro.mamba.pm/install.ps1 -UseBasicParsing).Content)

# 3. 创建虚拟环境
micromamba create -n qwen3-tts python=3.12 -y

# 4. 激活环境
micromamba activate qwen3-tts

# 5. 安装依赖
pip install -U qwen-tts modelscope

# 6. 下载模型
modelscope download --model Qwen/Qwen3-TTS-12Hz-0.6B-Base --local_dir ./engines/Qwen3-TTS-12Hz-0.6B-Base
```

#### Linux/macOS 用户

```bash
# 1. 安装Python 3.12+
# Ubuntu/Debian: sudo apt install python3.12
# macOS: brew install python@3.12

# 2. 安装Micromamba
curl -Ls https://micro.mamba.pm/install.sh | sh

# 3. 创建虚拟环境
micromamba create -n qwen3-tts python=3.12 -y

# 4. 激活环境
micromamba activate qwen3-tts

# 5. 安装依赖
pip install -U qwen-tts modelscope

# 6. 下载模型
modelscope download --model Qwen/Qwen3-TTS-12Hz-0.6B-Base --local_dir ./engines/Qwen3-TTS-12Hz-0.6B-Base
```

### VoiceCraft 配置

VoiceCraft使用在线API，无需特殊配置：

```bash
# 查看可用语音
python engines/edge-tts-cli.py --list-voices

# 查看语音风格
python engines/edge-tts-cli.py --list-styles

# 修改配置文件 (可选)
nano engines/edge-tts.config
```

### OpenAI TTS 配置

1. **获取API密钥**
   - 访问 [OpenAI Platform](https://platform.openai.com/)
   - 创建账户并获取API密钥

2. **创建配置文件**

```bash
# 创建配置文件 (如果不存在)
nano engines/openai-tts.config

# 编辑配置文件
[OpenAI]
api_key = your_openai_api_key_here
base_url = https://api.openai.com/v1
voice = alloy
model = tts-1
speed = 1.0
```

## 🎯 首次使用测试

### 测试 VoiceCraft (推荐首次测试)

```bash
# 基本测试
python tts-skill.py edge-tts "你好，世界！" --voice xiaoxiao

# 指定输出文件
python tts-skill.py edge-tts "测试文本" --voice yunxi --output test.mp3

# 调整参数
python tts-skill.py edge-tts "重要通知" --voice xiaoyan --speed 0.8 --style serious
```

### 测试 Qwen3-TTS

```bash
# 确保环境已安装
python tts-skill.py --install

# 使用默认音色
python tts-skill.py qwen3-tts "德玛西亚！" --voice 赵信

# 使用其他音色
python tts-skill.py qwen3-tts "测试文本" --voice 寒冰射手
```

### 测试 OpenAI TTS

```bash
# 确保已配置API密钥
python tts-skill.py openai-tts "Hello World" --voice alloy

# 使用高质量模型
python tts-skill.py openai-tts "测试文本" --voice nova --model tts-1-hd
```

## 🔧 故障排除

### 常见问题

#### Q: Python版本不兼容？
A: 确保使用Python 3.8-3.12版本，Qwen3-TTS需要Python 3.12。

#### Q: Micromamba安装失败？
A: 尝试手动安装：
- Windows: 使用PowerShell运行安装脚本
- Linux/macOS: 使用curl下载安装脚本

#### Q: Qwen3-TTS模型下载失败？
A: 检查网络连接，可能需要科学上网，或者手动下载模型。可以在配置文件中指定自定义模型路径。

#### Q: Qwen3-TTS配置文件如何设置？
A: 编辑 `engines/qwen3-tts.config` 文件，主要配置 `model_dir` 指向您的模型目录。

#### Q: OpenAI配置文件如何设置？
A: 编辑 `engines/openai-tts.config` 文件，主要配置 `api_key` 为您的OpenAI API密钥。

#### Q: VoiceCraft连接超时？
A: 检查网络连接，尝试使用备用API端点。

#### Q: OpenAI认证失败？
A: 确认API密钥正确，检查账户余额和权限。

### 调试信息

```bash
# 启用详细输出
python engines/qwen3-tts-cli.py "测试" --voice 赵信 --verbose

# 检查Python路径
which python
python --version

# 检查虚拟环境
micromamba env list
micromamba activate qwen3-tts
pip list | grep qwen
```

## 📁 项目结构说明

```
tts-skill/
├── .trae/
│   └── plans/                # 任务计划（Trae）
├── assets/                   # 参考音色文本（音频文件通常被 .gitignore 忽略）
│   ├── Lei.txt
│   ├── 寒冰射手.txt
│   ├── 布里茨.txt
│   └── 赵信.txt
├── engines/                  # TTS引擎目录
│   ├── edge-tts-cli.py
│   ├── edge-tts.config
│   ├── openai-tts-cli.py
│   ├── openai-tts.config
│   ├── qwen3-tts-cli.py
│   └── qwen3-tts.config
├── input/
│   └── text.txt              # 示例输入
├── output/                   # 默认输出目录
├── tts-skill.py              # 主入口脚本
├── INSTALL.md                # 英文安装指南
├── INSTALL.zh-CN.md          # 中文安装指南（本文件）
├── README.md                 # 英文说明
├── README.zh-CN.md           # 中文说明
├── SKILL.md                  # 英文技能说明
└── SKILL.zh-CN.md            # 中文技能说明
```

## 🚀 性能优化

### Qwen3-TTS 优化

```bash
# 安装FlashAttention减少内存使用
pip install -U flash-attn --no-build-isolation

# 使用CPU模式 (低配电脑)
# 在代码中设置 device = "cpu"
```

### 网络优化

```bash
# VoiceCraft备用API端点
api_url = https://backup-tts-api.com/v1/audio/speech

# 增加超时时间
# 在代码中设置 timeout = 30
```

## 🔄 更新维护

### 更新引擎

```bash
# 更新Qwen-TTS包
micromamba activate qwen3-tts
pip install -U qwen-tts

# 更新其他依赖
pip install -U modelscope requests
```

### 添加新音色

1. **准备参考音频**
   - 格式: MP3或WAV
   - 长度: 10-60秒
   - 质量: 清晰无噪音

2. **准备参考文本**
   - 创建同名TXT文件
   - 内容与音频对应
   - UTF-8编码

3. **放置文件**
   ```
   assets/zh/新音色.mp3
   assets/zh/新音色.txt
   ```

## 📞 获取帮助

### 在线资源
- **文档**: 查看项目中的SKILL.md和README.md
- **问题**: 提交GitHub Issue
- **讨论**: 加入项目Discussions

### 联系支持
- 📧 邮箱: support@example.com
- 🐛 Bug报告: GitHub Issues
- 💬 功能建议: GitHub Discussions

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

---

**🔧 安装完成！** 现在您可以开始使用TTS-Skill的强大功能了。

*如有问题，请参考故障排除部分或联系技术支持。*
