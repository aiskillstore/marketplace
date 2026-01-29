# 🎙️ TTS-Skill - 多引擎文本转语音技能

> **TTS-Skill** 是一个功能强大的多引擎文本转语音技能，支持本地音色克隆、在线TTS服务和商业API，为用户提供完整的语音生成解决方案。

## ✨ 核心特性

### 🚀 多引擎支持
- **🔊 Qwen3-TTS** - 本地音色克隆，支持自定义参考音频
- **🌐 VoiceCraft** - 在线Microsoft Edge TTS，20+种中文语音
- **🎯 OpenAI TTS** - 商业级高质量语音生成

### 🧠 智能功能
- **语义理解** - 支持自然语言指令
- **语言检测** - 智能识别中英文
- **音色匹配** - 自动匹配参考音色
- **一键生成** - 简化操作流程

## 📦 快速开始

### 🗣️ 基本使用

```bash
# 使用赵信音色生成语音
/tts-skill qwen3-tts "胜利在呼唤，勇往直前" --voice 赵信

# 使用微软晓晓朗读
/tts-skill edge-tts "你好，这是一个测试" --voice xiaoxiao

# 使用OpenAI语音生成
/tts-skill openai-tts "Hello, this is a test" --voice alloy
```

### 🎭 音色选择

**本地音色 (Qwen3-TTS):**
- `赵信` - 英雄联盟赵信角色音色
- `寒冰射手` - 英雄联盟艾希角色音色
- `Lei` - Lei角色音色
- `布里茨` - 机器人布里茨音色

**配置文件:** `engines/qwen3-tts.config` - 可配置模型路径、默认音色等

**在线语音 (VoiceCraft):**
- 女声: `xiaoxiao`(晓晓), `xiaoyi`(晓伊), `xiaochen`(晓辰)
- 男声: `yunxi`(云希), `yunyang`(云扬), `yunjian`(云健)

**商业语音 (OpenAI):**
- `alloy` - 中性平衡
- `echo` - 深沉磁性
- `nova` - 温暖女性
- `fable` - 轻快活泼
- `onyx` - 严肃有力
- `shimmer` - 清晰悦耳

**配置文件:** `engines/openai-tts.config` - 需配置API密钥

## 🔧 安装配置

### 环境要求
- Python 3.8+
- 网络连接 (VoiceCraft和OpenAI需要)
- GPU (Qwen3-TTS推荐)

### Qwen3-TTS 配置

```bash
# 安装环境
python engines/qwen3-tts-cli.py --install

# 验证安装
python engines/qwen3-tts-cli.py --list-voices

# 编辑配置文件 (可选)
nano engines/qwen3-tts.config
```

### VoiceCraft 配置

```bash
# 查看语音选项
python engines/edge-tts-cli.py --list-voices

# 查看风格选项
python engines/edge-tts-cli.py --list-styles
```

### OpenAI TTS 配置

创建配置文件 `engines/openai-tts.config`:
```ini
[OpenAI]
api_key = your_openai_api_key
voice = alloy
model = tts-1
speed = 1.0
```

## 📁 项目结构

```
tts-skill/
├── .trae/
│   └── plans/                 # 任务计划（Trae）
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
├── INSTALL.md                 # 英文安装指南
├── INSTALL.zh-CN.md           # 中文安装指南
├── README.md                  # 英文说明
├── README.zh-CN.md            # 中文说明
├── SKILL.md                   # 英文技能说明
└── SKILL.zh-CN.md             # 中文技能说明
```

## 🎯 详细功能

### Qwen3-TTS 引擎
- ✅ 本地音色克隆
- ✅ 自定义参考音频
- ✅ 中英文支持
- ✅ 智能环境检测
- ✅ 自动依赖安装

### VoiceCraft 引擎
- ✅ 20+种微软语音
- ✅ 多语言支持
- ✅ 语音风格调节
- ✅ 语速音调控制
- ✅ 流式下载

