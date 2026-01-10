---
name: external-tools-index
description: 外部CLI工具索引 - 提供快速访问所有外部工具文档的入口
version: 2.0.0
last_updated: 2025-11-14
---

# 外部工具装备系统

[![Skill](https://img.shields.io/badge/Skill-External%20Tools-blue)](EXTERNAL-TOOLS-SKILL.md)

本文件提供外部CLI工具的快速导航。**核心理念**: **整合 > 创造**

## 快速开始

```bash
# 进入工具装备目录
cd .ai-runtime/toolkit

# 查看所有外部工具
python3 discover-toolkit.py list --external

# 搜索工具
python3 discover-toolkit.py search 'search'

# 查看工具详情
python3 discover-toolkit.py show fzf
```

## 工具分类索引

### 基础必备 ⭐⭐⭐⭐⭐
| 工具 | 用途 | 详细文档 |
|-----|-----|---------|
| [fzf](../docs/tools/external/fzf.md) | 模糊查找 | 交互式选择和搜索 |
| [eza](../docs/tools/external/eza.md) | 文件列表 | 现代化ls替代品 |
| [bat](../docs/tools/external/bat.md) | 文件查看 | 语法高亮cat替代品 |
| [ripgrep](../docs/tools/external/ripgrep.md) | 代码搜索 | 极速递归搜索 |
| [zoxide](../docs/tools/external/zoxide.md) | 目录跳转 | AI驱动的cd |
| [jq](../docs/tools/external/jq.md) | JSON处理 | 命令行JSON处理器 |

## 安装指南

### 一键安装（macOS）
```bash
brew install fzf eza zoxide fd bat ripgrep jq
```

### 一键安装（Ubuntu/Debian）
```bash
sudo apt-get install fzf ripgrep jq bat
# 其他工具见详细文档
```

## 相关资源

- **[外部工具技能](EXTERNAL-TOOLS-SKILL.md)** - 核心功能和使用指南
- **[工具装备总览](registry.md)** - 完整的工具装备系统
- **[外部工具整合详解](../docs/guides/external-integration.md)** - 如何添加更多工具
- **[完整历史文档](external-tools-complete.md)** - 完整的外部工具文档（83行）

---

**总工具数**: 10+ 个外部CLI工具
**最后更新**: 2025-11-14
**文档版本**: 2.0.0 (基于anthropics/skills模式重构)

---

*基于anthropics/skills项目的文档组织模式 | 采用渐进式披露设计原则*