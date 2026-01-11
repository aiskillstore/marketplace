# AI Runtime 记忆系统

[![Skill](https://img.shields.io/badge/Skill-AI%20Runtime%20Memory-blue)](SKILL.md)

## 快速开始

### 使用技能系统
```bash
# 通过anthropics/skills加载
claude --skill ai-runtime-memory
```

### 直接查询
```bash
cd .ai-runtime/memory

# 查看今天的事件
python3 memory_cli.py query --where "date='$(date +%Y-%m-%d)'"

# 使用便捷脚本
./scripts/memory-query.sh today
```

## 系统概述

AI Runtime的记忆系统采用分层架构：

- **短期记忆** (`short-term/`): 当前会话上下文，自动清理
- **长期记忆** (`long-term/`): 跨项目技术知识，结构化存储
- **情景记忆** (`episodic/`): 项目历史事件，SQL风格查询

## 核心工具

- **[memory_cli.py](memory_cli.py)**: 命令行查询工具
- **[memory_discovery.py](memory_discovery.py)**: 编程接口和解析引擎
- **[scripts/memory-query.sh](scripts/memory-query.sh)**: 便捷查询脚本

## 详细文档

- **[SKILL.md](SKILL.md)** - 技能定义和核心说明
- **[references/core/architecture.md](references/core/architecture.md)** - 系统架构详解
- **[references/guides/tools.md](references/guides/tools.md)** - 工具使用指南
- **[references/advanced/maintenance.md](references/advanced/maintenance.md)** - 维护指南
- **[references/examples/examples.md](references/examples/examples.md)** - 使用示例
- **[README-complete.md](README-complete.md)** - 完整参考文档

## 相关链接

- [宪法文档](../constitution.md)
- [命令系统](../commands/)
- [认知记录](../cognition/)

---

*基于 anthropics/skills 渐进式披露架构设计*
