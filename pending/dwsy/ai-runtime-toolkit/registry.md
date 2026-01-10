---
name: toolkit-registry
description: AI Runtime工具装备系统主索引和注册表
category: registry
version: 2.0.0
last_updated: 2025-11-14
---

# AI Runtime 工具装备系统 - 主索引

[![Skill](https://img.shields.io/badge/Skill-AI%20Runtime%20Toolkit-blue)](SKILL.md)

## 快速导航

### 🎯 核心功能
- **8个内部工具**: Python/Bash/Node.js专业工具
- **10+个外部工具**: 深度整合的成熟CLI工具
- **智能发现**: 自动工具检测和元数据管理

### 🚀 快速开始
新手从这里开始，10分钟上手：
**[快速开始指南](references/guides/quickstart.md)**

### 🛠️ 工具分类

#### 内部工具（自主创建）
按语言分类的专业工具：

**[Python工具详解](../docs/references/internal-tools.md)**
- 依赖分析器、代码统计器、图形生成器、报告生成器

**[Bash工具详解](../docs/references/internal-tools.md)**
- 服务健康检查器、日志分析器、磁盘健康检查器

**[Node.js工具详解](../docs/references/internal-tools.md)**
- API测试工具

#### 外部工具（深度整合）
推荐的CLI工具生态：

**[外部工具详解](../docs/references/external-tools.md)**
- fzf、eza、bat、ripgrep、zoxide、jq等

### 📖 开发指南

#### 工具开发
**[创建新工具](../docs/guides/creating-tools.md)**
- 工具开发流程和最佳实践

#### 外部整合
**[外部工具整合](../docs/guides/external-integration.md)**
- 如何整合第三方CLI工具

### 📚 设计理念
**[工具哲学](references/core/toolkit-philosophy.md)**
- 设计原则、分类体系和发展策略

## 基本用法

```bash
# 进入工具装备目录
cd .ai-runtime/toolkit

# 查看所有工具
python3 discover-toolkit.py list

# 查看工具详情
python3 discover-toolkit.py show SERVICE-CHECK-001

# 运行工具
python3 discover-toolkit.py run dependency-analyzer . -o deps.json
```

## 系统状态

**版本**: 2.0.0
**内部工具**: 8个
**外部工具**: 10+个
**文档**: 6个核心文档
**最后更新**: 2025-11-14

## 详细文档

**[SKILL.md](SKILL.md)** - 工具装备系统核心功能
**[EXTERNAL-TOOLS-SKILL.md](EXTERNAL-TOOLS-SKILL.md)** - 外部工具专项技能
**[references/core/toolkit-philosophy.md](references/core/toolkit-philosophy.md)** - 工具哲学和设计理念
**[references/guides/quickstart.md](references/guides/quickstart.md)** - 快速开始指南

---

*基于 anthropics/skills 渐进式披露架构设计 | 整合优于创造*