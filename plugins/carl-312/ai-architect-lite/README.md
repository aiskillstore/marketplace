# AI Architect Lite

[中文](#中文) | [English](#english)

---

## 中文

### 概述

**AI Architect Lite** 是一个轻量级的 Claude 技能，将 AI Architecture 模式的核心概念以最小开销引入你的项目。它保留了 `.ai_context` 记忆协议和基于 manifest 的调度系统，非常适合新项目启动或现有模式迁移。

### 核心特性

- 🧠 **外部记忆系统**：在 `.ai_context/` 目录中维护项目上下文
- 🎯 **Slash 优先调度**：基于命令的工作流，支持 manifest
- 📝 **结构化日志**：带时间戳的仅追加开发日志
- 🚀 **最小开销**：仅包含必要的文件和脚本
- 🔄 **TDD 友好**：为新手内置的迷你 TDD 工作流

### 快速开始

1. **加载技能**：将此目录添加到你的 Claude Skills
2. **初始化上下文**：技能会自动创建 `.ai_context/03_ACTIVE_TASK.md`
3. **开始工作**：使用提供的脚本或让 Claude 引导你

### 项目结构

```
ai-architect-lite/
├── SKILL.md                    # 主技能定义文件
├── README.md                   # 本文件
├── LICENSE                     # MIT 许可证
├── scripts/
│   ├── append_log.py          # 记录开发动作
│   └── plan_helper.py         # 生成迷你执行计划
├── references/
│   ├── lite-protocol.md       # 协议规范
│   └── superpowers-lite.md    # 最佳实践指南
└── assets/                     # 为未来模板预留
```

### 使用示例

#### 1. 追加开发日志

```bash
python scripts/append_log.py \
  --note "初始化设置" \
  --action "初始化项目" \
  --changes "创建 .ai_context 结构" \
  --outcome "成功" \
  --next "开始实现功能"
```

#### 2. 生成迷你计划

```bash
python scripts/plan_helper.py \
  --goal "构建用户认证" \
  --constraints "使用 JWT 令牌" \
  --steps "设计,实现,测试" \
  --validation "运行 pytest 测试套件"
```

### 适用场景

- ✅ 使用 AI 辅助启动新项目
- ✅ 将现有项目迁移到结构化 AI 工作流
- ✅ 需要轻量级记忆/上下文管理
- ✅ 希望自动维护开发日志
- ✅ 偏好命令驱动的 AI 交互

### 环境要求

- Python 3.8+
- Claude Desktop 或兼容的支持 Skills 的 AI 助手

### 贡献

欢迎贡献！请随时提交 issue 或 pull request。

### 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---


## English

### Overview

**AI Architect Lite** is a lightweight Claude Skill that brings the core concepts of AI Architecture pattern into your projects with minimal overhead. It maintains the `.ai_context` memory protocol and manifest-driven dispatch system, perfect for bootstrapping new projects or porting existing patterns.

### Key Features

- 🧠 **External Memory System**: Maintains project context in `.ai_context/` directory
- 🎯 **Slash-First Dispatch**: Command-driven workflow with manifest support
- 📝 **Structured Logging**: Append-only development logs with timestamps
- 🚀 **Minimal Overhead**: Only essential files and scripts
- 🔄 **TDD-Friendly**: Built-in mini-TDD workflow for beginners

### Quick Start

1. **Load the Skill**: Add this directory to your Claude Skills
2. **Initialize Context**: The skill will create `.ai_context/03_ACTIVE_TASK.md` automatically
3. **Start Working**: Use the provided scripts or let Claude guide you

### Project Structure

```
ai-architect-lite/
├── SKILL.md                    # Main skill definition
├── README.md                   # This file
├── LICENSE                     # MIT License
├── scripts/
│   ├── append_log.py          # Log development actions
│   └── plan_helper.py         # Generate mini execution plans
├── references/
│   ├── lite-protocol.md       # Protocol specification
│   └── superpowers-lite.md    # Best practices guide
└── assets/                     # Reserved for future templates
```

### Usage Examples

#### 1. Append a Development Log

```bash
python scripts/append_log.py \
  --note "Initial setup" \
  --action "Initialize project" \
  --changes "Created .ai_context structure" \
  --outcome "Success" \
  --next "Start implementing features"
```

#### 2. Generate a Mini Plan

```bash
python scripts/plan_helper.py \
  --goal "Build user authentication" \
  --constraints "Use JWT tokens" \
  --steps "design,implement,test" \
  --validation "Run pytest suite"
```

### When to Use

- ✅ Starting a new project with AI assistance
- ✅ Migrating existing projects to structured AI workflows
- ✅ Need lightweight memory/context management
- ✅ Want to maintain development logs automatically
- ✅ Prefer command-driven AI interactions

### Requirements

- Python 3.8+
- Claude Desktop or compatible AI assistant with Skills support

### Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### License

MIT License - see [LICENSE](LICENSE) file for details.

---


**Made with ❤️ for the Claude Skills community**