### OpenAI TTS 引擎
- ✅ 商业级语音质量
- ✅ 6种标准语音
- ✅ 高质量模型
- ✅ API密钥管理
- ✅ 错误处理

## 🎨 参数调节

### 语音参数
| 参数 | 范围 | 说明 |
|------|------|------|
| `speed` | 0.5-2.0 | 语速调节 |
| `pitch` | -50到50 | 音调调节 |
| `style` | 多种风格 | 语音风格 |

### 风格选择
- `general` - 通用风格
- `assistant` - 智能助手
- `chat` - 聊天对话
- `customerservice` - 客服专业
- `newscast` - 新闻播报

## 🚀 高级特性

### 智能路由
系统自动检测输入文本语言，智能选择最合适的引擎和音色。

### 音色匹配
支持通过文件名前缀智能匹配参考音色，无需记忆复杂的语音ID。

### 自然语言指令
支持模糊语义理解，用户可以用自然语言描述需求。

## 📋 使用示例

### 基础示例
```bash
# 生成赵信音色
/tts-skill qwen3-tts "德玛西亚！" --voice 赵信

# 生成温柔女声
/tts-skill edge-tts "今天天气真好" --voice xiaoxiao --style cheerful

# 生成英文语音
/tts-skill openai-tts "Hello World" --voice alloy --speed 1.2
```

### 高级示例
```bash
# 从文件读取长文本
/tts-skill edge-tts --text-file script.txt --voice yunxi --style newscast

# 自定义输出路径
/tts-skill qwen3-tts "测试文本" --voice 寒冰射手 --output custom.mp3

# 调整语音参数
/tts-skill edge-tts "重要通知" --voice xiaoyan --speed 0.8 --pitch 10 --style serious
```

## 🔧 故障排除

### 常见问题

**Q: Qwen3-TTS安装失败？**
A: 确保已安装Python 3.12+和Micromamba，检查网络连接。

**Q: VoiceCraft连接超时？**
A: 检查网络连接，尝试使用备用API端点。

**Q: OpenAI认证失败？**
A: 确认API密钥正确，检查账户余额。

### 调试信息
```bash
# 启用详细输出
python engines/qwen3-tts-cli.py "测试" --voice 赵信

# 检查配置文件
cat engines/qwen3-tts.config

# 检查OpenAI配置
cat engines/openai-tts.config
```

## 📈 性能优化

### 硬件建议
- **CPU**: 4核以上处理器
- **内存**: 8GB+ RAM
- **GPU**: 4GB+ 显存 (Qwen3-TTS推荐)
- **存储**: 10GB+ 可用空间

### 使用建议
1. **个性化需求** → Qwen3-TTS本地音色克隆
2. **快速生成** → VoiceCraft在线服务
3. **专业应用** → OpenAI TTS商业API

## 🎯 最佳实践

### 音色制作
1. 选择清晰、无噪音的参考音频
2. 提供代表性的文本样本
3. 使用描述性的文件名
4. 确保音频格式兼容

### 参数调优
1. 根据内容类型调整语速
2. 匹配目标角色的音调
3. 选择合适的语音风格

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 📧 邮箱: support@example.com
- 🐛 Issue: GitHub Issues
- 💬 讨论: GitHub Discussions

---

**🎙️ TTS-Skill** - 让文字拥有声音，让创意更有温度！

*从本地音色克隆到在线TTS服务，AI驱动的多引擎语音生成解决方案。*

## 🌟 星标历史

如果这个项目对你有帮助，请给个⭐️支持！

[![Star History Chart](https://api.star-history.com/svg?repos=your-repo/tts-skill&type=Date)](https://star-history.com/#your-repo/tts-skill&Date)

## 🤝 致谢

本项目使用了 [https://github.com/wangwangit/tts](https://github.com/wangwangit/tts) 的组件。特别感谢原作者对TTS社区的贡献。
