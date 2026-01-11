---
name: ai-runtime-toolkit
description: AI Runtime工具装备系统，支持8个内部专业工具和10+个外部CLI工具的整合管理，提供工具发现、执行和配置功能，遵循整合优于创造的设计理念
license: MIT
version: 2.0.0
---

# AI Runtime 工具装备系统

## 概述

工具装备是AI Runtime的**外置能力扩展系统**，遵循"**整合 > 创造**"的核心理念，通过智能整合成熟的CLI工具和自主创建的专业工具，实现认知能力的有效扩展。

## 核心能力

### 双重工具体系
- **内部工具**: AI Runtime自主创建的专业工具（8个）
- **外部工具**: 深度整合的成熟CLI工具（10+个）

### 智能发现系统
- 自动工具检测和注册
- 元数据驱动的管理机制
- 命令行和编程接口双重支持

## 快速开始

### 查看所有工具
```bash
# 进入工具装备目录
cd toolkit

# 查看所有工具
python3 discover-toolkit.py list

# 查看外部工具
python3 discover-toolkit.py list --external
```

### 使用工具
```bash
# 查看工具详情
python3 discover-toolkit.py show SERVICE-CHECK-001

# 运行工具
python3 discover-toolkit.py run dependency-analyzer . -o deps.json

# 搜索工具
python3 discover-toolkit.py search monitor
```

## 工具分类

### 内部工具（自主创建）
- **Python工具**: 依赖分析器、代码统计器、图形生成器、报告生成器
- **Bash工具**: 服务健康检查器、日志分析器、磁盘健康检查器
- **Node.js工具**: API测试工具

### 外部工具（深度整合）
- **基础必备**: fzf、eza、bat、ripgrep、zoxide、jq
- **搜索增强**: fd、ripgrep
- **数据处理**: jq
- **界面优化**: fzf、eza、bat、starship

## 渐进式披露文档架构

基于 anthropics/skills 设计，按需加载详细信息：

### 核心理念
- **[工具哲学](references/core/toolkit-philosophy.md)** - 设计理念、分类体系和发展策略

### 使用指南
- **[快速开始](references/guides/quickstart.md)** - 10分钟上手工具装备系统

### 详细参考
- **[内部工具详解](../docs/references/internal-tools.md)** - 8个自主创建工具的详细说明
- **[外部工具集成](../docs/references/external-tools.md)** - 10+个CLI工具的整合指南

### 开发指南
- **[创建新工具](../docs/guides/creating-tools.md)** - 工具开发流程和最佳实践
- **[外部工具整合](../docs/guides/external-integration.md)** - 整合第三方CLI工具

## 设计理念

### 整合优于创造
- **成熟工具**: 使用经过社区验证的CLI工具
- **专注专业**: 每个工具只做一件事，做到极致
- **认知卸载**: 直接使用，无需重复开发

### 元数据驱动
- **.meta.yml**: 工具元数据标准格式
- **自动发现**: 基于文件系统结构自动注册
- **类型安全**: 明确的工具分类和版本管理

## 使用场景

### 代码分析
```bash
# 分析项目依赖
python3 discover-toolkit.py run dependency-analyzer . -o deps.json

# 生成代码统计
python3 discover-toolkit.py run code-stats src/ -o stats.json
```

### 系统监控
```bash
# 检查服务健康
python3 discover-toolkit.py run service-check http://localhost:3000

# 分析日志文件
python3 discover-toolkit.py run log-analyzer /var/log/app.log --level ERROR
```

### 数据处理
```bash
# 处理JSON数据
cat data.json | jq '.items[] | select(.status == "active")'

# 搜索代码
rg "TODO|FIXME" src/
```

## 相关系统

- **[宪法文档](../.ai-runtime/constitution.md)** - 治理原则和约束
- **[记忆系统](../memory/)** - 分层记忆管理
- **[认知记录](../cognition/)** - 分析洞察和探索报告
- **[命令系统](../commands/)** - 运行时命令和交互

## 版本信息

- **版本**: 2.0.0
- **内部工具**: 8个
- **外部工具**: 10+个
- **最后更新**: 2025-11-14

---

*基于 anthropics/skills 渐进式披露架构设计*
